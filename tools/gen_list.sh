#!/bin/bash

out=`mktemp`;

echo "================================================,================================================,=========,==========" > $out
echo "C,Ada,SPARK,SPARK(api)" >> $out
echo "================================================,================================================,=========,==========" >> $out

for i in `find kernel/ -type f -iname '*.c'|sort`; do
    file="";
    adbfile="";
    dir=`dirname $i`;
    file=`basename $i`;
    if test "${dir##*/}" = "syscalls"; then
        adadir=${dir%/*}/Ada/syscalls
    else
        adadir=${dir}/Ada
    fi

    if [ "$dir" != "kernel" ]; then
        # delete kernel/ prefix
        dir="${dir#*/}/"
    else
        dir=""
    fi
    echo -n "$dir$file," >> $out

    if [ -e "$adadir" ]; then
      adafile=`find $adadir -type f -iname ewok-${file%%.c}.adb -o -iname ${file%%.c}.adb`;
      adaheaderfile=`find $adadir -type f -iname ewok-${file%%.c}.ads -o -iname ${file%%.c}.ads`;
    else
        adafile=""
    fi
    if [ -n "$adafile" ]; then
        adbf=`basename $adbfile 2>/dev/null`;
        adbheaderf=`basename $adbfile 2>/dev/null`;
        cat $adafile|grep -i "Spark_Mode => on" >/dev/null 2>&1
        res=$?
        cat $adaheaderfile|grep -i "Spark_Mode => on" >/dev/null 2>&1
        res2=$?
    else
        adbf=""
        adbheaderf=""
        res=1
        res2=1
    fi;
    # delete kernel/ prefix
    adafile=${adafile#*/}
    adaheaderfile=${adaheaderfile#*/}
    echo -n $adafile, >> $out;
    if [ $res -eq 0 ]; then
        echo -n "**yes**," >> $out;
    elif [ -n "$adafile" ]; then
        echo -n "no," >> $out;
    else
        echo -n "," >> $out;
    fi
    if [ $res2 -eq 0 ]; then
        echo  "**yes**" >> $out;
    elif [ -n "$adaheaderfile" ]; then
        echo  "no" >> $out;
    else
        echo "" >> $out;
    fi

done

echo "================================================,================================================,=========,==========" >> $out

cat $out | column -t -s, -n | less -F -S -X -K

rm $out
