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
-include Makefile.objs.gen

.PHONY: $(libs-y)

all: libs

libs: $(libs-y)

__clean:
	for dir in $(libs-y); do make -C $$dir clean; done
	$(RM) $(RMFLAGS) Kconfig.gen

__distclean:
	for dir in $(libs-y); do make -C $$dir distclean; done


show:
	@echo "libs-y: $(libs-y)"
	@echo "libs-n: $(libs-n)"

##########################################

$(libs-y):
	make -C $@


