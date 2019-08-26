import os,sys
import numpy as np

from optparse import OptionParser
parser = OptionParser()



parser.add_option("-f", "--tiles_file",
                  action="store", type="string", dest="tiles_file")

# parser.add_option("-i", "--input_scheduler",
#                   action="store", type="string", dest="input_scheduler")

parser.add_option("-d", "--date",
                  action="store", type="string", dest="date")

# parser.add_option("-o", "--output_scheduler",
#                   action="store", type="string", dest="output_scheduler")

# parser.add_option("-c", "--fc_file",
#                   action="store", type="string", dest="fc_file")

parser.add_option("-t", "--telescope",
                  action="store", type="string", dest="telescope",help="Options: Swope, Thacher, Nickel")
parser.add_option("-a", "--now", help="Start Now -- True or False")
parser.add_option("-b", "--start", help="Desired Start Time in the format of HHMM")
parser.add_option("-c", "--end", help="Desired End Time in the format of HHMM")
	
(options, args) = parser.parse_args()



tiles_file=options.tiles_file

# input_scheduler=options.input_scheduler
date=options.date
telescope=options.telescope


input_scheduler='{0}_{1}_targets.csv'.format(date,telescope)

telescope=options.telescope
# output_scheduler=options.output_scheduler

# fc_file=options.fc_file

date=options.date

# print (telescope)

print("telescope is {0}".format(telescope))

print ("Tiles file converted into Scheduler input format")

os.system('python convert_GWoutput_to_scheduler_inverted_priority.py -t {0} -i {1}'.format(tiles_file,input_scheduler))

print ("***************************")


print ("Running Scheduler")

if telescope=='Swope':


	os.system('python CreateSchedule.py -d {0} -f {1} --obstele LCO:Swope --now {2} --start {3} --end {4}'.format(date,input_scheduler, options.now, options.start, options.end))

	print ("***************************")

	print ("Creating fields-center formatted file")


	os.system('python convert_scheduler_output_to_GWoutput.py -s LCO_Swope_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

elif telescope=='Thacher':

	os.system('python CreateSchedule.py -d {0} -f {1} --obstele Thacher:Thacher --now {2} --start {3} --end {4}'.format(date,input_scheduler, options.now, options.start, options.end))

	print ("***************************")


	print ("Creating fields-center formatted file")


	os.system('python convert_scheduler_output_to_GWoutput.py -s Thacher_Thacher_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

elif telescope=='Nickel':

	os.system('python CreateSchedule.py -d {0} -f {1} --obstele Lick:Nickel --now {2} --start {3} --end {4}'.format(date,input_scheduler, options.now, options.start, options.end))

	print ("***************************")


	print ("Creating fields-center formatted file")


	os.system('python convert_scheduler_output_to_GWoutput.py -s Lick_Nickel_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

elif telescope=='Keck':

	os.system('python CreateSchedule.py -d {0} -f {1} --obstele Keck:Keck --now {2} --start {3} --end {4}'.format(date,input_scheduler, options.now, options.start, options.end))

	print ("***************************")


	print ("Creating fields-center formatted file")


	os.system('python convert_scheduler_output_to_GWoutput.py -s Keck_Keck_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

os.system('python probs.py -f {0} --telescope {1} --date {2}'.format(tiles_file,telescope,date))