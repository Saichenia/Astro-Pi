import ephem
import datetime
from time import sleep

from picamera import PiCamera

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
a = [80, 80, 50]
g = [80, 56, 39]
b = [24, 64, 64]

img1 = [
    o,g,g,g,g,o,o,o,
    g,g,b,b,g,g,o,o,
    g,b,b,b,b,g,o,o,
    g,b,b,b,b,g,o,o,
    g,g,b,b,g,g,o,o,
    o,g,g,g,g,g,g,o,
    o,o,o,o,o,g,g,g,
    o,o,o,o,o,o,g,g,
    ]

img2 = [
    o,o,o,o,r,o,o,o,
    o,o,o,o,r,r,o,o,
    o,o,o,r,c,c,o,o,
    o,o,r,c,e,c,r,o,
    o,r,c,l,e,c,r,o,
    o,r,l,a,a,c,r,o,
    o,r,e,a,l,r,o,o,
    o,o,r,e,r,o,o,o,
    ]

#Variable that corresponds to the photo number
global photo_counter
photo_counter = 1

#Checker is 1 if in an area of interest and 0 otherwise
checker = 0

      
#Sets the logfile name and directory
logzero.logfile(dir_path+"/data01.csv")

# Sets the formatter
formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: \n%(message)s');
logzero.formatter(formatter)


#  
name = "ISS (ZARYA)"

line1 = "1 25544U 98067A   19042.02450189  .00001556  00000-0  31680-4 0  9994"

line2 = "2 25544  51.6415 268.6176 0005352  16.2049 127.1592 15.53252731155650"

iss = ephem.readtle(name, line1, line2)




# Initializes PiCamera and defines its resolution
cam = PiCamera()
cam.resolution = (2592,1944)


iss.compute()

def update_image(checker):

    # a list with all possible rotation values
    orientation = [0,90,270,180]
    if checker == 0:
        # picks one at random
        rotation = random.choice(orientation)
        # sets the rotation
        sh.set_rotation(rotation)
    
    elif checker == 1:
        # Resets the rotation
        sh.set_rotation(0)
        # Flickers the flame
        sh.flip_h()

def get_latlon(): # Function that assigns the EXIF data to the photos taken
    
    # Gets the lat/long values from ephem
    iss.compute() 

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
    
    return(str(lat_value), str(long_value))


def get_photo():  # Function that takes photos and saves the Latitude and Longitude information on the data01.csv file 
    global photo_counter
    try:
         
        # Gets Latitude and Longitude EXIF data
        lat, lon = get_latlon()
        
        # Saves the data to the .csv file
        logging.info("%s,%s,%s", "image_"+ str(photo_counter).zfill(5), lat, lon)
        
        
        #Takes the photo
        cam.capture(dir_path+"/image_"+ str(photo_counter).zfill(5)+".jpg")
        photo_counter += 1
                    
    except Exception as e:
       #Saves error information to the .csv file 
       logger.error("An error occurred: " + str(e))
       pass
                    
# Creates a datetime variable to store the start time
start_time = datetime.datetime.now()

# Creates a datetime variable to store the current time
now_time = datetime.datetime.now()
# Sets Sense Hat default image to img1 (Search Mode)
sh.set_pixels(img1)

#checks if the program is in condition to run, and repeats a cycle that checks whether a photo should be taken 
while ((now_time < start_time + datetime.timedelta(minutes = 175)) and (photo_counter < 980) and (cpu.temperature < 75)):
    
    # current location of the ISS
    iss.compute()
    latrad = float("%f" % (iss.sublat))
    longrad = float("%f" % (iss.sublong))
    
    # We only want photos of certain places, so we defined some "rectangles" of minimum and maximum longitude and latitude
    #The zones of interest are divided in 3 blocks so the condition checking is more efficient
    
    americas = [
        (-1.35616 < longrad < -0.85519 and 0.073888 < latrad < 0.207737), #Venezuela
        (-2.004805 < longrad < -1.649931 and 0.288185< latrad < 0.558909),#Mexico
        (-2.214386 < longrad < -1.338161 and 0.52683 < latrad < 0.7972), #USA
        (-1.652101< longrad < -1.1442582 and 0.138603 < latrad < 0.379025),# Guatmala
        (-1.333111< longrad < -0.588619 and -0.590034< latrad < -0.007321)]#Brazil
    
    central = [
        (-0.171779 < longrad < 0.052704 and 0.61969 < latrad < 0.767325),#Iberia
        (-0.314378 < longrad < 0.75828 and 0.052333 < latrad < 0.280259),# Top Africa
        (0.216237 < longrad < 0.741116 and -0.614419 < latrad < -0.010986),#Mid Africa
        (0.057017 < longrad < 0.537736 and 0.639903 < latrad < 0.814486)]#Mediterranean
    
    oceasia = [
        (1.184735 < longrad < 1.509269 and 0.088706 < latrad < 0.613406),#India
        (1.604362 < longrad < 2.185311 and 0.146123 < latrad < 0.601894),#Myanmar
        (2.069162 < longrad < 2.423922 and 0.571374 < latrad < 0.844868),#Korea
        (2.111045 < longrad < 2.399285 and -0.413486 < latrad < -0.195962),#Top Australia
        (1.997895 < longrad < 2.176838 and -0.490407 < latrad < -0.61162),# Southwest Australia
        (2.377186 < longrad < 2.688272 and -0.675403 < latrad < -0.421843)]#Southeast Australia
    
    #print("Americas: ", americas)
    #print("Central: ", central)
    #print("Oceasia: ", oceasia)
    #print(latrad, longrad) 
    

#the first conditions check in which block the ISS should be, so it doesn't have the conditions of the other zones

    if longrad < -0.442:
        if any(americas):  # if any of the conditions in the americas list is fullfilled, proceed 
            get_photo() #takes a photograph
            sh.set_pixels(img2) #if we're in a zone of interest, select the flame image
            checker = 1  # changes the checker to be different from when we're not in a zone of interest
    
    elif -0.442 < longrad < 1.058:
        if any(central):
            get_photo()
            sh.set_pixels(img2)
            checker = 1
            
    elif longrad > 1.058:
        if any(oceasia):
            get_photo()
            sh.set_pixels(img2)
            checker = 1
            
    # if the ISS is not over a zone of interest, the magnifying glass image is selected 
    if checker == 0:
       sh.set_pixels(img1)
        
    sleep(2) #two second pause
    
    # the selected image is displayed
    update_image(checker)

# update the current time
    now_time = datetime.datetime.now()
    
#checks the temperature 
    cpu = CPUTemperature()
    #print("Temp: ", cpu.temperature)   
    
#resets the checker value    
    checker = 0
    
    now_time = datetime.datetime.now()

cam.close() 
sh.clear()
#print("Finished. Signing out.")
