# basic skeleton for drvs
# list of activated drvs are in Makefile.objs for greater
# readability

PROJ_FILES = ../
VERSION = 1
#############################

CONFIG_MK = $(PROJ_FILES)/m_config.mk
include $(CONFIG_MK)
include $(PROJ_FILES)/m_generic.mk

# include (if found) various drivers)
-include socs/$(SOC)/Makefile.objs
-include socs/$(SOC)/Makefile.objs.gen

-include boards/$(BOARD)/Makefile.objs
-include boards/$(BOARD)/Makefile.objs.gen

#############################
# build all

.PHONY: $(drv-y) $(board-drv-y)

all: $(drv-y) $(board-drv-y)

$(drv-y):
	make -C socs/$(SOC)/$@

$(board-drv-y):
	make -C boards/$(BOARD)/$@

__clean:
	if [ ! -z "$(SOC)" ]; then for dir in $(drv-y); do make -C socs/$(SOC)/$$dir clean; done; fi
	if [ ! -z "$(BOARD)" ]; then for dir in $(board-drv-y); do make -C boards/$(BOARD)/$$dir clean; done; fi
	$(RM) $(RMFLAGS) Kconfig.gen
	$(RM) $(RMFLAGS) socs/Makefile.objs.gen
	$(RM) $(RMFLAGS) drivers/boards/Makefile.objs.gen
	if [ ! -z "$(SOC)" ]; then $(RM) $(RMFLAGS) drivers/socs/$(SOC)/Makefile.objs.gen; fi
	if [ ! -z "$(BOARD)" ]; then $(RM) $(RMFLAGS) drivers/boards/$(BOARD)/Makefile.objs.gen; fi

__distclean:
	if [ ! -z "$(SOC)" ]; then for dir in $(drv-y); do make -C socs/$(SOC)/$$dir distclean; done; fi
	if [ ! -z "$(BOARD)" ]; then for dir in $(board-drv-y); do make -C boards/$(BOARD)/$$dir distclean; done; fi

show:
	@echo
	@echo "SoC        : $(SOC)"
	@echo "Board      : $(BOARD)"
	@echo "---"
	@echo "drv-y      : $(drv-y)"
	@echo "board-drv-y: $(board-drv-y)"
	@echo
	@echo "drv-n      : $(drv-n)"
	@echo "board-drv-n: $(board-drv-n)"
	@echo
