

###############################################################################################################
## This program was made in the scope of ESA's AstroPi competition and its objective is to take photographs  ##
## of specific zones of Earth's surface that are likely to contain burned areas.                             ##
##                                                                                                           ##
## In order to  accurately compute ISS's position, the lines provided to ephem need to be updated to the     ##
## latest information provided.                                                                              ##
##                                                                                                           ##
## Several zones of interest are defined below by latitude and longitude intervals. When the ISS is above    ##
## one of these zones, a photo is taken and the information regarding the position is saved in an csv file   ##
## and in EXIF data. Besides that, the display image is also changed to signal that it is taking photos.     ##
##                                                                                                           ##
## A 2 second sleep in between photos was established in order to recalibrate the PiCamera's sensors.        ##
## We also keep track of CPU Temperature, running time and occupied memory in order to not exceed the amount ##
## stipulated by the competition.                                                                            ##
##                                                                                                           ##
## The resulting photographs will be later analysed in a seperate set of programs.                           ##
##                                                                                                           ##
## - Firewatchers                                                                                            ##
###############################################################################################################



import ephem
import datetime
from time import sleep
import time

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

# Define the display images (Magnifying glass when in search mode and Flame for capture mode)
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

# Initializing Latitude and Longitude variables
longrad = 0
latrad = 0


# Variable that corresponds to the photo number
global photo_counter
photo_counter = 1

# Occupied memory
global occmem
occmem = 0

# Checker is 1 if in a zone of interest and 0 otherwise
checker = 0


# Checks the temperature of the cpu
cpu = CPUTemperature()


# Sets the logfile name and directory
logzero.logfile(dir_path+"/data01.csv", disableStderrLogger = True)

# Sets the formatter
formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: \n%(message)s');
logzero.formatter(formatter)


# Retrieves the information necessary to compute the ISS's position
name = "ISS (ZARYA)"

# These lines must be updated with the most recent information
line1 = "1 25544U 98067A   19044.20416762  .00000480  00000-0  14912-4 0  9999"

line2 = "2 25544  51.6411 257.7655 0005559  22.4588  77.0361 15.53254839155998"

iss = ephem.readtle(name, line1, line2)



# Initializes PiCamera and defines its resolution
cam = PiCamera()
cam.resolution = (2592,1944)

iss.compute()

def update_image(checker):

    # A list with all possible rotation values
    orientation = [0,90,270,180]
    
    if checker == 0:
        # Picks one at random
        rotation = random.choice(orientation)
        
        # Sets the rotation
        sh.set_rotation(rotation)

    elif checker == 1:
        # Resets the rotation
        sh.set_rotation(0)
        
        # Flips the flame
        sh.flip_h()

def get_latlon(): # Function that assigns the EXIF data to the photos taken

    # Gets the lat/long values from ephem
    iss.compute()

    long_value = [float(i) for i in str(iss.sublong).split(":")]

    if long_value[0] < 0:

        cam.exif_tags['GPS.GPSLongitudeRef'] = "W"

    else:
        cam.exif_tags['GPS.GPSLongitudeRef'] = "E"

    cam.exif_tags['GPS.GPSLongitude'] = '%d/1,%d/1,%d/10' % (abs(long_value[0]), long_value[1], long_value[2]*10)

    lat_value = [float(i) for i in str(iss.sublat).split(":")]

    if lat_value[0] < 0:

        cam.exif_tags['GPS.GPSLatitudeRef'] = "S"

    else:
        cam.exif_tags['GPS.GPSLatitudeRef'] = "N"

    cam.exif_tags['GPS.GPSLatitude'] = '%d/1,%d/1,%d/10' % (abs(lat_value[0]), lat_value[1], lat_value[2]*10)

    return(str(lat_value), str(long_value))


