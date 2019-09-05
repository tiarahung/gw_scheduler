import Constants
import Telescope
from Utilities import UTC_Offset

import ephem
from dateutil.parser import parse
from datetime import tzinfo, timedelta, datetime
import pytz as pytz
import numpy as np
import operator
import copy
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.dates as md

class Observatory():
    def __init__(self, name, lon, lat, elevation, horizon, telescopes, obs_date_str, utc_offset, utc_offset_name, startNow, start, end):

        self.name = name
        self.ephemeris = ephem.Observer()
        self.ephemeris.lon = lon
        self.ephemeris.lat = lat
        self.ephemeris.elevation = elevation
        self.ephemeris.horizon = horizon
        self.telescopes = telescopes

        self.obs_date_string = obs_date_str
        obs_date = parse("%s 12:00" % obs_date_str) # UTC Noon
        self.obs_date = obs_date
        self.ephemeris.date = (self.obs_date - timedelta(hours=utc_offset)) # Local Noon n UTC

        self.utc_begin_night = self.ephemeris.next_setting(ephem.Sun(), use_center=True).datetime()
        self.utc_end_night = self.ephemeris.next_rising(ephem.Sun(), use_center=True).datetime()

        if startNow:
            self.utc_begin_night = datetime.utcnow()
        elif (start is not None) and (str(start[:2]) != 'No'):
            self.utc_begin_night = self.utc_begin_night.replace(hour=int(start[:2]))
            self.utc_begin_night = self.utc_begin_night.replace(minute=int(start[2:]))
            self.utc_end_night = self.ephemeris.next_rising(ephem.Sun(), use_center=True).datetime() + timedelta(-1)
        if (end is not None) and (str(end[:2]) != 'No'):
            self.utc_end_night = self.utc_end_night.replace(hour=int(end[:2]))
            self.utc_end_night = self.utc_end_night.replace(minute=int(end[2:]))
        if (self.utc_end_night<self.utc_begin_night):
            self.utc_end_night = self.utc_end_night + timedelta(1)

        self.local_begin_night = pytz.utc.localize(self.utc_begin_night) \
                                 .astimezone(UTC_Offset(utc_offset,utc_offset_name))
        self.local_end_night = pytz.utc.localize(self.utc_end_night) \
                                   .astimezone(UTC_Offset(utc_offset,utc_offset_name))
        timeDiff = self.local_end_night - self.local_begin_night
        self.length_of_night = int(round(timeDiff.total_seconds() / 60))

        self.utc_time_array = np.asarray([self.utc_begin_night + timedelta(minutes=minute) \
                                          for minute in range(self.length_of_night)])

        self.local_time_array = np.asarray([self.local_begin_night + timedelta(minutes=minute) \
                                      for minute in range(self.length_of_night)])

        self.sidereal_string_array = []
        self.sidereal_radian_array = []

        for utc_time in self.utc_time_array:
            self.ephemeris.date = utc_time
            st = self.ephemeris.sidereal_time()

            tokens = str(st).split(":")
            float_tokens = [float(t) for t in tokens]
            st_string = "%02d:%02d:%02d" % (float_tokens[0],float_tokens[1],float_tokens[2])

            self.sidereal_string_array.append(st_string)
            self.sidereal_radian_array.append(st)

        print("%s - %s deg Twilight Ends: %s" % (self.name, np.abs(self.ephemeris.horizon), self.local_begin_night))
        print("%s - %s deg Dawn Begins: %s" % (self.name, np.abs(self.ephemeris.horizon), self.local_end_night))

    def is_contiguous(self, int_array):
        i = iter(int_array)
        first = next(i)
        contiguous = all(a == b for a, b in enumerate(i, first + 1))
        return contiguous


    def schedule_targets(self, telescope_name, preview_plot=False, asap=False):

        # Update internal Target list with priorities and exposures
        telescope = self.telescopes[telescope_name]
        telescope.compute_exposures()
        telescope.compute_net_priorities()
        targets = telescope.get_targets()


        def packable(goodtime, tgt):
            """Find nearby time intervals that amount to the observing time of a tile"""
            m_start = None
            goodtime_len = len(goodtime[0])
            if goodtime_len < tgt.total_minutes:
                return None
            for m in range(len(goodtime[0][:-(tgt.total_minutes - 1)])):
                # Exclude sparse intervals t_i - t_0 > 45 min
                if (goodtime[0][m + (tgt.total_minutes - 1)] - goodtime[0][m]) < 45:
                    m_start = m
            return m_start

        def squeeze(tgt_i, targets, m_start):
            """ Move the scheduled time of the affected tiles to make room for a new tile """
            for tt in targets[:tgt_i]:
                affected_ind_up = goodtime[0][m_start + (tgt.total_minutes - 1)]
                affected_ind_low = goodtime[0][m_start]
                if (tt.starting_index < affected_ind_up) and (tt.starting_index > affected_ind_low):
                    ind_increment = len(np.where(goodtime[0][m_start : m_start + tgt.total_minutes] > tt.starting_index)[0])
                    tt.starting_index += ind_increment
                    # print(tt.starting_index)
            time_slots[affected_ind_low:affected_ind_up + 1] = 1
            return affected_ind_low

        # Sorted by priority and closeness to discovery
        if asap:
            targets.sort(key = operator.attrgetter('priority'))
        else:
            targets.sort(key = operator.attrgetter('net_priority')) # 'TotalGoodAirMass'

        length_of_night = len(self.utc_time_array) # In minutes

        for tgt in targets:
            print("%s: %s; %s min; Pri: %s" % (tgt.name, tgt.exposures, tgt.total_minutes, tgt.priority))

        time_slots = np.zeros(length_of_night)
        o = []
        bad_o = []

        for tgt_i, tgt in enumerate(targets):

            gam1 = copy.deepcopy(tgt.raw_airmass_array)
            gam2 = copy.deepcopy(tgt.raw_airmass_array)
            found = False

            while not found:
                if tgt.total_observable_min <= 0:
                    print("%s is unobservable!" % tgt.name)
                    break

                gam2[np.where(time_slots == 1)] = 8888 # make different than airmass cutoff flag
                goodtime = np.where(gam2 <= Constants.airmass_threshold)
                n = len(goodtime[0])

                current_start = -1 # So that iterator below starts at 0, the first index
                best_indices = []
                largest_airmass = 1e+6

                # We are crawling forward along the array, grabbing segments of length "total_min",
                # and incrementing in starting index

                for i in range(n):
                    current_start += 1 # start index
                    end = (current_start + tgt.total_minutes) # how many
                    candidate_indices = goodtime[0][current_start:end] # array of selected indices
                    # Check if this associated integrated airmass corresponds to a range of time that's contiguous
                    contiguous = self.is_contiguous(candidate_indices)
                    if len(candidate_indices) != tgt.total_minutes or not contiguous: # If this is at the end of the array, it won't be the size we need
        #                 print("%s: can't fit %s exp time in slot of size %s " % \
        #                       (obj.Name, obj.TotalMinutes, len(candidate_indices)))
        #                 print(candidate_indices)
                        continue

                    else:
                        # Compute the integrated airmass. We're looking for the smallest # => the best conditions
                        integrated_am = np.sum(gam1[candidate_indices])
                        if asap:
                            if (integrated_am <= (Constants.airmass_threshold * tgt.total_minutes)):
                                largest_airmass = integrated_am
                                best_indices = candidate_indices
                                break

                        else:
                        # if this is the smallest, and is for a contiguous span of time, it's the new one to beat
                            if integrated_am < largest_airmass and contiguous:
                                largest_airmass = integrated_am
                                best_indices = candidate_indices

                if largest_airmass < 1e+6:

                    found = True
                    time_slots[best_indices] = 1 # reserve these slots

                    # grab the corresponding
                    tgt.scheduled_airmass_array = np.asarray(tgt.raw_airmass_array)[best_indices]
                    tgt.scheduled_time_array = np.asarray(self.local_time_array)[best_indices]
                    tgt.starting_index = best_indices[0]

                    o.append(tgt)
                else:
                    m_start = packable(goodtime, tgt)
                    if asap and (m_start is not None):
                        tgt.starting_index = squeeze(tgt_i, targets, m_start)
                        o.append(tgt)
                        print('Successfully included field %i: %s %.3E' %(tgt_i, tgt.name, 1./tgt.priority/1000))
                        found = True
                        best_indices = np.arange(tgt.starting_index, tgt.starting_index + 4)
                        tgt.scheduled_airmass_array = np.asarray(tgt.raw_airmass_array)[best_indices]
                        tgt.scheduled_time_array = np.asarray(self.local_time_array)[best_indices]
                        break
                    else:
                        print("Can't fit %s. Skipping!" % tgt.name)
                        bad_o.append(tgt)
                        break

        self.plot_results(o, telescope_name, preview_plot)

        telescope.write_schedule(self.name, self.obs_date ,o)

    def plot_results(self, good_targets, telescope_name, preview_plot):
        good_targets.sort(key = operator.attrgetter('starting_index'))
        length_of_night = len(self.utc_time_array) # in minutes

        fig = plt.figure(figsize=(10,4))
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twiny()
        ax3 = ax1.twiny()

        ax1.invert_yaxis()
        ax1.set_ylim([Constants.airmass_threshold,0.8])
        n = len(good_targets)
        color=cm.rainbow(np.linspace(0,1,n))
        c = iter(color)

        ax1.set_ylabel("Relative Air Mass")
        ax1.set_xlabel("Local Time")
        ax1.grid(True)
        ax1.set_axisbelow(True)

        ax2.plot(self.utc_time_array, np.zeros(length_of_night))
        ax2.set_xlabel("UTC")
        ax2.get_xaxis().set_major_formatter(md.DateFormatter('%H:%M'))

        ax3.plot(self.utc_time_array, np.zeros(length_of_night))
        num_ticks = 7
        nn = round(length_of_night/num_ticks)
        ax3_ind = [i*nn for i in range(num_ticks)]
        ax3_ind.remove(0)
        ax3.set_xlabel("LST")
        ax3.xaxis.set_ticks_position("bottom")
        ax3.xaxis.set_label_position("bottom")
        ax3.set_xticks(np.asarray(self.utc_time_array)[ax3_ind])
        ax3.set_xticklabels(np.asarray(self.sidereal_string_array)[[ax3_ind]]) #,rotation=0,fontsize='small'
        # Offset the twin axis below the host
        ax3.spines["bottom"].set_position(("axes", -0.18))

        total_tgts = 0
        for tgt in good_targets:
            lbl = "%s\nNat Pri: %s\nNet Pri: %0.5f\n%s min" % (tgt.name, tgt.priority, tgt.net_priority, tgt.total_minutes)
            total_tgts += tgt.total_minutes
            col = next(c)

            ax1.plot(self.local_time_array,tgt.raw_airmass_array,c=col,linewidth=3.0,alpha=0.1)
            ax1.plot(tgt.scheduled_time_array,tgt.scheduled_airmass_array,c=col,label=lbl,linewidth=3.0)

        leg = ax1.legend(bbox_to_anchor=(1.01, 1.015), loc='upper left', ncol=2, prop={'size':8})
        # set the linewidth of each legend object
        for legobj in leg.legendHandles:
            legobj.set_linewidth(3.0)

        percent1 = 100*float(total_tgts)/float(self.length_of_night)
        fig.suptitle("%s %s: %s\nOpen Shutter Time: %0.2f%%" % \
             (self.name, telescope_name, self.obs_date.date(),percent1),y=1.10)

        fig_to_save = "%s_%s_%s_Plot.png" % (self.name, telescope_name, self.obs_date_string)
        fig.savefig(fig_to_save,bbox_inches='tight',dpi=300)

        if preview_plot:
            plt.show(block=False)
