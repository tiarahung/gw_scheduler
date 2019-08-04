# gw_scheduler
GW Scheduler based on Dave Coulter's SN scheduler

Some dependencies needed: 

pip install ephem

Usage: (python 3)


python master.py --tiles_file example_tiles.txt --date 20190728 --telescope Swope --start 0400 --end 0700

Telescope options: Swope, Thacher, Nickel

Note: exposure times, bands, etc, can be changed in the Telescopes.py file