def get_photo():  # Function that takes photos and saves the Latitude and Longitude information on the data01.csv file
    global photo_counter
    global occmem

    try:

       # Gets Latitude and Longitude EXIF data
    	lat, lon = get_latlon()

    	imagefile = "/image_"+str(photo_counter).zfill(5)+".jpg"

       # Saves the data to the .csv file
    	logger.info("%s,%s,%s", imagefile, lat, lon)

       # Takes the photo
    	cam.capture(dir_path+imagefile)

       # Adds the size  of the photo to the  occupied  memory (in kbytes)

    	occmem += (os.stat(dir_path+imagefile).st_size)/1024

    	photo_counter += 1

    except Exception as e:
       # Saves error information to the .csv file
    	logger.error("An error occurred: " + str(e))
    	pass

# Creates a datetime variable to store the start time
start_time = datetime.datetime.now()

# Creates a datetime variable to store the current time
now_time = datetime.datetime.now()

# Sets Sense Hat default image to img1 (Search Mode)
sh.set_pixels(img1)

# Checks if the program is in condition to run, and repeats a cycle that checks whether a photo should be taken
while ((now_time < start_time + datetime.timedelta(minutes = 177)) and (occmem < 3060000) and (cpu.temperature < 75)):

    # Computes the current location of the ISS
    iss.compute()

    latrad = float("%f" % (iss.sublat))
    longrad = float("%f" % (iss.sublong))

    # We only want photos of certain places, so we defined some "rectangles" of minimum and maximum longitude and latitude
    # The zones of interest are divided in 3 blocks so the condition checking is more efficient

    americas = [
        (-1.35616 < longrad < -0.85519 and 0.073888 < latrad < 0.207737), #Venezuela
        (-2.004805 < longrad < -1.649931 and 0.288185< latrad < 0.558909), #Mexico
        (-2.214386 < longrad < -1.338161 and 0.52683 < latrad < 0.7972), #USA
        (-1.652101< longrad < -1.1442582 and 0.138603 < latrad < 0.379025), #Guatmala
        (-1.333111< longrad < -0.588619 and -0.590034< latrad < -0.007321)] #Brazil

    central = [
        (-0.171779 < longrad < 0.052704 and 0.61969 < latrad < 0.767325), #Iberia
        (-0.314378 < longrad < 0.75828 and 0.052333 < latrad < 0.280259), #Top Africa
        (0.216237 < longrad < 0.741116 and -0.614419 < latrad < -0.010986), #Mid Africa
        (0.057017 < longrad < 0.537736 and 0.639903 < latrad < 0.814486)] #Mediterranean

    oceasia = [
        (1.184735 < longrad < 1.509269 and 0.088706 < latrad < 0.613406), #India
        (1.604362 < longrad < 2.185311 and 0.146123 < latrad < 0.601894), #Myanmar
        (2.069162 < longrad < 2.423922 and 0.571374 < latrad < 0.844868), #Korea
        (2.111045 < longrad < 2.399285 and -0.413486 < latrad < -0.195962), #Top Australia
        (1.997895 < longrad < 2.176838 and -0.490407 < latrad < -0.61162), #Southwest Australia
        (2.377186 < longrad < 2.688272 and -0.675403 < latrad < -0.421843)] #Southeast Australia


# These first conditions puts the ISS in one of three longitude sectors, so we dont need to check too many conditions

    if longrad < -0.442:
       	if any(americas):  # If any of the conditions in the americas list is fulfilled, it proceeds to take a photo
            get_photo() # Takes a photograph
            sh.set_pixels(img2) # If we're in a zone of interest, selects the Flame image
            checker = 1  # Changes the checker value to signal that we are in a zone of interest

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

    # If the ISS is not over a zone of interest, the Magnifying glass image is selected
    if checker == 0:
       sh.set_pixels(img1)
       
    # Two second pause in order to recalibrate the camera sensors
    sleep(2)

    # The display image is updated
    update_image(checker)


    # Checks the new CPU temperature
    cpu = CPUTemperature()

    # Resets the checker value
    checker = 0

    # Updates the current time
    now_time = datetime.datetime.now()

cam.close()
sh.clear()

