------------------------------------ GHosp --------------------------------------

 This repository disaggregates daily hospitalization from DATASUS 
 and creates netCDF files with aggregated hospitalization in regular areas. 
 
 Data sources:
     https://www.worldpop.org/project/categories?id=3
     https://www.qualocep.com/
     https://dados.gov.br/organization/instituto-brasileiro-de-geografia-e-estatistica-ibge?q=ra%C3%A7a&sort=score+desc%2C+metadata_modified+desc
     https://forest-gis.com/shapefile-bairros-das-cidades-brasileiras/
     
     Link to downlond the input folder and files:
     	https://1drv.ms/u/s!Agz0M0-_7f5bicp0HYkk5dP0x0SKYQ?e=JpWygW
 

 Inputs: 
     
     fileIds = identification of your input files
     
     lati: Initial latitude (lower-left)
     
     latf: Final latitude (upper-right)
     
     loni: Initial longitude (lower-left)
     
     lonf: Final longitude (upper-right)
     
     deltaX: Grid resolution/spacing in x direction
     
     deltaY: Grig resolution/spacing in y direction
                  
     runOrNotTemporal = Run or not daily temporal profile and daily netCDF
     
     vulGroup = Grouping tag. 
                 'TOTAL' = Total number of hospitalizations
                 'LESS14' = Total number of hospitalizations for younger than 14
                 'MORE60' = Total number of hospitalizations for older than 60
                 'ADULTS' = Total number of hospitalizations for adults (15-59)
                 'MENS' = Total number of hospitalizations for mens
                 'WOMANS' = Total number of hospitalizations for womans
                 'BLACKS' = Total number of hospitalizations for blacks 
                 'WHITES' = Total number of hospitalizations for whites
                 'BRONW' = Total number of hospitalizations for browns
                 'INDIGENOUS' = Total number of hospitalizations for indigenous
                 'ASIAN' = Total number of hospitalizations for asians
                 'VAL_TOT' = Total monetary value of hospitalization
                 'DEATHS' = Total number of deaths
          
 Outputs:
     
     Annual basis netCDF
     'HOSP_annual_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
     
     Daily basis netCDF
     'HOSP_daily_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
    
         
 Last update = 31/10/2022

 Author: Leonardo Hoinaski - leonardo.hoinaski@ufsc.br
