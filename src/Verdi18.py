#! /usr/bin/python
# Verdi.py
#
# A library of Verdi commands to use with Python.  This relies on the
# PySerial modules.
#
# Isaac Yeaton
# Oct 22, 2011

import time
import serial

ON  = 1
OFF = 0
EOL = "\r\n"

class verdiLaser:
    #TODO: add documentation here
    """
    """
    
    def __init__(self, ioport='/dev/ttyUSB0'):
        """ Initalize the verdieLaser object.
            
            It will grab the first available I/O serial port, as is
            consistent with the PySerial modules.
        """
        # configure the port
        self.port = serial.Serial()
        self.port.setBaudrate(38400)
        self.port.setPort(ioport)
        self.port.setByteSize(8)
        self.port.setStopbits(1)
        self.port.setTimeout(2)
        self.port.setParity(serial.PARITY_NONE)
        
        # try opening the port
        self.portOK = False
        try:
            self.port.open()
            self.portOK = True
        except:
            print("The Verdi port did not open")
            print("Please check the connection")
            self.port.close()
            traceback.print_exc()  # print the exception
        
        # put laser in a consistent mode
        if self.portOK:
            self.port.write("E = 0%s" % EOL)    # echo off
            time.sleep(0.1)
            self.port.write("> = 0%s" % EOL)    # prompt off
            time.sleep(0.1)
                
            # clear input buffer so ready to talk to laser
            self.port.flushInput()
    
    def portPause(self, pause=.1):
        """ Pause before querying the port.
        """
        if self.portOK:
            time.sleep(pause)
    
    def portClear(self):
        """ Clear the input buffer.  The Verdi sends back an EOL
            if it received the message successfully.  They can
            build up in the buffer, so when you read from the port,
            you get this information, and now what you wanted.  It is
            also good to not oversample the port.
        """
        if self.portOK:
            self.port.flushInput()
    
    def portClose(self):
        """ Close the port.
        """
        if self.portOK:
            self.port.close()
            self.portPause()
            self.portOK = False
    
    def portOpen(self):
        """ Open the port.
        """
        self.portOK = False
        try:
            self.port.open()
            self.portOK = True
        except:
            print("The Verdi port did not open")
            print("Please check the connection")
            self.port.close()
            traceback.print_exc()  # print the exception
    
    def laserHome(self):
        """ Set the laser in a safe state for work.  This means that
            power as low as it will go (0.01 W) and the shutter closed.
        """
        if self.portOK:
            self.setShutter(0)
            self.setPower(0.01)
    
    def inWaiting(self):
        """ See how many characters are input buffer.
        """
        if self.portOK:
            return self.port.inWaiting()
    
    #####
    def laserQuery(self, cmd):
        """ Submit a query to the Veri and return the value.
            It will try to get the return value 11 times, and
            if it fails, it will return the string '-999'.  If the
            port has an error (portOK != True), it returns '-888'
        """
        if self.portOK:
            cnt = 0
            while True:
                self.portClear()
                self.port.write("?%s%s" % (cmd, EOL))
                self.portPause()
                returnVal = self.port.readline()[:-2]
                cnt += 1
                if returnVal[0].isdigit():
                  # first letter is a digit, readline successful
                  break
                elif cnt > 10:
                  returnVal = '-999'
            return returnVal
        else:
            return '-888'
    #####
    
    def shutdown(self):
        """ Shutdown the laser and port.
        """
        if self.portOK:
            self.portClear()
            self.setShutter(0)
            self.portPause()
            self.setPower(0.01)
            self.portPause()
            self.port.close()
            self.portOK = False
    
    def standbyON(self):
        """ Put the laser in STANDBY.
        """
        if self.portOK:
            self.port.write("L = 0%s" % EOL)
    
    def enableON(self):
        """ ENABLE the laser.
        """
        if self.portOK:
            self.port.write("L = 1%s" % EOL)
        
    def getShutter(self):
        """ Check the state of the shutter.
            returns an int: 0 - shutter is closed; 1 - shutter is open
        """
        return int(self.laserQuery('S'))
    
    def setShutter(self, state):
        """ Set the shutter state.
        """
        if self.portOK:
            if state in (1, 0, "ON", "OFF"):
                self.port.write("S = %s%s" % (state, EOL))
    
    def getPower(self):
        """ Check the laser output power.
        """
        return float(self.laserQuery('P'))
    
    def setPower(self, power):
        """ Set the laser output power.
        """
        if self.portOK:
            if power <= 0:
                power = 0.01
            elif power >= 18:
                power = 18
            self.port.write("P = %s%s" % (power, EOL))
      
    def getDiodeCurrent(self):
        """ Returns the measured diode current, as a float.
        """
        return float(self.laserQuery('C'))
    
    def getLaserDiodeCurrent(self):
        """ Returns the measured laser diode current.
        """
        return float(self.laserQuery('D1C'))
    
    def getEtalonSetTemp(self):
        """ Returns the set Etalon temperature.
        """
        return float(self.laserQuery('EST'))
    
    def getEtalonTemp(self):
        """ Returns the measured Etalon temperature.
        """
        return float(self.laserQuery('ET'))
    
    def setEtalonTemp(self, etalonTemp):
        """ Set the Etalon tempature.
            Range is from 40 - 60 degC
        """
        if self.portOK:
            if etalonTemp > 60:  #TODO: find out an appropriate Etalon range
                etalonTemp = 60
            elif etalonTemp < 30:
                etalonTemp = 30
            self.port.write("ET = %s%s" % (etalonTemp, EOL))
    
    def getLBOSetTemp(self):
        """ Returns the LBO set temperature.
            RETURN: float nnn.nn degC
        """
        return float(self.laserQuery('LBOST'))
        
    def getLBOTemp(self):
        """ Returns the measured LBO temperature.
            RETURN: float nnn.nn degC
        """
        return float(self.laserQuery('LBOT'))
    
    def getVanadateSetTemp(self):
        """ Returns the Vanadate set temperature.
            RETURN: float nn.nn degC
        """
        return float(self.laserQuery('VST'))
    
    def getVanadateTemp(self):
        """ Returns the measured Vanadate set temperature.
            RETURN: float nn.nn degC
        """
        return float(self.laserQuery('VT'))
    
    def setVanadateTemp(self, vanadateTemp):
        """ Set the Vanadate temperature.
            INPUT: float, nn.nn degC
            The range has been limited from 20 - 45 degC
        """
        if self.portOK:
            if vanadateTemp > 45:
                vanadateTemp = 45.00
            elif vanadateTemp < 20:
                vanadateTemp = 20.00
            self.port.write("VT = %s%s" % (vanadateTemp, EOL))
    
    
    
        

# self-test
if __name__ == 'UPDATE_ME':
    laser = verdiLaser('/dev/ttyUSB0', 0)
    laser.enable()
    laser.setShutter(OFF)
    laser.setPower(0.02)
    
    print("")
    print("Self-test using the Verdi module")
    print("")
    print("SHUTTER should be closed")
    print("POWER should be 0.02 W")
    print("")
    print("Shutter test 1: %5s" % laser.shutter())
    print("Shutter test 2: %5s" % laser.getShutter())
    print("Power test 1: %5s" % laser.power())
    print("Power test 2: %5s" % laser.getPower())
    print("")
    print("End of self test.  Closing the port.")
    
    laser.shutdown()

