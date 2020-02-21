#!/usr/bin/env python3
import logging
import traceback
import serial
import serial.tools.list_ports
import time
import struct
from random import random

BAUD_RATE = 9600

START_BYTE = b'0'
END_BYTE = b'\n'

SERVER_RESPONSE_OK = b'1'
SERVER_RESPONSE_ERROR_WRONG_START_BYTE = b'2'
SERVER_RESPONSE_ERROR_UNKNOWN_OPTION = b'3'
SERVER_RESPONSE_ERROR_WRONG_END_BYTE = b'4'
SERVER_RESPONSE_ERROR_TOO_EARLY = b'5'
SERVER_RESPONSE_ERROR_ALREADY_RUNNING = b'6'
SERVER_RESPONSE_ERROR_ALREADY_STOPPED = b'7'

OPTION_GET_BME280_TEMP = b'a'
OPTION_GET_BME280_HUMID = b'b'
OPTION_GET_BME280_PRESSURE = b'c'

OPTION_GET_TEMP = b'a'
OPTION_GET_HUMID = b'b'
OPTION_GET_PRESSURE = b'c'
OPTION_PRESS_START_STOP = b'd'
OPTION_PRESS_SPEED_UP = b'e'
OPTION_PRESS_SPEED_DOWN = b'f'
OPTION_READ_VOLT = b'g'
OPTION_READ_CURRENT = b'h'
OPTION_GET_SPEED = b'i'
OPTION_PRESS_START = b'j'
OPTION_PRESS_STOP = b'k'

OK = 'OK'
READY = 'READY'
BUSY = 'BUSY'
ERROR_BUTTON_PRESS_EARLY = 'ERROR_BUTTON_PRESS_EARLY'
ERROR_ALREADY_RUNNING = 'ERROR_ALREADY_RUNNING'
ERROR_ALREADY_STOPPED = 'ERROR_ALREADY_STOPPED'

SERIAL_DEVICE =  '/dev/serial/by-id/usb-Arduino_LLC_Arduino_Nano_Every_A9873C9A51514743594A2020FF062C4A-if00'

def startShaker():
    try:
        response = getByteFromServer(OPTION_PRESS_START)
        if(response == SERVER_RESPONSE_OK):
            return OK
        elif(response == SERVER_RESPONSE_ERROR_TOO_EARLY):
            return ERROR_BUTTON_PRESS_EARLY
        elif(response == SERVER_RESPONSE_ERROR_ALREADY_RUNNING):
            return ERROR_ALREADY_RUNNING
        else:
            logging.error(ERROR_UNEXPECTED_RESPONSE_FROM_ARDUINO + " : " + str(response))
            return ERROR_UNEXPECTED_RESPONSE_FROM_ARDUINO
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(e)
        return ERROR_UNKNOWN

def stopShaker():
    try:
        response = getByteFromServer(OPTION_PRESS_STOP)
        if(response == SERVER_RESPONSE_OK):
            return OK
        elif(response == SERVER_RESPONSE_ERROR_TOO_EARLY):
            return ERROR_BUTTON_PRESS_EARLY
        elif(response == SERVER_RESPONSE_ERROR_ALREADY_STOPPED):
            return ERROR_ALREADY_STOPPED
        else:
            logging.error(ERROR_UNEXPECTED_RESPONSE_FROM_ARDUINO + " : " + str(response))
            return ERROR_UNEXPECTED_RESPONSE_FROM_ARDUINO
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(e)
        return ERROR_UNKNOWN

def getStatus():
    try:
        speed = getSpeed()
        if(speed == 0):
            return READY
        else:
            return BUSY
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(e)
        return ERROR_UNKNOWN
    

def getSpeed():
    speed = getFloatFromServer(OPTION_GET_SPEED)
    return speed

def getByteFromServer(option):
    response = getBytesFromServer(option, 1)
    return response

def getSerialConnection(serial_device, baud_rate, timeout=2):
    conn = serial.Serial(serial_device, baud_rate, timeout=2)
    while(conn.isOpen() == False):
        time.sleep(0.05)
    
    conn.reset_input_buffer()
    conn.reset_output_buffer()

    time.sleep(0.01)

    return conn

def getFloatFromServer(option):
    response = getBytesFromServer(option, 4)
    float_as_bytes = response

    # cast to float and return
    float_as_struct = struct.unpack('f', float_as_bytes)
    return float_as_struct[0]

def getBytesFromServer(option, nBytes):
    server = getSerialConnection(SERIAL_DEVICE, BAUD_RATE)
    # send message to server
    server.write(START_BYTE)
    server.write(option)
    server.write(END_BYTE)

    # read response
    start_byte = server.read(1)
    response_option = server.read(1)
    response = server.read(nBytes)
    endbyte = server.read(1)

    # check response
    if(start_byte != START_BYTE):
        raise Exception("Error wrong startbyte:" + str(start_byte) + " expected: " + str(START_BYTE))

    if(option != response_option):
        raise Exception("Error wrong response option:" + str(response_option) + " expected: " + str(option))

    if(endbyte != END_BYTE):
        raise Exception("Error wrong endbyte:" + str(endbyte) + " expected: " + str(START_BYTE))

    logging.info("response: " + str(response))
    return response

def printSpeed():
    speed = getFloatFromServer(OPTION_GET_SPEED)
    print("Speed = " + str(speed) + " rpm")


def testRun1():
    logging.info("getStatus():" + getStatus())
    logging.info("startShaker():" + startShaker())
    logging.info("getStatus():" + getStatus())
    logging.info("startShaker():" + startShaker())
    logging.info("sleep()")
    time.sleep(4)
    logging.info("getStatus():" + getStatus())
    logging.info("stopShaker():" + stopShaker())
    logging.info("getStatus():" + getStatus())

    for n in range(10):
        logging.info("getStatus():" + getStatus())
        logging.info("getSpeed():" + str(getSpeed()))
        logging.info("sleep(), n=" + str(n))
        time.sleep(1)


def testRun2():

        # Open named port at “19200,8,N,1”, Xs timeout:
    with serial.Serial(SERIAL_DEVICE, BAUD_RATE, timeout=2) as server:

        ## Read and discard what is in buffer
        #time.sleep(3)
        while(server.isOpen() == False):
            time.sleep(0.01)

        logging.info("Connected to Serial")

        server.reset_input_buffer()
        server.reset_output_buffer()

        # Serial seem to need a little time to get ready
        time.sleep(0.5)
        
        getByteFromServer(OPTION_PRESS_START)
        printSpeed()
        time.sleep(2)
        printSpeed()
        getByteFromServer(OPTION_PRESS_STOP)
        printSpeed()
        time.sleep(5)
        time.sleep(random())
        getByteFromServer(OPTION_PRESS_STOP)
        printSpeed()
        time.sleep(1)
        printSpeed()
        getByteFromServer(OPTION_PRESS_STOP)
    
        nLoop = 5
        while(nLoop > 0):

            try:
                # Get speed
                speed = getFloatFromServer(OPTION_GET_SPEED)
                print("Speed = " + str(speed) + " rpm")

            except Exception as e:
                print(traceback.format_exc())
                logging.error(e)
                time.sleep(1)
                server.reset_input_buffer()
                server.reset_output_buffer()

            time.sleep(1)
            nLoop -= 1



if __name__ == '__main__':
    #
    # Configure logging
    #
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

    testRun1()


