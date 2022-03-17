# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 14:00:01 2022


Resíduo - Internações e população 

@author: moore
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import netCDF4 as nc
import numpy.matlib
from netCDFcreator import createNETCDFtemporal
import datetime


#dados de internações
def pop_relativization(years,disType,prefix):
    
    rootPath= os.path.abspath(os.getcwd())
     
    for year in years:
        path_total = rootPath+ '/Outputs/HOSP_daily_INTER_BR_'+str(year)+'_'+disType+'.csv_'+prefix+'_'+str(year)+'_Total.nc'
        hosp_total = nc.Dataset(path_total)
        
        path_pop = rootPath+'/Outputs/pop_regrid_'+str(year)+'_'+prefix+'.csv'
        pop = pd.read_csv(path_pop, sep=",")
        pop['pop'][pop['pop']==0] = np.nan
        hosp_t = nc.Dataset(path_total)
        hosp_total = hosp_t['TOTAL'][:]
        
        hosp_mat=[]
        for ii in range(0, hosp_total.shape[0]):
            hosp_mat.append(hosp_total[ii,0,:,:].transpose().flatten())
        #hosp_mat = np.array(hosp_mat)    
        hosp_total_reshape = np.array(hosp_mat) 
        #hosp_total_reshape = hosp_total.reshape((hosp_total.shape[0],hosp_total.shape[2]*hosp_total.shape[3]))
        
        hosp_total_rel = hosp_total_reshape/np.matlib.repmat(
            pop['pop'], hosp_total_reshape.shape[0],1)*10000
        
    
        hosp_mat = np.zeros((hosp_total.shape[0],hosp_total.shape[1],hosp_total.shape[3],hosp_total.shape[2]))
        for ii in range(0, hosp_total_rel.shape[0]):
            hosp_mat[ii,0,:,:] = hosp_total_rel[ii,:].reshape(
                (hosp_total.shape[3],hosp_total.shape[2]))
        
        
        hosp_mat = np.transpose(hosp_mat, (0, 1, 3, 2))
        
       
    
        startDate = datetime.datetime(year, 1, 1, 0, 0)
        endDate = datetime.datetime(year+1, 1, 1, 0, 0)
        datePfct = np.arange(np.datetime64(startDate),np.datetime64(endDate),3600000000*24)
        datePfct = pd.DataFrame(datePfct)
        datePfct['year'] = pd.DatetimeIndex(datePfct.iloc[:,0]).year
        datePfct['month'] = pd.DatetimeIndex(datePfct.iloc[:,0]).month  
        datePfct['day'] = pd.DatetimeIndex(datePfct.iloc[:,0]).day
        
        polCoords=[]
        pop['geometry']= gpd.GeoSeries.from_wkt(pop['geometry'])
        for ii in range(0, pop.shape[0]):        
            polCoords.append(pop['geometry'][ii].exterior.coords.xy)
        
        polCoords = np.array(polCoords)
        y = np.unique(polCoords[:,1,:])
        x = np.unique(polCoords[:,0,:])
        xv, yv = np.meshgrid(x, y)
        

        createNETCDFtemporal(rootPath+ '/Outputs','Relative_'+path_total.split('/')[-1],hosp_mat,xv,yv,y,x,datePfct,'Daily')


    

