import time
from datetime import datetime
import board
import busio
import digitalio
import adafruit_max31865
import pymysql #.connector as mariadb
from enum import Enum

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23,GPIO.OUT) # PIN FOR RELAY CONTROLLING HEATING ELEMENT

def c_to_f(celcius):
    return celcius * (9/5) + 32

'''
class EventID(Enum):
    #Null = Idle
    Start = 1
    Preheat = 2
    HeaterOn = 3
    HeaterOff = 4
    Coast = 5
    Idle = 6
    Done = 7
    DoneIdle = 8
    Error = 9
'''

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
#spi1 = busio.SPI(board.D21, MOSI=board.D20, MISO=board.D19)

cs1 = digitalio.DigitalInOut(board.D6) #This is the GPIO pin on of the MAX318650 Board
cs2 = digitalio.DigitalInOut(board.D5) #This is the GPIO pin on of the MAX318650 Board

pitsensor = adafruit_max31865.MAX31865(spi,cs1,wires=3,rtd_nominal=100.0,ref_resistor=430.0)
meatsensor = adafruit_max31865.MAX31865(spi,cs2,wires=3,rtd_nominal=100.0,ref_resistor=430.0)


## CONFIGURATIONS && PARAMETERS

''' """Later we can get these from user input """'''

meat_type = "Boston Butt"
weight = 8.5 #lbs
recipe = "Butt-Smoker Testing Recipe"
done_temp = 100.00 #degF Internal Meat Probe Temperature
set_point = 100.00 # degF Smoker Hold Temperature


interval = 5 #seconds
lower_bound = set_point - 2 # Smoker Turns On at this Temp
upper_bound = set_point + 5 # Smoker Turns Off at this Temp

enable = 1 #By deault, Heating loop is enabled
heating_flag = 0 # Initialized as 0
done_flag = 0
i = 0

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
print(timestamp,': Initialized Successfully!')
print('---- Configuration Settings ---')
print('-- Set Point Temperature:',set_point,'--')
print('-----  Upper Bound:', upper_bound,' -----')
print('-----  Lower Bound:', lower_bound,' -----')
print('------------------------------')
print('Establishing SQL Connection...')


## SQL VARIABLES

#db = PyMySQL.connect("localhost:port","username","password","database_name")
db = pymysql.connect(user='smoker', password='sauceman', database='MY_SMOKER')
cursor = db.cursor()
print('Database Connected!')

try:
    while True: #Always

    ## WAITING FOR START SIGNAL, CHECK DB

    #Here we should check database for start signal
    # And/Or check start button
        start = 1

        if start == 1:
            
            #GET TEMPS
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pit_temp = c_to_f(pitsensor.temperature)
            pit_temp = round(pit_temp,2)
            meat_temp = c_to_f(meatsensor.temperature)
            meat_temp = round(meat_temp,2)
            #meat_temp = 0
            print(timestamp,': Pit Temperature:',pit_temp,'F')
            print(timestamp,': Meat Temperature:',meat_temp,'F')
            
            if i == 0:           # IF FIRST LOOP
                event_id = 1
                start_temp = pit_temp
                ## Update Run_Num from Database
                try:
                    cursor.execute("INSERT INTO RunLog (date) VALUES (%s)", (timestamp))
                    db.commit()
                    cursor.execute("SELECT id FROM RunLog ORDER BY id DESC LIMIT 1")               
                    result = cursor.fetchall()
                    run_num = result[0][0]
                    print(timestamp,': Run ID#:',run_num)                
                except pymysql.Error as error:
                    print(timestamp, ": Some Error Getting RUN ID from Database:", error)
                    enable = 0
                    db.close()
                    
                ## Store Parameters in Database
                try:
                    cursor.execute("INSERT INTO ParameterLog (time, meat_type, weight, recipe, set_temp, done_temp, upper_bound, lower_bound, time_interval, start_temp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (timestamp, meat_type, weight, recipe, set_point, done_temp, upper_bound, lower_bound, interval, start_temp))
                    db.commit()                
                except pymysql.Error as error:
                    print(timestamp, ": Some Error Storing Parameters in Database:", error)
                    enable = 0
                    db.close()
                    
                    
                time.sleep(1)
                print(timestamp,': Starting Loop....')
            
            #Check if Meat is Done
            if meat_temp >= done_temp:
                if done_flag == 0:
                    print(timestamp,': Meat is done !!')
                    event_id = 7
                    done_flag =  1
                else:
                    i = i
                    event_id = 8
                    
                enable = 0
                time.sleep(interval * 2)
            
            # DETERMINE HEATING
            err = round((pit_temp - set_point),2)
            print(timestamp,': Error of',err,'*F')
            
            if (enable == 1 and i > 0):
                if pit_temp > upper_bound:      #Cut Off above Upper Bound
                    heating_flag = 0
                    heat_time = 0
                    #event_id = EventID.HeaterOff
                    event_id = 4



                elif pit_temp < lower_bound:    #Cut On Below Lower Bound
                    heating_flag = 10
                    heat_time = interval
                    #event_id = EventID.HeaterOn
                    event_id = 3

                    
                else:
                    i = i                      #Do Nothing Between Setpoints (Keep previous setting)
                    #event_id = EventID.Coast
                    event_id = 5

                
                if heating_flag == 0:
                    print('{}: Skipping Heating Cycle'.format(timestamp))
                    time.sleep(interval)
                    
                    
                elif heating_flag == 10:         # HEATING SEQUENCE
                    #Store database values
                    #event_id = EventID.HeaterOn
                    print(timestamp,": HEATING ELEMENT ON -",heat_time,"s")
                    GPIO.output(23,GPIO.HIGH)
                    time.sleep(heat_time)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(timestamp,": HEATING ELEMENT OFF")
                    GPIO.output(23,GPIO.LOW)
                    time.sleep(interval-heat_time)
                    
            else:
                    GPIO.output(23,GPIO.LOW)           #IDLE SEQUENCE.. Always Turn Off if not enabled
                    #event_id = EventID.Idle
                    if event_id == 1:               #Startup Loop
                            time.sleep(interval)
                    else:
                        event_id = 6
                        print(timestamp,': Idle - Waiting for Enable Signal')
                        time.sleep(interval)
                    
            # SEND DATA TO SQL
            try:
                cursor.execute("INSERT INTO TempLog (run_num, time, pit_temp, meat_temp, eventid) VALUES (%s, %s, %s, %s, %s)", (run_num, timestamp, pit_temp, meat_temp, event_id))
                db.commit()
            except pymysql.Error as error:
                print(timestamp, ": Some Error WRITING Database:", error)
                db.close()

            ## READ TEMP FROM DATABASE, >> FOR TESTING <<
            '''
            try:
                cursor.execute("SELECT * FROM temps ORDER BY id DESC LIMIT 1")
                result = cursor.fetchall()
                print('DB Temperature: {}'.format(result[0][2]))
                print('DB Timestamp: {}'.format(result[0][1]))
                #print('DB Temperature: {}'.format(result[0][1]))

            except pymysql.Error as error:
                print('Some Error READING Database: {}'.format(error))
                db.close()
            '''
            
            i = i + 1
            
            #time.sleep(interval)
        
    db.close()

except KeyboardInterrupt:
    print(timestamp,": Manual Exit, Turning off Heating Element")
    GPIO.output(23,GPIO.LOW)
    GPIO.cleanup()
except:
    print("Some Other Error Occured and the program is shutting down...")
    GPIO.output(23,GPIO.LOW)
    GPIO.cleanup()
finally:
    print("Shutting Down")
    GPIO.output(23,GPIO.LOW)
    GPIO.cleanup()
    
