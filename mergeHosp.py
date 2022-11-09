#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 12:23:24 2022

@author: leohoinaski
"""

import netCDF4 as nc
import numpy
import os
from netCDFcreator import createNETCDFtemporal
import datetime
import numpy as np
import pandas as pd

def mergeHosp(fileId,prefix,vulGroups,year):
    rootPath= os.path.abspath(os.getcwd())
    outPath = rootPath+'/Outputs/'+prefix
    file0='HOSP_'+str(year)+'_'+fileId+'_'+prefix+'_'+'annual.nc'
    file1= 'HOSP_'+str(year)+'_'+fileId+'_disagUnusedCEP__'+prefix+'_'+'annual.nc'
    file='HOSP_'+str(year)+'_'+fileId+'_'+prefix+'_'+'annual_Merged.nc' 
    ds0 = nc.Dataset(outPath+'/'+file0)
    ds1 = nc.Dataset(outPath+'/'+file1)
    variables = ds0.variables.keys()
    print(variables)
    variables=list(variables)
    #print(variables)
    variables.remove('LON')
    variables.remove('LAT')
    variables.remove('TFLAG')
    #print(variables)
    ds=numpy.full([ds1['TOTAL'][:].shape[0],len(variables),ds1['TOTAL'][:].shape[2],
                  ds1['TOTAL'][:].shape[3]],0, dtype=None)
    #print(ds.shape)
    for i,vv in enumerate(variables):
        ds[:,i,:,:] = ds0[vv][:]+ds1[vv][:]
               
    xX = ds0['LON'][:]
    yY = ds0['LAT'][:]
    startDate = datetime.datetime(year, 1, 1, 0, 0)
    endDate = datetime.datetime(year, 1, 1, 1, 0)
    datePfct = np.arange(np.datetime64(startDate),np.datetime64(endDate),3600000000)
    dates = pd.DataFrame(datePfct)   
    dates['year'] = year
    dates['month'] = 1
    dates['day'] = 1
    dates['hour'] = 00
    createNETCDFtemporal(outPath,file,ds,xX,yY,dates,'Annual')
    startDate = datetime.datetime(year, 1, 1, 0, 0)
    endDate = datetime.datetime(year+1, 1, 1, 0, 0)
    datePfct = np.arange(np.datetime64(startDate),np.datetime64(endDate),3600000000*24)
    datePfct = pd.DataFrame(datePfct)
    datePfct['year'] = pd.DatetimeIndex(datePfct.iloc[:,0]).year
    datePfct['month'] = pd.DatetimeIndex(datePfct.iloc[:,0]).month  
    datePfct['day'] = pd.DatetimeIndex(datePfct.iloc[:,0]).day
    #print(datePfct)
    for vulGroup in vulGroups:
        file0='HOSP_'+str(year)+'_'+fileId+'_'+prefix+'_'+vulGroup+'_daily'+'.nc'
        file1= 'HOSP_'+str(year)+'_'+fileId+'_disagUnusedCEP__'+prefix+'_'+vulGroup+'_daily'+'.nc'
        file= 'HOSP_'+str(year)+'_'+fileId+'_'+prefix+'_'+vulGroup+'_daily_Merged'+'.nc'
        ds0 = nc.Dataset(rootPath+'/Outputs/'+prefix+'/'+file0)
        ds1 = nc.Dataset(rootPath+'/Outputs/'+prefix+'/'+file1)
        ds = ds0['TOTAL'][:]+ds1['TOTAL'][:]
        #print('SHAPE---'+str(ds.shape))
        createNETCDFtemporal(outPath,file,ds,xX,yY,datePfct,'Daily')
        
        file0='Relative_HOSP_'+str(year)+'_'+fileId+'_'+prefix+'_'+vulGroup+'_daily'+'.nc'
        file1= 'Relative_HOSP_'+str(year)+'_'+fileId+'_disagUnusedCEP__'+prefix+'_'+vulGroup+'_daily'+'.nc'
        file= 'Relative_HOSP_'+str(year)+'_'+fileId+'_'+prefix+'_'+vulGroup+'_daily_Merged'+'.nc'
        ds0 = nc.Dataset(rootPath+'/Outputs/'+prefix+'/'+file0)
        ds1 = nc.Dataset(rootPath+'/Outputs/'+prefix+'/'+file1)
        ds = ds0['TOTAL'][:]+ds1['TOTAL'][:]
        createNETCDFtemporal(outPath,file,ds,xX,yY,datePfct,'Daily')
    
    return ds


