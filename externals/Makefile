PROJ_FILES = ../

VERSION = 1

#########################################
######### menuconfig inclusion.
# these rules are accessible only wen the configuration is done
# These rules requires a consistent .conf to use properly its content
include $(PROJ_FILES)/Makefile.conf

# generic rules for all Makefiles. These rules can be used at
# any sublevel of the sources
include $(PROJ_FILES)/Makefile.gen

-include Makefile.objs

.PHONY: $(EC_UTILS) std gnat hmac aes $(libs-y)

KEY2HEADER       = $(PROJ_FILES)/tools/key2header.py

##########################################
##### Libecc cryptographic library

external_targets :=

ifeq ($(CONFIG_USR_LIB_SIGN),y)
external_targets += libsign $(EC_UTILS)
endif

ifeq ($(USE_LLVM),y)
HOST_CC=$(CLANG_PATH)
else
HOST_CC=gcc
endif

all: $(external_targets)


libsign: $(BUILD_DIR)
	if test -f $(PROJ_FILES)/externals/libecc/build/ec_utils; then \
	  CFLAGS="-DWITH_LIBECC_CONFIG_OVERRIDE $(LIBSIGN_CFLAGS)" $(MAKE) BUILD_DIR="$(BUILD_DIR)" -C $(PROJ_FILES)/externals/libecc clean; \
	else \
	  mkdir -p $(PROJ_FILES)/externals/libecc/build; \
	fi; \
	if test ! -f $(BUILD_DIR)/$@/libsign.a; then \
	  mkdir -p $(BUILD_DIR)/libs/$@; \
	  $(MAKE) -C $(PROJ_FILES)/externals/libecc CFLAGS="$(LIBSIGN_CFLAGS) $(AFLAGS) $(WARN_CFLAGS) $(HARDEN_CFLAGS) -pedantic -fno-builtin -std=c99 -D_FORTIFY_SOURCE=2 $(LIB_OPTIM_CFLAGS) -ffunction-sections -fdata-sections -fno-pie -fno-pic -O3" \
	  BUILD_DIR="build" CC=$(CC) AR=$(AR) RANLIB=$(RANLIB) LIBECC_NOSTDLIB=1 build/libsign.a; \
	  cp $(PROJ_FILES)/externals/libecc/build/libsign.a $(BUILD_DIR)/libs/$@/libsign.a; \
	fi; \

$(EC_UTILS): $(BUILD_DIR)/tools
	mkdir -p $(PROJ_FILES)/externals/libecc/build; \
	CFLAGS="-DWITH_LIBECC_CONFIG_OVERRIDE $(LIBSIGN_CFLAGS)" BUILD_DIR="build" make -C $(PROJ_FILES)/externals/libecc clean; \
	CFLAGS="-DWITH_LIBECC_CONFIG_OVERRIDE $(LIBSIGN_CFLAGS) -fPIC" BUILD_DIR="build" CC=$(HOST_CC) AR=ar AS=as OBJCOPY=objcopy LD=ld RANLIB=ranlib $(MAKE) -C $(PROJ_FILES)/externals/libecc; \
	cp $(PROJ_FILES)/externals/libecc/build/ec_utils $@; \

$(BUILD_DIR)/tools:
	$(call cmd,mkdir)
