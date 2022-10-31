import json
import os
import time
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

import paths


def infoCallback(client, userdata, message):
    print("\n-msg recieved-\n")
    temp = message.payload
    response.append(temp)


def commandCallback(client, userdata, message):
    print("\n-cmd recieved-\n")
    print(json.dumps(json.loads(message.payload.decode('utf-8')), indent=4))
    print("--------------\n")


def aws_config():
    config_file = paths.get_paths("api_utils/aws_keys.json")
    config = open(config_file)
    data = json.load(config)
    return data


def waitforresponse(timeout, seq):
    x = 0
    while x < timeout:
        for msg in response:
            if seq in str(msg):
                jsonmsg = json.loads(msg.decode('utf-8'))
                return jsonmsg
        time.sleep(1)
        x += 1
    return -1


class MQTTController:

    def __init__(self, env, site_id, driver_map):
        self.cfg = aws_config()
        self.siteid = site_id
        self.env = env
        self.drivers = driver_map
        self.myMQTTClient = self.get_mqtt_connection()

    def get_mqtt_connection(self):
        # Creates a certificate based connection
        MQTTClient = AWSIoTMQTTClient("qa-automation", useWebsocket=True)
        MQTTClient.configureEndpoint(self.cfg[self.env]['endpoint'], 443)
        MQTTClient.configureCredentials(paths.get_paths("api_utils/aws_cert.pem"))
        # Infinite offline Publish queueing
        MQTTClient.configureOfflinePublishQueueing(-1)
        MQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        MQTTClient.configureConnectDisconnectTimeout(60)  # 60 sec
        MQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        # AWS IoT MQTT Client
        MQTTClient.configureIAMCredentials(self.cfg[self.env]['key'], self.cfg[self.env]['secret'])

        return MQTTClient

    def sync_request(self, payload, timeout=30):
        global response
        response = []
        try:
            self.myMQTTClient.connect()
        except:
            # time.sleep(30)
            self.myMQTTClient = self.get_mqtt_connection()
            self.myMQTTClient.connect()
        command = commandCallback
        self.myMQTTClient.subscribe('command/' + self.siteid, 1, command)
        info = infoCallback
        self.myMQTTClient.subscribe('info/' + self.siteid, 1, info)
        self.myMQTTClient.publish('command/' + self.siteid, json.dumps(payload), 1)
        request_id = payload['hdr']['seq']
        response = waitforresponse(timeout, request_id)

        self.clean()
        return response

    def clean(self):
        self.myMQTTClient.unsubscribe('info/' + self.siteid)
        self.myMQTTClient.unsubscribe('command/' + self.siteid)
        self.myMQTTClient.disconnect()
        return response

    @staticmethod
    def get_request_id():
        """
        Gets the timestamp for the start of a test as a digit string.
        The digits are used as a unique identifier for the test requests.
        """
        now = datetime.now()
        return now.strftime("%Y%m%d%S%f")
