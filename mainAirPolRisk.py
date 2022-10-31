#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:06:19 2022

 This is the repository script to disaggregate daily hospitalization from DATASUS 
 and create netCDF files with aggregated hospitalization in regular areas. 
 
 Data sources:
     https://www.worldpop.org/project/categories?id=3
     https://www.qualocep.com/
     https://dados.gov.br/organization/instituto-brasileiro-de-geografia-e-estatistica-ibge?q=ra%C3%A7a&sort=score+desc%2C+metadata_modified+desc
     https://forest-gis.com/shapefile-bairros-das-cidades-brasileiras/
 

 Inputs:      
     fileIds = identification of your input files     
     gridType = grid type used in the database / 0 for user-defined / MCIP grid
     lati: Initial latitude (lower-left)
     latf: Final latitude (upper-right)
     loni: Initial longitude (lower-left)
     lonf: Final longitude (upper-right)
     deltaX: Grid resolution/spacing in x direction
     deltaY: Grig resolution/spacing in y direction
     runOrNotTemporal = Run or not daily temporal profile and daily netCDF
     vulGroup = Grouping tag. 
                 'TOTAL' = Total number of hospitalizations
                 'LESS14' = Total number of hospitalizations for younger than 14
                 'MORE60' = Total number of hospitalizations for older than 60
                 'ADULTS' = Total number of hospitalizations for adults (15-59)
                 'MENS' = Total number of hospitalizations for mens
                 'WOMANS' = Total number of hospitalizations for womans
                 'BLACKS' = Total number of hospitalizations for blacks 
                 'WHITES' = Total number of hospitalizations for whites
                 'BRONW' = Total number of hospitalizations for browns
                 'INDIGENOUS' = Total number of hospitalizations for indigenous
                 'ASIAN' = Total number of hospitalizations for asians
                 'VAL_TOT' = Total monetary value of hospitalization
                 'DEATHS' = Total number of deaths
          
 Outputs:
     
     Annual basis netCDF
     'HOSP_annual_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
     
     Daily basis netCDF
     'HOSP_daily_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
    
         
 Last update = 31/10/2022

 Author: Leonardo Hoinaski - leonardo.hoinaski@ufsc.br

-------------------------------------------------------------------------------
"""

from HospDisaggregation_v2 import HospDisaggregation
from pop_regrid import pop_regrid
from pop_rel import pop_relativization
import os
from gridding import domainAndGrid, gridding, domainAndGridMCIP
import geopandas as gpd
from disagUnusedCEP import disagUnusedCEP
from pop_disag import pop_disag
from mergeHosp import mergeHosp


#%%------------------------Hospitalization Data--------------------------------
fileIds = ['INTER_BR_2008_RESP.csv']
# Files with prefix equal to hospFile in Inputs folder
# fileIds = [filename for filename in os.listdir(rootPath+'/Inputs/') if 
#                      filename.startswith(hospFile)]

#-------------------------Setting grid resolution------------------------------
gridType=1 # 0 for user-defined grid

# Users can change the domain and resolution here.
lati =-38 #lati = int(round(bound.miny)) # Initial latitude (lower-left)

latf = 8 #latf = int(round(bound.maxy)) # Final latitude (upper-right)

loni = -76.875 #loni = int(round(bound.minx)) # Initial longitude (lower-left)

lonf = -30 #lonf = int(round(bound.maxx)) # Final longitude (upper-right)

deltaX = 0.625 # Grid resolution/spacing in x direction

deltaY = 0.5 # Grig resolution/spacing in y direction

mcipGRIDDOT2DPath='GRIDDOT2D_BR_2019.nc' # path to GRIDDOT2D file if gridType other than 1

#prefix = str(deltaX)+'x'+str(deltaY) # grid definition identification
prefix = '20x20km' # grid definition identification
#------------------------------Outputfile--------------------------------------
runOrNotTemporal = 1 # Run or not daily temporal profile and daily netCDF


#----------------------------Grouping options----------------------------------
vulGroups =  ['TOTAL','LESS14','MORE60','ADULTS',
             'MENS','WOMANS','BLACKS','WHITES',
             'BROWN','INDIGENOUS','ASIAN','VAL_TOT','DEATHS']


#%% ---------------------------PROCESSING--------------------------------------



baseGridFile = 'baseGrid_'+prefix+'.csv'

# Seting root folder
rootPath= os.path.abspath(os.getcwd())

# Seting output folder
outPath=rootPath+'/Outputs'
if os.path.isdir(outPath)==0:
    os.mkdir(outPath)
outPath=rootPath+'/Outputs/'+prefix
if os.path.isdir(outPath)==0:
    os.mkdir(outPath)


if gridType==1:
    polygons,x,y=domainAndGridMCIP(rootPath+'/Inputs/grid/'+mcipGRIDDOT2DPath)
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
    mergeHosp(fileId,prefix,vulGroups,year)
