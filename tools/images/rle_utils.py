import sys, os, array, time, inspect, signal
import binascii, io

FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
SCRIPT_PATH = os.path.dirname(os.path.abspath(FILENAME)) + "/"
# Import our ECC python primitives
sys.path.append(SCRIPT_PATH + "/" + "../")

from common_utils import *

# For image processing
from PIL import Image

from ctypes import *
from struct import *

import argparse

class StructHelper(object):
    def __get_value_str(self, name, fmt='{}'):
        val = getattr(self, name)
        if isinstance(val, Array):
            val = list(val)
        return fmt.format(val)

    def __str__(self):
        result = '{}:\n'.format(self.__class__.__name__)
        maxname = max(len(name) for name, type_ in self._fields_)
        for name, type_ in self._fields_:
            value = getattr(self, name)
            result += ' {name:<{width}}: {value}\n'.format(
                    name = name,
                    width = maxname,
                    value = self.__get_value_str(name),
                    )
        return result

    def __repr__(self):
        return '{name}({fields})'.format(
                name = self.__class__.__name__,
                fields = ', '.join(
                    '{}={}'.format(name, self.__get_value_str(name, '{!r}')) for name, _ in self._fields_)
                )

    @classmethod
    def _typeof(cls, field):
        """Get the type of a field
        Example: A._typeof(A.fld)
        Inspired by stackoverflow.com/a/6061483
        """
        for name, type_ in cls._fields_:
            if getattr(cls, name) is field:
                return type_
        raise KeyError
    @classmethod
    def read_from(cls, buff):
        if len(buff) != sizeof(cls):
            print("Error: trying to import buffer of size %d in structure of size %d" % (len(buff), sizeof(cls)))
            raise EOFError
        result = cls.from_buffer_copy(buff)
        return result

    def serialize(self, field_name):
        if field_name == '':
            return bytearray(self)
        for name, type_ in self._fields_:
            if name == field_name:
                val = getattr(self, name)
                if isinstance(val, Array):
                    return bytearray(val)
                elif type_ == c_uint8:
                    return pack("<B", val)
                elif type_ == c_uint16:
                    return pack("<H", val)
                elif type_ == c_uint32:
                    return pack("<I", val)
                else:
                    # Constructed type: call serialize again
                    return val.serialize('')
        print("Error: %s field not found!" % field_name)
        raise KeyError

    def deserialize(self, field_name, buff):
        if field_name == '':
            a = type(self).read_from(buff)
            for name, type_ in self._fields_:
                f = copy.deepcopy(getattr(a, name))
                setattr(self, name, f)
            return
        for name, type_ in self._fields_:
            if name == field_name:
                setattr(self, name, type_.from_buffer_copy(buff))
                return
        print("Error: %s field not found!" % field_name)
        raise KeyError

def rle_encoded_img(nbcoul, nbdata):
    class _rle_encoded_img(Structure, StructHelper):
        _pack_ = 1
        _fields_ = [
            ('width', c_uint32),
            ('height', c_uint32),
            ('nbcoul', c_uint32),
            ('colormap', c_uint8 * (3 * nbcoul)),
            ('nbdata', c_uint32),
            ('data', c_uint8 * (2 * nbdata)),
            ]
        def __init__(self):
            self.nbcoul = nbcoul
            self.nbdata = nbdata
    return _rle_encoded_img
        
