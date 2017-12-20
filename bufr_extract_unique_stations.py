#!/usr/bin/python2.7

"""
Extract unique set of station locations (and names) along with number of obs

RJHD - Exeter - October 2017

"""

# ECMWF import defaults
import traceback
import sys

from eccodes import *

# RJHD imports
import cartopy
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import gc


VERBOSE = 1 # verbose error reporting.

ATTRS = [
    'code',
    'units',
    'scale',
    'reference',
    'width'
    ]

INTMDI = 2147483647


#***************************************************
def process_file(infilename, station_names, fixed_station, latitudes, longitudes, observations, start_year, end_year):

    infile = open(infilename)

    year = int(infilename.split(".")[0].split("_")[-1])

    cmatch = 0
    counter = 0

    # loop all messages (with stop statement)
    while 1:

        """OPEN MESSAGE"""

        # get handle for message
        bufr = codes_bufr_new_from_file(infile)
        if bufr is None:
            break

        if counter%100000 == 0:
            print "message: {:d}".format(counter)
 
        # we need to instruct ecCodes to expand all the descriptors
        # i.e. unpack the data values
        codes_set(bufr, 'unpack', 1)

        """ITERATOR TO EXTRACT KEYS"""

        these_keys = []

        # get BUFR key iterator
        iterid = codes_bufr_keys_iterator_new(bufr)
 
        # loop over the keys
        while codes_bufr_keys_iterator_next(iterid):
            # print key name
            keyname = codes_bufr_keys_iterator_get_name(iterid)
#            print("  %s" % keyname)
            these_keys += [keyname]

        # delete the key iterator
        codes_bufr_keys_iterator_delete(iterid)
        
        # Use these to select obs from land/marine surface
        name_keys = ["#1#shipOrMobileLandStationIdentifier", "#1#stationNumber"]

        processed = False
        for nk in name_keys:
            if nk in these_keys:
                try:
                    name = codes_get(bufr, nk)

                    lat = codes_get(bufr, "#1#latitude")
                    lon = codes_get(bufr, "#1#longitude")

                    sloc = tloc = nloc = [-1]
                    if name in station_names:
                        sloc, = np.where(station_names == name)
                    if lat in latitudes:
                        tloc, = np.where(latitudes == lat)
                    if lon in longitudes:
                        nloc, = np.where(longitudes == lon)


                    if tloc[0] == -1 and nloc[0] == -1:
                        # if not in list, then add
                        station_names = np.append(station_names, name)
                        latitudes = np.append(latitudes, lat)
                        longitudes = np.append(longitudes, lon)
                        observations = np.append(observations, 1)
                        start_year = np.append(start_year, year)
                        end_year = np.append(end_year, year)

                        # allow splitting of land and marine/mobile
                        if nk == "#1#stationNumber":
                            fixed_station = np.append(fixed_station, True)
                        else:
                            fixed_station = np.append(fixed_station, False)

                    elif (tloc[0] != -1 or nloc[0] != -1) and tloc[0] != nloc[0]:
                        # add if one element of position is unique
                        station_names = np.append(station_names, name)
                        latitudes = np.append(latitudes, lat)
                        longitudes = np.append(longitudes, lon)
                        observations = np.append(observations, 1)
                        start_year = np.append(start_year, year)
                        end_year = np.append(end_year, year)

                        # allow splitting of land and marine/mobile
                        if nk == "#1#stationNumber":
                            fixed_station = np.append(fixed_station, True)
                        else:
                            fixed_station = np.append(fixed_station, False)

                    elif tloc[0] != -1 and tloc[0] == nloc[0]:
                        # if position matches exactly, up observation counter
                        observations[tloc[0]] += 1
                        end_year[tloc[0]] = year

                        # allow splitting of land and marine/mobile
                        if nk == "#1#stationNumber":
                            if fixed_station[tloc[0]] != True:
                                # if listed as land and now marine, take marine
                                fixed_station[tloc[0]] = False
                            
                        else:
                            if fixed_station[tloc[0]] != False:
                                # easier to leave as mobile/marine than to move
                                # hopefully will stand out later
                                pass

                    else:
                        cmatch += 1

                    processed = True

                except CodesInternalError:
                    raw_input("key error?")

        # check for new keys which give station ID information
        if not processed:
            other_keys = ["#1#carrierBalloonOrAircraftIdentifier", "#1#aircraftFlightNumber"]
            new_key = True
            for ok in other_keys:
                if ok in these_keys: new_key = False

            if new_key:
                raw_input(these_keys)            

#        if counter > 10000: break
        counter += 1
        codes_release(bufr)


