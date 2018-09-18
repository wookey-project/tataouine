#!/usr/bin/perl

#---
# usage: ./gen_ld.pl <builddir> <outfile> <devmap_file>
#---

# This file generate the LaTeX documentation of the
# Wookey devmap for the SoC given in argument $1
# This is done in this very script as doxygen does not generate
# a clean and readable content for the devmap global variable.

$,=' ';

# Check the inputs
@ARGV == 3 or usage();
( -d "$ARGV[0]" ) or die "$ARGV[0] is not a directory as is ought to be";
( -f "$ARGV[1]" ) or die "$ARGV[1] is not a regular as is ought to be";
( -f "$ARGV[2]" ) or die "$ARGV[2] is not a regular as is ought to be";

my $builddir = shift;
my $outfile = shift;
my %hash;

#---
# Main
#---
open my $OUT, ">", "$outfile" or die "unable to open $outfile";

{
  local $/;
  %hash = (<> =~ /^  \{ \"([^"]+)\"\, (.*) \}\,$/mg);
}

printf $OUT "\\section{Device mapping}\n";

printf $OUT "\\definecolor{devmapgreen}{rgb}{0.1,0.6,0.1}\n";
foreach my $i (sort(keys(%hash))) {
  printf $OUT "\\subsection{${i}}\n";

  my @params = split /,?[ ]+/, $hash{"${i}"};
  my $footnote = "";

  #
  # Managing permissions
  #

  if ($params[4] =~ /0/) { $params[4] = "{\\color{orange}{No user mapping allowed}}"; }
  if ($params[6] =~ /0/) { $params[6] = "No IRQ line registered"; }
  if ($params[9] =~ /0/) { $params[9] = "{\\color{devmapgreen}{no}}"; } else { $params[9] = "{\\color{red}{yes}}"; }
  if ($params[10] =~ /0/) { $params[10] = "{\\color{devmapgreen}{no}}"; } else { $params[10] = "{\\color{red}{yes}}"; }
  if ($params[11] =~ /0/) { $params[11] = "{\\color{devmapgreen}{no}}"; } else { $params[11] = "{\\color{red}{yes}}"; }
  if ($params[12] =~ /0/) { $params[12] = "{\\color{devmapgreen}{no}}"; } else { $params[12] = "{\\color{red}{yes}}"; }
  if ($params[13] =~ /0/) { $params[13] = "{\\color{devmapgreen}{no}}"; } else { $params[13] = "{\\color{red}{yes}}"; }
  if ($i =~ "dma.-all") {
    $footnote = "{\\color{red}{This device is allowed only in unsafe DMA mode. This is only available in C/ASM kernel mode and only for debug purpose.}}\n\n";
  }
  if ($i =~ "dma.-str.") {
    $footnote = "{\\color{orange}{This device is declared here for kernel purpose. Interacting with DMA in userspace is done using the kernel secure DMA API (see kernel\\_api documentation for more information). It is {\\bf not} possible to map DMA devices in userpsace.}}\n";
  }

  printf $OUT "\n\\par About device physical properties\n\n";
  print $OUT "These properties define the device physical informations, such as mapping and size. These information are SoC specific.\n\n";
  printf $OUT "\\begin{DoxyCompactItemize}\n";
  printf $OUT "  \\item Address in memory: $params[1]\n" =~ s/_/\\_/gr;
  printf $OUT "  \\item Device size (allowed for user mapping): $params[4]\n" =~ s/_/\\_/gr;
  printf $OUT "  \\item RCC bus register: $params[2]\n" =~ s/_/\\_/gr;
  printf $OUT "  \\item RCC bus register enable bit for device: $params[3]\n" =~ s/_/\\_/gr;
  printf $OUT "  \\item Region mask (if needed): $params[5]\n" =~ s/_/\\_/gr;
  printf $OUT "  \\item IRQ number (if exists): $params[6]\n" =~ s/_/\\_/gr;
  printf $OUT "\\end{DoxyCompactItemize}\n" =~ s/_/\\_/gr;
  printf $OUT "\n\\par About device security requirements\n\n" =~ s/_/\\_/gr;
  print $OUT "These properties define the device associated security properties. They are EwoK-specific and associate the device to a list of permissions and security constraints reducing its usage by userpsace.\n\n";
  printf $OUT "\\begin{DoxyCompactItemize}\n";
  printf $OUT "  \\item Should device be mappped read-only ? $params[7]\n";
# perm:
  printf $OUT "  \\item Device needs dev-access permission ? $params[9]\n";
  printf $OUT "  \\item Device needs crypto-cfg permission ? $params[10]\n";
  printf $OUT "  \\item Device needs crypto-user permission ? $params[11]\n";
  printf $OUT "  \\item Device needs ext-io permission ? $params[12]\n";
  printf $OUT "  \\item Device needs cycles permission ? $params[13]\n";
  printf $OUT "\\end{DoxyCompactItemize}\n";
  printf $OUT "$footnote";
}

#---
# Utility functions
#---

sub usage()
{
  print STDERR "usage: $0 <builddir> <outfile> <devmap_file>";
  exit(1);
}

