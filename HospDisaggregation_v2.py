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
import os
from shapely.geometry import Polygon
from netCDFcreator import createNETCDFtemporal
from gridding import gridding,populatingGrid,populatingGridMatHOSP
import datetime
from ismember import ismember



#%% ----------------------------PROCESSING-------------------------------------

def HospDisaggregation(hospFile,listCEPfile,lati,latf,loni,lonf,
                       deltaX,deltaY,prefix,runOrNotTemporal,vulGroups):
    # Seting root folder
    rootPath= os.path.abspath(os.getcwd())
    
    # Seting output folder
    outPath=rootPath+'/Outputs'
    if os.path.isdir(outPath)==0:
        os.mkdir(outPath)
    
    # Reading CEP to latlon file
    listCEP = pd.read_csv(rootPath+'/Inputs/'+listCEPfile, delimiter="|",encoding='utf8')
    
    
    
    # Replacing strings and outrange -  by nan 
    listCEP['longitude']=listCEP['longitude'].replace('-', np.nan)
    listCEP['latitude']=listCEP['latitude'].replace('-', np.nan) 
    listCEP['longitude'] = listCEP['longitude'].replace('overquota', np.nan)
    listCEP['latitude'] = listCEP['latitude'].replace('overquota', np.nan)
    listCEP['longitude']=listCEP['longitude'].astype(np.float32)
    listCEP['latitude']=listCEP['latitude'].astype(np.float32)
    listCEP[listCEP['longitude']>lonf] = np.nan
    listCEP[listCEP['longitude']<loni] = np.nan
    listCEP[listCEP['latitude']>latf] = np.nan
    listCEP[listCEP['latitude']<lati] = np.nan
    listCEP = listCEP.dropna()
    
    
    # Files with prefix equal to hospFile in Inputs folder
    fileIds = [filename for filename in os.listdir(rootPath+'/Inputs/') if 
                         filename.startswith(hospFile)]
    years=[]
    # Loop over files
    for fileId in fileIds:
    
    	# Reading hospitalization data
        hosp = pd.read_csv(rootPath+'/Inputs/'+fileId,delimiter=';')
    	    
    	#----------------------Hospitalization CEP to latlon---------------------------
    
    	# Getting latlon of hospitalization data from DATASUS
        hosplat=[]
        hosplon=[]
        ii=0
        
        listCEPok = np.in1d(listCEP.cep, hosp.CEP)
        listCEPused = listCEP[listCEPok].copy()
        listCEPused = listCEPused.reset_index(drop=True)
        
        hospok = np.in1d(hosp.CEP,listCEPused.cep)
        hospUsed = hosp[hospok].copy()
        hospUsed = hospUsed.reset_index(drop=True)
        
        # Start fail reports
        report = pd.DataFrame()
        report['listCEP_original'] = listCEP.shape[0]
        report['listCEP_valid'] = listCEP.shape[0]
        report['Hosp_total'] = hosp.shape[0]
        report['Hosp_with_latlon'] = hospUsed.shape[0]
        report.to_csv(outPath+ '/report_'+fileId, header=True)
        
        lia, loct = ismember(np.array(hospUsed.CEP,dtype=float),
                            np.array(listCEPused.cep,dtype=float))
    
        hospUsed['lon'] = np.array(listCEPused.iloc[loct,2])
        hospUsed['lat'] = np.array(listCEPused.iloc[loct,1])
        
        
        
    #     for cc in hospUsed.CEP:   
    # 	    cepRight = listCEPused[listCEPused.cep==cc]
    # 	    if cepRight.empty:
    # 	        print(str(cc)+' not found')
    # 	        hosplat.append(np.nan)
    # 	        hosplon.append(np.nan)
    # 	    else:
    # 	        print("Yeaaahh "+str(cc))
    # 	        hosplat.append(np.array(float(cepRight.latitude.values)))
    # 	        hosplon.append(np.array(float(cepRight.longitude.values)))
    
    #     hosp['lon'] = hosplon
    #     hosp['lat'] = hosplat
    
    	# Setting conditions for vulnerability groups
        hospUsed['Total'] = 1
    
    	# less than five years old
        less14=[]
        for age in hospUsed.IDADE:
            if age>14:
                less14.append(0)
            else:
    	        less14.append(1)
    	        
    	# More than 60 years old
        more60=[]
        for age in hospUsed.IDADE:
            if age>60:
                more60.append(1)
            else:
                more60.append(0)
    
    	# Less than 60 and more than 14
        adults=[]
        for age in hospUsed.IDADE:
            if age<59 and age>15:
                adults.append(1)
            else:
                adults.append(0)
    	        
    	# Mens
        mens=[]
        for sexo in hospUsed.SEXO:
            if sexo==1:
                mens.append(1)
            else:
                mens.append(0)
    	        
    	# Womans
        wo=[]
        for sexo in hospUsed.SEXO:
            if sexo==3:
                wo.append(1)
            else:
    	        wo.append(0)
    	        
    	# Blacks
        bl=[]
        for raca in hospUsed.RACA_COR:
            if raca==2:
                bl.append(1)
            else:
    	        bl.append(0)
    	        
    	# Whites
        wh=[]
        for raca in hospUsed.RACA_COR:
            if raca==1:
                wh.append(1)
            else:
                wh.append(0)
    	        
    	# Brown
        bro=[]
        for raca in hospUsed.RACA_COR:
            if raca==3:
                bro.append(1)
            else:
                bro.append(0)
    
    	# Indigenous
        ind=[]
        for raca in hospUsed.RACA_COR:
            if raca==5:
                ind.append(1)
            else:
                ind.append(0)
    	        
    	# Asian
        asi=[]
        for raca in hospUsed.RACA_COR:
            if raca==4:
                asi.append(1)
            else:
                asi.append(0)
    	        
    	# Adding data to dataframe
        hospUsed['more60'] = more60
        hospUsed['less14'] = less14
        hospUsed['adults'] = adults
        hospUsed['mens'] = mens
        hospUsed['womans'] = wo
        hospUsed['blacks'] = bl
        hospUsed['whites'] = wh
        hospUsed['brown'] = bro
        hospUsed['indigenous'] = ind
        hospUsed['asian'] = asi
    
    
    	# Converting collumn to datetime
        hospUsed['DT_INTER']=pd.to_datetime(hospUsed['DT_INTER'],format='%Y%m%d')
        hospUsed = hospUsed.sort_values(by="DT_INTER")
    
    	# Converting to geodataframe   
        hospGPD = gpd.GeoDataFrame(
            hospUsed, geometry=gpd.points_from_xy(hospUsed.lon, hospUsed.lat))
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
        name = 'HOSP_annual_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hospUsed.ANO_CMPT[0])+'.nc'
    
    	# Calling createNETCDFtemporal - ANNUAL HOSPITALIZATION
        startDate = datetime.datetime(hospUsed.ANO_CMPT[0], 1, 1, 0, 0)
        endDate = datetime.datetime(hospUsed.ANO_CMPT[0], 1, 1, 1, 0)
        datePfct = np.arange(np.datetime64(startDate),np.datetime64(endDate),3600000000)
        dates = pd.DataFrame(datePfct)   
        dates['year'] = hospUsed.ANO_CMPT[0]
        dates['month'] = 1
        dates['day'] = 1
        dates['hour'] = 00
        
        years.append(hospUsed.ANO_CMPT[0])
    
    	# cd to the main folder
        os.chdir(rootPath)
    
    	# Creating output directory
        if os.path.isdir(outPath)==0:
            os.mkdir(outPath)
    	    
        createNETCDFtemporal(outPath,name,dataAnnual,xv,yv,y,x,dates,'Annual')
    
    	# Name of you output file
        if runOrNotTemporal==1:
            # print('Start parallell processing')
            # cpus = mp.cpu_count()-2
            # fileChunks = np.array_split(fileIds, cpus)
            # pool = mp.Pool(processes=cpus)  
            # chunk_processes = [pool.apply_async(hospDisag, 
            #                                     args=(chunk,rootPath,outPath,listCEPfile,lati,latf,loni,lonf,deltaX,deltaY,prefix,runOrNotTemporal,vulGroups)) for chunk in fileChunks]                    
            # #new section
            # pool.close()
            # pool.join()  
            # pool.terminate()
            # #end new section
            for vulGroup in vulGroups:
                name = 'HOSP_daily_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hospUsed.ANO_CMPT[0])+'_'+vulGroup+'.nc'
                dataTempo,datePfct= populatingGridMatHOSP(hospGPD,dataHosp[vulGroup],center,xX,yY,hospUsed.ANO_CMPT[0]) 
                createNETCDFtemporal(outPath,name,dataTempo,xv,yv,y,x,datePfct,'Daily')
        
       
    
    return years
    
    
    
