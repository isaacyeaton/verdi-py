# Isaac Yeaton
# Mar 21, 2012
#
# Scan the Verdi etalon temperature over a range of temperatures
# and recored photodiode voltages.  Do this my applying a step
# input to the laser and then querying the etalon temperature
# and then quickly recording one photodiode voltage from each
# channel.
#
# How to read the data in:
# data = np.genfromtxt(fname, skip_header=1)

import u3
import numpy as np
import Verdi18 as Verdi
import time
import sys

fname = sys.argv[1]
stopTemp = 60

# open the laser
openLaser = True
if openLaser:
    laser = Verdi.verdiLaser('/dev/ttyUSB0')
    time.sleep(.5)

# open the LabJack
d = u3.U3()

## open the file and begin recording data
with open(fname, 'w') as fid:

    # print welcome message
    print("Saving to file:  {0}\n".format(fname))

    # write the header to the file
    fid.write("%15s %15s %15s\n" % ('get T', 'ch0', 'ch1'))

    # record data until exceed stop temp
    actualTemp = 30
    laser.setEtalonTemp(stopTemp)
    time.sleep(0.2)
    while actualTemp <= stopTemp - 1:

        # record the etalon temperature
        actualTemp = laser.getEtalonTemp()

        # write to the file
        fid.write("%15s %15s %15s\n" % (actualTemp, d.getAIN(2), d.getAIN(3)))

        # print the measured temperature
        print("Etalon get temp: {:.2f}".format(actualTemp))
        time.sleep(0.070)

## shut the measurement down
# close the LabJack
d.close()

# close the laser port
laser.portClose()
