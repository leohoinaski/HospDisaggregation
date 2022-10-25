# -*- coding: utf-8 -*-
"""
----------------------------------pop_grid.py----------------------------------

This function regrids the population data from XXX to an specific grid size, 
according to baseGrid file created in HospDisaggregation function. 

Inputs: 
    basefile =  name of baseGrid file
    years = years considered in the disaggregation
    
Outputs:
    


Created on Mon Mar 14 11:33:07 2022

@author: Julia Moore and Leonardo Hoinaski
-------------------------------------------------------------------------------
"""
# Importing libraries
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import xarray as xr

#----------------------------Start Processing----------------------------------

#%% regrid function
def regridding(year,basefile,polCoords,rootPath,grid_int):
    #abrindo o arquivo tiff
    pop_path =  rootPath+'/Inputs/pop/bra_ppp_'+str(year)+'_1km_Aggregated_UNadj.tif'
    pop = xr.open_rasterio(pop_path)
    
    # lat inicial e final da grade de dados de população
    lat_pop = pop['y'].values
    lon_pop = pop['x'].values
    
    xvPop, yvPop = np.meshgrid(lon_pop, lat_pop)
    xvPop = xvPop.flatten()
    yvPop = yvPop.flatten()
    popFlat = np.array(pop[:,:,:]).flatten()
    popFlat[popFlat == -99999]=0
    
    
    grid_pop=[]
    
    for ii in range(0,polCoords.shape[0]):    
        mask = ((xvPop<polCoords[ii,0,:].max()) & (xvPop>polCoords[ii,0,:].min()) &
                (yvPop<polCoords[ii,1,:].max()) & (yvPop>polCoords[ii,1,:].min()))
        popFlatSum = np.nansum(popFlat[mask],axis=0)
        print('Cell number = '+str(ii) +' popsum = ' + str(popFlatSum) )
        grid_pop.append(popFlatSum)
    
    grid_int['pop'] = grid_pop
    grid_int.to_csv(rootPath+'/Outputs/pop_regrid_'+str(year)+'_'+basefile.split('_')[1])
    return grid_pop

#%% Calling the function 

def pop_regrid(year,basefile):
    #Set root folder
    rootPath= os.path.abspath(os.getcwd())
    
    # Opening baseGrid file
    path_grid = rootPath+'/Outputs/'+basefile
    grid_int = pd.read_csv(path_grid, sep=",")
    grid_int['geometry'] = gpd.GeoSeries.from_wkt(grid_int['geometry'] )
    grid_int = gpd.GeoDataFrame({'geometry':grid_int['geometry']})
    grid_int.crs = "EPSG:4326"
    
    polCoords =[]
    # Get centroid from baseGrid
    for excoord in grid_int.geometry:
        polCoords.append(excoord.exterior.coords.xy)
        
    polCoords = np.array(polCoords)
    
    regridding(year,basefile,polCoords,rootPath,grid_int)
    
