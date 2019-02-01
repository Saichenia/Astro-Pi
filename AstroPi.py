import ephem
import datetime
from time import sleep
from picamera import PiCamera

import time

from gpiozero import CPUTemperature
from sense_hat import SenseHat

import logging
import logzero
from logzero import logger

import random

import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Connect to the Sense Hat
sh = SenseHat()

# define some colours - keep brightness low
o = [0,0,0]
r = [73,40,21]
e = [73, 70, 2]
l = [73, 51, 5]
c = [73, 40, 23]
a = [73,100,50]
g = [80, 56, 39]
b = [24, 64, 64]


img1 = [
    o,o,o,o,r,o,o,o,
    o,o,o,o,r,r,o,o,
    o,o,o,r,c,c,o,o,
    o,o,r,c,e,c,r,o,
    o,r,c,l,e,c,r,o,
    o,r,l,a,a,c,r,o,
    o,r,e,a,l,r,o,o,
    o,o,r,e,r,o,o,o,
    ]

img2 = [
    o,g,g,g,g,o,o,o,
    g,g,b,b,g,g,o,o,
    g,b,b,b,b,g,o,o,
    g,b,b,b,b,g,o,o,
    g,g,b,b,g,g,o,o,
    o,g,g,g,g,g,g,o,
    o,o,o,o,o,g,g,g,
    o,o,o,o,o,o,g,g,
    ]



longrad = 0
latrad = 0
global photo_counter
photo_counter = 0
checker = 0
cpu = CPUTemperature()
       
       
# Set a logfile name
logzero.logfile(dir_path+"/data01.csv")

# Set a custom formatter
formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: \n%(message)s');
logzero.formatter(formatter)


n = 0.0 

name = "ISS (ZARYA)"

line1 = "1 25544U 98067A   19032.30987313  .00001170  00000-0  25693-4 0  9997"

line2 = "2 25544  51.6429 316.9782 0004973 340.0425 166.5613 15.53214053154148"

iss = ephem.readtle(name, line1, line2)




####
cam = PiCamera()
cam.resolution = (2592,1944)
iss.compute()
print(iss.sublat, iss.sublong)
n = iss.sublat
print("%f" % (iss.sublat),"%f" %  n, ephem.degrees(n))

def update_image(checker):

        # a list with all possible rotation values
    orientation = [0,90,270,180]
    print(checker)
    if checker == 0:
    # pick one at random
        rotation = random.choice(orientation)
        # set the rotation
        sh.set_rotation(rotation)
    elif checker == 1:
        sh.flip_h()

def get_latlon():
    iss.compute() # Get the lat/long values from ephem

    long_value = [float(i) for i in str(iss.sublong).split(":")]

    if long_value[0] < 0:

        long_value[0] = abs(long_value[0])
        cam.exif_tags['GPS.GPSLongitudeRef'] = "W"
    else:
        cam.exif_tags['GPS.GPSLongitudeRef'] = "E"
    cam.exif_tags['GPS.GPSLongitude'] = '%d/1,%d/1,%d/10' % (long_value[0], long_value[1], long_value[2]*10)

    lat_value = [float(i) for i in str(iss.sublat).split(":")]

    if lat_value[0] < 0:

        lat_value[0] = abs(lat_value[0])
        cam.exif_tags['GPS.GPSLatitudeRef'] = "S"
    else:
        cam.exif_tags['GPS.GPSLatitudeRef'] = "N"

    cam.exif_tags['GPS.GPSLatitude'] = '%d/1,%d/1,%d/10' % (lat_value[0], lat_value[1], lat_value[2]*10)
    print(str(lat_value), str(long_value))
    return(str(lat_value), str(long_value))


def get_photo():
    global photo_counter
    try:
         
        # get latitude and longitude
        lat, lon = get_latlon()
        # Save the data to the file
        logger.info("%s,%s,%s", "photo_"+ str(photo_counter).zfill(5), lat, lon )
        # use zfill to pad the integer value used in filename to 3 digits (e.g. 001, 002...)
                    
        cam.capture(dir_path+"/photo_"+ str(photo_counter).zfill(5)+".jpg")
        photo_counter += 1
                    
    except Exception as e:
       logger.error("An error occurred: " + str(e))
       pass
                    
# create a datetime variable to store the start time
start_time = datetime.datetime.now()
start_time2 = time.time()
# create a datetime variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.datetime.now()
# run a loop for 2 minutes
#sh.set_pixels(img1)
#cam.start_preview()
#cam.start_preview()
while ((now_time < start_time + datetime.timedelta(minutes=175)) and (photo_counter < 980) and (cpu.temperature < 70)):
    iss.compute()
    latrad = float("%f" % (iss.sublat))
    longrad = float("%f" % (iss.sublong))
    
    americas = [
        (-1.35616 < longrad < -0.85519 and 0.073888 < latrad < 0.207737), #venezuela
        (-2.004805 < longrad < -1.649931 and 0.288185< latrad < 0.558909),#mexico
        (-2.214386 < longrad < -1.338161 and 0.52683 < latrad < 0.7972), #USA
        (-1.652101< longrad < -1.1442582 and 0.138603 < latrad < 0.379025),# Guatmala
        (-1.333111< longrad < -0.588619 and -0.590034< latrad < -0.007321)]#Brazil
    
    central = [
        (-0.171779 < longrad < 0.052704 and 0.61969 < latrad < 0.767325),#Ibéria
        (-0.314378 < longrad < 0.75828 and 0.052333 < latrad < 0.280259),# top africa
        (0.216237 < longrad < 0.741116 and -0.614419 < latrad < -0.010986),#mid africa
        (0.057017 < longrad < 0.537736 and 0.639903 < latrad < 0.814486)]#mediterraneo
    
    oceasia = [
        (1.184735 < longrad < 1.509269 and 0.088706 < latrad < 0.613406),#India
        (1.604362 < longrad < 2.185311 and 0.146123 < latrad < 0.601894),#Myanmar
        (2.069162 < longrad < 2.423922 and 0.571374 < latrad < 0.844868),#Korea
        (2.111045 < longrad < 2.399285 and -0.413486 < latrad < -0.195962),#Top Australia
        (1.997895 < longrad < 2.176838 and -0.490407 < latrad < -0.61162),# South left Australia
        (2.377186 < longrad < 2.688272 and -0.675403 < latrad < -0.421843)]#South right Australia
    print("Americas: ", americas)
    print("Central: ", central)
    print("Oceasia: ", oceasia)
    print(latrad, longrad)   
    if longrad < -0.442:
        if any(americas):
            get_photo()
            sh.set_pixels(img1)
            checker = 1
    
    elif -0.442 < longrad < 1.058:
        if any(central):
            get_photo()
            sh.set_pixels(img1)
            checker = 1
            
    elif longrad > 1.058:
        if any(oceasia):
            get_photo()
            checker = 1
            
    if checker == 0:
       sh.set_pixels(img2)
    elif checker == 1:
        sh.set_pixels(img1)
        
    sleep(2)

    update_image(checker)

# update the current time
    now_time = datetime.datetime.now()

    cpu = CPUTemperature()
    checker = 0
    print("Temp: ", cpu.temperature)
    print("Time: ", time.time()-start_time2)
    
    now_time = datetime.datetime.now()

cam.close()
print("Finished. Signing out.")

