#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 09:12:49 2022

https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2020/Brasil/BR/BR_Municipios_2020.zip

@author: leohoinaski
"""
import geopandas as gpd
import os
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
from HospDisaggregation_v2 import dataSUSvulGroups,Hosp2netCDF
import warnings
warnings.filterwarnings('ignore')


#%%

rootPath= os.path.abspath(os.getcwd())
outPath=rootPath+'/Outputs'

def disagUnusedCEP(fileId,outPath,year,prefix,
                   xX,yY,vulGroups):
    
    citySHP = gpd.read_file(rootPath+"/Inputs/shapefiles/BR_Municipios_2020.shp")
    citySHP = citySHP.to_crs("EPSG:4326")
    hospUnused = pd.read_csv(outPath+ '/report_hospUnused_'+fileId)
   
    path_pop = rootPath+'/Outputs/pop_regrid_'+str(year)+'_'+prefix+'.csv'
    pop = pd.read_csv(path_pop, sep=",")
    
    pop['geometry'] = gpd.GeoSeries.from_wkt(pop['geometry'] )
    pop = gpd.GeoDataFrame(pop,geometry=pop['geometry'])
    pop.crs = "EPSG:4326"
    pop = pop.to_crs("EPSG:4326")
    pop['center']=pop.geometry.centroid
    
    
    # fig, ax = plt.subplots(1, 1)
    # pop.plot(ax=ax,column='pop')
    # citySHP.plot(ax=ax)
    
    hospUnused['Total'] = 1
    hospUnused = dataSUSvulGroups(hospUnused)
    hospUnused['DT_INTER']=pd.to_datetime(hospUnused['DT_INTER'],format='%Y%m%d')
    hospUnused = hospUnused.sort_values(by="DT_INTER")
    hospUnused = hospUnused.reset_index(drop=True)
    hospUnused['lon']=np.nan
    hospUnused['lat']=np.nan
    for uns in range(0,hospUnused.shape[0]):
        print('Disagregating hospitalization in city: '+str(hospUnused.MUNIC_RES[uns]))
        popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
               hospUnused.MUNIC_RES[uns]]['geometry'])
        if popCity.shape[0]==0:
            print('Buffering city shape')
            popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
                    hospUnused.MUNIC_RES[uns]]['geometry'].buffer(0.01))
        if popCity.shape[0]==0:
            print('Buffering city shape')
            popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
                    hospUnused.MUNIC_RES[uns]]['geometry'].buffer(0.05))
        if popCity.shape[0]==0:
            print('Buffering city shape')
            popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
                    hospUnused.MUNIC_RES[uns]]['geometry'].buffer(0.1))
        
        if popCity.empty:
            hospUnused['lon'][uns]=np.nan
            hospUnused['lat'][uns]=np.nan
        else:
            hospUnused['lon'][uns] = pop['center'][np.argmax(pop['pop'][popCity.index])].x
            hospUnused['lat'][uns] = pop['center'][np.argmax(pop['pop'][popCity.index])].y
    
    hospNotFound = hospUnused[hospUnused['lon']==np.nan].copy()
    report = pd.DataFrame({'hospUnused':[hospUnused.shape[0]],
                           'hospNotFound': [hospNotFound.shape[0]]})
    report.to_csv(outPath+ '/report_'+fileId+'_hospNotFound', header=True)

    hospNotFound.to_csv(outPath+ '/report_hospNotFound_'+fileId, header=True)
    
    hospUsed = hospUnused[hospUnused['lon']!=np.nan].copy()

    Hosp2netCDF(hospUsed,xX,yY,fileId+'_disagUnusedCEP_',outPath,
                    prefix,vulGroups)