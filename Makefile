# This is the root Makefile. This Makefile
# shall not be included in any other Makefile
# of the project. Use config.mk instead for
# generic target and .config variables inclusion.
# This Makefile manage the overall project
# build, based on the choice made at configuration time

IMAGE_TYPE = 1
VERSION = 1

#########################################
######### menuconfig inclusion.
# these rules are accessible only wen the configuration is done
# These rules requires a consistent .conf to use properly its content
include Makefile.conf

# generic rules for all Makefiles. These rules can be used at
# any sublevel of the sources
include Makefile.gen

#########################################
######### apps, drivers, libs inclusion

# Applications hex files, define, through app-fw-y and app-dfu-y vars, the list of
# configured applications that need to be compiled
-include apps/Makefile.objs
-include apps/Makefile.objs.gen


#########################################
######### root Makefile variables declaration

# we have to generate the list of all app hex files with
# their relative path to the root Makefile.
# first we duplicate the app name (foreach+adduffix), to
# transform ldr/ in ldr/ldr/ then we get the perfix $(BUILD_DIR)
# to all app to finish we substitute the last '/' by .hex
# this require that the app name should finish with a '/'
APPS_FW1_HEXFILES = $(patsubst %,%.fw1.hex,$(addprefix "$(BUILD_DIR)/apps/",$(foreach path, $(app-fw-y), $(addsuffix $(path),$(path)/))))
APPS_FW2_HEXFILES = $(patsubst %,%.fw2.hex,$(addprefix "$(BUILD_DIR)/apps/",$(foreach path, $(app-fw-y), $(addsuffix $(path),$(path)/))))

APPS_DFU1_HEXFILES = $(patsubst %,%.dfu1.hex,$(addprefix "$(BUILD_DIR)/apps/",$(foreach path, $(app-dfu-y), $(addsuffix $(path),$(path)/))))
APPS_DFU2_HEXFILES = $(patsubst %,%.dfu2.hex,$(addprefix "$(BUILD_DIR)/apps/",$(foreach path, $(app-dfu-y), $(addsuffix $(path),$(path)/))))

APPS_HEXFILES = $(APPS_FW1_HEXFILES)
ifeq ($(CONFIG_FIRMWARE_DUALBANK),y)
  APPS_HEXFILES += $(APPS_FW2_HEXFILES)
endif

KERNEL_FW1_HEXFILE = $(BUILD_DIR)/kernel/kernel.fw1.hex
KERNEL_FW2_HEXFILE = $(BUILD_DIR)/kernel/kernel.fw2.hex

KERNEL_DFU1_HEXFILE = $(BUILD_DIR)/kernel/kernel.dfu1.hex
KERNEL_DFU2_HEXFILE = $(BUILD_DIR)/kernel/kernel.dfu2.hex

KERNEL_HEXFILES = $(KERNEL_FW1_HEXFILE)
ifeq ($(CONFIG_FIRMWARE_DUALBANK),y)
  KERNEL_HEXFILES += $(KERNEL_FW2_HEXFILE)
endif
ifeq ($(CONFIG_FIRMWARE_MODE_MONO_BANK_DFU),y)
  KERNEL_HEXFILES += $(KERNEL_DFU1_HEXFILE)
endif

ifeq ($(CONFIG_FIRMWARE_MODE_DUAL_BANK_DFU),y)
  KERNEL_HEXFILES += $(KERNEL_DFU1_HEXFILE)
endif

showapps:
	@echo $(APPS_FW1_HEXFILES)
	@echo $(APPS_FW2_HEXFILES)

# Memory layout
MEM_LAYOUT       = $(BUILD_DIR)/layout.ld
MEM_APP_LAYOUT   = $(BUILD_DIR)/layout.apps.ld
MEM_LAYOUT_DEF   = $(PROJ_FILES)/layouts/arch/socs/$(SOC)/layout.def
MEM_APP_LAYOUT_DEF   = $(PROJ_FILES)/layouts/arch/socs/$(SOC)/layout.apps.def

# project target binaries name, based on .config
BIN_NAME         = $(CONFIG_PROJ_NAME).bin
HEX_NAME         = $(CONFIG_PROJ_NAME).hex
ELF_NAME         = $(CONFIG_PROJ_NAME).elf

DOCU             = doxygen

