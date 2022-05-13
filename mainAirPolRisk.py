#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:06:19 2022

@author: leohoinaski
"""

from HospDisaggregation_v2 import HospDisaggregation
from pop_regrid import pop_regrid
from pop_rel import pop_relativization
import numpy as np
import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Polygon

#%%-----------------------------INPUTS-----------------------------------------

#popfile = 'bra_ppp_2019_1km_Aggregated.tif'

hospFile = 'INTER_BR_' # Hospitalization file

listCEPfile = 'qualocep_geo.csv'

#-------------------------Setting grid resolution------------------------------

# Users can change the domain and resolution here.
deltaX = 0.625 # Grid resolution/spacing in x direction

deltaY = 0.5 # Grid resolution/spacing in y direction

lati =-34.5 -(deltaY/2) #lati = int(round(bound.miny)) # Initial lati>

latf = 6  -(deltaY/2) #latf = int(round(bound.maxy)) # Final latitude>

loni = -74.375 -(deltaX/2) #loni = int(round(bound.minx)) # Initial l>

lonf = -33.75 -(deltaX/2)

prefix = str(deltaX)+'x'+str(deltaY) # grid definition identification

prefix = str(deltaX)+'x'+str(deltaY) # grid definition identification

#fileId = 'BR_respiratory' # Code to identify your output files

disType = 'RESP'

runOrNotTemporal = 0 # Run or not daily temporal profile and daily netCDF

vulGroups =  ['Total','less14','more60','adults',
             'mens','womans','blacks','whites',
             'brown','indigenous','asian']

baseGridFile = 'baseGrid_'+prefix+'.csv'
years =range(2002,2019)
years = [2020]

#%%

#years = HospDisaggregation(hospFile, listCEPfile, lati, latf, loni, lonf, 
#                   deltaX, deltaY, prefix,runOrNotTemporal, vulGroups)

# Seting root folder
rootPath= os.path.abspath(os.getcwd())

# Seting output folder
outPath=rootPath+'/Outputs'
if os.path.isdir(outPath)==0:
    os.mkdir(outPath)                   
# ------------------------- Creating grid ------------------------------------- 
print('Setting domain borders')
x = np.arange(loni, lonf+deltaX, deltaX)
y = np.arange(lati, latf+deltaY, deltaY)

#Loop over each cel in x direction
polygons=[]
for ii in range(1,x.shape[0]):
    #Loop over each cel in y direction
    for jj in range(1,y.shape[0]):
        #roadClip=[]
        lat_point_list = [y[jj-1], y[jj], y[jj], y[jj-1]]
        lon_point_list = [x[ii-1], x[ii-1], x[ii], x[ii]]
        cel = Polygon(zip(lon_point_list, lat_point_list))
        polygons.append(cel)

    
# Creating basegridfile
baseGrid = gpd.GeoDataFrame({'geometry':polygons})
baseGrid.to_csv(outPath+'/baseGrid_'+prefix+'.csv')
baseGrid.crs = "EPSG:4326" 
print('baseGrid_'+prefix+'.csv was created at ' + outPath )               

pop_regrid(years,baseGridFile)

#pop_relativization(years,disType,prefix)
