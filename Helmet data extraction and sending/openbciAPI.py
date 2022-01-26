import argparse
import time
from datetime import datetime
from datetime import timedelta
import numpy as np
import json
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import jsonpickle
import requests



#!/home/pi/openbci_scripts/main_script/bcivenv/bin/python
ipaddress = "192.168.0.236"

class DataPackage:
    def __init__(self, helmName):
        self.HelmName = helmName
    HelmName = None
    Channels = None
    TimeStamp = None


board_id = brainflow.BoardIds.CYTON_BOARD
packageCounter = 0 #ofwel counter in datapackage ofwel datetime, counter is meer performant
helmName = "helm3"
frequency = 250
desiredDPtimeWindow = 1
sampleNumbers = frequency*desiredDPtimeWindow
packetBuffer = [None]*10

def Init():
    input_params = BrainFlowInputParams()
    input_params.serial_port = "/dev/ttyUSB1"
    # input_params.serial_port = "COM5"
    board_shim = BoardShim(board_id, input_params)
    board_shim.prepare_session()
    board_shim.start_stream()
    return board_shim


while True:
    try:
        board_shim = Init()
        timestamp = datetime.now()
        time.sleep(1)
        packetCounter = 0
        unprocessed_data = board_shim.get_board_data()
        while True:
            if len(unprocessed_data[0]) > sampleNumbers:
                dP = DataPackage(helmName)
                dataPackageData = unprocessed_data[:, 0:sampleNumbers]
                unprocessed_data = unprocessed_data[:, sampleNumbers:]
                dP.Channels = dataPackageData.tolist()
                dP.TimeStamp = timestamp + timedelta(0, packetCounter*sampleNumbers/250)
                dP.TimeStamp = dP.TimeStamp.isoformat()
                if len(dP.Channels[0]) != sampleNumbers:
                    print("Datapackage was not %i samples (%i freq, %i desiredtimewindow)", (sampleNumbers, frequency, desiredDPtimeWindow))
                else:
                    r = requests.post('http://%s:3000/brains/postData' % ipaddress, json=dP.__dict__)
                    while r.text == 'false':
                        r = requests.post('http://%s:3000/brains/postData' % ipaddress, json=dP.__dict__)
                    packetCounter = packetCounter + 1
                    print(dP.TimeStamp)
                    print("package succesfully sent.")
            elif len(unprocessed_data[0]) == sampleNumbers:
                dP = DataPackage(helmName)
                dataPackageData = unprocessed_data
                unprocessed_data = board_shim.get_board_data()
                dP.Channels = dataPackageData.tolist()
                dP.TimeStamp = timestamp + timedelta(0, packetCounter*sampleNumbers/250)
                dP.TimeStamp = dP.TimeStamp.isoformat()


                if len(dP.Channels[0]) != sampleNumbers:
                    print("Datapackage was not %i samples (%i freq, %i desiredtimewindow)", (sampleNumbers, frequency, desiredDPtimeWindow))
                else:
                    r = requests.post('http://%s:3000/brains/postData' % ipaddress, json=dP.__dict__)
                    while r.text == 'false':
                        r = requests.post('http://%s:3000/brains/postData' % ipaddress, json=dP.__dict__)
                    packetCounter = packetCounter + 1
                    print("package succesfully sent.")
            elif len(unprocessed_data[0]) < sampleNumbers and len(unprocessed_data[0]) != sampleNumbers:
                print("waiting for more samples.")
                time.sleep(sampleNumbers/250*desiredDPtimeWindow * 0.8)
                newData = board_shim.get_board_data()
                if len(newData[0]) != 0:
                    unprocessed_data = np.concatenate((unprocessed_data, newData), axis=1)

            elif len(unprocessed_data[0]) == 0:
                unprocessed_data = board_shim.get_board_data()

    except:
        print("Something went wrong.")
        time.sleep(2)