BUILDDFU         = $(PROJ_FILES)/tools/gen_firmware.py
BUILD_LIBECC_DIR = $(PROJ_FILES)build/$(ARCH)/$(BOARD)

# Flags (deprecated, replaced by .config)
LDFLAGS         += -T$(MEM_LAYOUT) $(AFLAGS) -fno-builtin -nostdlib

# The apps dir(s)
APPS             = apps

# the userspace drivers dir
DRVS             = drivers

# Documentation files
DOC_DIR ?= ./doc/

# local files to delete
TODEL_CLEAN = .config.old doc/doxygen $(BUILD_DIR)/$(BIN_NAME) $(BUILD_DIR)/$(HEX_NAME) $(BUILD_DIR)/$(ELF_NAME) $(BUILD_DIR)/$(BIN_NAME).sign
TODEL_DISTCLEAN = .config include $(CONFIG_BUILD_DIR) $(CONFIG_PRIVATE_DIR)

#########################################
######### root Makefile rules

# target for the classical menuconfig, the only one defined. In theory, we can
# also define make config (dialog) and make qconfig (qt) but menuconfig should
# be enough by now
menuconfig:
	$(call cmd,kconf_app_gen)
	$(call cmd,kconf_drv_gen)
	$(call cmd,kconf_lib_gen)
	$(call cmd,kconf_root)
	$(call cmd,nokconfig)
	$(call cmd,menuconfig)
	$(call cmd,mkobjlist_libs)
	$(call cmd,mkobjlist_apps)
	$(call cmd,mkobjlist_drvs)
	$(call cmd,prepare)

#########################################
# from now on, a config file must exists before executing one of the following
# rules
ifeq ($(CONFIG_DONE),y)
all: clean_kernel_headers prepare $(BUILD_DIR)/$(BIN_NAME)
else
all:
	@echo "###########################################"
	@echo "# Wookey SDK information"
	@echo "###########################################"
	@echo "No configuration set. You must first configure the project"
	@echo "This can be done by selecting an existing configuration using:"
	@echo "  $$ make defconfig_list"
	@echo "You can also create a new one using:"
	@echo "  $$ make menuconfig"
	@echo "it is highly recommended to start with an existing configuration"
endif

ifeq ("$(CONFIG_DONE)","y")

