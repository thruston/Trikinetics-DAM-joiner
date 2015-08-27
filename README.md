# Trikinetics-DAM-joiner
Short Python script for collecting data from Trikinetics DAM logs

This file describes the Python program to join all the fly data monitor files.

To run the program you need python version 2.7+ or 3.3+ installed. 

If you are using a modern Mac, you should already have Python V2.7 installed.

To run the program do the following

 1. Put all the data files into appropriate subdirectories beneath the directory
    where this program is.

 2. The program assumes that each file is named 'xxxxxxxMnnnCnn.txt'
    where the first few characters are just some name, 'Mnnn' is the 
    monitor number and 'Cnn' is the channel number.

    It would not be hard to adapt the program to some other naming convention, but
    that's what it is at present.

 3. Open a terminal window and navigate to the directory where the program is.
    The command `ls` should show you the program, and a bunch of directories with your data 
    files in. 

 4. Run the program using `python joiner.py`.  When you do that the output will be written 
    all over the screen (after a second or so), so what you need to do is to capture the 
    output into a file.  So run it again using the output redirection feature:

        `python joiner.py > combinedfly.data`

    or some other suitable output file name.  This will create a new file with the output
    which you can load into R or Excel or wherever.  On my system the program takes about 
    1.6 seconds to run with python V2 and about 1.3 seconds with python V3.


The following assumptions are made.

1. All the flies in channels 1-16 are control flies, while all the flies in 17-32 are test.

2. Zero beam counts for 5 consecutive minutes counts as a sleep bout

3. If all the beam counts for a channel are zero, we assume the channel was empty, and it's excluded.

4. If the channel data ends with a sleep bout longer than 1400 minutes we assume the fly died, and it's excluded.

The following columns are produced

        Monitor   - the monitor label Mxxx
        Fly       - the Monitor+Channel MxxxCyy
        Type      - control or test (ie channel 1-16 or 17-32)
        Hour      - hour of the experiment (starting at 1, so hour 25 is in day 2...)
        Date      - calendar date of this hour
        Time      - clock time of this hour
        Period    - day (08:00 to 19:59) or night (20:00 to 07:59)
        Activity  - beam breaks in this hour
        Latency   - minutes to first sleep in this hour (60 if there was no sleep)
        Bouts     - bouts of sleep in this hour
        Sleep     - total duration of the sleep bouts in minutes in this hour


Toby Thurston -- 27 Aug 2015 
