#!/bin/sh

cp -r /build/oracle_javacard_sdks/* /build/javacard/applet/sdks/
/bin/bash -c "rm -r /build/setenv.local.sh && export CROSS_COMPILE=arm-none-eabi- && cd /build && rm -rf /build/build && rm -rf /build/private/ && rm -rf /build/javacard/applet/ant-javacard.jar && rm -rf /build/javacard/applet/gp.jar && rm -rf /build/javacard/applet/build_auth && rm -rf /build/javacard/applet/build_dfu && rm -rf /build/javacard/applet/build_sig && source setenv.sh && make wookey-v2/graphic_hs_defconfig && make prepare && make genkeys && make javacard_compile"

# We launch pcscd
pcscd -f &>/tmp/log_pcsc &

# We launch jcardsim
java -cp /build/jcardsim/target/jcardsim-3.0.5-SNAPSHOT.jar:/build/javacard/applet/build_auth/wookey_auth.jar:/build/javacard/applet/build_dfu/wookey_dfu.jar:/build/javacard/applet/build_sig/wookey_sig.jar com.licel.jcardsim.remote.VSmartCard /build/tools/javacard_tests/wookey.cfg &>/tmp/log_jcardsim &

# Sleep a bit to wait insertion
sleep 2

# Install our applets
opensc-tool -s "80b80000110a45757477747536417070050000020F0F00" -s "80b80000110a45757477747536417071050000020F0F00" -s "80b80000110a45757477747536417072050000020F0F00"

# Launch the basic Python tests
echo "===== TESTING AUTH TOKEN ==================="
python3 tools/javacard_tests/basic_token_test.py AUTH /build/private 1234 1337
echo "===== TESTING DFU  TOKEN ==================="
python3 tools/javacard_tests/basic_token_test.py DFU /build/private 1234 1234
echo "===== TESTING SIG  TOKEN ==================="
python3 tools/javacard_tests/basic_token_test.py SIG /build/private 1234 1234

# Now check our make sign and make verify targets
mkdir -p ./build/armv7-m/wookey/
dd if=/dev/urandom of=./build/armv7-m/wookey/flip_fw.bin bs=1024 count=1024
dd if=/dev/urandom of=./build/armv7-m/wookey/flop_fw.bin bs=1024 count=1024
/bin/bash -c "export CROSS_COMPILE=arm-none-eabi- && source setenv.sh && make sign tosign=flop chunksize=4096 version=1.0.0.1 && make sign tosign=flip chunksize=4096 version=1.0.0.2"
/bin/bash -c "export CROSS_COMPILE=arm-none-eabi- && source setenv.sh && make verify toverify=flip:flop"
