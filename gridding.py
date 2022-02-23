#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 16:50:56 2021

@author: leohoinaski
"""
#import netCDF4 as nc4
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import MultiLineString
from shapely.ops import polygonize
import datetime
import numpy.matlib

#%% Gridding and populatingGrid functions

def gridding(lon,lat):
    xv, yv = np.meshgrid(lon, lat)
    hlines = [((x1, yi), (x2, yi)) for x1, x2 in zip(lon[:-1], lon[1:]) for yi in lat]
    vlines = [((xi, y1), (xi, y2)) for y1, y2 in zip(lat[:-1], lat[1:]) for xi in lon]
    grids = list(polygonize(MultiLineString(hlines + vlines)))
    grids = gpd.GeoDataFrame(grids) 
    grids.columns =['geometry'] 
    grids['geometry'] = grids['geometry']
    grids.crs = "EPSG:4326"  
    grids['X'] = grids.geometry.centroid.x
    grids['Y'] = grids.geometry.centroid.y
    xX = np.array(grids['X']).reshape((lon.shape[0]-1,lat.shape[0]-1)).transpose()
    yY = np.array(grids['Y']).reshape((lon.shape[0]-1,lat.shape[0]-1)).transpose()
    return grids,xv,yv,xX,yY

def populatingGrid(dataHosp,center,xX,yY,xv,yv):   
    data = np.zeros([1,dataHosp.shape[1],np.size(yv,0)-1, np.size(xv,1)-1])
    xcenter = center.geometry.centroid.x
    ycenter = center.geometry.centroid.y
   
    for ii in range(0,dataHosp.shape[0]):
        dist = ((xcenter[ii]-xX)**2 + (ycenter[ii]-yY)**2)**(1/2)
        mindist = np.where(dist == np.amin(dist))
        print('Hospitalization number '+str(ii)+' from '+str(dataHosp.shape[0]))
        for kk in range (0,dataHosp.shape[1]):
            data[0,kk,mindist[0][0],mindist[1][0]]= data[0,kk,mindist[0][0],mindist[1][0]]+dataHosp.iloc[ii,kk]     
    return data

def populatingGridMatHOSP(hospGPD,dataHosp,center,xX,yY,year):
    
    # Extracting year, month and day 
    hospGPD['year'] = pd.DatetimeIndex(hospGPD["DT_INTER"]).year
    hospGPD['month'] = pd.DatetimeIndex(hospGPD["DT_INTER"]).month  
    hospGPD['day'] = pd.DatetimeIndex(hospGPD["DT_INTER"]).day
    
    # Creating a perfect day array
    startDate = datetime.datetime(year, 1, 1, 0, 0)
    endDate = datetime.datetime(year+1, 1, 1, 0, 0)
    datePfct = np.arange(np.datetime64(startDate),np.datetime64(endDate),3600000000*24)
    datePfct = pd.DataFrame(datePfct)
    datePfct['year'] = pd.DatetimeIndex(datePfct.iloc[:,0]).year
    datePfct['month'] = pd.DatetimeIndex(datePfct.iloc[:,0]).month  
    datePfct['day'] = pd.DatetimeIndex(datePfct.iloc[:,0]).day
    # Creating a new array with perfect date, var and cells
    #dataTempo = np.zeros([np.size(datePfct,0),dataEmissBB.shape[1],np.size(yY,0), np.size(xX,1)])
    dataTempo = np.zeros([np.size(datePfct,0),1,np.size(yY,0), np.size(xX,1)])
    # extracting centroids from BB cases
    xcenter = center.geometry.centroid.x
    ycenter = center.geometry.centroid.y
    
    for jj in range(0,datePfct.shape[0]):
        hospGPDused = hospGPD[(hospGPD['month']==datePfct['month'][jj]) & (hospGPD['day']==datePfct['day'][jj])]
        xcenterUsed = xcenter[(hospGPD['month']==datePfct['month'][jj]) & (hospGPD['day']==datePfct['day'][jj])]
        ycenterUsed = ycenter[(hospGPD['month']==datePfct['month'][jj]) & (hospGPD['day']==datePfct['day'][jj])]      
        dataHospUsed = dataHosp[(hospGPD['month']==datePfct['month'][jj]) & (hospGPD['day']==datePfct['day'][jj])]
 
        if hospGPDused.shape[0]>0:
            for ii in range(0,hospGPDused.shape[0]):
                dist = ((xcenterUsed.iloc[ii]-xX)**2 + (ycenterUsed.iloc[ii]-yY)**2)**(1/2)
                mindist = np.where(dist == np.amin(dist))
                print('Hospitalization number = ' + str(ii) + ' day number = '+str(jj))
                print (str(dataHospUsed.iloc[ii]))
                dataTempo[jj,0,mindist[0][0],mindist[1][0]]= dataTempo[jj,0,mindist[0][0],mindist[1][0]]+dataHospUsed.iloc[ii]

        else:
            dataTempo[jj,0,:,:]=0
            
    
    return dataTempo,datePfct
