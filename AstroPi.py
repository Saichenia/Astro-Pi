import time
import ephem

n = 0.0 

name = "ISS (ZARYA)"
line1 = "1 25544U 98067A   18355.62429255  .00000834  00000-0  19892-4 0  9995"

line2 = "2 25544  51.6392 164.6201 0004717 167.6800 317.8237 15.54085122147663"

iss = ephem.readtle(name, line1, line2)

iss.compute()

print(iss.sublat, iss.sublong)
n = iss.sublat
print("%f" % (iss.sublat),"%f" %  n, ephem.degrees(n))

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
