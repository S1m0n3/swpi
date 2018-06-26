###########################################################################
#     Sint Wind PI
#     Copyright 2012 by Tonino Tarsi <tony.tarsi@gmail.com>
#   
#     Please refer to the LICENSE file for conditions 
#     Visit http://www.vololiberomontecucco.it
# 
##########################################################################

"""This module defines the base sensorssimulator ."""


import threading
import time
import config
import random
import datetime
import sqlite3
from TTLib import  *
import sys
import subprocess
import globalvars
import meteodata
import sensor_thread
import sensor 

class Sensor_External(sensor.Sensor):
    
    def __init__(self,cfg ):
        sensor.Sensor.__init__(self,cfg )
        
    def Detect(self):
        return True,"","",""
    
    def GetData(self):
             
        seconds = datetime.datetime.now().second
        if ( seconds < 30 ):
            time.sleep(30-seconds)
        else:
            time.sleep(90-seconds)
        time.sleep(10)      
            
        mydata = getCurrentMeteoDataFromUrl(self.cfg.external_sensor_path)
        
        if (mydata["offline"] == 1):
            self.offline = True
        else:
            self.offline = False
            
            
        globalvars.meteo_data.last_measure_time = mydata["last_measure_time"]
        globalvars.meteo_data.idx = mydata["idx"]
        globalvars.meteo_data.status  = mydata["status"]
        globalvars.meteo_data.delay = mydata["delay"]       
        globalvars.meteo_data.hum_in  = mydata["hum_in"]
        globalvars.meteo_data.temp_in  = mydata["temp_in"]    
        globalvars.meteo_data.hum_out  = mydata["hum_out"]    
        globalvars.meteo_data.temp_out   = mydata["temp_out"]  
        globalvars.meteo_data.abs_pressure = mydata["abs_pressure"]
        globalvars.meteo_data.wind_ave     = mydata["wind_ave"]
        globalvars.meteo_data.wind_gust    = mydata["wind_gust"]
        globalvars.meteo_data.wind_dir     = mydata["wind_dir"]
        globalvars.meteo_data.wind_dir_code = mydata["wind_dir_code"]
        globalvars.meteo_data.rain  = mydata["rain"]      
        globalvars.meteo_data.illuminance = mydata["illuminance"]
        globalvars.meteo_data.uv = mydata["uv"]
        
            
     
        #sensor.Sensor.GetData(self)

            


if __name__ == '__main__':

   
    configfile = 'swpi.cfg'
    
   
    cfg = config.config(configfile)
    
    ss = Sensor_External(cfg)
    
    while ( 1 ) :
        ss.GetData()
        
        
    
    