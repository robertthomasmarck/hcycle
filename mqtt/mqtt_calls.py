import json

import paths
from mqtt.mqtt_request_controller import MQTTRequestsController


class MQTTCalls(MQTTRequestsController):

    def get_driver_states(self):
        row = {}
        body = {"d1": ["lvl", "tlvl", "sv", "st", "dv", "i", "c"]}
        for name, driver in self.drivers.items():
            details = self.request(call="GET",
                                   command="state",
                                   body=body,
                                   device_id=driver["driverHardwareId"],
                                   gateway_id=driver["gatewayHardwareId"],
                                   target='nodes')["details"]["d1"]
            for d, id in details.items():
                row[f"{name} {d}"] = id
        return row

