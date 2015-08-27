# take all the files from a directory tree and join them by monitor/channel
# Toby Thurston -- 25 Jul 2015 

from __future__ import print_function, with_statement, generators
import os
import sys
import re
import datetime as dt
import itertools as it
import collections
breaks_for = collections.defaultdict(list)

dt_format = 'D%Y-%m-%dT%H%M'
filename_matcher = re.compile(r'\S+(M\d\d\dC\d\d)\.txt')

for root, dirs, files in os.walk('.'):
    for name in files:
        filename = os.path.join(root, name)
        fm = filename_matcher.match(filename)
        if fm:
            with open(filename) as f:
                id, d, m, y = f.readline().split()
                date = [d,m,y]
                mins = int(f.readline().strip())
                n = int(f.readline().strip())
                time = f.readline().strip()
                breaks = [int(x) for x in f.readlines()]
           
            # check everything is as expected
            try:
                assert(name == id + '.txt')
                assert(time == '0800')
                assert(n == 1)
                assert(mins == 1441)
                assert(len(breaks) == 1441)
            except AssertionError:
                print("---> Unexpected information in file:", name, file=sys.stderr)
                raise

            id = id[7:14] # extract the MnnnCmm bit
            key = fm.group(1)
            assert(key==id)

            start = dt.datetime.strptime(' '.join(date) + ' ' + time, '%d %b %Y %H%M')

            breaks_for[id].append( (start.strftime(dt_format), breaks) )

out = list()
for k in sorted(breaks_for):
    # join the breaks lists in the right order (skipping the duplicated value at the end of each day)
    breaks = list()
    for i in (y[:-1] for x,y in sorted(breaks_for[k])):
        for j in i:
            breaks.append(j)
    
    # skip empty channels
    if sum(breaks)==0:
        print("---> Assumed empty channel:", k, file=sys.stderr)
        continue

    # retreive the first time stamp
    start = dt.datetime.strptime(sorted(breaks_for[k])[0][0], dt_format)

    # split the id up into Mnnn and Cmm, determine what "type" this is
    monitor = k[0:4]
    channel = k[4:]

    # This is a huge assumption!  test flies are in channels 17-32
    if channel > 'C16':
        type = 'control'
    else:
        type = 'test'

    # z = run length of zeros, threshold is how long to wait before it counts as sleep
    z = 0
    threshold = 5  # <- another assumption
    sleeps = list()
    for b in breaks:
        if b==0:
            z = z+1
        else:
            if z >= threshold:
                s = 1
            else:
                s = 0
            for i in range(z):
                sleeps.append(s)
            z = 0
            sleeps.append(0)
    
    # repeat check at end of array in case we are asleep at the end
    # and also check that the fly has not died - ignore it's data if it has
    if z>0:
        if z >= threshold:
            s = 1
        else:
            s = 0
        for i in range(z):
            sleeps.append(s)
        # assume dead if final sleep is > 1400 mins
        if z>1400:
            print("---> Assumed fly died:", k, file=sys.stderr)
            continue

    # sleeps should now match breaks with a 1 for each minute in a sleep bout
    assert(len(sleeps)==len(breaks))

    days = int(len(breaks)/1440)
    assert(len(sleeps)==1440*days)

    for d in range(days):
        for h in range(24):
            if h < 12:
                period = 'day'
            else:
                period = 'night'

            offset = 1440*d+60*h
            s = sleeps[offset:offset+60]

            try:
                latency = s.index(1)
            except ValueError:
                latency = 60

            bouts = list()
            for (k,g) in it.groupby(s):
                if k==1:
                    bouts.append(sum(g))
            bout_count = len(bouts)
            bout_total = sum(bouts)
            out.append('{:8} {:8} {:8} {:4d} {} {:7} {:7d} {:7d} {:5d} {:5d}'.format(
                    monitor,
                    monitor+channel, 
                    type, 
                    1+24*d+h, 
                    start+dt.timedelta(hours=24*d+h), 
                    period,
                    sum(breaks[offset:offset+60]), 
                    latency, 
                    bout_count, 
                    bout_total))

print(
        "Monitor ",
        "Fly     ",
        "Type    ",
        "Hour",
        "Date      ",
        "Time    ",
        "Period",
        "Activity",
        "Latency",
        "Bouts",
        "Sleep"
        )

for x in out:
   print(x)
