set terminal png enhanced size 800,800
set style fill transparent solid 0.5
set output "sdio.png"
set multiplot layout 2, 1 title "SD card access with DMA (10000 chunks)"
set margin 15
unset key
# legende en dessous:
#set key outside below; set key title "Caption"; set key box reverse; set key box lw 2 lc 4 
set key left
set title ' SD-card read'
set xlabel ' DMA Chunck size'
set ylabel ' performances in Mb/s'
#set logscale y
set grid
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 2 lc rgb '#ad0060' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 3 lc rgb '#0060ad' lt 1 lw 1 pt 4 pi -1 ps 1.4
set pointintervalbox 3
set style fill transparent solid 0.5 noborder
plot "sdio_rd_c.log" using 6:($4*512*8/($9/168.0)) title "EwoK/C user driver SD read" with linespoints ls 1, \
     "sdio_rd_ada.log" using 6:($4*512*8/($9/168.0)) title "EwoK/Ada user driver SD read" with linespoints ls 3, \
     "sdio_rd_bare.log" using ($2*512):(10000*512*8/($4/168.0)) title "Bare metal driver SD read" with linespoints ls 2
unset key
set margin 15
# legende en dessous:
#set key outside below; set key title "Caption"; set key box reverse; set key box lw 2 lc 4 
set key left
set title ' SD-card write'
set xlabel ' DMA Chunck size'
set ylabel ' performances in Mb/s'
#set logscale y
set grid
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 2 lc rgb '#ad0060' lt 1 lw 2 pt 7 pi -1 ps 1.5
set style line 3 lc rgb '#0060ad' lt 1 lw 1 pt 4 pi -1 ps 1.4
set pointintervalbox 3
set style fill transparent solid 0.5 noborder
plot "sdio_wr_c.log" using 6:($4*512*8/($9/168.0)) title "EwoK/C user driver SD write" with linespoints ls 1, \
     "sdio_wr_ada.log" using 6:($4*512*8/($9/168.0)) title "EwoK/Ada user driver SD write" with linespoints ls 3, \
     "sdio_wr_bare.log" using ($2*512):(10000*512*8/($4/168.0)) title "Bare metal driver SD write" with linespoints ls 2
unset multiplot