###############
# Implement run length encoding
def _RLE_compress_buffer(in_img_buff, target_dim=None, colors=None, show=False, alpha=(255, 255, 255)):
    img = Image.open(io.BytesIO(in_img_buff))
    # Remove alpha if necessary
    if alpha == None:
        alpha = (255, 255, 255)
    if img.mode == "RGBA":
        print("[+] Trying to remove alpha channel with (%d, %d, %d) background" % alpha)
        try:
            background = Image.new("RGBA", img.size, alpha)
            img = Image.alpha_composite(background, img)
        except:
            print("[-] Failed to remove alpha channel ...")
            pass
    # Normalize our RGB colormap to limited colors for compression
    if colors != None:
        img = img.quantize(colors)
    else:
        img = img.quantize(16)
    # Resize our image if necessary
    if target_dim != None:
        print("[+] Resizing image from (%d, %d) to (%d, %d)" % (img.width, img.height, target_dim[0], target_dim[1]))
        img = img.resize(target_dim, Image.ANTIALIAS)
    print("[+] Compressing image of (%d, %d)" % (img.width, img.height))
    # Load pixels and RLE compress them    
    pixels = img.load()
    colormap = []
    rle_data = []
    last_color = None
    num_color = 0
    for y in range(0, img.height):
        for x in range(0, img.width):
            rgb = pixels[x, y]
            # Get the current palette
            pal = img.getpalette()
            (r, g, b) = (pal[3*rgb], pal[(3*rgb)+1], pal[(3*rgb)+2])
            if last_color == None:
                last_color = (r, g, b)
            if last_color == (r, g, b):
                num_color += 1
            if (num_color == 255) or (last_color != (r, g, b)) or ((x == img.width-1) and (y == img.height-1)):
                # Add mapping if necessary
                if last_color in colormap:
                    index = colormap.index(last_color)
                else:
                    index = len(colormap)
                    colormap.append(last_color)
                rle_data.append((index, num_color))
                if num_color == 255:
                    num_color = 0
                else:
                    num_color = 1
            last_color = (r, g, b)
    # Serialize
    img_class = (rle_encoded_img(len(colormap), len(rle_data)))()
    img_class.width = img.width
    img_class.height = img.height
    idx = 0
    for i in range(0, len(colormap)):
        img_class.colormap[idx] = colormap[i][0]
        idx += 1
        img_class.colormap[idx] = colormap[i][1]
        idx += 1
        img_class.colormap[idx] = colormap[i][2]
        idx += 1
    idx = 0
    for i in range(0, len(rle_data)):
        img_class.data[idx] = rle_data[i][0]
        idx += 1
        img_class.data[idx] = rle_data[i][1]
        idx += 1
    # Serialize
    out_buff = img_class.serialize('')
    if show == True:
        img.show()
    return out_buff, img_class, img

def RLE_compress_buffer(in_img_buff, target_dim=None, colors=None, target_size=None, show=False, alpha=(255, 255, 255)):
    if target_size != None:
        # Adjust colors until we reach our target size
        colors = 256
        out_buff, img_class, img = _RLE_compress_buffer(in_img_buff, target_dim, colors, show=False, alpha=alpha)
        while (len(out_buff) > target_size) and (colors > 2):
            print("[-] Compressed size evaluation: %d bytes, target is %d bytes" % (len(out_buff), target_size))
            out_buff, img_class, img = _RLE_compress_buffer(in_img_buff, target_dim, colors, show=False, alpha=alpha)
            colors -= 5
            if colors <= 0:
                print("[-] Giving up trying to fit size ...")
                break
    else:
        out_buff, img_class, img = _RLE_compress_buffer(in_img_buff, target_dim, colors, show=False, alpha=alpha)
    # Output compressed size evaluation
    print("[+] Compressed size evaluation: %d bytes" % (len(out_buff)))
    if show == True:
        img.show()
    return out_buff, img_class, img

