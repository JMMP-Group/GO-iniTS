# GO-iniTS

Code to generate T & S fields compliant with OMIP protocol to initialise GOSI configurations. 

According to OMIP-1 ([Griffies et al. 2016](https://gmd.copernicus.org/articles/9/3231/2016/gmd-9-3231-2016.pdf)) and OMIP-2 ([Tsujino et al. 2020](https://gmd.copernicus.org/articles/13/3643/2020/gmd-13-3643-2020.pdf)) protocols, OMIP simulations are initialised with temperature and salinity taken from [WOA13.v2](https://www.ncei.noaa.gov/data/oceans/woa/WOA13/DATAv2/): 

>Potential temperature and practical salinity are initialized in the upper 1500 m using January observational-based climatology from version 2 of Locarnini et al. (2013) for temperature and Zweng et al. (2013) for salinity. We refer to these data as WOA13v2. The January fields from WOA13v2 stop at 1500 m. We filled deeper depths with the mean from January/February/March (winter in the north and summer in the south). Initial conditions are provided at the OMIP website, with both 1 ◦ and 1/4 ◦ versions. Interpolation should be made to the respective model grid. Conversion to Conservative Temperature and Absolute Salinity should be made for models based on IOC et al. (2010).

The initial temperature and salinity fields are therefore each a composit of two different variants:

1) upper 1500m: January mean (averaged decades between 1955-2012)
2) below 1500m: seasonal mean (Jan-Feb-Mar; all decades)

The Geomar [CMIP6-OMIP/OMIP-input](https://git.geomar.de/cmip6-omip/omip-input) repository provides an example of the workflow and the code to generate an initial ocean state in agreement with OMIP protocol.

The documentation for [WOA13.v2](https://www.ncei.noaa.gov/data/oceans/woa/WOA13/DATAv2/) dataset can be found [here](https://www.ncei.noaa.gov/data/oceans/woa/WOA13/DOC/woa13documentation.pdf). WOA13v2 datset includes in-situ temperature and practical salinity. Therefore, in order to use this data to initialise our TEOS10 based configurations they need to be converted in Conservative Temperature and Absolute Salinity first.

## Quick-start

### 1. Clone the repository
```
git clone git@github.com:JMMP-Group/GO-iniTS.git
cd GO-iniTS
```
### 2. Create and activate conda environment
```
conda env create -f pyogcm.yml
conda activate pyogcm
```
## Generating WOA13v2-based initial condition following OMIP protocol

Before running the code, make sure to adapt the `Input parameters` section of each script to your needs.

### 1. Download WAO13v2 data
```
cd src
./download_woa13v2_data.sh
```

### 2. Generate T/S initial condition
```
python  generate_iniTS.py
```
N.B: on Met Office machines, this script is run using SLURM with the [submit_generate_iniTS.batch](https://github.com/JMMP-Group/GO-iniTS/blob/main/src/submit_generate_iniTS.batch) script file. 

### 3. Generate a mesh_mask.nc file for WOA13v2 data
```
python create_woa_mesh_mask.py
```
N.B: on Met Office machines, this script is run using SLURM with the [submit_create_woa_mesh_mask.batch](https://github.com/JMMP-Group/GO-iniTS/blob/main/src/submit_create_woa_mesh_mask.batch) script file.

## Interpolating WOA13v2-omip fields onto eORCA-025 grid wir $z$-coordinates


