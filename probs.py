import numpy as np
from astropy.io import ascii

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--tiles_file",
                  action="store", type=str, dest="tiles_file")

parser.add_argument("-s", "--schedule",
                  action="store", type=str, dest="schedule")

args = parser.parse_args()


schedule_file = args.schedule

schedule = np.loadtxt(schedule_file, delimiter=',', unpack=True, usecols=0, skiprows=1, dtype=str)
scheduled_tiles = []
for i in schedule:
    if i != "":
        scheduled_tiles.append(i)

scheduled_tiles = np.array(scheduled_tiles)
print ("Number of tiles scheduled: ",len(scheduled_tiles))

# infile=options.tiles_file

tiles_file = np.loadtxt(args.tiles_file, delimiter=',', skiprows=1, dtype=str)
coincidence, ind1, ind2 = np.intersect1d(scheduled_tiles, tiles_file[:,0], return_indices=True)




print ("Coincidence", len(coincidence), "(must be equal to number above): it's # overlapping tiles between original tiles file and scheduled tiles)")
# print (ps)
print("Sum of Priorities: ", sum(tiles_file[ind2, 6].astype(float)))

#print("Probability: ", 100*np.sum(ps))


