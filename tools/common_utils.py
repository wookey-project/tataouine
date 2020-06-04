# Various utils and helpers common to all our scripts

import sys, os, array, time
import binascii
from subprocess import Popen, PIPE, STDOUT
from threading import Timer
import math

# Import our ECC python primitives
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + "../externals/libecc/scripts/")

from expand_libecc import *

### Ctrl-C handler
def handler(signal, frame):
    print("\nSIGINT caught: exiting ...")
    exit(0)

# Helper to execute an external command
def sys_cmd(cmd):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    kill = lambda process: process.kill()
    timer = Timer(100, kill, [p])
    timer.start()
    out = p.stdout.read()
    if timer.is_alive():
        timer.cancel()
    p.wait()
    if p.returncode != 0:
        print("Error when executing command: "+cmd)
        print("Exec Trace:\n"+str_decode(out))
        sys.exit(-1)
    return out

# Remove a file
def sys_rm_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
    return

# Read a string from a file
def read_in_file(infilename):
    infile = open(infilename, 'rb')
    data = infile.read()
    infile.close()
    if is_python_2() == False:
        data = data.decode('latin-1')
    return data

# Save a string in a file
def save_in_file(data, outfilename):
    if is_python_2() == False:
        data = data.encode('latin-1')
    outfile = open(outfilename, 'wb')
    outfile.write(data)
    outfile.close()

# Helper to generate a random string with proper entropy
def gen_rand_string(size):
    if is_python_2() == True:
        return os.urandom(size)
    else:
        return os.urandom(size).decode('latin-1')

# Python 2/3 hexlify helper
def local_hexlify(str_in):
    if is_python_2() == True:
        return binascii.hexlify(str_in)
    else:
        return (binascii.hexlify(str_in.encode('latin-1'))).decode('latin-1')


# Python 2/3 unhexlify helper
def local_unhexlify(str_in):
    if is_python_2() == True:
        return binascii.unhexlify(str_in)
    else:
        return (binascii.unhexlify(str_in.encode('latin-1'))).decode('latin-1')

# Python 2/3 string handling
def str_decode(b):
    if is_python_2() == False:
        return b.decode('latin-1')
    else:
        return b

def str_encode(b):
    if is_python_2() == False:
        return b.encode('latin-1')
    else:
        return b

## High level helpers
# Helper to check the entropy of a string. Second argument
# tells if this is a common string, a PIN, or a password
def check_string_security_policy(instr, strtype='PASSWORD'):
    if (strtype != 'PASSWORD') and (strtype != 'PIN') and (strtype != 'NAME'):
        return False
    # TODO: complete the checks!
    return True

