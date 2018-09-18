#!/bin/sh

# the goal of this file is to test the build sequence in various cases
# it should works without failing in all the following cases.

# clean: delete obj and depend files in the build dir, but not include/
# and generated binaries (libsign.a, ec_utils and wookey results)
#
# distclean: delete the build directory (which means all generated binaries)
# the include/ directory and the current config (.config file)
#
# this test file should be executed from the root dir.

set +x
set -e

# reseting repo
git clean -df
rm -rf build include libs/libecc/* libs/libecc/.git*
rm .config
git submodule update

# first build
make stm32f4_usbfs_dfu_defconfig
make prepare
make

make clean
make

make clean
make prepare
make

make clean
make


make distclean
make stm32f4_usbfs_dfu_defconfig
make prepare
make


echo "+++ All OK"
