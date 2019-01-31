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
r = [250,20,45]
e = [250, 205, 5]
l = [250, 130, 10]
c = [250, 80, 50]
a = [250,225,13]



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


longrad = 0
latrad = 0
global photo_counter
photo_counter = 0
       
       
# Set a logfile name
logzero.logfile(dir_path+"/data01.csv")

# Set a custom formatter
formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: \n%(message)s');
logzero.formatter(formatter)


n = 0.0 

name = "ISS (ZARYA)"

line1 = "1 25544U 98067A   19031.57359954  .00001065  00000-0  24060-4 0  9999"

line2 = "2 25544  51.6426 320.6439 0005003 336.8866  10.0660 15.53211219154026"

iss = ephem.readtle(name, line1, line2)




####
cam = PiCamera()
cam.resolution = (2592,1944)
iss.compute()
print(iss.sublat, iss.sublong)
n = iss.sublat
print("%f" % (iss.sublat),"%f" %  n, ephem.degrees(n))


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
sh.set_pixels(img1)
#cam.start_preview()
#cam.start_preview()
while (now_time < start_time + datetime.timedelta(minutes=20)):
    
    iss.compute()
    latrad = float("%f" % (iss.sublat))
    longrad = float("%f" % (iss.sublong))
    
    americas = [
        (-1.345255 < longrad < -0.995251 and 0.073888 < latrad < 0,234312), 
        (-2.004805 < longrad < -1.346902 and 0.108598 < latrad < 0.558909),
        (-2.214386 < longrad < -1.877563 and 0.578183 < latrad < 0.7972)]
    
    central = [
        (-0.171779 < longrad < 0.052704 and 0.052704 < latrad < 0.767325),
        (0.280024 < longrad < 0.776268 and -0.239076 < latrad < 0.328873),
        (0.216237 < longrad < 0.657971 and -0.239076 < latrad < -0.010986),
        (0.307307 < longrad < 0.527298 and -0.613214 < latrad < -0.551439)]
    
    oceasia = [
        (1.139716 < longrad < 1.509269 and 0.088706 < latrad < 0.613406),
        (1.604362 < longrad < 2.135446 and 0.00472 < latrad < 0.601894),
        (2.069162 < longrad < 2.379131 and 0.571374 < latrad < 0.844868),
        (2.068996 < longrad < 2.399285 and -0.413486 < latrad < -0.195962),
        (1.997895 < longrad < 2.629614 and -0.665449 < latrad < -0.503788)
        ]
    print("Americas: ", americas)
    print("Central: ", central)
    print("Oceasia: ", Oceasia)
    print(latrad, longrad)   
    if longrad < -0.442:
        if any(americas):
            get_photo()
    
    elif -0.442 < longrad < 1.058:
        if any(central):
            get_photo()
    
    elif longrad > 1.058:
        if any(oceasia):
            get_photo()

    sleep(2)

# update the current time
    now_time = datetime.datetime.now()

    cpu = CPUTemperature()
    print("Temp: ", cpu.temperature)
    print("Time: ", time.time()-start_time2)

cam.close()



"""
if ephem.degrees(iss.sublat) < -20:
    print("WTF")





def iszoi(currloc, zoi):

    for coord in zoi:
        latmin = coord[0] - 1.5
        latmax = coord[0] + 1.5
        longmin = coord[1] - 1.5
        longmax = coord[1] + 1.5
    
        if(latmin <= currloc[0]) and (latmax >= currloc[0]) and (longmin <= currloc[1]) and (longmax >= currloc[1]):
            return True

print("Process = start")    

while True:
    print("Inicializing Zone Check")
    latrad = "%f" % (iss.sublat)
    longrad = "%f" % (iss.sublong)
    currloc = [latrad, longrad]

    if iszoi(currloc, zoi):
        printf("Zone accept")
    else:
        print("Zone reject")

    time.sleep(3)
"""

