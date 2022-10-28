#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:06:19 2022

 This is the main script to disaggregate daily hospitalization from DATASUS and
 create netCDF files with aggregated hospitalization in regular areas. 
 
 https://www.worldpop.org/project/categories?id=3
 
 https://www.qualocep.com/
 
 

 Inputs: 
     
     rootPath: Path to functions
     
     outPath: Path to outputs folder
     
     lati: Initial latitude (lower-left)
     
     latf: Final latitude (upper-right)
     
     loni: Initial longitude (lower-left)
     
     lonf: Final longitude (upper-right)
     
     deltaX: Grid resolution/spacing in x direction
     
     deltaY: Grig resolution/spacing in y direction
                  
     fileId = identification of your output files
     
     runOrNotTemporal = Run or not daily temporal profile and daily netCDF
     
     vulGroup = vunerability group tag. 
                 'Total' = Total number of hospitalizations
                 'less14' = Total number of hospitalizations for younger than 14
                 'more60' = Total number of hospitalizations for older than 60
                 'adults' = Total number of hospitalizations for adults (15-59)
                 'mens' = Total number of hospitalizations for mens
                 'womans' = Total number of hospitalizations for womans
                 'blacks' = Total number of hospitalizations for blacks 
                 'whites' = Total number of hospitalizations for whites
                 'brown' = Total number of hospitalizations for browns
                 'indigenous' = Total number of hospitalizations for indigenous
                 'asian' = Total number of hospitalizations for asians
          
 Outputs:
     
     Annual basis netCDF
     'HOSP_annual_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
     
     Daily basis netCDF
     'HOSP_daily_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
    
     
 External functions:
     gridding, netCDFcreator
     
 Last update = 29/10/2021

 Author: Leonardo Hoinaski - leonardo.hoinaski@ufsc.br

@author: leohoinaski
"""

from HospDisaggregation_v2 import HospDisaggregation
from pop_regrid import pop_regrid
from pop_rel import pop_relativization
import os
from gridding import domainAndGrid, gridding, domainAndGridMCIP
import geopandas as gpd
from disagUnusedCEP import disagUnusedCEP
from pop_disag import pop_disag

#%%-----------------------------INPUTS-----------------------------------------

#popfile = 'bra_ppp_2019_1km_Aggregated.tif'

hospFile = 'INTER_BR_' # Hospitalization file



#-------------------------Setting grid resolution------------------------------

# Users can change the domain and resolution here.
lati =-38 #lati = int(round(bound.miny)) # Initial latitude (lower-left)

latf = 8 #latf = int(round(bound.maxy)) # Final latitude (upper-right)

loni = -76.875 #loni = int(round(bound.minx)) # Initial longitude (lower-left)

lonf = -30 #lonf = int(round(bound.maxx)) # Final longitude (upper-right)

deltaX = 0.625 # Grid resolution/spacing in x direction

deltaY = 0.5 # Grig resolution/spacing in y direction

prefix = str(deltaX)+'x'+str(deltaY) # grid definition identification

fileIds = ['INTER_BR_2011_RESP.csv'] # Code to identify your output files

runOrNotTemporal = 1 # Run or not daily temporal profile and daily netCDF

vulGroups =  ['TOTAL','LESS14','MORE60','ADULTS',
             'MENS','WOMANS','BLACKS','WHITES',
             'BROWN','INDIGENOUS','ASIAN','VAL_TOT','DEATHS']

baseGridFile = 'baseGrid_'+prefix+'.csv'
mcipGRIDDOT2DPath=[]
gridType=0 # 0 for user-defined grid

#%%

    # Seting root folder
rootPath= os.path.abspath(os.getcwd())

# Seting output folder
outPath=rootPath+'/Outputs'
if os.path.isdir(outPath)==0:
    os.mkdir(outPath)
outPath=rootPath+'/Outputs/'+prefix
if os.path.isdir(outPath)==0:
    os.mkdir(outPath)

# Files with prefix equal to hospFile in Inputs folder
# fileIds = [filename for filename in os.listdir(rootPath+'/Inputs/') if 
#                      filename.startswith(hospFile)]

if gridType==1:
    domainAndGridMCIP(mcipGRIDDOT2DPath)
else:
    # Calling  domainAndGrid
    polygons,x,y=domainAndGrid(lati,loni,latf,lonf, deltaX,deltaY)

# Creating basegridfile
baseGrid = gpd.GeoDataFrame({'geometry':polygons})
baseGrid.to_csv(outPath+'/baseGrid_'+prefix+'.csv')
baseGrid.crs = "EPSG:4326" 
print('baseGrid_'+prefix+'.csv was created at ' + outPath )

# Calling gridding function 
grids,xv,yv,xX,yY = gridding(x,y)

for fileId in fileIds:        
    year = HospDisaggregation(fileId,xX,yY,prefix,runOrNotTemporal,vulGroups)
    
    if os.path.isfile(rootPath+'/Outputs/'+prefix+'/pop_regrid_'+str(year)+'_'+baseGridFile.split('_')[1]):
        print("File exists")
    else:
        grid_pop = pop_regrid(prefix,year,baseGridFile)
        
    if os.path.isfile(rootPath+'/Outputs/'+prefix+'/pop_regrid_byVulgroup_'+str(year)+'_'+prefix+'.csv'):
        print("File exists")
    else:   
        pop_disag(vulGroups,prefix,year)

    disagUnusedCEP(fileId,year,prefix,xX,yY,vulGroups)
    pop_relativization(year,fileId,prefix,xX,yY)

