# Isaac Yeaton
# Mar 21, 2012
#
# Do a slow etalon scan of the V18 laser
#
# Required arguments - filename to save to, as a string

import u3
import numpy as np
import Verdi18 as Verdi
import time
import sys

fname = sys.argv[1]
openLaser = True
startTemp = 30
stopTemp = 60
dT = 0.05       # temperature increment

if openLaser:
    laser = Verdi.verdiLaser('/dev/ttyUSB0')
    time.sleep(.5)

d = u3.U3()

with open(fname, 'w') as fid:
    print("Saving to file:  {0}\n".format(fname))
    fid.write("%15s %15s %15s %15s\n" %
        ('set T', 'get T', 'pd0', 'pd1'))

    for ETemp in np.arange(startTemp, stopTemp + dT, dT):
        ain0 = []
        ain1 = []
        cnt = 0
        print("Etalon set temp: {:.2f}".format(ETemp))

        if openLaser:
            laser.setEtalonTemp(ETemp)
            time.sleep(.2)  # increased from 0.2 seconds

        #print("Reading in data")
        while cnt < 150:
            cnt += 1
            tmp0 = d.getAIN(2)
            tmp1 = d.getAIN(3)
            ain0.append(tmp0)
            ain1.append(tmp1)

        actualTemp = laser.getEtalonTemp()
        print("Etalon get temp: {:.2f}".format(actualTemp))
        

        ain0 = np.array(ain0)
        ain1 = np.array(ain1)

        fid.write("%15s %15s %15s %15s\n" %
            (ETemp, actualTemp, ain0.mean(), ain1.mean()))
        print('Ch0:  {0}   ~~  Ch1:  {1}'.format(ain0.mean(), ain1.mean()))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')

# close the LabJack
d.close()

# how to read the data in
#data = np.genfromtxt(fname, skiprows=1)
