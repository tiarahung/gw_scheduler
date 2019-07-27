#!/usr/bin/env python
from __future__ import print_function
import sys
import numpy as np
from astropy.io import ascii

infile=sys.argv[1]

outfile=sys.argv[2]



tile_name=np.loadtxt('{0}.csv'.format(infile),delimiter=',',unpack=True,usecols=0,skiprows=1,
                     dtype=str)

print (len(tile_name))

new=[]
for i in tile_name:
    if i != "":
        # print (i
        new.append(i)

print (len(new))

print (new)


lines_to_keep = []
with open('{0}.csv'.format(outfile), "r") as f:

     for line in f.readlines():
     	for i in new:
         if i in line:
             lines_to_keep.append(line)

# Write all the links in our list to the file
with open("test.txt", "w") as f:

    for line in lines_to_keep:
        f.write(line)
f.close()