PROJ_FILES := ../

include $(PROJ_FILES)Makefile.conf
include $(PROJ_FILES)Makefile.gen

# case of make doc without config
ifeq ($(CONFIG_PROJ_NAME),)
PROJNAME = "generic"
else
PROJNAME = $(CONFIG_PROJ_NAME)
endif

TODEL_CLEAN += pdf doxygen latex
TODEL_DISTCLEAN +=

# list of man pages (by now
#
MANS_SYSCALLS_SRC_DIR := $(PROJ_FILES)/doc/sphinx/source/ewok/syscalls
MANS_SYSCALLS_SRC := \
	$(MANS_SYSCALLS_SRC_DIR)/sys_init.rst \
    $(MANS_SYSCALLS_SRC_DIR)/sys_cfg.rst  \
    $(MANS_SYSCALLS_SRC_DIR)/sys_ipc.rst \
    $(MANS_SYSCALLS_SRC_DIR)/sys_yield.rst \
    $(MANS_SYSCALLS_SRC_DIR)/sys_get_systick.rst \
    $(MANS_SYSCALLS_SRC_DIR)/sys_reset.rst \
    $(MANS_SYSCALLS_SRC_DIR)/sys_sleep.rst \
    $(MANS_SYSCALLS_SRC_DIR)/sys_lock.rst
MANS_SYSCALLS := $(patsubst %.rst,$(BUILD_DIR)/doc/man/man2/%.2,$(notdir $(MANS_SYSCALLS_SRC)))
MANS_SYSCALLS := $(patsubst %.rst,$(BUILD_DIR)/doc/man/man2/%.2,$(notdir $(MANS_SYSCALLS_SRC)))

MANS_STD_SRC_DIR := $(PROJ_FILES)/doc/sphinx/source/std/functions
MANS_STD_SRC := \
	$(MANS_STD_SRC_DIR)/printf.rst \
	$(MANS_STD_SRC_DIR)/strlen.rst \
	$(MANS_STD_SRC_DIR)/itoa.rst   \
	$(MANS_STD_SRC_DIR)/sprintf.rst\
	$(MANS_STD_SRC_DIR)/strncpy.rst\
	$(MANS_STD_SRC_DIR)/wmalloc_init.rst\
	$(MANS_STD_SRC_DIR)/wmalloc.rst\
	$(MANS_STD_SRC_DIR)/wfree.rst\
	$(MANS_STD_SRC_DIR)/semaphore_init.rst\
	$(MANS_STD_SRC_DIR)/semaphore_trylock.rst\
	$(MANS_STD_SRC_DIR)/semaphore_release.rst
MANS_STD      := $(patsubst %.rst,$(BUILD_DIR)/doc/man/man3/%.3,$(notdir $(MANS_STD_SRC)))

show:
	@echo "MANS_SYSCALLS_SRC: $(MANS_SYSCALLS_SRC)"
	@echo "MANS_SYSCALLS:     $(MANS_SYSCALLS)"
	@echo "MANS_STD_SRC:      $(MANS_STD_SRC)"
	@echo "MANS_STD:          $(MANS_STD)"

.PHONY: $(BUILD_DIR)/doc/kernel_devmap $(BUILD_DIR)/doc/kernel_api $(BUILD_DIR)/doc/man $(BUILD_DIR)/doc/sphinx $(BUILD_DIR)/doc/libstd_api

$(BUILD_DIR)/doc/sphinx:
	$(call cmd,mkdir)
	$(call cmd,mkhtml)

sphinx: $(BUILD_DIR)/doc/sphinx

$(BUILD_DIR)/doc/kernel_api: Doxyfile.api
	$(call cmd,mkdir)
	$(call cmd,doxygen)

# TODO: this should be replaced by a formalized (YAML?) devmap which generate the C and Ada sources
# instead of parsing the sources
#$(BUILD_DIR)/doc/kernel_devmap: Doxyfile.devmap
#	$(call cmd,mkdir)
#	$(call cmd,doxygen)
#	$(call cmd,doxy_custom)

$(BUILD_DIR)/doc/libstd_api: Doxyfile.std
	$(call cmd,mkdir)
	$(call cmd,doxygen)

doc:  $(BUILD_DIR)/doc/sphinx $(BUILD_DIR)/doc/libstd_api $(BUILD_DIR)/doc/kernel_api $(BUILD_DIR)/doc/man man

$(BUILD_DIR)/doc/man/man2:
	$(call cmd,mkdir)

$(BUILD_DIR)/doc/man/man3:
	$(call cmd,mkdir)

$(MANS_SYSCALLS): $(MANS_SYSCALLS_SRC_DIR)
	$(call cmd,mkman2)

$(MANS_STD): $(MANS_STD_SRC_DIR)
	$(call cmd,mkman3)

man: $(BUILD_DIR)/doc/man/man2 $(BUILD_DIR)/doc/man/man3 $(MANS_SYSCALLS) $(MANS_STD)

all: doc

__clean:
	BUILDDIR=../$(BUILD_DIR)/doc/sphinx	make -C sphinx clean

__distclean:
	BUILDDIR=../$(BUILD_DIR)/doc/sphinx	make -C sphinx distclean