def RLE_uncompress_buffer(in_img_buff, target_dim=None, show=False):
    # Infer our lengths
    colormap_len = unpack("<I", in_img_buff[8:8+4])[0]    
    rle_data_len = unpack("<I", in_img_buff[8+4+(3*colormap_len):8+4+(3*colormap_len)+4])[0]
    # Deserialize
    img_class = (rle_encoded_img(colormap_len, rle_data_len))()
    img_class.deserialize('', in_img_buff)
    # Initialize image
    img = Image.new("RGB", (img_class.width, img_class.height))
    # Now uncompress our raw pixels
    idx = 0
    for i in range(0, len(img_class.data) // 2):
        index = img_class.data[(2*i)]
        num_color = img_class.data[(2*i)+1]
        for j in range(0, num_color):
            x = (idx % img_class.width)
            y = (idx // img_class.width)
            (r, g, b) = (img_class.colormap[(3*index)], img_class.colormap[(3*index)+1], img_class.colormap[(3*index)+2])            
            img.putpixel((x, y), (r, g, b))
            idx += 1
    # Resize if necessary
    if target_dim != None:
        print("[+] Resizing image to (%d, %d)" % (target_dim[0], target_dim[1]))
        img = img.resize(target_dim, Image.ANTIALIAS)
    if show == True:
        img.show()
    return img, img_class

def RLE_save_header(out_file_name, img_class):
    # Format our header content
    header_content = ""
    header_content += ("const int %s_nbcoul = %d;\n" % (out_file_name, img_class.nbcoul))
    header_content += ("const int %s_width = %d, %s_height = %d;\n\n" % (out_file_name, img_class.width, out_file_name, img_class.height))
    header_content += ("const uint8_t %s_colormap[%d] = {" % (out_file_name, len(img_class.colormap)))
    for c in img_class.colormap:
        header_content += ("0x%02x, " % c)
    header_content += "};\n\n"
    header_content += ("const uint8_t %s[%d] = {" % (out_file_name, len(img_class.data)))
    for d in img_class.data:
        header_content += ("0x%02x, " % d)
    header_content += "};\n" 
    print("[+] Writing header to %s" % out_file_name)
    f = open(out_file_name, "wb")
    f.write(header_content.encode("latin-1"))
    f.close()
    return header_content

def RLE_file(in_img, compress='c', target_dim=None, colors=None, target_size=None, show=False, header=False, alpha=(255, 255, 255)):
    if not os.path.isfile(in_img):
        print("Error: file %s does not exist!" % in_img)
        sys.exit(-1)
    with open(in_img, "rb") as f:
        in_img_buff = f.read()
    if compress == 'c':
        out_buff, img_class, img = RLE_compress_buffer(in_img_buff, target_dim, colors, target_size, show, alpha=alpha)
        # Save output file
        with open(in_img+".rle", "wb") as f:
            f.write(out_buff)
            f.close()
        # Save header if necessary
        if header == True:
            base_name = os.path.basename(in_img)
            base_name = os.path.dirname(in_img)+"/"+os.path.splitext(base_name)[0]+"_rle.h"
            RLE_save_header(base_name, img_class)
    elif compress == 'u':
        img, img_class = RLE_uncompress_buffer(in_img_buff, target_dim, show)
        # Save output file
        img.save(in_img+".uncompressed.png", "PNG")
    else:
        print("Error: unknown method %s (either 'c' or 'd')" % compress)
    return

if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", help="Compress/Uncompress", choices=["c", "u"], required=True)
    parser.add_argument("--width", type=int, help="Image width (default is original width)")
    parser.add_argument("--height", type=int, help="Image height (default is original height)")
    parser.add_argument("--colors", type=int, help="Number of colors (default is 16)")
    parser.add_argument("--size", type=int, help="Ideal target size")
    parser.add_argument("--header", help="Generate C header file", action="store_true")
    parser.add_argument("--show", help="Show the result", action="store_true")
    parser.add_argument("--input", type=str, help="Input file", required=True)
    parser.add_argument("--alpha", type=int, nargs='+', help="Alpha channel replacement color")
    args = parser.parse_args()
    if (args.width != None) and (args.height == None):
        print("Error: --width provided but no --height provided!")
        sys.exit(-1)
    if (args.height != None) and (args.width == None):
        print("Error: --height provided but no --width provided!")
        sys.exit(-1)
    if (args.width != None) and (args.width != None):
        target_dim = (args.width, args.height)
    else:
        target_dim = None
    if args.action == "u":
        if args.colors != None:
            print("Error: --colors is incompatible with action Uncompress")
            sys.exit(-1)
        if args.size != None:
            print("Error: --size is incompatible with action Uncompress")
            sys.exit(-1)
        if args.header == True:
            print("Error: --header is incompatible with action Uncompress")
            sys.exit(-1)
        if args.alpha != None:
            print("Error: --alpha is incompatible with action Uncompress")
            sys.exit(-1)
    alpha = None
    if args.alpha != None:
        if len(args.alpha) != 3:
            print("Error: --alpha expects exactly 3 integers (r, g, b), %d given!" % len(args.alpha))
            sys.exit(-1)
        alpha = (args.alpha[0], args.alpha[1], args.alpha[2])
    if (args.size != None) and (args.colors != None):
        print("Error: --size and --colors are incompatible")
        sys.exit(-1)
    RLE_file(args.input, compress=args.action, target_dim=target_dim, colors=args.colors, target_size=args.size, show=args.show, header=args.header, alpha=alpha)
