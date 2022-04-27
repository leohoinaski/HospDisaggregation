#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:06:19 2022

@author: leohoinaski
"""

from HospDisaggregation_v2 import HospDisaggregation
from pop_regrid import pop_regrid
from pop_rel import pop_relativization

#%%-----------------------------INPUTS-----------------------------------------

#popfile = 'bra_ppp_2019_1km_Aggregated.tif'

hospFile = 'INTER_BR_' # Hospitalization file

listCEPfile = 'qualocep_geo.csv'

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

#%%

years = HospDisaggregation(hospFile, listCEPfile, lati, latf, loni, lonf, 
                   deltaX, deltaY, prefix,runOrNotTemporal, vulGroups)

pop_regrid(years,baseGridFile)

pop_relativization(years,disType,prefix)
