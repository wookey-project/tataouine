#!/usr/bin/env sh

export WOOKEY_ENV=true

# this is the script for setting user environment in order to set the various
# tools paths and names
# this script is separated from the Kconfig content in order to allow the user
# to specify its own paths and name without having them overloaded when using
# defconfig files.
# This file is keeped in git, as it contains all the explanation for all
# requested variables. As the user is intented to update this very variables with
# this own values, this script is sourcing the local file named 'setenv.local.sh'
# in the same way as OpenBSD configuration scripts.
# This permit the user to write a setenv.local.conf file with its own variables
# set, with a fallback to the following variables if not needed.
# The setenv.local.sh file is not requested if the following variables are
# correctly set for the local user's configuration.

# 1) The Ada runtime installation path. This path is the parent directory of
# the gnat cross-toolchain. It should contains directories such as arm-eabi/
# (for the target runtime), /bin (for the host tools), and so on.
# Setting this directory *does not* means that you can avoid adding the bin/ subdir
# of the Ada toolchain to you PATH. This is a required action.
if [ -z "$ADA_RUNTIME" ]
then
    export ADA_RUNTIME=$(dirname $(dirname $(which arm-eabi-gnat)))
else
    export ADA_RUNTIME=$ADA_RUNTIME
fi

# 3) This is the path (including the name) of the st-flash tool. This tool
# is used to flash STM32 boards. Setting this path is not required as you
# can flash the target with another tool (gdb+openocd, telnet+openocd, and so
# on).
if [ -z "$ST_FLASH" ]
then
    export ST_FLASH="/usr/local/bin/st-flash"
else
    export ST_FLASH=$ST_FLASH
fi

# 4) This is the path (including the name) of the st-util tool. This tool
# is used to interact with the STM32 boards. Setting this path is not required
# as this is only a helper tool and is not required to build and flash the
# target. Although, it can be helpfull to get back some information about your
# board as it is used by the tataouine 'burn' helper target which compile the
# firmware and flash the device.
if [ -z "$ST_UTIL" ]
then
    export ST_UTIL="/usr/local/bin/st-util"
else
    export ST_UTIL=$ST_UTIL 
fi

# 5) The classical "CROSS_COMPILE" variable, specifying the cross-toolchain prefix.
# This variable is used only for the C compiler (not for Ada which is using its
# own in its gpr files). Depending on your C cross-compiler installation, this
# prefix may varies.
# WARNING: if you use the Ada toochain, please be sure to use the Ada toolchain C compiler
# to avoid unexpected link and run problems due to incompatible compilers versions.
# The AdaCore Ada toolchain is using the arm-eabi- prefix for its toolchain
if [ -z "$CROSS_COMPILE" ]
then
    export CROSS_COMPILE="arm-none-eabi-"
else
    export CROSS_COMPILE=$CROSS_COMPILE
fi

# 6) By default, the SDK is using GCC for cross-compiling. It is possible to
# use LLVM to get a better static analysis through clang and build-check.
# Although, *this requires clang 7 and higher*. By now, LLVM support is
# *EXPERIMENTAL* and is not yet fully integrated.
# Using LLVM still requires GNU LD greater than 2.30 (which is typically not
# the case if you use the Ada Cross-toolchain integrated CC compiler suite).
# set this variable to 'y' if you which to use LLVM/Clang instead of gcc
if [ -z "$USE_LLVM" ]
then
    export USE_LLVM=n
else
    export USE_LLVM=$USE_LLVM
fi

# 7) Specify clang path, if you clang installation is not standard (multiple
# versions, etc.).
#
if [ -z "$CLANG_PATH" ]
then
    export CLANG_PATH="/usr/bin/clang"
else
    export CLANG_PATH=$CLANG_PATH
fi

# 8) Specify the Javacard Oracle SDK installation path. This SDK is used in
# order to compile the Javacard applets. Please specify the SDK root directory
# (for e.g. /opt/java_sc_3.0.4)
if [ -z "$JAVA_SC_SDK" ]
then
    export JAVA_SC_SDK="$PWD/javacard/applet/sdks/jc303_kit/"
else
    export JAVA_SC_SDK=$JAVA_SC_SDK
fi

# 9) Specify the python command line we want. This can be "python",
# "python2", "python3", "/usr/bin/python", etc.
# By default, it is the distribution python.
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
else
    export PYTHON_CMD=$PYTHON_CMD 
fi

# All the above variables are "standard values". Now you can override any of
# them by rewriting 'export VARNAME="content" on your own setenv.local.sh file
# if needed to overload any of the above. For that, just create the setenv.local.sh
# file in this same directory and update the variables you need.
# You can also specifically override them by exporting them before executing setenv.sh.

# overriding the above variable with the user configuration, if the file exists.
if test -f setenv.local.sh; then
    source setenv.local.sh
fi

which ${CROSS_COMPILE}gcc > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: your cross-toolchain is not in your path !"
    echo "please update your PATH variable first by including your cross-toolchain"
    echo "bin/ directory"
    return 1
fi

# Sanity check on the chosen python command
if $PYTHON_CMD -c 'import smartcard, Crypto, intelhex' &>/dev/null;
then
    echo "Python sanity check OK"
else
    echo -e "\e[31mWARNING: either smartcard, Crypto or intelhex Python package has not been found\e[0m"
    echo -e "\e[31mwith the selected Python command ... Compilation might fail!\e[0m"
    echo -e "\e[31mContinue if you know what you are doing\e[0m"
fi

# Sanity check on the perl command
if perl -e '' &>/dev/null;
then
    echo "Perl sanity check OK"
else
    echo -e "\e[31mWARNING: Perl sanity check fails ... Compilation might fail!\e[0m"
    echo -e "\e[31mContinue if you know what you are doing\e[0m"
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
        echo -e "\e[31mWARNING: JDK version cannot be detected ...\e[0m"
        echo -e "\e[31m  Do you have java JDK (8 to 11) installed?\e[0m"
        echo -e "\e[31m  Compilation might fail!\e[0m"
else
    if [ "$JAVA_VERSION" -le 7 ]; then
        echo -e "\e[31mWARNING: JDK version $JAVA_VERSION is < 8\e[0m"
        echo -e "\e[31m  This JDK version is not compatible with\e[0m"
        echo -e "\e[31m  the Javacard SDK, compilation might fail!\e[0m"
    else
        if [ "$JAVA_VERSION" -ge 12 ]; then
            echo -e "\e[31mWARNING: JDK version $JAVA_VERSION is > 11\e[0m"
            echo -e "\e[31m  This JDK version is not compatible with\e[0m"
            echo -e "\e[31m  the Javacard SDK, compilation might fail!\e[0m"
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

if test -z "$ADA_RUNTIME"; then
    echo "Invalid ADA_RUNTIME! Please check that your Ada toolchain binaries are in your PATH"
fi
