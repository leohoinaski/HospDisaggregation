 -------------------------------------------------------------------------------
                              HospDisaggregation.py
                              
                              
 This is the main script to disaggregate daily hospitalization from DATASUS and
 create netCDF files with aggregated hospitalization in regular areas. 
 
 You need to donwload the input data at: 

     https://arquivos.ufsc.br/d/c3b26a10e6e946fb890e/

 You should create an Inputs folder within the same directory of the main function.
 Paste you inputs into the "Inputs" folder 
 
 

 Inputs: 
     
     rootPath: Path to functions
     
     outPath: Path to outputs folder
     
     lati: Initial latitude (lower-left)
     
     latf: Final latitude (upper-right)
     
     loni: Initial longitude (lower-left)
     
     lonf: Final longitude (upper-right)
     
     deltaX: Grid resolution/spacing in x direction
     
     deltaY: Grig resolution/spacing in y direction
                  
     fileId = identification of your output files
     
     hospFile = hospitalization file from DATASUS - daily basis
     
     listCEPfile = list of coordinates of Braziliam postal codes
     
     runOrNotTemporal = Run or not daily temporal profile and daily netCDF
     
     vulGroup = vunerability group tag. 
                 'Total' = Total number of hospitalizations
                 'less14' = Total number of hospitalizations for younger than 14
                 'more60' = Total number of hospitalizations for older than 60
                 'adults' = Total number of hospitalizations for adults (15-59)
                 'mens' = Total number of hospitalizations for mens
                 'womans' = Total number of hospitalizations for womans
                 'blacks' = Total number of hospitalizations for blacks 
                 'whites' = Total number of hospitalizations for whites
                 'brown' = Total number of hospitalizations for browns
                 'indigenous' = Total number of hospitalizations for indigenous
                 'asian' = Total number of hospitalizations for asians
          
 Outputs:
     
     Annual basis netCDF
     'HOSP_annual_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
     
     Daily basis netCDF
     'HOSP_daily_'+fileId+'_'+str(deltaX)+'x'+str(deltaY)+'_'+str(hosp.ANO_CMPT[0])+'.nc'
    
     
 External functions:
     gridding, netCDFcreator
     
 Last update = 29/10/2021

 Author: Leonardo Hoinaski - leonardo.hoinaski@ufsc.br

 ------------------------------------------------------------------------------
