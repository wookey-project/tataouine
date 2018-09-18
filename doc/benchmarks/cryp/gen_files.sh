#!/bin/sh

# $1 filename
# $2 ada or c (depending on the kernel config)

set -e

if test "$1" = "-h"; then
    echo "$0: generate separated log file for each CRYP coprocessor usage"
    echo "$0 <input_log> [ada|c]"
    echo
    echo "Should be executed in the benchmark directory"
    exit 0
fi

if test $# -ne 2; then
    echo "not enough arguments!"
    exit 1
fi

if test ! -f $1; then
    echo "file $1 not found !"
    exit 1
fi


cat $1 |grep ECB__ENCRYPT > crypto_perf_aes_ecb_encrypt_$2.log
cat $1 |grep ECB__DECRYPT > crypto_perf_aes_ecb_decrypt_$2.log

cat $1 |grep CBC__ENCRYPT > crypto_perf_aes_cbc_encrypt_$2.log
cat $1 |grep CBC__DECRYPT > crypto_perf_aes_cbc_decrypt_$2.log

cat $1 |grep CBC__ENCRYPT > crypto_perf_aes_ctr_encrypt_$2.log
cat $1 |grep CBC__DECRYPT > crypto_perf_aes_ctr_decrypt_$2.log
