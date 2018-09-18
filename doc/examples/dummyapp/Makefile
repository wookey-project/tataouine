APP_NAME ?= dummy

PROJ_FILES = ../../
BIN_NAME = $(APP_NAME).bin
HEX_NAME = $(APP_NAME).hex
ELF_NAME = $(APP_NAME).elf

VERSION = 1
#############################

-include $(PROJ_FILES)/Makefile.conf
-include $(PROJ_FILES)/Makefile.gen

# use an app-specific build dir
APP_BUILD_DIR = $(BUILD_DIR)/$(APP_NAME)

CFLAGS += $(DEBUG_CFLAGS)
CFLAGS += -Isrc/ -Iinc/
CFLAGS += -MMD -MP

LDFLAGS += $(AFLAGS) -fno-builtin -nostdlib -nostartfiles

BUILD_DIR ?= $(PROJ_FILE)build

DRVSRC := $(drv-y) $(drv-$(APP_NAME)-y)
DRVOBJ := $(patsubst %.c,$(APP_BUILD_DIR)/%.o,$(DRVSRC))
DRVDEP := $(DRVOBJ:.o=.d)

CORE_SRC = $(core-y)
CORE_OBJ := $(patsubst %.c,$(APP_BUILD_DIR)/%.o,$(CORE_SRC))
CORE_DEP := $(CORE_OBJ:.o=.d)

SOC_SRC = $(socdrv-y)
SOC_OBJ := $(patsubst %.c,$(APP_BUILD_DIR)/%.o,$(SOC_SRC))
SOC_OBJ := $(patsubst %.s,$(APP_BUILD_DIR)/%.o,$(SOC_OBJ))
SOC_DEP := $(SOC_OBJ:.o=.d)

#C sources files
BOARD_SRC = $(board-y)
BOARD_OBJ = $(patsubst %.c,$(APP_BUILD_DIR)/%.o,$(BOARD_SRC))
BOARD_DEP = $(BOARD_OBJ:.o=.d)

CSRC_DIR = src
SRC = $(wildcard $(CSRC_DIR)/*.c)
OBJ = $(patsubst %.c,$(APP_BUILD_DIR)/%.o,$(SRC))
DEP = $(OBJ:.o=.d)

#Rust sources files
RSSRC_DIR=rust/src
RSRC= $(wildcard $(RSRCDIR)/*.rs)
ROBJ = $(patsubst %.rs,$(APP_BUILD_DIR)/%.o,$(RSRC))

#ada sources files
ASRC_DIR = ada/src
ASRC= $(wildcard $(ASRC_DIR)/*.adb)
AOBJ = $(patsubst %.adb,$(APP_BUILD_DIR)/%.o,$(ASRC))

OUT_DIRS = $(dir $(DRVOBJ)) $(dir $(BOARD_OBJ)) $(dir $(SOC_OBJ)) $(dir $(CORE_OBJ)) $(dir $(AOBJ)) $(dir $(OBJ)) $(dir $(ROBJ))

LDSCRIPT_NAME = $(APP_BUILD_DIR)/$(APP_NAME).ld

# file to (dist)clean
# objects and compilation related
TODEL_CLEAN += $(ROBJ) $(OBJ) $(SOC_OBJ) $(DRVOBJ) $(BOARD_OBJ) $(CORE_OBJ) $(DEP) $(TESTSDEP) $(SOC_DEP) $(DRVDEP) $(BOARD_DEP) $(CORE_DEP) $(LDSCRIPT_NAME)
# targets
TODEL_DISTCLEAN += $(APP_BUILD_DIR)

.PHONY: app

#############################################################
# build targets (driver, core, SoC, Board... and local)

all: $(APP_BUILD_DIR) app

app: $(APP_BUILD_DIR)/$(ELF_NAME) $(APP_BUILD_DIR)/$(HEX_NAME)

$(APP_BUILD_DIR)/%.o: %.c
	$(call if_changed,cc_o_c)

# Core C sources files
$(APP_BUILD_DIR)/%.o: $(CORE_DIR)/%.c
	$(call if_changed,cc_o_c)

# SoC C sources files
$(APP_BUILD_DIR)/%.o: $(SOC_DIR)/%.c
	$(call if_changed,cc_o_c)

# SoC ASM sources files
$(APP_BUILD_DIR)/%.o: $(SOC_DIR)/%.s
	$(call if_changed,cc_o_c)

# Board C sources files
$(APP_BUILD_DIR)/%.o: $(BOARD_DIR)/%.c
	$(call if_changed,cc_o_c)

# Drivers C sources files
$(APP_BUILD_DIR)/%.o: $(DRVSRC_DIR)/%.c
	$(call if_changed,cc_o_c)

# LDSCRIPT
$(LDSCRIPT_NAME): $(ROBJ) $(OBJ) $(SOBJ) $(DRVOBJ) $(BOARD_OBJ) $(CORE_OBJ) $(SOC_OBJ)
	$(call if_changed,ldscript)

# ELF
$(APP_BUILD_DIR)/$(ELF_NAME): $(LDSCRIPT_NAME)
	$(call if_changed,link_o_target)

# HEX
$(APP_BUILD_DIR)/$(HEX_NAME): $(APP_BUILD_DIR)/$(ELF_NAME)
	$(call if_changed,objcopy_ihex)

# BIN
$(APP_BUILD_DIR)/$(BIN_NAME): $(APP_BUILD_DIR)/$(ELF_NAME)
	$(call if_changed,objcopy_bin)

$(APP_BUILD_DIR):
	$(call cmd,mkdir)

