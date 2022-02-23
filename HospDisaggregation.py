# -*- coding: utf-8 -*-
"""
 -------------------------------------------------------------------------------
                              HospDisaggregation.py
                              
                              
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

 ---------------------------------------------------------------


"""
import numpy as np
import geopandas as gpd
import pandas as pd
# import fiona
# import rasterio
# import rasterio.mask
import os
from shapely.geometry import Polygon
from netCDFcreator import createNETCDFtemporal
from gridding import gridding,populatingGrid,populatingGridMatHOSP
import datetime
import multiprocessing as mp

#%%-----------------------------INPUTS-----------------------------------------

rootPath='/home/artaxo/airPollutionRisk/HospDisaggregation'

outPath='/home/artaxo/airPollutionRisk/HospDisaggregation/Outputs'

#popfile = 'bra_ppp_2019_1km_Aggregated.tif'

hospFile = 'INTER_BR_' # Hospitalization file

listCEPfile = 'qualocep_geo.csv'

#-------------------------Setting grid resolution------------------------------

# Users can change the domain and resolution here.
lati =-35 #lati = int(round(bound.miny)) # Initial latitude (lower-left)

latf = 15 #latf = int(round(bound.maxy)) # Final latitude (upper-right)

loni = -75 #loni = int(round(bound.minx)) # Initial longitude (lower-left)

lonf = -25 #lonf = int(round(bound.maxx)) # Final longitude (upper-right)

deltaX = 0.625 # Grid resolution/spacing in x direction

deltaY = 0.5 # Grig resolution/spacing in y direction

prefix = str(deltaX)+'x'+str(deltaY) # grid definition identification

fileId = 'BR_respiratory' # Code to identify your output files

runOrNotTemporal = 1 # Run or not daily temporal profile and daily netCDF

vulGroups =  ['Total','less14','more60','adults',
             'mens','womans','blacks','whites',
             'brown','indigenous','asian']



#%% ----------------------------PROCESSING-------------------------------------

fileIds = [filename for filename in os.listdir(rootPath+'/Inputs/') if 
                     filename.startswith(hospFile)]

