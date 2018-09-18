#!/usr/local/bin/python
import sys


def findset(input):
   res = []
   i = len(input)
   for b in input:
     i-=1
     if b == '1':
         res.append(i)
   return res

if sys.argv[1][:2] == "0x":
    value = int(sys.argv[1][2:], 16)
else:
    value = int(sys.argv[1][:2])

res = findset(bin(value)[2:])
print bin(value)[2:]
print res
