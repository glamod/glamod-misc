#!/usr/bin/python2.7

"""
Testing BUFR processing tools to extract ECMWF MARS files to CDM format

RJHD - Exeter - October 2017

"""

# ECMWF import defaults
import traceback
import sys

from eccodes import *

# RJHD imports


INFILE = "mars_era40_1957.bufr"
VERBOSE = 1 # verbose error reporting.

ATTRS = [
    'code',
    'units',
    'scale',
    'reference',
    'width'
    ]

INTMDI = 2147483647

"""CODE TABLES"""
# https://software.ecmwf.int/wiki/display/ECC/WMO%3D6+code-flag+table
# extract the few that are needed

stationType = {0 : "Automatic", 1 : "Manned", 2 : "Hybrid", 3: "Missing"} # 002001
# characteristicOfPressureTendency->units: CODE TABLE - 010063
# presentWeather->units: CODE TABLE - 020003
# pastWeather1->units: CODE TABLE - 020004
# pastWeather2->units: CODE TABLE - 020005
# verticalSignificanceSurfaceObservations->units: CODE TABLE - 008002
cloudAmount = {0: "0 oktas, 0/10", 1 : "1 okta or less but not zero, 1/10 or less, but not zero", 2 : "2 oktas, 2/10-3/10", 3 : "3 oktas, 4/10", 4 : "4 oktas, 5/10", 5 : "5 oktas, 6/10", 6 : "6 oktas, 7/10-8/10", 7 : "7 oktas or more but not eight, 9/10 or more but not 10/10", 8 : "8 oktas, 10/10", 9 : "sky obscured by fog or other meteorological phenomena", 10 : "cloud cover is indiscernable for reasons other than fog or other meteorological phenomena; or other reason why observation was not made"} # 020011
# cloudType->units: CODE TABLE - 020012
# centre->units: CODE TABLE - 001031
# generatingApplication->units: CODE TABLE - 001032





def get_all_keys(infilename):

    infile = open(infilename)

    counter = 0

    # loop all messages (with stop statement)
    while 1:

        """OPEN MESSAGE"""

        # get handle for message
        bufr = codes_bufr_new_from_file(infile)
        if bufr is None:
            break
 
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
 
        """EXTRACT DATA & ATTRIBUTES FOR ALL KEYS"""

        for key in these_keys:

            try:
                # get the key values
                print '  {:s}: {:}'.format(key, codes_get(bufr, key))

                # get the attributes as well
                for attr in ATTRS:
                    attr_key = key + "->" + attr
                    try:
                        print '  {:s}: {:}'.format(attr_key, codes_get(bufr, attr_key))
                    except CodesInternalError as err:
                        # print('Error with key="%s" : %s' % (attr_key, err.msg))
                        pass


                # try to get arrays sensibly
                # get size
                num = codes_get_size(bufr, key)
                if num > 1:
                    try:
                        print '  size of {:s} is: {}'.format(key, num)

                        # get values
                        values = codes_get_array(bufr, key)
                        for i in range(len(values)):
                            print "   {:d} {:06d}".format(i + 1, values[i])

                    except CodesInternalError as err:
                        print 'Error with key="{:s}" : {:s}'.format(attr_key, err.msg)
                        

            except CodesInternalError as err:
                # print('Error with key="%s" : %s' % (key, err.msg))
                pass

            if key == "#1#shipOrMobileLandStationIdentifier":
                stn_name = codes_get(bufr, key)


        """CLOSE MESSAGE AND OPTION TO MOVE ON"""

        counter += 1
 
        # delete handle
        codes_release(bufr)

        print "Station Name: {:s}".format(stn_name)
        raw_input("next message?")


    # close the file
    infile.close()
    
    return # get_all_keys

#***************************************************
def main():
    try:
        get_all_keys(INFILE)
    except CodesInternalError as err:
        if VERBOSE:
            traceback.print_exc(file=sys.stderr)
        else:
            sys.stderr.write(err.msg + '\n')
 
        return 1

    return # main
 
 
#***************************************************
if __name__ == "__main__":
    sys.exit(main())


#***************************************************
# END
#***************************************************
