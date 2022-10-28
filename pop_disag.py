#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 11:54:37 2022

@author: leohoinaski
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import os

# vulGroups =  ['Total','less14','more60','adults',
#              'mens','womans','blacks','whites',
#              'brown','indigenous','asian','VAL_TOT','deaths']

#%%
def pop_disag_byclass(grid_pop,vulGroup):
    
    rootPath= os.path.abspath(os.getcwd())
    if vulGroup=='BLACKS':
        path = rootPath+'/Inputs/pop_disag/vw_per_pessoas_pretas.csv'
        popRace = pd.read_csv(path, sep=",")
    elif vulGroup=='WHITES':
        path = rootPath+'/Inputs/pop_disag/vw_per_pessoas_brancas.csv'
        popRace = pd.read_csv(path, sep=",")
    elif vulGroup=='BROWN':
        path = rootPath+'/Inputs/pop_disag/vw_per_pessoas_parda.csv' 
        popRace = pd.read_csv(path, sep=",")
    elif vulGroup=='INDIGENOUS':
        path = rootPath+'/Inputs/pop_disag/vw_per_pessoas_indigena.csv'
        popRace = pd.read_csv(path, sep=",")
    elif vulGroup=='ASIAN':
        path = rootPath+'/Inputs/pop_disag/vw_per_pessoas_amarela.csv' 
        popRace = pd.read_csv(path, sep=",")
    elif vulGroup=='LESS14':
        path = rootPath+'/Inputs/pop_disag/vw_per_pessde0a14anos.csv' 
        popRace = pd.read_csv(path, sep=",")
    elif vulGroup=='MORE60':
        path = rootPath+'/Inputs/pop_disag/vw_per_pess60anosoumais.csv' 
        popRace = pd.read_csv(path, sep=",")        
    elif vulGroup=='ADULTS':
        path1 = rootPath+'/Inputs/pop_disag/vw_per_pessde0a14anos.csv'
        path2 = rootPath+'/Inputs/pop_disag/vw_per_pess60anosoumais.csv' 
        popRace1 = pd.read_csv(path1, sep=",").reset_index().set_index('gid')
        popRace2 = pd.read_csv(path2, sep=",").reset_index().set_index('gid')
        popRace= popRace1.copy()
        popRace.iloc[:,7] = 100-(popRace1.iloc[:,7]+popRace2.iloc[:,7])
        popRace.rename(columns={'PER_PESSde0a14anos':'ADULTS'}, inplace=True)
        popRace=popRace.reset_index(drop=True)
    elif vulGroup=='MENS':
        path = rootPath+'/Inputs/pop_disag/vw_razao_de_sexo.csv' 
        popRace = pd.read_csv(path, sep=",")       
        popRace.iloc[:,7] = popRace.iloc[:,5]/(popRace.iloc[:,5]+popRace.iloc[:,6])
    elif vulGroup=='WOMANS':
        path = rootPath+'/Inputs/pop_disag/vw_razao_de_sexo.csv' 
        popRace = pd.read_csv(path, sep=",")       
        popRace.iloc[:,7] = popRace.iloc[:,6]/(popRace.iloc[:,5]+popRace.iloc[:,6])
    else:
        print('Total population')
        
    if vulGroup=='TOTAL':
        grid_pop=grid_pop
    elif vulGroup=='VAL_TOT':
        grid_pop=grid_pop
    elif vulGroup=='DEATHS':
        grid_pop=grid_pop
    else:   
        popRace['geometry'] = gpd.GeoSeries.from_wkt(popRace['geom'] )
        popRace = gpd.GeoDataFrame(
            popRace, geometry=popRace.geometry)
        popRace.crs = "EPSG:4326"
        #popRace.plot(column='PER_Pessoas_Pretas')
        
        #grid_pop[vulGroups]=np.nan
        grid_pop['prop'+vulGroup]=np.nan
        
        for city in range(0,popRace.shape[0]):
            print(str(city)+'/'+str(popRace.shape[0]))       
            popRaceCity = gpd.clip(grid_pop['center'].to_crs("EPSG:4326"), 
                                   popRace['geometry'][city].buffer(0.1))
            for ii in range(0,popRaceCity.shape[0]):
                grid_pop['prop'+vulGroup][popRaceCity.index[ii]]= np.nanmean([
                    grid_pop['prop'+vulGroup][popRaceCity.index[ii]],popRace.iloc[city,7]])
                
        grid_pop[vulGroup]=grid_pop['prop'+vulGroup]*grid_pop['pop']
        
        grid_pop = grid_pop.fillna(0)      
        #grid_pop.plot(column='pop')
        
    return  grid_pop

def pop_disag(vulGroups,prefix,year):
        
    rootPath= os.path.abspath(os.getcwd())
    grid_pop = pd.read_csv(rootPath+'/Outputs/'+prefix+
                           '/pop_regrid_'+str(year)+'_'+prefix+'.csv', sep=",")
    grid_pop['geometry'] = gpd.GeoSeries.from_wkt(grid_pop['geometry'] )
    grid_pop = gpd.GeoDataFrame(
        grid_pop, geometry=grid_pop.geometry)
    grid_pop.crs = "EPSG:4326"
    grid_pop['center']=grid_pop.geometry.centroid
    
    for vulGroup in vulGroups:
        print('Starting vulGroup = '+vulGroup)
        grid_pop = pop_disag_byclass(grid_pop,vulGroup)
    
    grid_pop.to_csv(rootPath+'/Outputs/'+prefix+'/pop_regrid_byVulgroup_'+str(year)+'_'+prefix+'.csv')
    return grid_pop
    
        
    