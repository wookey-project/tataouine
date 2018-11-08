# basic skeleton for apps
# list of activated apps are in Makefile.objs for greater
# readability

PROJ_FILES = ../
VERSION = 1
#############################

CONFIG_MK = $(PROJ_FILES)/Makefile.conf
-include $(CONFIG_MK)
-include $(PROJ_FILES)/Makefile.gen

-include Makefile.objs
-include Makefile.objs.gen

#############################
# build all

.PHONY: $(app-fw-y) $(app-dfu-y)

app-y := $(sort $(app-fw-y) $(app-dfu-y))

all: $(app-y)

$(app-y): outdir
	$(call if_changed,ldscript)
	$(call if_changed,buildapp)


#	cp $(BUILD_DIR)/libs/*/lib*.a $(BUILD_DIR)/apps/$@
#	cp $(BUILD_DIR)/drivers/*/lib*.a $(BUILD_DIR)/apps/$@
#	if [ -f $(BUILD_DIR)/apps/$@/$@.fw1.ld ]; then make -C $@ all EXTRA_LDFLAGS=-T$@.fw1.ld APP_NAME=$@.fw1; fi
#ifeq ($(CONFIG_FIRMWARE_DUALBANK),y)
#	if [ -f $(BUILD_DIR)/apps/$@/$@.fw2.ld ]; then make -C $@ all EXTRA_LDFLAGS=-T$@.fw2.ld APP_NAME=$@.fw2; fi
#endif
#	if [ -f $(BUILD_DIR)/apps/$@/$@.dfu1.ld ]; then make -C $@ all EXTRA_LDFLAGS=-T$@.dfu1.ld APP_NAME=$@.dfu1; fi
#ifeq ($(CONFIG_FIRMWARE_DUALBANK),y)
#	if [ -f $(BUILD_DIR)/apps/$@/$@.dfu2.ld ]; then make -C $@ all EXTRA_LDFLAGS=-T$@.dfu2.ld APP_NAME=$@.dfu2; fi
#endif

outdir:
	for dir in $(app-fw-y); do mkdir -p $(BUILD_DIR)/apps/$$dir; done
ifeq ($(CONFIG_FIRMWARE_DFU),y)
	for dir in $(app-dfu-y); do mkdir -p $(BUILD_DIR)/apps/$$dir; done
endif

__clean:
	for dir in $(app-fw-y); do make -C $$dir clean; done
ifeq ($(CONFIG_FIRMWARE_DFU),y)
	for dir in $(app-dfu-y); do make -C $$dir clean; done
endif
	$(RM) $(RMFLAGS) Kconfig.gen

__distclean:
	for dir in $(app-fw-y); do make -C $$dir distclean; done
ifeq ($(CONFIG_FIRMWARE_DFU),y)
	for dir in $(app-dfu-y); do make -C $$dir distclean; done
endif

show:
	@echo
	@echo "app-y    : $(app-y)"
	@echo "app-fw-y : $(app-fw-y)"
	@echo "app-dfu-y: $(app-dfu-y)"
	@echo
