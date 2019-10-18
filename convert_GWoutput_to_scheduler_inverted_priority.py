#!/usr/bin/env python
from __future__ import print_function
import sys
import numpy as np

import argparse


def main():


    fout = open(outfile,'w')
    with open(infile) as fin:
        print("Name,RA,DEC,Priority,DiscDates,DiscMags,Type",file=fout)
        for line in fin:
            # print(line)
            line = line.replace('\n','')
            line = line.replace(' ','')
            if line == '' or line.startswith('F') or line.startswith('#'):
                continue

            lineparts = line.split(',')
            lineparts[4] = addstring
            # print (1/np.float(lineparts[6])/1000)
            lineparts[3] = np.str(1/np.float(lineparts[6])/1000)

            print(",".join(lineparts[:5]),file=fout)


    # print ("Tiles file converted into Scheduler input format")
    fout.close()

if __name__ == "__main__":

    addstring='2019-04-12,12,GW'
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tiles_file",
                      action="store", type=str, dest="tiles_file")

    parser.add_argument("-i", "--input_scheduler",
                      action="store", type=str, dest="input_scheduler")

    args = parser.parse_args()

    infile = args.tiles_file

    outfile = args.input_scheduler
    main()
