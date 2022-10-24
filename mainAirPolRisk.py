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

#fileId = 'BR_respiratory' # Code to identify your output files

disType = 'RESP'

runOrNotTemporal = 1 # Run or not daily temporal profile and daily netCDF

vulGroups =  ['Total','less14','more60','adults',
             'mens','womans','blacks','whites',
             'brown','indigenous','asian']

baseGridFile = 'baseGrid_'+prefix+'.csv'
years =range(2002,2019)
years = [2008]
useClosestCEP=True

#%%

    # Seting root folder
rootPath= os.path.abspath(os.getcwd())

# Seting output folder
outPath=rootPath+'/Outputs'
if os.path.isdir(outPath)==0:
    os.mkdir(outPath)

# Files with prefix equal to hospFile in Inputs folder
fileIds = [filename for filename in os.listdir(rootPath+'/Inputs/') if 
                     filename.startswith(hospFile)]

for fileId in fileIds:        
    years = HospDisaggregation(fileId, lati, latf, loni, lonf, 
                       deltaX, deltaY, prefix,runOrNotTemporal, vulGroups,useClosestCEP)

pop_regrid(years,baseGridFile)

pop_relativization(years,disType,prefix)
