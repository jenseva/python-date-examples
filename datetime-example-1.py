# -*- coding: utf-8 -*-
"""
Created on Wed Sep 02, 2015
Examples of datetime and pytz
usage, conversions

@author: 
Jennifer Patterson
CeNCOOS
jpatterson@mbari.org

Example input time
231,3:03:17 PM
yearday, time in hh:mm:ss UTC, 12 hour clock

"""

from pylab import date2num
import dateutil
from pytz import timezone
import pytz
from datetime import datetime, timedelta
import os, errno

def findAge(timeUTC):
    
    # find age from pytz date in utc
    timeNowUTC = datetime.utcnow().replace(tzinfo = pytz.utc)
    diffnowUTC = timeNowUTC - timeUTC
    return(diffnowUTC)
    


utc = pytz.utc
pacific = timezone('US/Pacific') 
timeNowUTC = datetime.utcnow().replace(tzinfo = utc)
thisYear = timeNowUTC.year
    
ldir ='/datetime-example-1-sensorFile.txt'

print "\nChecking OS Dates on Local Files"

lFiles = []

for filenames in os.walk(ldir):
    for fn in filenames[2]: lFiles.append(fn)

sortedFiles = sorted(lFiles)

files2open = []

for f in sortedFiles:       # parse file os timestamp and make utc date, not timestamp in file text
    MM = f[0:2]
    DD = f[3:5]
    YYYY  = f[6:10]
    hh = f[11:13]
    mm = f[14:16]
    ss = f[17:19]
    
    # look at files now minus 4 days for backfilling in case of collection/server issues
    
    ftime = MM+'/'+DD+'/'+YYYY+' '+hh+':'+mm+':00'
    
    pacific = timezone('US/Pacific')
    
    fdatetime = datetime(int(YYYY), int(MM), int(DD), int(hh), int(mm), int(ss))
    print 'fdatetime = ',fdatetime

    fpytzUTC = utc.localize(fdatetime)
    print 'fpytz =',fpytzUTC
    
    a = findAge(fpytzUTC)

    if a.days < 4 and fpytzUTC.year == thisYear:
        files2open.append(f)

    print 'file age in days = ',a.days
    
    # file will be older than 4 days but for the sake of the example
    # lets add it to the list anyway so we can continue
    
    files2open.append(f)
        
lfn = 'datetime-example-1-lastOutputFile.csv'

# open last csv file                                                     
# check for new timestamps
# csv file timestamps are local (pacific)

lf = open(lfn,'r')                                  
lfc = lf.readlines()

for r in lfc:
    rc = r.split(',')
    lastdate = rc[2]
lf.close()

print '\nReading CSV file Date =',lastdate

ftime = dateutil.parser.parse(lastdate)
print ftime

'''
if this was a utc timestamp, add that info here
lastpytzUTC = utc.localize(ftime)    
print lastpytzUTC
'''

# But this reads a file with a local time stamp, so applying pacific time
lastpytzL = pacific.localize(ftime)    
print lastpytzL

ffn = ldir +'/' + fn

profilerfile = open(ffn,'r')
s = profilerfile.readlines()
theseTimes = []
count = 0

# --- Get timestamp from inside the file ---

#reading lines in data file
for line in s:
    line = line.rstrip('\n')
    
    if count >= 1:                                                      # start after the header lines
      
        line = line.split(',')
        
        # parse file yearday
        fyd = datetime(thisYear, 1, 1) + timedelta(int(line[0]) - 1)
       
        
        # parse file time 
        fts = dateutil.parser.parse(line[1])

        # combine into one timestamp
        ts = fyd.replace(year=thisYear, hour=fts.hour, minute=fts.minute, second=fts.second)

        # attach time zone to the datetime obj
        pytzUTC = utc.localize(ts)

        #  converts to pacific time
        convertedtoLocal = pacific.normalize(pytzUTC.astimezone(pacific))
        
        theseTimes.append(convertedtoLocal) 
       
    count= count +1
        
if lastpytzL > min(theseTimes) and lastpytzL < max(theseTimes):
    # same time as last profile processed. closing file
    profilerfile.close()
    
elif lastpytzL > min(theseTimes):
    # older time than last profile processed. closing file
    profilerfile.close()
    
else:
    # new profile data, Continuing processing, checking for surface data    
    data = []
    header = ['Parameter', 'Last value', 'Local Time']
    count = 0
    times = []
    surface_values = []
    surface = 0
        
    for line in s:
        line = line.rstrip('\n')
        linesplit = [x.strip() for x in line.split(',')]
        
        if count == 0:
            parameters = linesplit[2:]

        if count >= 1:                                                              # start after the header lines

            if (surface == 0) and float(linesplit[2]) > 1.75:                       # if surface not found yet look for surface
                
                fyd = datetime(thisYear, 1, 1) + timedelta(int(linesplit[0]) - 1)   # parse file yearday
                fts = dateutil.parser.parse(linesplit[1])                           # parse file time stamp
                ts = fyd.replace(year=thisYear, hour=fts.hour, minute=fts.minute)   # combine into one timestamp
                pytzUTC = utc.localize(ts)
                pytzL = pacific.normalize(pytzUTC.astimezone(pacific))      
                surface_values = (linesplit[2:])
                
                for x in surface_values: times.append(pytzL.strftime("%m/%d/%y %I:%M %p"))

        count = count + 1                  
    profilerfile.close()
    

