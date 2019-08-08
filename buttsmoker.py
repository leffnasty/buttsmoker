#### Primary block for issuing commands to the smoker system ####

import os
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

f = open('smokerdata.dat', 'w')



def measuretemperature():
    global meattemp
    global pittemp
    meattemp = 50
    pittemp = 220

def heatup():   # HEATING SEQUENCE
    global err
    global interval
    global errfactor
    global loopnum

    heattime = errfactor*interval
    if loopnum <= 1:
        GPIO.setup(18,GPIO.OUT)

    print("HEATING ELEMENT ON - ",heattime,"s")
    GPIO.output(18,GPIO.HIGH)
    time.sleep(heattime)
    print("HEATING ELEMENT OFF")
    GPIO.output(18,GPIO.LOW)
    time.sleep(interval-heattime)

def runtime():  # CALCULATES RUNTIME OF SMOKER
    global loopnum
    global seconds
    global minutes
    global hours
    loopnum = loopnum + 1
    seconds = seconds + interval
    #if seconds > 60:
        #minutes = minutes + 1
        #seconds = seconds - 60
    #if minutes > 60:
        #hours = hours + 1
        #minutes = minutes - 60
    print("Runtime",hours,":",minutes,":",seconds)



#### PARAMETERS AND DECLARATIONS  ####

setpoint = 225 #default value
finaltemp = 165 #final meat temperature
seconds = 0
minutes = 0
hours = 0
loopnum = 0
meattemp = 0
pittemp = 0
errfactor = 1
#
interval = 5 #seconds
run = 1

while (run == 1):

    #### pull temps ####
    #meattemp = temp.meatprobe
    measuretemperature()

    err = setpoint - pittemp
    if meattemp >= finaltemp:
        run = 0
        print("Your Meat is Done!")
        break
    else:
        print("Meat Temp = ",meattemp," F")
        print("Pit Temp = ",pittemp," F")
        print("Temp Delta =",err," F")


    #### determine heating time ####
    if run == 0:
        break
    elif err < 0:
        time.sleep(interval)
    elif err == 0:
        errfactor = 0.25
        heatup()
    elif err < 10:
        errfactor = 0.1 * err
        heatup()
    else:
        errfactor = 1
        heatup()


    #### print runtime  ####
    runtime()

    data = "{} {} {} {}\n".format(seconds,meattemp,pittemp,err)
    f.write(data)

    if loopnum == 10:
        run = 0

print("Out of Loop!")
#f.close()