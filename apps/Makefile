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
	@touch $(BUILD_DIR)/apps/.apps_done

$(app-y): outdir
	$(call if_changed,ldscript)
	$(call if_changed,buildapp)


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
	$(RM) $(RMFLAGS) Makefile.objs.gen

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
