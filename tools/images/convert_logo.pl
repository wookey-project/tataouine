#!/usr/bin/perl -l
use Image::Magick;
$p = new Image::Magick;
$p->Read($ARGV[0]);
($width,$height)=$p->Get("attribute","width","height");

#tableau couleur RGB 
@pixels=($p->GetPixels(height =>$height , width=>$width,map  => 'RGB'));
@pixels = map {int(int($_/65535*255))} @pixels;

my %coul;
my $nbcoul=1;
my $currentcolor=0;
my $currentnb;
my $toto="";
while($i<@pixels)
{
	($r,$g,$b)=@pixels[$i..($i+3)];
	$coul{$r}{$g}{$b}=$nbcoul++ and $colors.=int($r/255.*255).",".int($g/255.*255).",".int($b/255.*255).", " unless ($coul{$r}{$g}{$b}); 

	if (($coul{$r}{$g}{$b}==$currentcolor) and ($currentnb<255))
	{
	  $currentnb++;
	}
	else
	{
	  $toto.=($currentcolor-1).",$currentnb, ";
	  $currentnb=1;
	  $currentcolor=$coul{$r}{$g}{$b};
	  $size+=2;
	}
  $i+=3;
}
#
$toto=~s/.*?,,//;
$toto.="$currentcolor,$currentnb";
#print $toto;
sub find_nearest
{
  my ($colors,$bound)=@_;
  my $res=0;
  my $mindist=100000000000000000;
  my @coord=$colors=~/(\d+),(\d+),(\d+), /g;
  for $index (0..$bound-1,$bound+1..$nbcoul-1)
  {
    my $dist=($coord[3*$index]-$coord[3*($bound+1)])**2
    	+($coord[3*$index]+1-$coord[3*($bound+1)+1])**2
	+($coord[3*$index+2]-$coord[3*($bound+1)+2])**2;
    ($res=$index) and ($mindist=$dist) if($dist<$mindist);
  }
  return $res;
}
#Let us postprocess image and eliminate colors non appearing too often
my $tmp=0;
for my $colo (0..$nbcoul)
{
  my @list=$toto=~/ $colo,(\d+)/g;
  my $max;
  @list=sort { $a <=> $b } @list;
  $max = pop @list;
  # 20 is the minimal number to appear in the final image. more reduce the number of colors, less increase it
  if ($max <10 )
  {
    	my $replace_color=find_nearest($colors,$tmp);
	$replace_color+=$colo-$tmp if $replace_color>$tmp;
	$toto=~s/ $colo(,\d+,)/ $replace_color$1/g;
        $colors=~s/^((\d+,\d+,\d+, ?){$tmp})(\d+,\d+,\d+, ?)((\d+,\d+,\d+, ?)*)$/$1$4/;
	$tmp--;
	$nbcoul--;
  }
  else
  {
#finally adjust the color number to report suppressed ones
  $toto=~s/ $colo(,\d+,)/ $tmp$1/g;
  }
  $tmp++;

}


# Finally post process the image for compressing
@list=($toto=~/ (\d+),(\d+),?/g);
#print "@list";
my $currentnb=0;
my $currentcolor=0;
my $i=0;
$size=0;
while ($i<(@list-1))
{
  #print $list[$i]," ",$list[$i+1];
  if (($list[$i]!=$currentcolor) or (($currentnb+$list[$i+1])>255))
  {
    $totores.=" $currentcolor,$currentnb,";
    $currentcolor=$list[$i];
    $currentnb=$list[$i+1];
    $size+=2;
  }
  else
  {
    $currentnb+=$list[$i+1];
   }
}
continue
{
  $i+=2;
}
$totores.=" $currentcolor,$currentnb,";
$size+=2;

$toto=$totores;

my $prefix=$ARGV[0]=~s/^.*?\/?([^\/]+)\.[^.]*?$/\1/r;


$colors=~s/,$//;
$res="#ifndef \U${prefix}_H\E\n#define \U${prefix}_H\E\nconst int ${prefix}_nbcoul = $nbcoul;\nconst uint8_t ${prefix}_colormap[]={$colors};\nconst int ${prefix}_width =$width, ${prefix}_height = $height;\nconst uint8_t ${prefix}[$size]={$toto};\n#endif\n";

print $res;