for fileId in fileIds:

	# Reading hospitalization data
	hosp = pd.read_csv(rootPath+'/Inputs/'+fileId,delimiter=';')

	# Reading CEP to latlon file
	listCEP = pd.read_csv(rootPath+'/Inputs/'+listCEPfile, delimiter="|",encoding='utf8')

	# Replacing -  by nan 
	listCEP['longitude']=listCEP['longitude'].replace('-', np.nan)
	listCEP['latitude']=listCEP['latitude'].replace('-', np.nan)

	# with fiona.open(rootPath+'/Inputs/'+cityFile, "r") as shapefile:
	#     shapes = [feature["geometry"] for feature in shapefile]

	# with rasterio.open(rootPath+'/Inputs/'+popfile) as src:
	#     out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
	#     out_meta = src.meta

	    
	#----------------------Hospitalization CEP to latlon---------------------------

	# Getting latlon of hospitalization data from DATASUS
	hosplat=[]
	hosplon=[]
	ii=0
	for cc in hosp.CEP:   
	    cepRight = listCEP[listCEP.cep==cc]
	    if cepRight.empty:
	        print(str(cc)+' not found')
	        hosplat.append(np.nan)
	        hosplon.append(np.nan)
	    else:
	        print("Yeaaahh "+str(cc))
	        hosplat.append(np.array(float(cepRight.latitude.values)))
	        hosplon.append(np.array(float(cepRight.longitude.values)))

	hosp['lon'] = hosplon
	hosp['lat'] = hosplat

	# Setting conditions for vulnerability groups
	hosp['Total'] = 1

	# less than five years old
	less14=[]
	for age in hosp.IDADE:
	    if age>14:
	        less14.append(0)
	    else:
	        less14.append(1)
	        
	# More than 60 years old
	more60=[]
	for age in hosp.IDADE:
	    if age>60:
	        more60.append(1)
	    else:
	        more60.append(0)

	# Less than 60 and more than 14
	adults=[]
	for age in hosp.IDADE:
	    if age<59 and age>15:
	        adults.append(1)
	    else:
	        adults.append(0)
	        
	# Mens
	mens=[]
	for sexo in hosp.SEXO:
	    if sexo==1:
	        mens.append(1)
	    else:
	        mens.append(0)
	        
	# Womans
	wo=[]
	for sexo in hosp.SEXO:
	    if sexo==3:
	        wo.append(1)
	    else:
	        wo.append(0)
	        
	# Blacks
	bl=[]
	for raca in hosp.RACA_COR:
	    if raca==2:
	        bl.append(1)
	    else:
	        bl.append(0)
	        
	# Whites
	wh=[]
	for raca in hosp.RACA_COR:
	    if raca==1:
	        wh.append(1)
	    else:
	        wh.append(0)
	        
	# Brown
	bro=[]
	for raca in hosp.RACA_COR:
	    if raca==3:
	        bro.append(1)
	    else:
	        bro.append(0)

	# Indigenous
	ind=[]
	for raca in hosp.RACA_COR:
	    if raca==5:
	        ind.append(1)
	    else:
	        ind.append(0)
	        
	# Asian
	asi=[]
	for raca in hosp.RACA_COR:
	    if raca==4:
	        asi.append(1)
	    else:
	        asi.append(0)
	        
	# Adding data to dataframe
	hosp['more60'] = more60
	hosp['less14'] = less14
	hosp['adults'] = adults
	hosp['mens'] = mens
	hosp['womans'] = wo
	hosp['blacks'] = bl
	hosp['whites'] = wh
	hosp['brown'] = bro
	hosp['indigenous'] = ind
	hosp['asian'] = asi


	# Converting collumn to datetime
	hosp['DT_INTER']=pd.to_datetime(hosp['DT_INTER'],format='%Y%m%d')
	hosp = hosp.sort_values(by="DT_INTER")

	# Converting to geodataframe   
	hospGPD = gpd.GeoDataFrame(
	     hosp, geometry=gpd.points_from_xy(hosp.lon, hosp.lat))
	hospGPD.crs = "EPSG:4326"

	hospGPD = hospGPD[pd.DatetimeIndex(hospGPD["DT_INTER"]).year==hospGPD["ANO_CMPT"][0]]

	# Removing bad geometries
	hospGPD.dropna(subset=['lat'], how='any',inplace=True)
	hospGPD=hospGPD[hospGPD['geometry'].is_valid].reset_index(drop=True)

	dataHosp = hospGPD[['Total','less14','more60','adults',
	                    'mens','womans','blacks','whites',
	                    'brown','indigenous','asian']].copy() 

	# Collecting hospitalization centroids 
	center = hospGPD.geometry.centroid
	center.to_crs("EPSG:4326")
	center = center.reset_index(drop=True)

	# ------------------------- Creating grid ------------------------------------- 
	print('Setting domain borders')
	x = np.linspace(loni, lonf, int((lonf-loni)/deltaX))
	y = np.linspace(lati, latf, int((latf-lati)/deltaY))

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

	# Calling gridding function 
	grids,xv,yv,xX,yY = gridding(x,y)

	#-------------------- Calling populatingGrid function -------------------------

	# Populating grid and consolidating for one year
	dataAnnual = populatingGrid(dataHosp,center,xX,yY,xv,yv)

	#---------------------------Creating netCDF file-------------------------------

	# Name of you output file
	name = 'HOSP_annual_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'

	# Calling createNETCDFtemporal - ANNUAL HOSPITALIZATION
	startDate = datetime.datetime(hosp.ANO_CMPT[0], 1, 1, 0, 0)
	endDate = datetime.datetime(hosp.ANO_CMPT[0], 1, 1, 1, 0)
	datePfct = np.arange(np.datetime64(startDate),np.datetime64(endDate),3600000000)
	dates = pd.DataFrame(datePfct)   
	dates['year'] = hosp.ANO_CMPT[0]
	dates['month'] = 1
	dates['day'] = 1
	dates['hour'] = 00

	# cd to the main folder
	os.chdir(rootPath)

	# Creating output directory
	if os.path.isdir(outPath)==0:
	    os.mkdir(outPath)
	    
	createNETCDFtemporal(outPath,name,dataAnnual,xv,yv,y,x,dates,'Annual')

	# Name of you output file
	if runOrNotTemporal==1:
		for vulGroup in vulGroups:
		    name = 'HOSP_daily_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'_'+vulGroup+'.nc'
		    dataTempo,datePfct= populatingGridMatHOSP(hospGPD,dataHosp[vulGroup],center,xX,yY,hosp.ANO_CMPT[0])
		    createNETCDFtemporal(outPath,name,dataTempo,xv,yv,y,x,datePfct,'Daily')
