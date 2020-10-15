#!/usr/bin/env sh


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
    echo "Looking for suitable python and deps"
    # Try to guess which python we want to use depending on the installed
    # packages. We need Pyscard, Crypto, and IntelHex
    for i in python python3 python2; do
      if [ -x "`which $i`" ]; then 
        PYTHON_CMD=$i
        MISSING=""
        for j in smartcard Crypto intelhex; do
          eval "$i -c 'import $j' 2>/dev/null" || MISSING="$MISSING $j"
        done
        if [ -z "$MISSING" ];then 
          echo "\tFound $PYTHON_CMD and the required deps"
          break
        else
          echo "\tFound $PYTHON_CMD but $MISSING is not available" >&2
          PYTHON_CMD=""
        fi
      else
          echo "\tFailed to find $i" 
      fi
    done  
    if [ -z "$PYTHON_CMD" ]; then
      echo "Failed to find working python cmd!" >&2
    else
      export PYTHON_CMD
   fi
fi


#---
# End of variables
#---


which ${CROSS_COMPILE}gcc > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: cross-toolchain '${CROSS_COMPILE}gcc' is not in your path !"
    echo "please update your PATH variable first by including your cross-toolchain"
    echo "bin/ directory"
    return 1
fi


if test "${ADA_RUNTIME}/bin/${CROSS_COMPILE}gcc" != "$(which ${CROSS_COMPILE}gcc)"; then
    echo -e "\e[41mPlease check that your Ada toolchain is in your PATH: $ADA_RUNTIME/bin\e[0m"
fi

# Sanity check on the chosen python command
if $PYTHON_CMD -c 'import smartcard, Crypto, intelhex' &>/dev/null;
then
    echo "Python sanity check OK"
else
    echo -e "\e[41mWARNING: either smartcard, Crypto or intelhex Python package has not been found\e[0m"
    echo -e "\e[41mwith the selected Python command ... Compilation might fail!\e[0m"
    echo -e "\e[41mContinue if you know what you are doing\e[0m"
fi

# Sanity check on the perl command
if perl -e '' &>/dev/null;
then
    echo "Perl sanity check OK"
else
    echo -e "\e[41mWARNING: Perl sanity check fails ... Compilation might fail!\e[0m"
    echo -e "\e[41mContinue if you know what you are doing\e[0m"
fi

# Sanity check on the Java JDK version
# This has been taken from http://eed3si9n.com/detecting-java-version-bash
# Sanity check on the chosen Java JDK version
# returns the JDK version.
# 8 for 1.8.0_nn, 9 for 9-ea etc, and "no_java" for undetected
jdk_version() (
  if which java >/dev/null; then
    java_cmd=java
  elif [ (-n "$JAVA_HOME") -a (-x "$JAVA_HOME/bin/java") ]; then
    java_cmd="$JAVA_HOME/bin/java"
  fi
  result=$("$java_cmd" -Xms32M -Xmx32M -version 2>&1 | perl -ne '/version\s+"(1\.)?(\d+)/ and print "$2"')
  echo "${result:-no_java}"
) 

JAVA_VERSION="$(jdk_version)"
TERMRED=`tput setaf 1`
TERMNORM=`tput sgr0`

if [ "$JAVA_VERSION" = "no_java" ]; then
cat <<EOF
$TERMRED WARNING: JDK version cannot be detected ...
  Do you have java JDK (8 to 11) installed?
  Compilation might fail!$TERNORM
EOF
else
    if [ "$JAVA_VERSION" -le 7 ]; then
cat <<EOF        
$TERMRED WARNING: JDK version $JAVA_VERSION is < 8
  This JDK version is not compatible with
  the Javacard SDK, compilation might fail!$TERMNORM
EOF
    else
        if [ "$JAVA_VERSION" -ge 12 ]; then
cat <<EOF         
$TERMRED WARNING: JDK version $JAVA_VERSION is > 11
  This JDK version is not compatible with
  the Javacard SDK, compilation might fail!$TERMNORM
EOF
        else
            echo "Java JDK $JAVA_VERSION OK"
        fi
    fi
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


if  [ -z "$ADA_RUNTIME" ]; then
    echo "Invalid ADA_RUNTIME! Please check that your Ada toolchain binaries are in your PATH"
fi
