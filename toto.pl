use List::Util qw(reduce);

my $init=0x53747421;
my $bla=$init;

open $toto,"/dev/urandom";
binmode $toto;
my $char;


my @fliped;
my $i;
while (( reduce { $a + $b } @fliped) < 16) {
sysread $toto,$char,1;
$char=unpack "c",$char;
$char=$char % 32;
printf("[$i] fliping char $char\n");
unless ($fliped[$char]) {
    $fliped[$char]=1;
    $bla ^= 1 << $char;
}
$i++;
}

printf "init:  %x, %s\n", $init, join("",unpack("B32",pack("I",$init)));
printf "other: %x, %s\n", $bla, join("",unpack("B32",pack("I",$bla)));
