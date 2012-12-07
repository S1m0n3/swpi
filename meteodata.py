###########################################################################
#     Sint Wind PI
#     Copyright 2012 by Tonino Tarsi <tony.tarsi@gmail.com>
#   
#     Please refer to the LICENSE file for conditions 
#     Visit http://www.vololiberomontecucco.it
# 
##########################################################################

"""MeteoData class"""

import time
import sqlite3
import WeatherStation
import datetime
import TTLib
import config
            

class MeteoData(object):
    
    def __init__(self,cfg):
        
        self.cfg = cfg
        
        self.last_measure_time = None
        self.previous_measure_time = None

        # Station data
        self.idx = None
        self.status = -9999
        self.wind_dir = None
        self.wind_ave = None
        self.wind_gust = None

        self.temp_out = None
        self.hum_out = None
        self.abs_pressure = None
        self.rain = None
        self.rain_rate = None
        self.temp_in = None
        self.hum_in = None
        self.uv = None
        self.illuminance = None        
        
        self.rb_wind_dir = TTLib.RingBuffer(cfg.number_of_measure_for_wind_dir_average)
        
        #calculated values
        self.wind_dir_code = None
        self.wind_chill = None
        self.temp_apparent = None
        self.dew_point = None
        
        self.previous_rain = None   
        
        self.wind_dir_ave = None
                                    
        if ( not self.getLastTodayFromDB() ):
            
            self.ResetStatistic()
            
    def CalcMeanWindDir(self):
        rb = TTLib.RingBuffer(self.cfg.number_of_measure_for_wind_dir_average)
        while 1:
            rb.append(self.wind_dir)
            yield  rb.getMeanDir()

    def ResetStatistic(self):
    
            #statistics values
            self.winDayMin = None
            self.winDayMax = None

            self.winDayGustMin = None
            self.winDayGustMax = None        
            
            self.TempInMin = None
            self.TempInMax = None

            self.TempOutMin = None
            self.TempOutMax = None

            self.UmInMin = None
            self.UmInMax = None

            self.UmOutMin = None
            self.UmOutMax = None

            self.PressureMin = None
            self.PressureMax = None
            
      
    def CalcStatistics(self):
        
        self.wind_chill = WeatherStation.wind_chill(self.temp_out, self.wind_ave)
        self.temp_apparent = WeatherStation.apparent_temp(self.temp_out, self.hum_out, self.wind_ave)
        self.dew_point = WeatherStation.dew_point(self.temp_out, self.temp_out)
        
        if ( self.previous_rain != None and self.previous_measure_time != None ):
            self.rain_rate = self.rain - self.previous_rain
        
        if ( ( self.previous_measure_time != None ) and  (datetime.datetime.strftime(self.last_measure_time,'%m/%d/%Y') !=  datetime.datetime.strftime(self.previous_measure_time,'%m/%d/%Y')  ) ):
            
            self.ResetStatistic()

        else:
        
            if ( self.winDayMin == None or self.wind_ave < self.winDayMin ) : 
                self.winDayMin  = self.wind_ave
            if ( self.winDayMax == None or self.wind_ave > self.winDayMax ) : 
                self.winDayMax  = self.wind_ave       
                
            if ( self.winDayGustMin == None or self.wind_gust < self.winDayGustMin ) : 
                self.winDayGustMin  = self.wind_gust
            if ( self.winDayGustMax == None or self.wind_gust > self.winDayGustMax ) : 
                self.winDayGustMax  = self.wind_gust                            
                     
                    
            if ( self.TempOutMin == None or self.temp_out < self.TempOutMin ) : 
                self.TempOutMin  = self.temp_out
            if ( self.TempOutMax == None or self.temp_out > self.TempOutMax ) : 
                self.TempOutMax  = self.temp_out                       
                    
                    
            if ( self.TempInMin == None or self.temp_in < self.TempInMin ) : 
                self.TempInMin  = self.temp_in
            if ( self.TempInMax == None or self.temp_in > self.TempInMax ) : 
                self.TempInMax  = self.temp_in                       
                    
                    
            if ( self.UmInMin == None or self.hum_in < self.UmInMin ) : 
                self.UmInMin  = self.hum_in
            if (  self.UmInMax == None or self.hum_in > self.UmInMax ) : 
                self.UmInMax  = self.hum_in                       
                    
            if ( self.UmOutMin == None or self.hum_out < self.UmOutMin ) : 
                self.UmOutMin  = self.hum_out
            if ( self.UmOutMax == None or self.hum_out > self.UmOutMax ) : 
                self.UmOutMax  = self.hum_out                       
                    
            if ( self.PressureMin == None or  self.abs_pressure < self.PressureMin ) : 
                self.PressureMin  = self.abs_pressure
            if ( self.PressureMax == None or self.abs_pressure > self.PressureMax ) : 
                self.PressureMax  = self.abs_pressure                       
                
        self.rb_wind_dir.append(self.wind_dir)
        self.wind_dir_ave = self.rb_wind_dir.getMean()

        self.previous_measure_time = self.last_measure_time
        
        self.previous_rain = self.rain
        
        
        
    def LogDataToDB(self):
            conn = sqlite3.connect('db/swpi.s3db',200)
            dbCursor = conn.cursor()
            #dbCursor.execute("insert into METEO(TIMESTAMP_LOCAL,TIMESTAMP_IDX,WINDIR_CODE,WIND_DIR,WIND_AVE,WIND_GUST,TEMP,PRESSURE,HUM,RAIN,RAIN_RATE,TEMPINT,HUMINT,WIND_CHILL,TEMP_APPARENT,DEW_POINT,UV_INDEX,SOLAR_RAD,WIND_DAY_MIN,WIND_DAY_MAX) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (self.last_measure_time,self.last_measure_time,self.wind_dir_code,self.wind_dir,self.wind_ave,self.wind_gust,self.temp_out,self.abs_pressure,self.hum_out,self.rain,0,self.temp_in,self.hum_in,self.wind_chill,self.temp_apparent,self.dew_point,self.uv,self.illuminance,self.winDayMin,self.winDayMax))                        
            #print self.last_measure_time,self.last_measure_time,self.wind_dir_code,self.wind_dir,self.wind_ave,self.wind_gust,self.temp_out,self.abs_pressure,self.hum_out,self.rain,0,self.temp_in,self.hum_in,self.wind_chill,self.temp_apparent,self.dew_point,self.uv,self.illuminance,self.winDayMin,self.winDayMax,self.winDayGustMin,self.winDayGustMax,self.TempOutMin,self.TempOutMax,self.TempInMin,self.TempInMax,self.UmOutMin,self.UmOutMax,self.UmInMin,self.UmInMax,self.PressureMin,self.PressureMax,self.wind_dir_ave
            dbCursor.execute("insert into METEO(TIMESTAMP_LOCAL,TIMESTAMP_IDX,WINDIR_CODE,WIND_DIR,WIND_AVE,WIND_GUST,TEMP,PRESSURE,HUM,RAIN,RAIN_RATE,TEMPINT,HUMINT,WIND_CHILL,TEMP_APPARENT,DEW_POINT,UV_INDEX,SOLAR_RAD,WIND_DAY_MIN,WIND_DAY_MAX,WIND_DAY_GUST_MIN ,WIND_DAY_GUST_MAX ,TEMP_OUT_DAY_MIN ,TEMP_OUT_DAY_MAX,TEMP_IN_DAY_MIN ,TEMP_IN_DAY_MAX ,HUM_OUT_DAY_MIN ,HUM_OUT_DAY_MAX ,HUM_IN_DAY_MIN ,HUM_IN_DAY_MAX ,PRESSURE_DAY_MIN ,PRESSURE_DAY_MAX,WIND_DIR_AVE ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (self.last_measure_time,self.last_measure_time,self.wind_dir_code,self.wind_dir,self.wind_ave,self.wind_gust,self.temp_out,self.abs_pressure,self.hum_out,self.rain,0,self.temp_in,self.hum_in,self.wind_chill,self.temp_apparent,self.dew_point,self.uv,self.illuminance,self.winDayMin,self.winDayMax,self.winDayGustMin,self.winDayGustMax,self.TempOutMin,self.TempOutMax,self.TempInMin,self.TempInMax,self.UmOutMin,self.UmOutMax,self.UmInMin,self.UmInMax,self.PressureMin,self.PressureMax,self.wind_dir_ave))                        
            conn.commit()
            conn.close()
            msg = ""
            if self.wind_dir_code !=None :
                msg = msg + "Dir: " + str(self.wind_dir_code)
            if self.wind_ave != None :
                msg = msg + " - Spd: " + str(self.wind_ave)
            if self.wind_gust != None :
                msg = msg + " - Gst: " + str(self.wind_gust) 
            if self.temp_out != None :
                msg = msg + " - T: " + str(self.temp_out)     
            if self.abs_pressure != None :
                msg = msg + " - P: %.1f" % self.abs_pressure   
            if self.hum_out != None :
                msg = msg + " - U: %d" % self.hum_out                                             
            TTLib.log(msg)


    def getLastTodayFromDB(self):
        conn = sqlite3.connect('db/swpi.s3db',200)
        
        dbCursor = conn.cursor()
        dbCursor.execute("SELECT * FROM METEO where date(TIMESTAMP_LOCAL) = date('now') order by rowid desc limit 1")
        data = dbCursor.fetchall()
        if ( len(data) != 1):
            if conn:
                conn.close()
            return False

# "2012-10-19 11:15:50.375000"

#        self.last_measure_time = datetime.datetime.strptime(data[0][0],"%Y-%m-%d %H:%M:%S.%f")   
#        self.idx = datetime.datetime.strptime(data[0][1],"%Y-%m-%d %H:%M:%S.%f")
#        self.wind_dir_code = (data[0][2])
#        self.wind_dir = (data[0][3])
#        self.wind_ave = (data[0][4])
#        self.wind_gust = (data[0][5])
#        self.temp_out = (data[0][6])
#        self.abs_pressure = (data[0][7])
#        self.hum_out = (data[0][8])
#        self.rain = (data[0][9])
#        self.rain_rate = (data[0][10])
#        self.temp_in = (data[0][11])
#        self.hum_in = (data[0][12])
#        self.wind_chill = (data[0][13])
#        self.temp_apparent = (data[0][14])
#        self.dew_point = (data[0][15])
#        self.uv = (data[0][16])
#        self.illuminance = (data[0][17])
        self.winDayMin = (data[0][18])
        self.winDayMax = (data[0][19])
        self.winDayGustMin = (data[0][20])
        self.winDayGustMax = (data[0][21]     )   
        self.TempOutMin = (data[0][22])
        self.TempOutMax = (data[0][23])
        self.TempInMin = (data[0][24])
        self.TempInMax = (data[0][25])
        self.UmOutMin = (data[0][26])
        self.UmOutMax = (data[0][27])
        self.UmInMin = (data[0][28])
        self.UmInMax = (data[0][29])
        self.PressureMin = (data[0][30])
        self.PressureMax = (data[0][31])

#        self.previous_rain = self.rain
#        self.previous_measure_time = self.last_measure_time

        
        if conn:
            conn.close()
            
        return True
            
            
#    def getLastFromDB(self):
#        conn = sqlite3.connect('db/swpi.s3db',200)
#        dbCursor = conn.cursor()
#        dbCursor.execute('SELECT * FROM METEO order by rowid desc limit 1')
#        data = dbCursor.fetchall()
#        if ( len(data) != 1):
#            if conn:
#                conn.close()
#            return   
#
#        self.last_measure_time = data[0][0]
#        self.idx = data[0][1]
#        self.wind_dir_code = data[0][2]
#        self.wind_dir = data[0][3]
#        self.wind_ave = data[0][4]
#        self.wind_gust = data[0][5]
#        self.temp_out = data[0][6]
#        self.abs_pressure = data[0][7]
#        self.hum_out = data[0][8]
#        self.rain = data[0][9]
#        self.rain_rate = data[0][10]
#        self.temp_in = data[0][11]
#        self.hum_in = data[0][12]
#        self.wind_chill = data[0][13]
#        self.temp_apparent = data[0][14]
#        self.dew_point = data[0][15]
#        self.uv = data[0][16]
#        self.illuminance = data[0][17]
#        self.winDayMin = data[0][18]
#        self.winDayMax = data[0][19]
#        self.TempOutMin = data[0][20]
#        self.TempOutMax = data[0][21]
#        self.TempInMin = data[0][22]
#        self.TempInMax = data[0][23]
#        self.UmOutMin = data[0][24]
#        self.UmOutMax = data[0][25]
#        self.UmInMin = data[0][26]
#        self.UmInMax = data[0][27]
#        self.PressureMin = data[0][28]
#        self.PressureMax = data[0][29]
#
#        self.previous_rain = self.rain
#
#        if conn:
#            conn.close()            
            
            
if __name__ == '__main__':

    
    configfile = 'swpi.cfg'
    
   
    cfg = config.config(configfile)
   
    
    
    mt = MeteoData(cfg)
    
    mt.wind_dir = 10
    a = mt.CalcMeanWindDir()
    print a.next()
 
    mt.wind_dir = 2
    print a.next()
    
#    mt.getLastFromDB()
#    mt.getLastTodayFromDB()
    
 

