#!/bin/bash

# Input parameters

woa13="https://data.nodc.noaa.gov/woa/WOA13/DATAv2/"
Ftype="netcdf/decav/0.25"
Sdata="/data/users/dbruciaf/NOAA_WOA13v2/1955-2012/025/salinity"
Tdata="/data/users/dbruciaf/NOAA_WOA13v2/1955-2012/025/temperature"

# ------------------------------------------------------------------------

# 1) Downloading data

for mm in {1..16}; do
    m=`printf "%02d" ${mm}`
    echo $m
    wget ${woa13}/salinity/${Ftype}/woa13_decav_s${m}_04v2.nc
    wget ${woa13}/temperature/${Ftype}/woa13_decav_t${m}_04v2.nc
    ncatted -a units,time,m,c,"months since 0001-01-01" woa13_decav_s${m}_04v2.nc
    ncatted -a units,time,m,c,"months since 0001-01-01" woa13_decav_t${m}_04v2.nc
    mv woa13_decav_s${m}_04v2.nc ${Sdata}
    mv woa13_decav_t${m}_04v2.nc ${Tdata}
done

# 2) 