#    print "Number of unique locations in this year: {}".format(len(latitudes))

    return station_names, fixed_station, latitudes, longitudes, observations, start_year, end_year # process_file

#***************************************************
def scatter_map(outname, data, lons, lats, cmap, bounds, cb_label, title = "", figtext = "", doText = False):
    '''
    Standard scatter map

    :param str outname: output filename root
    :param array data: data to plot
    :param array lons: longitudes
    :param array lats: latitudes
    :param obj cmap: colourmap to use
    :param array bounds: bounds for discrete colormap
    :param str cb_label: colorbar label
    '''
     
    norm=mpl.cm.colors.BoundaryNorm(bounds,cmap.N)

    fig = plt.figure(figsize =(10,6.5))

    plt.clf()
    ax = plt.axes([0.05, 0.10, 0.90, 0.90], projection=cartopy.crs.Robinson())
    ax.gridlines() #draw_labels=True)
    ax.add_feature(cartopy.feature.LAND, zorder = 0, facecolor = "0.9", edgecolor = "k")
    ax.coastlines()

    ext = ax.get_extent() # save the original extent

    scatter = plt.scatter(lons, lats, c = data, cmap = cmap, norm = norm, s=10, \
                        transform = cartopy.crs.Geodetic(), edgecolor = "r", linewidth = 0.1)


    cb=plt.colorbar(scatter, orientation = 'horizontal', pad = 0.05, fraction = 0.05, \
                        aspect = 30, ticks = bounds[1:-1], label = cb_label, drawedges=True)

    # thicken border of colorbar and the dividers
    # http://stackoverflow.com/questions/14477696/customizing-colorbar-border-color-on-matplotlib

#    cb.set_ticklabels(["{:g}".format(b) for b in bounds[1:-1]])
#    cb.outline.set_color('k')
#    cb.outline.set_linewidth(2)
    cb.dividers.set_color('k')
    cb.dividers.set_linewidth(2)

    ax.set_extent(ext, ax.projection) # fix the extent change from colormesh

    plt.title(title)
    if doText:  plt.text(0.01, 0.98, "#stations: {}".format(data.shape[0]), transform = ax.transAxes, fontsize = 10)

    plt.savefig(outname)
    plt.close()

    return # scatter_map

#***************************************************
def main(ms = "era40_", year = 1980):

    LOCS = "/group_workspaces/jasmin2/c3s311a_lot2/data/incoming/mars/v20170628/data/"

    print year

    station_names = np.array([])
    fixed_station = np.array([])
    latitudes = np.array([])
    longitudes = np.array([])
    observations = np.array([])
    start_year = np.array([])
    end_year = np.array([])

    if ms == "erai_" and year < 1979:
        return
    else:

        INFILE = "{}mars_{}{}.bufr".format(LOCS, ms, year)

        try:
            station_names, fixed_station, latitudes, longitudes, observations, start_year, end_year = \
                process_file(INFILE, station_names, fixed_station, latitudes, longitudes, observations, start_year, end_year)
        except CodesInternalError as err:
            if VERBOSE:
                traceback.print_exc(file=sys.stderr)
            else:
                sys.stderr.write(err.msg + '\n')

    land = np.where(np.array(fixed_station) == True)
    marine = np.where(np.array(fixed_station) == False)

    bounds = np.linspace(0,max(observations),10).astype(int)
    cmap = plt.cm.YlOrRd_r

    if ms == "erai_":
        title = "MARS - SYNOP - {}".format(year)
    else:
        title = "MARS - ERA40 - {}".format(year)

    scatter_map("mars_{}{}_land_observations.png".format(ms, year), observations[land], longitudes[land], latitudes[land], cmap, bounds, "Number of Observations", title, doText = True)

    scatter_map("mars_{}{}_marine_observations.png".format(ms, year), observations[marine], longitudes[marine], latitudes[marine], cmap, bounds, "Number of Observations", title)

    station_names = 0
    fixed_station = 0
    latitudes = 0
    longitudes = 0
    observations = 0
    start_year = 0
    end_year = 0
    land = 0
    marine = 0
    gc.collect()


    return # main


#***************************************************
if __name__ == "__main__":
    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--ms', dest='ms', action='store', default = "era40_",
                        help='Run on ERA40 ["era40_"] (default) or ERA-I ["erai_"] data')
    parser.add_argument('--year', dest='year', action='store', default = 1980,
                        help='Which year to process - default 1980')
    args = parser.parse_args()

    main(ms = args.ms, year = args.year)
   
    sys.exit()


#***************************************************
# END
#***************************************************
