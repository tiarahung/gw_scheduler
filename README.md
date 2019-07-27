# gw_scheduler
GW Scheduler based on Dave Coulter's SN scheduler


Usage: (python 3)



python convert_GWoutput_to_scheduler_inverted_priority.py S190510_swope_150.txt S190510_swope_targets_example

python CreateSchedule.py --date 20190726 --file S190510_swope_targets_example.csv --obstele LCO:Swope

python convert_scheduler_output_to_GWoutput.py LCO_Swope_20190726_GoodSchedule.csv S190510_swope_150.txt 

Note: exposure times, bands, etc, can be changed in the Targets.py file
