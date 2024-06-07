#!/usr/bin/env python

import xarray as xr
import numpy as np

#=======================================================================================
def hvrsn_dst(lon1, lat1, lon2, lat2):
    '''
    This function calculates the great-circle distance in meters between 
    point1 (lon1,lat1) and point2 (lon2,lat2) using the Haversine formula 
    on a spherical earth of radius 6372.8 km. 

    The great-circle distance is the shortest distance over the earth's surface.
    ( see http://www.movable-type.co.uk/scripts/latlong.html)

    If lon2 and lat2 are 2D matrixes, then dist will be a 2D matrix of distances 
    between all the points in the 2D field and point(lon1,lat1).

    If lon1, lat1, lon2 and lat2 are vectors of size N dist wil be a vector of
    size N of distances between each pair of points (lon1(i),lat1(i)) and 
    (lon2(i),lat2(i)), with 0 => i > N .
    '''
    deg2rad = np.pi / 180.
    ER = 6372.8 * 1000. # Earth Radius in meters

    dlon = np.multiply(deg2rad, (lon2 - lon1))
    dlat = np.multiply(deg2rad, (lat2 - lat1))

    lat1 = np.multiply(deg2rad, lat1)
    lat2 = np.multiply(deg2rad, lat2)

    # Computing the square of half the chord length between the points:
    a = np.power(np.sin(np.divide(dlat, 2.)),2) + \
        np.multiply(np.multiply(np.cos(lat1),np.cos(lat2)),np.power(np.sin(np.divide(dlon, 2.)),2))

    # Computing the angular distance in radians between the points
    angle = np.multiply(2., np.arctan2(np.sqrt(a), np.sqrt(1. -a)))

    # Computing the distance 
    dist = np.multiply(ER, angle)

    return dist


# ====================================================================================================
# Input parameters

INPfile = "/data/users/dbruciaf/NOAA_WOA13v2/1955-2012/025/temperature/woa13_decav_t13_04v2.nc"

# ====================================================================================================
# Loading fields
ds_woa = xr.open_dataset(INPfile, decode_times=False).squeeze()
ds_msh = ds_woa.drop_vars(list(ds_woa.data_vars))

# -----------------------------------------------------------
# Computing lon and lat
lonT = ds_woa.lon
latT = ds_woa.lat
lonU = lonT.rolling({'lon':2}).mean().fillna(ds_woa.lon_bnds[-1][-1])
lonV = ds_woa.lon
lonF = lonT.rolling({'lon':2}).mean().fillna(ds_woa.lon_bnds[-1][-1])
latU = ds_woa.lat
latV = latT.rolling({'lat':2}).mean().fillna(ds_woa.lat_bnds[-1][-1])
latF = latT.rolling({'lat':2}).mean().fillna(ds_woa.lat_bnds[-1][-1])

latT2, lonT2 = xr.broadcast(latT,lonT)
latU2, lonU2 = xr.broadcast(latU,lonU)
latV2, lonV2 = xr.broadcast(latV,lonV)
latF2, lonF2 = xr.broadcast(latF,lonF)

ds_msh['glamt'] = lonT2
ds_msh['gphit'] = latT2
ds_msh['glamu'] = lonU2
ds_msh['gphiu'] = latU2
ds_msh['glamv'] = lonV2
ds_msh['gphiv'] = latV2
ds_msh['glamf'] = lonF2
ds_msh['gphif'] = latF2

# -----------------------------------------------------------
# Computing e1t and e2t
lat_bnd = ds_woa.lat_bnds.values
lon_bnd = ds_woa.lon_bnds.values
lat = ds_woa.lat.values
lon = ds_woa.lon.values
e2t = np.zeros((len(lat),len(lon)))
e1t = np.zeros((len(lat),len(lon)))

for j in range(len(lat)):                                            
    for i in range(len(lon)):
        e1t[j,i] = hvrsn_dst(lon_bnd[i][0], lat[j]    , lon_bnd[i][1], lat[j]    )
        e2t[j,i] = hvrsn_dst(lon[i]    , lat_bnd[j][0], lon[i]    , lat_bnd[j][1])

ds_msh['e1t'] = (('lat','lon'), e1t)
ds_msh['e2t'] = (('lat','lon'), e2t) 
for grd in ['u','v','f']:
    ds_msh['e1'+grd] = ds_msh.e1t
    ds_msh['e2'+grd] = ds_msh.e2t

# -----------------------------------------------------------
# Computing e3t
depth_bnd = ds_woa.depth_bnds
e3t_1d = np.zeros((len(depth_bnd),))
depwh  = np.zeros((len(depth_bnd),))

for k in range(len(e3t_1d)): 
    e3t_1d[k] = depth_bnd[k][1] - depth_bnd[k][0]
    depwh[k]  = depth_bnd[k][0]

ds_msh['e3t_1d'] = (('depth'), e3t_1d)
ds_msh['gdept_1d'] = ds_msh.depth
ds_msh['gdepw_1d'] = (('depth'), depwh)

depth3, dummy = xr.broadcast(ds_msh.depth,ds_woa.t_an)
depwh3, dummy = xr.broadcast(ds_msh.gdepw_1d,ds_woa.t_an)
e3t, dummy    = xr.broadcast(ds_msh.e3t_1d,depth3)
del dummy

for grd in ['t','u','v','f']: ds_msh['e3'+grd+'_0'] = e3t
ds_msh['gdept_0'] = depth3
ds_msh['gdepw_0'] = depwh3

# -----------------------------------------------------------
# Computing tmask
tmask = xr.where(np.isnan(ds_woa.t_an), 0, 1)
ds_msh['tmask'] = tmask

# Need to shift and replace last row/colum with tmask
# umask(i, j, k) = tmask(i, j, k) ∗ tmask(i + 1, j, k)
umask = tmask.rolling(lon=2).prod().shift(lon=-1)
umask = umask.where(umask.notnull(), tmask)
ds_msh['umask'] = umask

# vmask(i, j, k) = tmask(i, j, k) ∗ tmask(i, j + 1, k)
vmask = tmask.rolling(lat=2).prod().shift(lat=-1)
vmask = vmask.where(vmask.notnull(), tmask)
ds_msh['vmask'] = vmask

# fmask(i, j, k) = tmask(i, j, k) ∗ tmask(i + 1, j, k) ∗ tmask(i, j, k) ∗ tmask(i + 1, j, k)
fmask = tmask.rolling(lon=2).prod().shift(lon=-1)
fmask = fmask.rolling(lat=2).prod().shift(lat=-1)
fmask = fmask.where(fmask.notnull(), tmask)
ds_msh['fmask'] = fmask

# -----------------------------------------------------------
# Taking care of dimensions
ds_msh = ds_msh.rename({'lon':'x','lat':'y','depth':'z'})
ds_msh = ds_msh.assign_coords(
                 x=range(len(ds_msh.x)),
                 y=range(len(ds_msh.y)),
                 z=range(len(ds_msh.z)),
         )

ds_msh = ds_msh.expand_dims(dim=['t'],axis=None)
ds_msh = ds_msh.drop_vars(['time'])

# -----------------------------------------------------------
# Writing to netCDF
enc = {}
for i in ds_msh.coords: enc[i] = {"_FillValue": None }
for i in ds_msh.data_vars: enc[i] = {"_FillValue": None }

out_file = 'mesh_mask_woa13v2.nc'
ds_msh.to_netcdf(out_file, encoding=enc, unlimited_dims={'t':True})
