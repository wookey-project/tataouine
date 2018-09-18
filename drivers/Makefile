# basic skeleton for drvs
# list of activated drvs are in Makefile.objs for greater
# readability

PROJ_FILES = ../
VERSION = 1
#############################

CONFIG_MK = $(PROJ_FILES)/Makefile.conf
include $(CONFIG_MK)
include $(PROJ_FILES)/Makefile.gen

# include (if found) various drivers)
-include socs/$(SOC)/Makefile.objs
-include socs/$(SOC)/Makefile.objs.gen

#############################
# build all

.PHONY: $(drv-y)

all: $(drv-y) 

$(drv-y):
	make -C socs/$(SOC)/$@

__clean:
	if [ ! -z "$(SOC)" ]; then for dir in $(drv-y); do make -C socs/$(SOC)/$$dir clean; done; fi
	$(RM) $(RMFLAGS) Kconfig.gen

__distclean:
	if [ ! -z "$(SOC)" ]; then for dir in $(drv-y); do make -C socs/$(SOC)/$$dir distclean; done; fi

show:
	@echo
	@echo "SoC  : $(SOC)"
	@echo "---"
	@echo "drv-y: $(drv-y)"
	@echo
	@echo "drv-n: $(drv-n)"
	@echo
