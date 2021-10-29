#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
                            netCDFcreator.py
                            
This function creates the netCDF files ready to use in CMAQ from FINN inventory.

Inputs:
    
    folder: folter to output files
    
    name: output names
    
    data: matrix with data ready to convert in netCDF
    
    xv, yv: meshgrid outputs - grid definition
    
    lat, lon = grid latitude and longitudes
    
    year: respective years of emission inventories
    
    month: respective month of emission inventories
    
    dates: dates from emission file
    
    specation = speciation profile used. It could be GEOS-CHEM, 
            MOZART or SAPRC99

Outputs:
        
    netdCDF files

        

Last update = 21/10/2021

Author: Leonardo Hoinaski - leonardo.hoinaski@ufsc.br
---------------------------------------------------------------
"""
import netCDF4 as nc4
import numpy as np
import datetime


def createNETCDFtemporal(folder,name,data,xv,yv,lat,lon,dates,outType):
    cdate = datetime.datetime.now()
    cdateStr = int(str(cdate.year)+str(cdate.timetuple().tm_yday))
    ctime = int(str(cdate.hour)+str(cdate.minute)+str(cdate.second))
    tflag = np.empty([dates.shape[0],data.shape[1],2],dtype='i4')
    
    for ii in range(0,dates.shape[0]):
        tflag[ii,:,0]=int(dates['year'][0]*1000 + dates.iloc[ii,0].timetuple().tm_yday)
        tflag[ii,:,1]=int(str(dates.iloc[ii,0].hour)+'0000')
    
    sdate =  dates['year'][0]*1000 + dates.iloc[0,0].timetuple().tm_yday  
    
    f2 = nc4.Dataset(folder+'/'+name,'w', format='NETCDF3_CLASSIC') #'w' stands for write    
    #Add global attributes
    f2.IOAPI_VERSION ='$Id: @(#) ioapi library version 3.1 $'
    f2.EXEC_ID = '???????????????'
    f2.FTYPE =  1
    f2.CDATE= cdateStr
    f2.CTIME= ctime
    f2.WDATE= cdateStr
    f2.WTIME= ctime
    f2.SDATE= sdate
    f2.STIME= 0
    f2.TSTEP= 240000
    f2.NTHIK= 1
    f2.NCOLS= np.size(xv,1)-1
    f2.NROWS= np.size(yv,0)-1
    f2.NLAYS= 1
    f2.NVARS= 62 #dataEmiss.shape[1]
    f2.GDTYP= 1
    f2.P_ALP= -10
    f2.P_BET= 0
    f2.P_GAM= np.mean(xv)
    f2.XCENT= np.mean(xv)
    f2.YCENT= np.mean(yv)
    f2.XORIG= xv.min()
    f2.YORIG= yv.min()
    f2.XCELL= xv[0,1] - xv[0,0]
    f2.YCELL= yv[1,0] - yv[0,0]
    f2.VGTYP= -1
    f2.VGTOP= 0.0
    f2.VGLVLS= [0,0]
    
    strVAR = 'Total less5 more60 adults mens womans blacks whites \n\
        brown indigenous asian'      
    f2.VAR_LIST=strVAR
    f2.FILEDESC= 'Disaggregated hospitalization'
    f2.HISTORY ='' 
       
    # # Specifying dimensions
    #tempgrp = f.createGroup('vehicularEmissions_data')
    f2.createDimension('TSTEP', dates.shape[0])
    f2.createDimension('DATE-TIME', 2)
    f2.createDimension('LAY', 1)
    f2.createDimension('VAR', data.shape[1])
    f2.createDimension('ROW', len(lat)-1)
    f2.createDimension('COL', len(lon)-1)
    
    # Building variables
    TFLAG = f2.createVariable('TFLAG', 'i4', ('TSTEP', 'VAR', 'DATE-TIME'))
    print(f2['TFLAG'])
    TOTAL = f2.createVariable('TOTAL', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
    if outType=='Annual':
        LESS5 = f2.createVariable('LESS5', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        MORE60 = f2.createVariable('MORE60', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        ADULTS = f2.createVariable('ADULTS', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        MENS = f2.createVariable('MENS', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        WOMANS = f2.createVariable('WOMANS', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        BLACKS = f2.createVariable('BLACKS', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        WHITES = f2.createVariable('WHITES', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        BROWN = f2.createVariable('BROWN', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        INDIGENOUS = f2.createVariable('INDIGENOUS', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        ASIAN = f2.createVariable('ASIAN', 'f4', ('TSTEP', 'LAY', 'ROW','COL'))
        LESS5[:,:,:,:] =  data[:,1,:,:]
        MORE60[:,:,:,:] =  data[:,2,:,:]
        ADULTS[:,:,:,:] =  data[:,3,:,:]
        MENS[:,:,:,:] =  data[:,4,:,:]
        WOMANS[:,:,:,:] =  data[:,5,:,:]
        BLACKS[:,:,:,:] =  data[:,6,:,:]
        WHITES[:,:,:,:] =  data[:,7,:,:]
        BROWN[:,:,:,:] =  data[:,8,:,:]
        INDIGENOUS[:,:,:,:] =  data[:,9,:,:]
        ASIAN[:,:,:,:] =  data[:,10,:,:]
        LESS5.units = 'Less than 5 year old'
        MORE60.units = 'More than 60 years old'
        ADULTS.units = 'Total number of adults'
        MENS.units = 'Total number of mens'
        WOMANS.units = 'Total number os womans'
        BLACKS.units = 'Total number of blacks'
        WHITES.units = 'Total number of whites'
        BROWN.units = 'Total number browns'
        INDIGENOUS.units = 'Total number of indigenous'
        ASIAN.units = 'Total number of asian'


    print(tflag.shape)
    TFLAG[:,:,:] = tflag
    #TFLAG[:] = dates.iloc[:,0].dt.strftime('%Y-%m-%d %H:%M:%S')
    TOTAL[:,:,:,:] =  data[:,0,:,:]

    
    #Add local attributes to variable instances
    TFLAG.units = '<YYYYDDD,HHMMSS>'
    TOTAL.units = 'Total number'



    
    f2.close()

