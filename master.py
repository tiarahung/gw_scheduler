import os,sys
import numpy as np
import argparse


if __name__ == '__main__':
    obs = {'Swope': 'LCO', 'Thacher': 'Thacher', 'Nickel': 'Lick', 'Keck': 'Keck'}

    working_dir = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--tiles_file",
                      action="store", type=str, dest="tiles_file")

    parser.add_argument("-d", "--date",
                      action="store", type=str, dest="date")

    parser.add_argument("-t", "--telescope",
                      action="store", type=str, dest="telescope",help="Options: Swope, Thacher, Nickel")
    parser.add_argument("-a", "--now", help="Start Now -- True or False")
    parser.add_argument("-b", "--start", help="Desired Start Time in the format of HHMM")
    parser.add_argument("-c", "--end", help="Desired End Time in the format of HHMM")
    parser.add_argument("-A", "--asap", action='store_true', default=False)
    parser.add_argument("-e", "--exp", help="exposure time", type=int, default=120)
    parser.add_argument("-o", "--outdir", action="store", type=str, dest="outdir")


    args = parser.parse_args()
    telescope = args.telescope
    tiles_file=args.tiles_file
    date=args.date
    # Make new directory
    dirname = "%s_%s_%s" %(telescope, os.path.splitext(tiles_file)[0], date)
    dirpath = os.path.join(working_dir, dirname)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    # input_scheduler=args.input_scheduler

    input_scheduler=os.path.join(dirpath, '{0}_{1}_targets.csv'.format(date, telescope))

    date=args.date

    print("telescope is {0}".format(telescope))

    print ("Tiles file converted into Scheduler input format")

    convert_scheduler = os.path.join(working_dir, "convert_GWoutput_to_scheduler_inverted_priority.py")
    os.system('python {0} -t {1} -i {2}'.format(convert_scheduler, tiles_file, input_scheduler))
    print ("***************************")


    print ("Running Scheduler")

    create_schedule_script = os.path.join(working_dir, 'CreateSchedule.py')
    create_schedule_cmd = 'python {0} -d {1} -f {2} --obstele {3}:{4} --now {5} --start {6} --end {7} --exp {8} --outdir {9}'.format(create_schedule_script, date,input_scheduler, obs[telescope], telescope, args.now, args.start, args.end, args.exp, dirpath)
    if args.asap:
        create_schedule_cmd += " -A"

    os.system(create_schedule_cmd)

    print ("***************************")

    print ("Creating fields-center formatted file")


    convert_scheduler_script = os.path.join(working_dir, 'convert_scheduler_output_to_GWoutput.py')

    goodschedule_file = os.path.join(dirpath, "%s_%s_%s_GoodSchedule.csv" %(obs[telescope], telescope, date,))
    FC_file = os.path.join(dirpath, 'FC_%s_%s.txt' %(telescope, date,))
    convert_scheduler_cmd = 'python {0} -s {1} -t {2} -c {3}'.format(convert_scheduler_script, goodschedule_file, tiles_file, FC_file)
    os.system(convert_scheduler_cmd)

    print ("Calculate Probability")

    prob_script = os.path.join(working_dir, 'probs.py')
    os.system('python {0} -f {1} -s {2}'.format(prob_script, tiles_file, goodschedule_file))



"""
if telescope=='Swope':

    oscommand = 'python CreateSchedule.py -d {0} -f {1} --obstele LCO:Swope --now {2} --start {3} --end {4}'.format(date,input_scheduler, args.now, args.start, args.end)
    if args.asap:
        oscommand += " -A"
    os.system(oscommand)

    print ("***************************")

    print ("Creating fields-center formatted file")


    os.system('python convert_scheduler_output_to_GWoutput.py -s LCO_Swope_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

elif telescope=='Thacher':

    os.system('python CreateSchedule.py -d {0} -f {1} --obstele Thacher:Thacher --now {2} --start {3} --end {4}'.format(date,input_scheduler, args.now, args.start, args.end))

    print ("***************************")


    print ("Creating fields-center formatted file")


    os.system('python convert_scheduler_output_to_GWoutput.py -s Thacher_Thacher_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

elif telescope=='Nickel':

    os.system('python CreateSchedule.py -d {0} -f {1} --obstele Lick:Nickel --now {2} --start {3} --end {4}'.format(date,input_scheduler, args.now, args.start, args.end))

    print ("***************************")


    print ("Creating fields-center formatted file")


    os.system('python convert_scheduler_output_to_GWoutput.py -s Lick_Nickel_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

elif telescope=='Keck':

    os.system('python CreateSchedule.py -d {0} -f {1} --obstele Keck:Keck --now {2} --start {3} --end {4}'.format(date,input_scheduler, args.now, args.start, args.end))

    print ("***************************")


    print ("Creating fields-center formatted file")


    os.system('python convert_scheduler_output_to_GWoutput.py -s Keck_Keck_{0}_GoodSchedule.csv -t {1} -c FC_{0}_{2}.txt'.format(date,tiles_file,telescope))

os.system('python probs.py -f {0} --telescope {1} --date {2}'.format(tiles_file,telescope,date))"""
