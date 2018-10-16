#!/usr/bin/perl -l
use Image::Magick;
$p = new Image::Magick;
$string=pack "C*",1,1,1,1,1,1,1,1,1,1,1,11..128;
$string=~s/'/'"'"'/;
$output=$ARGV[0]=~s/\..*?$//r.".png";
system("fontimage $ARGV[0] --o $output --pixelsize 30 --text '$string'");
$p->Read("$output");
($width,$height)=$p->Get("attribute","width","height");

#tableau couleur RGB 
@pixels=($p->GetPixels(height =>$height , width=>$width,map  => 'RGB'));
while($i<@pixels)
{
	($r,$g,$b)=@pixels[$i..($i+3)];
	if(($r==65535) and ($g==65535) and ($b == 65535)) 
	#if($r|$g|$b) 
	{
	  $toto.="0,";
	}
	else
	{
	  $toto.="1,";
	}
  $i+=3;
}
$toto=~s/.$//;
@toto=$toto=~/((?:[01],){$width})/g;
#Bourrage jusqu'au prochain multiple de 8 bit non necessaire
#mais on ajuste le $width
$width+=(8-($width%8))%8;
@fin=map {(pack "b*",s/,//gr)} @toto;
for (@toto)
{
  $blankskip++;
  last if (!/^\s*(0,)+$/);
}
#=~s/,//g;
#$binres=pack "b*",$toto;
$res.=((unpack "H*")=~s/../0x$&,/gr)."\n" for(@fin);
$res="const int font_blankskip=$blankskip;\nconst int font_width =$width, font_height = $height;\nconst char font[]={".$res=~s/,\n?$//r."};\n";

print $res;
