#!/bin/bash
# Quick wrapper to pass one year and one type at a time to python



mars_types="era40_ erai_" # ERA-I doesn't read yet!
mars_types="era40_"


end_year=2017

for ms in $mars_types
do
    
    if [ "$ms" = "erai_" ]; then
        start_year=1979
    else
        start_year=1957
    fi

    for year in $(seq $start_year $end_year)
    do
        
        python2.7 bufr_extract_unique_stations.py --ms $ms --year $year
        
    done
done