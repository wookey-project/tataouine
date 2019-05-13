#!/usr/bin/perl -l
#

use strict;

#---
# Usage: ./gen_ld.pl <build_dir> <.config_file>
#---

# Add space between array element printing

$,=' ';

# Check the inputs
@ARGV == 2 or usage();
( -d "$ARGV[0]" ) or die "$ARGV[0] is not a directory as is ought to be";
( -f "$ARGV[1]" ) or die "$ARGV[1] is not a regular as is ought to be";

my $builddir = shift;
my %hash;

#---
# Main
#---

# Slurp the config file and parse it
get_apps_from_config();

# Iterate over all modes
for my $mode ("FW1", "FW2", "DFU1", "DFU2") {
  my $slot = 1;
  my $is_flip = 0;
  my $is_flop = 0;
  my $is_fw   = 0;
  my $is_dfu  = 0;

  if ($mode =~ "FW1") {
      $is_flip = 0xf0;
      $is_fw   = 0xf0;
  }
  if ($mode =~ "FW2") {
      $is_flop = 0xf0;
      $is_fw   = 0xf0;
  }
  if ($mode =~ "DFU1") {
      $is_flip = 0xf0;
      $is_dfu  = 0xf0;
  }
  if ($mode =~ "DFU2") {
      $is_flop = 0xf0;
      $is_dfu  = 0xf0;
  }


  # Iterate over all apps
  for my $i (grep {!/_/} sort(keys(%hash))) {

    # Leave if this app is not for current mode
    my $stem_mode=($mode=~s/[12]$//r);
    next if (not defined($hash{"${i}_${stem_mode}"}));

    open my $OUTLD, ">","$builddir/apps/\L$i/$i.$mode\E.ld"
    		or die "unable to open $builddir/apps/\L$i/$i.$mode\E.ld";

    # Check if we have specific values for slot number and stack size
    # Or use default values
    my $num_slots = $hash{"${i}_NUMSLOTS"} // 1;
    # [RB] FIXME: it should be more logical to stick to the current mode
    # slot size ...
    # DFU slots are 2*smallers than FW ones. if the task exists in both
    # mode, it uses 2n slots in DFU mode for n slots in FW mode
    if ($stem_mode eq 'DFU' and defined($hash{"${i}_FW"})) {
        $num_slots = $num_slots * 2;
    }
    my $stacksize = $hash{"${i}_STACKSIZE"} // 8192;
    my $totalslot = ${slot} + ${num_slots} - 1;

    # And here we print the template linker script with the right replacement values
    print $OUTLD <<EOF
/* \L$i\E.ld */

/* this is required to place do_starttask *before* main in the .text section */
STARTUP ( libstd.a )

ENTRY(do_starttask)

INCLUDE ../../$builddir/layout.apps.ld

__is_flip = $is_flip;
__is_flop = $is_flop;
__is_fw   = $is_fw;
__is_dfu  = $is_dfu;


/* Define output sections */
SECTIONS
{
	numslots = ${num_slots};

	/* The program code and other data goes into FLASH */
	/* this is the kernel code part */
	.text :
	{
		_s_text = .;	            /* create a global symbol at data start */
		*startup*(.text.do_starttask)
		*(.text*)
		*(.rodata)         	/* .rodata sections (constants, strings, etc.) */
		*(.rodata*)         	/* .rodata sections (constants, strings, etc.) */
		*(.glue_7)         	/* glue arm to thumb code */
		*(.glue_7t)        	/* glue thumb to arm code */
		*(.eh_frame)
		KEEP (*(.init))
		KEEP (*(.fini))
		__e_text = .;        	/* define a global symbols at end of code */
	}>${mode}_APP${slot}_APP${totalslot}

	. = ALIGN(4);

	/* used by the startup to initialize got */
	.got :
	{
		_s_got = .;
		*(.got)
		*(.got*)
		/* declaring variables for various task slots and add them to flash */
		__e_got = .;
	}>${mode}_APP${slot}_APP${totalslot}

	. = ALIGN(4);
	_s_data_in_flash = .;

	.stacking :
	{
		_s_stack = .;         /* define a global symbol after .data+.bss+.stack size content */
		. = . + ${stacksize}; /*  thread stack */
		_e_stack = .;         /* define a global symbol after .data+.bss+.stack size content */
	}>RAM_APP${slot}_APP${totalslot}

	. = ALIGN(4);

	/* Initialized data sections goes into RAM, load LMA copy after code *
	 * Used at the startup to initialize data                            */
	.data : AT (_s_data_in_flash)
	{
		_s_data = .;        /* create a global symbol at data start */
		*(.data)           /* .data sections */
		*(.data*)          /* .data* sections */
		_e_data = .;        /* define a global symbol at data end */
	}>RAM_APP${slot}_APP${totalslot}

	. = ALIGN(4);

	/* Uninitialized data section */
	.bss : AT (.)
	{
		/* This is used by the startup in order to initialize the .bss section */
		_s_bss = .;         /* define a global symbol at bss start */
		_bss_start__ = _s_bss;
		*debug.o(.bss)
		*(.bss)
		*(.bss*)
		*(COMMON)
		_e_bss = .;         /* define a global symbol at bss end */
	}>RAM_APP${slot}_APP${totalslot}

	. = ALIGN(4);

	/* Remove information from the standard libraries */
	/DISCARD/ :
	{
		libgcc.a ( * )
	}

}
EOF
      ;
    $slot += $num_slots;
  } # End of inner for

}# End of outter for


#---
# Utility functions
#---

sub usage()
{
  print STDERR "usage: $0 <build_dir> <.config_file>";
  exit(1);
}

sub get_apps_from_config()
{
  local $/;
  my $tmp=<>;

  # A config file line can be one of : empty/start with # /or start with CONFIG
  $tmp =~ /^(\s*\n|\s*#.*\n|\s*CONFIG([^=]+)=(.*)\n)*$/
  	or die "WARNING: your config file does not look correct";

  %hash = ($tmp =~ /^CONFIG_APP_([^=]+)=(.*)/mg);
}
