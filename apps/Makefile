# basic skeleton for apps
# list of activated apps are in Makefile.objs for greater
# readability

PROJ_FILES = ../
VERSION = 1
#############################

CONFIG_MK = $(PROJ_FILES)/m_config.mk
-include $(CONFIG_MK)
-include $(PROJ_FILES)/m_generic.mk

-include Makefile.objs
-include Makefile.objs.gen

#############################
# build all

.PHONY: $(app-fw-y) $(app-dfu-y)

.NOTPARALLEL: $(app-fw-y) $(app-dfu-y)

app-y := $(sort $(app-fw-y) $(app-dfu-y))

all: prepare dummy layout final

prepare:
	#$(call if_changed,ldscript)

dummy: outdir
	$(call if_changed,builddummyapp)

layout:
	$(call if_changed,app_layout)

final:
	$(call if_changed,buildapp)


outdir:
	for dir in $(app-fw-y); do mkdir -p $(BUILD_DIR)/apps/$$dir/fw; done
ifeq ($(CONFIG_FIRMWARE_DFU),y)
	for dir in $(app-dfu-y); do mkdir -p $(BUILD_DIR)/apps/$$dir/dfu; done
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
