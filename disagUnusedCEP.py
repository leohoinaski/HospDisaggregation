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
from random import shuffle

#%%

def CEP2cityCoord(hospUnused,citySHP,pop):
    cepNoCoord = hospUnused.groupby(['MUNIC_RES']).size()
    for uns in range(0,cepNoCoord.shape[0]):
        print('Pop pixels in city: '+str(cepNoCoord.index[uns]))
        print(str(uns)+'/'+str(cepNoCoord.size))       
        popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
               cepNoCoord.index[uns]]['geometry'])
        if popCity.shape[0]==0:
            print('Buffering city shape - 0.01°')
            popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
                    cepNoCoord.index[uns]]['geometry'].buffer(0.01).to_crs("EPSG:4326"))
        if popCity.shape[0]==0:
            print('Buffering city shape - 0.05°')
            popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
                    cepNoCoord.index[uns]]['geometry'].buffer(0.05))
        if popCity.shape[0]==0:
            print('Buffering city shape - 0.2°')
            popCity = gpd.clip(pop['center'].to_crs("EPSG:4326"), citySHP[np.floor(citySHP.CD_MUN.astype(float)/10).astype(int)==
                   cepNoCoord.index[uns]]['geometry'].buffer(0.2))
            
        if popCity.empty or popCity.shape[0]==0:
            
            hospUnused['lon'][hospUnused['MUNIC_RES']==cepNoCoord.index[uns]]=np.nan
            hospUnused['lat'][hospUnused['MUNIC_RES']==cepNoCoord.index[uns]]=np.nan
            
        else:
            probPop = pop['pop'][popCity.index]/pop['pop'][popCity.index].sum()
            cityNoCEP = hospUnused[hospUnused['MUNIC_RES']==cepNoCoord.index[uns]]

            x = [[i] for i in cityNoCEP.index]
            shuffle(x)
            nPop = (probPop*cityNoCEP.shape[0]).astype(int)
            nPop[nPop==nPop.max()] = nPop.max() + cityNoCEP.shape[0]-nPop.sum()
            xgroups = np.split(x, np.cumsum(nPop))
            
            for jj in range(0,nPop.shape[0]):
                
                hospUnused['lon'][xgroups[jj].flatten()] = pop['center'][nPop.index[jj]].x
                hospUnused['lat'][xgroups[jj].flatten()] = pop['center'][nPop.index[jj]].y
        
    return hospUnused
#%%

def disagUnusedCEP(fileId,year,prefix,xX,yY,vulGroups):
    
    rootPath= os.path.abspath(os.getcwd())
    outPath=rootPath+'/Outputs/'+prefix
    
    citySHP = gpd.read_file(rootPath+"/Inputs/shapefiles/BR_Municipios_2020.shp")
    citySHP = citySHP.to_crs("EPSG:4326")
    
    hospUnused = pd.read_csv(outPath+ '/report_hospUnused_'+fileId)
   
    path_pop = rootPath+'/Outputs/'+prefix+'/pop_regrid_'+str(year)+'_'+prefix+'.csv'
    pop = pd.read_csv(path_pop, sep=",")
    pop['geometry'] = gpd.GeoSeries.from_wkt(pop['geometry'] )
    pop = gpd.GeoDataFrame(pop,geometry=pop['geometry'])
    pop.crs = "EPSG:4326"
    pop = pop.to_crs("EPSG:4326")
    pop['center']=pop.geometry.centroid
    
    # fig, ax = plt.subplots(1, 1)
    # pop.plot(ax=ax,column='pop')
    # citySHP.plot(ax=ax)
    
    hospUnused['TOTAL'] = 1
    hospUnused = dataSUSvulGroups(hospUnused)
    hospUnused['DT_INTER']=pd.to_datetime(hospUnused['DT_INTER'],format='%Y%m%d')
    hospUnused = hospUnused.sort_values(by="DT_INTER")
    hospUnused = hospUnused.reset_index(drop=True)
    hospUnused['lon']=np.nan
    hospUnused['lat']=np.nan
    
    hospUnused = CEP2cityCoord(hospUnused,citySHP,pop)
    
    hospNotFound = hospUnused[hospUnused['lon']==np.nan].copy()
    report = pd.DataFrame({'hospUnused':[hospUnused.shape[0]],
                           'hospNotFound': [hospNotFound.shape[0]]})
    report.to_csv(outPath+ '/report_'+fileId+'_hospNotFound', header=True)

    hospNotFound.to_csv(outPath+ '/report_hospNotFound_'+fileId, header=True)
    
    hospUsed = hospUnused[hospUnused['lon']!=np.nan].copy()

    Hosp2netCDF(hospUsed,xX,yY,fileId+'_disagUnusedCEP_',outPath,
                    prefix,vulGroups)