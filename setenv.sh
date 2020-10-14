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
    # Try to guess which python we want to use depending on the installed
    # packages. We need Pyscard, Crypto, and IntelHex
    if python -c 'import smartcard, Crypto, intelhex' &>/dev/null;
    then
        export PYTHON_CMD="python"
    else
        if python3 -c 'import smartcard, Crypto, intelhex' &>/dev/null;
        then
            export PYTHON_CMD="python3"
        else
            if python2 -c 'import smartcard, Crypto, intelhex' &>/dev/null;
            then
                export PYTHON_CMD="python2"
            else
                echo "Failed to find a suitable Python with Pyscard, Crypto, and IntelHex packages! Please install them or provide custom \$PYTHON_CMD variable!"
            fi
        fi
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
jdk_version() {
  local result
  local java_cmd
  if [[ -n $(type -p java) ]]
  then
    java_cmd=java
  elif [[ (-n "$JAVA_HOME") && (-x "$JAVA_HOME/bin/java") ]]
  then
    java_cmd="$JAVA_HOME/bin/java"
  fi
  local IFS=$'\n'
  # remove \r for Cygwin
  local lines=$("$java_cmd" -Xms32M -Xmx32M -version 2>&1 | tr '\r' '\n')
  if [[ -z $java_cmd ]]
  then
    result=no_java
  else
    for line in $lines; do
      if [[ (-z $result) && ($line = *"version \""*) ]]
      then
        local ver=$(echo $line | sed -e 's/.*version "\(.*\)"\(.*\)/\1/; 1q')
        # on macOS, sed doesn't support '?'
        if [[ $ver = "1."* ]]
        then
          result=$(echo $ver | sed -e 's/1\.\([0-9]*\)\(.*\)/\1/; 1q')
        else
          result=$(echo $ver | sed -e 's/\([0-9]*\)\(.*\)/\1/; 1q')
        fi
      fi
    done
  fi
  echo "$result"
} 
JAVA_VERSION="$(jdk_version)"
if [ "$JAVA_VERSION" == "no_java" ]; then
        echo -e "\e[41mWARNING: JDK version cannot be detected ...\e[0m"
        echo -e "\e[41m  Do you have java JDK (8 to 11) installed?\e[0m"
        echo -e "\e[41m  Compilation might fail!\e[0m"
else
    if [ "$JAVA_VERSION" -le 7 ]; then
        echo -e "\e[41mWARNING: JDK version $JAVA_VERSION is < 8\e[0m"
        echo -e "\e[41m  This JDK version is not compatible with\e[0m"
        echo -e "\e[41m  the Javacard SDK, compilation might fail!\e[0m"
    else
        if [ "$JAVA_VERSION" -ge 12 ]; then
            echo -e "\e[41mWARNING: JDK version $JAVA_VERSION is > 11\e[0m"
            echo -e "\e[41m  This JDK version is not compatible with\e[0m"
            echo -e "\e[41m  the Javacard SDK, compilation might fail!\e[0m"
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

