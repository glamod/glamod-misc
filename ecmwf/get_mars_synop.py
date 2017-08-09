#!/usr/bin/python2.7

'''
Code to download and transfer the MARS SYNOP data from 
ECMWF to the JASMIN GWS for Copernicus C3S 311a Lot2

lifted and adapted from
     https://software.ecmwf.int/wiki/display/WEBAPI/Python+ERA-interim+examples 

But wanting MARS access
     https://software.ecmwf.int/wiki/display/WEBAPI/Access+MARS

14/6/2017 RJHD, Exeter

-------------------------------------------

To find observations online:

Mars Catalogue / Operational Archive / Atmospheric Model / 1 / Observations-Observations / Year / Month / Conventional Data / 

select day, time and observation type (scroll to Synop)
'''

import os
import datetime as dt
import calendar
import numpy as np

from ecmwfapi import ECMWFService

server = ECMWFService("mars") # want the MARS archive

# JASMIN group work space
GWS = "/group_workspaces/jasmin2/c3s311a_lot2/data/incoming/"
outdir = "mars/"
version = "v20170628/"

"""
OBSTYPE:

https://software.ecmwf.int/wiki/display/UDOC/Identification+keywords#Identificationkeywords-obstype

Land surface and sea surface data types are:
LSD - 1/2/3/4/140/
SSD - 9/11/12/13/14/19/20/21/22/23/

Liz Kent said not to worry about Reduced COADS data - #20
"""


#*************************************************************
def run_mars_request(start, end, outfile):

    server.execute({
            # Specify the ERA-Interim data archive. Don't change.
            "class": "od", # operational data
            "expver": "1", # version of the data
            "date": "{}/to/{}".format(start,end), # date range to extract
            "obsgroup": "con", # conventional observations
            "obstype": "1/2/3/4/140/9/11/12/13/14/19/21/22/23", 
            "stream": "oper", # operational atmospheric model
            "time": "00:00:00/03:00:00/06:00:00/09:00:00/12:00:00/15:00:00/18:00:00/21:00:00", # all 3 hourly timesteps
            "type": "ob", # observations
            },
                   outfile
                   )

    return # run_mars_request

#*************************************************************
#*************************************************************
SplitMonths = False

today = dt.datetime.now()


# spin through each year
#for year in range(1979, dt.datetime.now().year + 1):
for year in range(2017, dt.datetime.now().year + 1):


    if SplitMonths:

        # spin through each month
        for month in (1 + np.arange(12)):
	
            start = dt.datetime.strftime(dt.datetime(year,month,1), "%Y-%m-%d")
	    if year == today.year and month == today.month:
                end = dt.datetime.strftime(today, "%Y-%m-%d")
	    elif year == today.year and month > today.month:
	        break	
	    else:
                end = dt.datetime.strftime(dt.datetime(year,month,calendar.monthrange(year,month)[1]), "%Y-%m-%d")

	    	

            # set up the start and end dates in correct format
            start = dt.datetime.strftime(dt.datetime(year,month,1), "%Y-%m-%d")
            end = dt.datetime.strftime(dt.datetime(year,month,calendar.monthrange(year,month)[1]), "%Y-%m-%d")

            # make output filename
            filename = "mars_{}.bufr".format(dt.datetime.strftime(dt.datetime(year,month,1), "%Y_%m"))

            # replace with run request and GWS once ready
            print start, end, filename

            run_mars_request(start, end, os.path.join(GWS, outdir, version, "data", filename))      

    else:
        
        start = dt.datetime.strftime(dt.datetime(year,1,1), "%Y-%m-%d")
	
	if year == today.year:
            end = dt.datetime.strftime(today, "%Y-%m-%d")
	else:
            end = dt.datetime.strftime(dt.datetime(year,12,31), "%Y-%m-%d")

        # make output filename
        filename = "mars_{}.bufr".format(dt.datetime.strftime(dt.datetime(year,1,1), "%Y"))

        # replace with run request and GWS once ready
        print start, end, filename

        run_mars_request(start, end, os.path.join(GWS, outdir, version, "data", filename))      


print "finished"

#*************************************************************
