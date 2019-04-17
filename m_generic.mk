# generic verbose management
# To put more focus on warnings, be less verbose as default
# Use 'make V=1' to see the full commands
ifeq ("$(origin V)", "command line")
  KBUILD_VERBOSE = $(V)
  VERBOSE = $(V)
endif
ifndef KBUILD_VERBOSE
  KBUILD_VERBOSE = 0
endif

ifeq ($(KBUILD_VERBOSE),1)
  quiet =
  Q =
else
  quiet=quiet_
  Q = @
  VERBOSE = 0
endif

# If the user is running make -s (silent mode), suppress echoing of
# commands

ifneq ($(findstring s,$(filter-out --%,$(MAKEFLAGS))),)
  quiet=silent_
  tools_silent=s
endif

# here, we update the drivers and libs inclusion cflags
# to be relative to the current compoent build directory.
# For this, we update the CFLAGS value, replacing the
# @PROJFILES@ with the local value of $(PROJ_FILES)
#
LIBS_CFLAGS := $(subst @PROJFILES@,$(PROJ_FILES),$(LIBS_CFLAGS))
DRIVERS_CFLAGS := $(subst @PROJFILES@,$(PROJ_FILES),$(DRIVERS_CFLAGS))
APPS_CFLAGS := $(subst @PROJFILES@,$(PROJ_FILES),$(APPS_CFLAGS))



# disable directory entering/leaving printout
#MAKEFLAGS += --no-print-directory

export quiet Q KBUILD_VERBOSE MAKE MAKEFLAGS

# including Kbuild related tools for silent CC
include $(PROJ_FILES)/tools/Kbuild.include
include $(PROJ_FILES)/m_build.mk

# GENERIC TARGETS
default: all

.PHONY: clean distclean

clean:
	$(call cmd,clean)

distclean: clean
	$(call cmd,distclean)

$(BUILD_DIR):
	$(call cmd,mkdir)

ifeq (y,$(USE_LLVM))
sanitize:
	scan-build --use-cc=$(CC) --analyzer-target=thumbv7m-none-eabi --use-analyzer=$(CLANG_PATH) -enable-checker alpha.security.ArrayBoundV2 -enable-checker alpha.security.ReturnPtrRange -enable-checker alpha.core.CastToStruct -enable-checker alpha.core.DynamicTypeChecker -enable-checker alpha.core.FixedAddr -enable-checker alpha.core.IdenticalExpr -enable-checker alpha.core.PointerArithm -enable-checker alpha.core.PointerSub -enable-checker alpha.core.SizeofPtr -enable-checker alpha.core.TestAfterDivZero -enable-checker alpha.deadcode.UnreachableCode -o $(APP_BUILD_DIR)/scan make
endif