#
# As any modification in the user apps permissions or configuration impact the kernel
# generated headers, the kernel headers and as a consequence the kernel binaries need
# to be built again. We decide to require a kernel rebuilt at each all target to be
# sure that the last potential configuration or userspace layout upgrade is taken into
# account in the kernel
#
clean_kernel_headers:
	rm -rf kernel/Ada/generated/*
	rm -rf kernel/generated/*
	rm -rf $(BUILD_DIR)/kernel/kernel.*.hex

# prepare generate the include/generated/autoconf.h from the
# .config file. This allows source files to use configured values
# as defines in their code
__prepare:
	$(call cmd,kconf_app_gen)
	$(call cmd,kconf_drv_gen)
	$(call cmd,kconf_lib_gen)
	$(call cmd,nokconfig)
	$(call cmd,mkincludedir)
	$(call cmd,prepareada)
	$(call cmd,prepare)
	$(call cmd,mkobjlist_libs)
	$(call cmd,mkobjlist_apps)
	$(call cmd,mkobjlist_drvs)

prepare: $(BUILD_DIR) __prepare layout libs $(CONFIG_PRIVATE_DIR)

# generate the memory layout for the target
layout: $(MEM_LAYOUT_DEF)
	$(call if_changed,layout)

# generate the permissions header for EwoK
# from now-on, and downto the endif, these rules
# depend on the existence of the .config file. This is
# checked using the CONFIG_DONE variable. If not,
# these rules are simply ignored, please use
# make prepare and make menuconfig to create the
# .config file.

.PHONY: libs prepare loader prove externals $(DRVS) $(APPS) $(APPS_PATHS) $(BUILD_LIBECC_DIR) $(BUILD_DIR)


applet:
	$(Q)$(MAKE) -C javacard $@

$(BUILD_DIR)/kernel/kernel.fw1.hex:
	$(call cmd,prepare_kernel_header_for_fw1)
	$(Q)$(MAKE) -C kernel all EXTRA_LDFLAGS=-Tkernel.fw1.ld APP_NAME=kernel.fw1

$(BUILD_DIR)/kernel/kernel.fw2.hex:
ifeq ($(CONFIG_FIRMWARE_DUALBANK),y)
	$(call cmd,prepare_kernel_header_for_fw2)
	$(Q)$(MAKE) -C kernel all EXTRA_LDFLAGS=-Tkernel.fw2.ld APP_NAME=kernel.fw2
endif

$(BUILD_DIR)/kernel/kernel.dfu1.hex:
ifeq ($(CONFIG_FIRMWARE_MODE_MONO_BANK_DFU),y)
	$(call cmd,prepare_kernel_header_for_dfu1)
	$(Q)$(MAKE) -C kernel all EXTRA_LDFLAGS=-Tkernel.dfu1.ld APP_NAME=kernel.dfu1
endif
ifeq ($(CONFIG_FIRMWARE_MODE_DUAL_BANK_DFU),y)
	$(call cmd,prepare_kernel_header_for_dfu1)
	$(Q)$(MAKE) -C kernel all EXTRA_LDFLAGS=-Tkernel.dfu1.ld APP_NAME=kernel.dfu1
endif


$(BUILD_DIR)/kernel/kernel.dfu2.hex:
ifeq ($(CONFIG_FIRMWARE_MODE_DUAL_BANK_DFU),y)
	$(call cmd,prepare_kernel_header_for_dfu2)
	$(Q)$(MAKE) -C kernel all EXTRA_LDFLAGS=-Tkernel.dfu2.ld APP_NAME=kernel.dfu2
endif



loader: 
	$(Q)$(MAKE) -C $@ EXTRA_CFLAGS="-DLOADER"

libs:
	$(Q)$(MAKE) -C $@

$(DRVS):
	$(Q)$(MAKE) -C $@

$(APPS):
	$(Q)$(MAKE) -C $@

externals:
	$(Q)$(MAKE) -C $@

prove:
	$(Q)$(MAKE) -C kernel/$@ all && cat kernel/$@/gnatprove/gnatprove.out |head -15 > doc/sphinx/source/ewok/ada_proof.rst

################# final integration
#
# App1.fw1.elf    \
# App2.fw1.elf     -> wookey.hex -> wookey.bin
# App3.fw1.elf     |
# kernel.fw1.elf   |
# ...              |
#                  |
# App1.fw2.elf     |
# App2.fw2.elf     |
# App3.fw2.elf     |
# kernel.fw2.elf   |
# loader.elf      /
#
#
# user applications ldscripts have their sections prefixed with APP_NAME
# kernel ldscript has specific sections such as .isr_region
# these ldscript are not SoC dependent
#
# fw1.ld and fw2.ld host both app and kernel sections, mapped properly
# depending on the SoC.

# from all elf, finalize into one single binary file
$(BUILD_DIR)/loader/loader.hex: libs loader

$(APPS_FW1_HEXFILES): layout libs externals $(DRVS) $(APPS)

$(APPS_FW2_HEXFILES): layout libs externals $(DRVS) $(APPS)

$(BUILD_DIR)/$(HEX_NAME): $(APPS_HEXFILES) $(KERNEL_HEXFILES) $(BUILD_DIR)/loader/loader.hex
	$(call if_changed,final_hex)

$(BUILD_DIR)/$(BIN_NAME): $(BUILD_DIR)/$(HEX_NAME)
	$(call if_changed,final_bin)

endif # CONFIG_DONE=y

# __clean is for local complement of generic clean target.
# the generic clean target will clean $(TODEL_CLEAN) and call __clean if
# the target exist. If not, it will not
__clean:
	$(MAKE) -C apps clean
	$(MAKE) -C kernel clean
	$(MAKE) -C libs clean
	$(MAKE) -C drivers clean
	$(MAKE) -C externals clean
	$(RM) $(RMFLAGS) include

dumpconfig:
	@echo '======================'
	@echo 'ARCH         : $(ARCH)'
	@echo 'BOARD        : $(BOARD)'
	@echo 'BUILD_DIR    : $(BUILD_DIR)'
	@echo 'BIN_NAME     : $(BIN_NAME)'
	@echo 'CROSS_COMPILE: $(CROSS_COMPILE)'
	@echo 'CC           : $(CC)'
	@echo 'LD           : $(LD)'
	@echo 'AR           : $(AR)'
	@echo 'OBJCOPY      : $(OBJCOPY)'
	@echo 'GDB          : $(GDB)'
	@echo 'RANLIB       : $(RANLIB)'
	@echo 'CFLAGS       : $(CFLAGS)'
	@echo 'AFLAGS       : $(AFLAGS)'
	@echo 'DBGFLAGS     : $(DEBUG_CFLAGS)'
	@echo 'APPS_CFLAGS  : $(APPS_CFLAGS)'
	@echo '======================'
	@echo 'KERNEL_HEXFILES: $(KERNEL_HEXFILES)'
	@echo 'APPS_HEXFILES : $(APPS_HEXFILES)'
	@echo '======================'

#########################################
# these targets manage the device itself
# See the various README for complete information

burn: $(BUILD_DIR)/$(BIN_NAME)
	$(STFLASH) write $(BUILD_DIR)/$(BIN_NAME) 0x8000000

flash: burn

debug: $(ELF_NAME)
	$(GDB) -x gdbfile $(ELF_NAME)

run: $(ELF_NAME)
	$(GDB) -x gdbfile_run $(ELF_NAME)

#########################################
# these targets manage all doc-related builds

#doc: $(PROJ_FILES)/tools/kernel-doc
#	$^ -html `find -name '*.[ch]'` > doc.html 2>/dev/null

.PHONY: doc

$(DOCDIR):
	$(MKDIR) $@

doc:
	$(MAKE) -C doc

#########################################
# defconfig support, small and easy

defconfig_list:
	$(call cmd,listdefconfig)

%_defconfig:
	$(call cmd,rm_builddir)
	$(call cmd,kconf_app_gen)
	$(call cmd,kconf_drv_gen)
	$(call cmd,kconf_lib_gen)
	$(call cmd,kconf_root)
	$(call cmd,nokconfig)
	$(call cmd,mkincludedir)
	$(call cmd,defconfig)
	$(call cmd,mkobjlist_libs)
	$(call cmd,mkobjlist_apps)
	$(call cmd,mkobjlist_drvs)

#########################################
# these targets manage the test suite
test:
	$(foreach p, $(APPS_PATHS), $(Q)$(MAKE) -C $(p) &&  ) true


tests_suite: CFLAGS += -Itests/ -DTESTS

tests_suite: $(TESTSOBJ) $(ROBJ) $(OBJ) $(SOBJ) $(DRVOBJ)

tests: clean tests_suite $(LDS_GEN)
	$(CC) $(LDFLAGS) -o $(ELF_NAME) $(ROBJ) $(SOBJ) $(OBJ) $(DRVOBJ) $(TESTSOBJ)
	$(GDB) -x gdbfile_run $(ELF_NAME)


#########################################
# Rust related
# these target preemare the Rust libcore for the target
# in order to support Rust apps

libcore:
	if [ ! -f  "rust/libcore/$(TARGET)/$(RUSTBUILD)/libcore.rlib" ];then \
	    if [ ! -d  "rust/libcore/$(TARGET)/$(RUSTBUILD)/build" ];then mkdir -p \
			rust/libcore/$(TARGET)/$(RUSTBUILD)/build; \
		fi;\
		if [ ! -f  "rust/libcore/$(TARGET)/$(RUSTBUILD)/build/$(TARGET).json" ];\
			then cp $(TARGET).json rust/libcore/$(TARGET)/$(RUSTBUILD)/build/;\
		fi;\
		cd rust/libcore/$(TARGET)/$(RUSTBUILD)/build;\
		if [ ! -f  rust.tar.gz ]; then	\
			wget -q -O rust.tar.gz $(RUSTCOREURL); \
		fi;\
		tar -zx --strip-components=1 -f rust.tar.gz;\
		rm rust.tar.gz;\
		if [ ! -f  "../libcore.rlib" ]; \
			then $(RUSTC) -C opt-level=2 -Z \
			no-landing-pads --target $(TARGET) -g src/libcore/lib.rs \
			--out-dir ../; fi;\
		rm -rf ../build; \
	fi;

cleanlibcore:
	rm $(LIBCORE_PATH)/libcore.rlib


$(CONFIG_PRIVATE_DIR):
	if [ -d "$(PROJ_FILES)/javacard" ]; then \
	  if [ ! -d $@ ]; then \
		mkdir $(PROJ_FILES)/$@; \
		make -C externals keys; \
	  fi; \
	fi

