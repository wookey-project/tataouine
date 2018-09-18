set terminal png enhanced size 800,800
set output "crypto_perf.png"
set multiplot layout 2, 1 title "CRYP with DMA using syscall for DMA reconf"
set margin 15
unset key
# legende en dessous:
#set key outside below; set key title "Caption"; set key box reverse; set key box lw 2 lc 4 
set key right bottom
set title ' DMA-based AES256 Encryption time'
set xlabel ' Chunck size (in hexadecimal)'
set ylabel ' Performances in Mb/s'
set format x "%x"
set xtics 2048
#set logscale y
set grid
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 2 lc rgb '#ad0060' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 3 lc rgb '#20ad20' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 4 lc rgb '#0060ad' lt 1 lw 1 pt 5 pi -1 ps 1.5
set style line 5 lc rgb '#ad0060' lt 1 lw 1 pt 5 pi -1 ps 1.5
set style line 6 lc rgb '#20ad20' lt 1 lw 1 pt 5 pi -1 ps 1.5
set style fill transparent solid 0.5 noborder
plot "crypto_perf_aes_cbc_encrypt_c.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/C AES CBC Encrypt" with linespoints ls 1, \
"crypto_perf_aes_ctr_encrypt_c.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/C AES CTR Encrypt" with linespoints ls 2, \
"crypto_perf_aes_ecb_encrypt_c.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/C AES ECB Encrypt" with linespoints ls 3, \
"crypto_perf_aes_cbc_encrypt_ada.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/Ada AES CBC Encrypt" with linespoints ls 4, \
"crypto_perf_aes_ctr_encrypt_ada.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/Ada AES CTR Encrypt" with linespoints ls 5, \
"crypto_perf_aes_ecb_encrypt_ada.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/Ada AES ECB Encrypt" with linespoints ls 6

unset key
set margin 15
# legende en dessous:
#set key outside below; set key title "Caption"; set key box reverse; set key box lw 2 lc 4 
set key
set title ' DMA-based AES256 Decryption time'
set xlabel ' Chunck size (in hexadecimal)'
set ylabel ' Performances in Mb/s'
#set logscale y
set format x "%x"
set grid
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 2 lc rgb '#ad0060' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 3 lc rgb '#20ad20' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 4 lc rgb '#0060ad' lt 1 lw 1 pt 5 pi -1 ps 1.5
set style line 5 lc rgb '#ad0060' lt 1 lw 1 pt 5 pi -1 ps 1.5
set style line 6 lc rgb '#20ad20' lt 1 lw 1 pt 5 pi -1 ps 1.5
set style fill transparent solid 0.5 noborder
plot "crypto_perf_aes_cbc_decrypt_c.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/C AES CBC Decrypt" with linespoints ls 1, \
"crypto_perf_aes_ctr_decrypt_c.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/C AES CTR Decrypt" with linespoints ls 2, \
"crypto_perf_aes_ecb_decrypt_c.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/C AES ECB Decrypt" with linespoints ls 3, \
"crypto_perf_aes_cbc_decrypt_ada.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/Ada AES CBC Decrypt" with linespoints ls 4, \
"crypto_perf_aes_ctr_decrypt_ada.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/Ada AES CTR Decrypt" with linespoints ls 5, \
"crypto_perf_aes_ecb_decrypt_ada.log" using 8:(168.0/(($5/(16*8)))) title "EwoK/Ada AES ECB Decrypt" with linespoints ls 6

unset multiplot
