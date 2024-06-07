#!/usr/bin/env python

import numpy as np
import xarray as xr
import gsw

INPdir = "/data/users/dbruciaf/NOAA_WOA13v2/1955-2012/025"  # main path where woa13v2 input data are stored
inpS = INPdir + "/salinity"                                 # directory containing salinity woa13v2 data
inpT = INPdir + "/temperature"                              # directory containing temperature woa13v2 data

for mm in range(1,13):

    print('Processing month ', f"{mm:02d}")
   
    if mm in [1, 2, 3]:
       ss = 13
    elif mm in [4, 5, 6]:
       ss = 14
    elif mm in [7, 8, 9]:
       ss = 15
    elif ss in [10, 11, 12]:
       ss = 16

    Tfile1 = inpT + "/woa13_decav_t"+f"{mm:02d}"+"_04v2.nc"
    Sfile1 = inpS + "/woa13_decav_s"+f"{mm:02d}"+"_04v2.nc"
    Tfile2 = inpT + "/woa13_decav_t"+f"{ss:02d}"+"_04v2.nc"
    Sfile2 = inpS + "/woa13_decav_s"+f"{ss:02d}"+"_04v2.nc"
    ds_T1  = xr.open_dataset(Tfile1, decode_times=False)
    ds_S1  = xr.open_dataset(Sfile1, decode_times=False)
    ds_T2  = xr.open_dataset(Tfile2, decode_times=False)
    ds_S2  = xr.open_dataset(Sfile2, decode_times=False)

    ds_T2 = ds_T2.assign_coords(time=ds_T1.time)
    ds_S2 = ds_S2.assign_coords(time=ds_S1.time)

    if mm == 1:
       i1500 = np.argwhere(ds_S1.depth.where(ds_S1.depth == 1500., 0.).values)[0][0]

    da_T = xr.concat([ds_T1.t_an.sel(depth=slice(None,1500.)),
                      ds_T2.t_an.isel(depth=slice(i1500+1,None))
                     ], 
                     dim='depth'
                    )
    da_S = xr.concat([ds_S1.s_an.sel(depth=slice(None,1500.)),
                      ds_S2.s_an.isel(depth=slice(i1500+1,None))
                     ], 
                     dim='depth'
                    )

    if mm == 1:
       daT = da_T.copy()
       daS = da_S.copy()
    else:
       daT = xr.concat([daT, da_T], dim='time')
       daS = xr.concat([daS, da_S], dim='time')

# Absolute Salinity
daS = gsw.SA_from_SP(daS,
                     gsw.p_from_z(-daS.depth, daS.lat),
                     daS.lon,
                     daS.lat
                     )

# Conservative Temperature
daT = gsw.CT_from_t(daS,
                    daT,
                    gsw.p_from_z(-daT.depth, daT.lat)
                   )

dsT = daT.to_dataset()
dsS = daS.to_dataset()

dsT = dsT.rename_vars({"s_an":"thetao_con"})
dsS = dsS.rename_vars({"s_an":"so_abs"})


encT = {}
encS = {}
for i in dsT.coords: encT[i] = {"_FillValue": None }
for i in dsT.data_vars: encT[i] = {"_FillValue": None }
for i in dsS.coords: encS[i] = {"_FillValue": None }
for i in dsS.data_vars: encS[i] = {"_FillValue": None }

# Writing to netCDF
dsT.to_netcdf(INPdir + "/woa13v2.omip-clim.con_tem.nc", encoding=encT, unlimited_dims={'time':True})
dsS.to_netcdf(INPdir + "/woa13v2.omip-clim.abs_sal.nc", encoding=encS, unlimited_dims={'time':True})
