# -*- coding: utf-8 -*-
"""
 -------------------------------------------------------------------------------
                              HospDisaggregation.py                             
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import os
from netCDFcreator import createNETCDFtemporal
from gridding import gridding,populatingGrid,populatingGridMatHOSP,domainAndGrid
import datetime
from ismember import ismember


#%% ----------------------------PROCESSING-------------------------------------
def dataSUSvulGroups(hospUsed):
    less14=[]
    more60=[]
    adults=[]
    mens=[]
    wo=[]
    bl=[]
    wh=[]
    bro=[]
    ind=[]
    asi=[]
    for ii in range(0,hospUsed.shape[0]):
        age = hospUsed.IDADE[ii]
        sexo = hospUsed.SEXO[ii]
        raca = hospUsed.RACA_COR[ii]
        #print(ii)
        if age>14:
            less14.append(0)
        else:
            less14.append(1)
            
        if age>60:
            more60.append(1)
        else:
            more60.append(0)
        
        if age<59 and age>15:
            adults.append(1)
        else:
            adults.append(0)

        if sexo==1:
            mens.append(1)
        else:
            mens.append(0)

        if sexo==3:
            wo.append(1)
        else:
            wo.append(0)
            
        if raca==2:
            bl.append(1)
        else:
            bl.append(0)

        if raca==1:
            wh.append(1)
        else:
            wh.append(0)

        if raca==3:
            bro.append(1)
        else:
            bro.append(0)

        if raca==5:
            ind.append(1)
        else:
            ind.append(0)

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
    return hospUsed

def HospDisaggregation(fileId,lati,latf,loni,lonf,
                       deltaX,deltaY,prefix,runOrNotTemporal,vulGroups):
    
    # Seting root folder
    rootPath= os.path.abspath(os.getcwd())
    
    # Seting output folder
    outPath=rootPath+'/Outputs'
    
    listCEPfile = 'qualocep_geo.csv'
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
     
    # Reading hospitalization data
    hosp = pd.read_csv(rootPath+'/Inputs/'+fileId,delimiter=';')
    	    
   	#----------------------Hospitalization CEP to latlon---------------------------
   
   	# Getting latlon of hospitalization data from DATASUS
    listCEPok = np.in1d(listCEP.cep, hosp.CEP)
    listCEPused = listCEP[listCEPok].copy()
    listCEPused = listCEPused.reset_index(drop=True)
    
    hospok = np.in1d(hosp.CEP,listCEPused.cep)
    hospUsed = hosp[hospok].copy()
    hospUsed = hospUsed.reset_index(drop=True)
    hospUnused = hosp[hospok==False].copy()
    
    # Start fail reports
    #report = pd.DataFrame()
    report = pd.DataFrame({'listCEP_original':[listCEP.shape[0]],
                           'listCEP_valid': [listCEP.shape[0]],
                           'Hosp_total':[hosp.shape[0]],
                           'Hosp_with_latlon': [hospUsed.shape[0]]})

    hospUnused.to_csv(outPath+ '/report_hospUnused'+fileId, header=True)
    report.to_csv(outPath+ '/report_'+fileId, header=True)
    
    lia, loct = ismember(np.array(hospUsed.CEP,dtype=float),
                    np.array(listCEPused.cep,dtype=float))
    
    hospUsed['lon'] = np.array(listCEPused.iloc[loct,2])
    hospUsed['lat'] = np.array(listCEPused.iloc[loct,1])
    
    # Setting conditions for vulnerability groups
    hospUsed['Total'] = 1
    
    #Grouping by vulnerability
    hospUsed = dataSUSvulGroups(hospUsed)
    
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
    
    # Calling  domainAndGrid
    polygons,x,y=domainAndGrid(lati,loni,latf,lonf, deltaX,deltaY)
    
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
    
    year = hospUsed.ANO_CMPT[0]
    
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
        
       
     
    return year
     
 
 
