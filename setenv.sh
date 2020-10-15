#!/usr/bin/env sh

# Reseting variables

unset WOOKEY_ENV
unset ADA_RUNTIME
unset CROSS_COMPILE
unset ST_FLASH
unset ST_UTIL
unset USE_LLVM
unset CLANG_PATH
unset JAVA_SC_SDK
unset PYTHON_CMD

# All the variables below are standard values that can be changed by creating
# a 'setenv.local.sh' file.

if test -f setenv.local.sh; then
    source setenv.local.sh
fi

#------------------------------------------------------------------------------
# WARNING!
# DO NOT EDIT VARIABLE BELOW. PUT YOUR PREFERENCES IN 'setenv.local.sh'
#------------------------------------------------------------------------------

#---
# Exported variables
#---

export WOOKEY_ENV=true

#
# Ada runtime installation path
#
# Parent directory of the gnat cross-toolchain. It should contains directories
# such as arm-eabi/ for the target runtime and bin/ for the host tools.
#
# Note: don't forget to set your PATH accordingly
#
if [ -z "$ADA_RUNTIME" ]
then
    export CROSS_COMPILE="arm-eabi-"
    export ADA_RUNTIME=$(dirname $(dirname $(which ${CROSS_COMPILE}gnat)))
fi

#
# Cross-toolchain prefix
#
# WARNING: if you use the Ada toochain, please be sure to use the Ada toolchain C compiler
# to avoid unexpected link and run problems due to incompatible compilers versions.
# The AdaCore Ada toolchain uses the 'arm-eabi-' prefix
#
if [ -z "$CROSS_COMPILE" ]
then
    export CROSS_COMPILE="arm-none-eabi-"
fi

#
# st-flash tool path
#
# This tool is used to flash STM32 boards. Setting this path is not mandatory
# and you can always flash the target with another tool (ie. openocd)
#
if [ -z "$ST_FLASH" ]
then
    export ST_FLASH="/usr/local/bin/st-flash"
fi

#
# st-util tools path
#
# Tools used to interact with the STM32 boards. Setting this path is not mandatory
# as this is only a helper tool and is not required to build and flash the
# target.
#
if [ -z "$ST_UTIL" ]
then
    export ST_UTIL="/usr/local/bin/st-util"
fi

#
# Uses LLVM instead of GCC
#
# By default, the SDK is using GCC for cross-compiling. It is possible to
# use LLVM to get a better static analysis through clang and build-check.
# Set this variable to 'y' if you want to use LLVM/Clang instead of gcc.
#
# Notes:
#   - LLVM support is EXPERIMENTAL and is not fully integrated
#   - requires clang 7 and higher
#   - requires gnu LD greater than 2.30 (which is not always provided by
#     the Adacore cross-toolchain).
#
if [ -z "$USE_LLVM" ]
then
    export USE_LLVM=n
fi

#
# Clang path
#
if [ -z "$CLANG_PATH" ]
then
    export CLANG_PATH="/usr/bin/clang"
fi

#
# Javacard Oracle SDK installation path
#
# Mandatory for compiling the Javacard applets. Please specify the SDK root directory
# (for e.g. /opt/java_sc_3.0.4)
#
if [ -z "$JAVA_SC_SDK" ]
then
    export JAVA_SC_SDK="$PWD/javacard/applet/sdks/jc303_kit/"
fi

#
# Python binary
#
# Specify your prefered python binary: "python", "python2", "python3",
# "/usr/bin/python", etc.
# Default, it is the binary distributed by your system.
#
if [ -z "$PYTHON_CMD" ]
then
    # Try to guess which python we want to use depending on the installed
    # packages. We need Pyscard, Crypto, and IntelHex
    for i in python python3 python2; do
        if [ -x "$(which $i)" ]; then
            MISSING=""
            for j in smartcard Crypto intelhex; do
                eval "$i -c 'import $j' 2>/dev/null" || MISSING="$MISSING $j"
            done
            if [ -z "$MISSING" ]; then
                export PYTHON_CMD=$i
                break
            fi
        fi
    done
fi


#---
# End of variables
#---

which ${CROSS_COMPILE}gcc > /dev/null
if [ $? -ne 0 ]; then
    echo -e "\e[41mCross-toolchain '${CROSS_COMPILE}gcc' is not in your path !\e[0m"
    return 1
fi

if test "${ADA_RUNTIME}/bin/${CROSS_COMPILE}gcc" != "$(which ${CROSS_COMPILE}gcc)"; then
    echo -e "\e[41mPlease check that your Ada toolchain is in your PATH: $ADA_RUNTIME/bin\e[0m"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "\e[41mPython must be installed with Smartcard, Crypto and intelhex packages\e[0m"
else
    if ! $PYTHON_CMD -c 'import smartcard, Crypto, intelhex' &>/dev/null;
    then
        echo -e "\e[41mPython packages Smartcard, Crypto or intelhex not found\e[0m"
    fi
fi

if ! perl -e '' &>/dev/null;
then
    echo -e "\e[41mPerl check fails ... Compilation might fail!\e[0m"
fi

# Checking the Java JDK version
# This has been taken from http://eed3si9n.com/detecting-java-version-bash
jdk_version() (
    if which java >/dev/null; then
        java_cmd=java
    elif [ -n "$JAVA_HOME" -a -x "$JAVA_HOME/bin/java" ]; then
        java_cmd="$JAVA_HOME/bin/java"
    fi
    result=$("$java_cmd" -Xms32M -Xmx32M -version 2>&1 | perl -ne '/version\s+"(1\.)?(\d+)/ and print "$2"')
    echo "${result:-no_java}"
)

JAVA_VERSION="$(jdk_version)"

if [ "$JAVA_VERSION" = "no_java" ]; then
    echo -e "\e[41mJDK version cannot be detected... Do you have java JDK (8 to 11) installed?\e[0m"
elif [ "$JAVA_VERSION" -le 7 ]; then
    echo -e "\e[41mJDK version $JAVA_VERSION is < 8 This JDK version is not compatible with the Javacard SDK\e[0m"
elif [ "$JAVA_VERSION" -ge 12 ]; then
    echo -e "\e[41mJDK version $JAVA_VERSION is > 11 This JDK version is not compatible with the Javacard SDK\e[0m"
fi

# Let's print you current configuration

echo "========================================================="
echo "=== Tataouine environment configuration"
echo "========================================================="
echo
echo "  *: required to fully build the project"
echo
echo " *ADA_RUNTIME   = $ADA_RUNTIME"
echo "  ST_FLASH      = $ST_FLASH"
echo "  ST_UTIL       = $ST_UTIL"
echo " *CROSS_COMPILE = $CROSS_COMPILE"
echo "  USE_LLVM      = $USE_LLVM"
echo "  CLANG_PATH    = $CLANG_PATH"
echo " *JAVA_SC_SDK   = $JAVA_SC_SDK"
echo " *PYTHON_CMD    = $PYTHON_CMD"
echo
echo "========================================================="

