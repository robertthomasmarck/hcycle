from mqtt.mqtt_controller import MQTTController


class MQTTRequestsController(MQTTController):

    def payload_gen(self, method, command, body, device_id, gatewayId, target=None, version=1):
        """
        We're constructing the payload here.
        Every request is roughly the same with some variation.
        :param method: Api request type - GET, PUT, PULL, DELETE
        :param command: First part of the message string
        :param body: The body or the message
        :param target: Can be nodes, nodeconfig, or None.
        :param device: Which device do we want to talk to. Usually the driver, but can be gateway.
        :param version: 1. We don't have a reason for a different version yet.
        :return: The completed request object string.
        """

        if target is None:
            msg = command
        else:
            target_driver = target + "/" + device_id
            if command is not None:
                msg = target_driver + "/" + command
            else:
                msg = target_driver

        return {"hdr": {
                    "to": gatewayId,
                    "sender": "automatedTestingDriver",
                    "seq": self.get_request_id(),
                    "msg_type": msg,
                    "version": version,
                    "method": method
                },
            "body": body}

    def request(self, call, command, body, device_id, gateway_id, target):
        """
        Generic method for sending requests to devices on a Halio site.
        :param call: GET PUT POST DELETE
        :param id: Hardware id for driver or gateway
        :param body: Json or dict object sent as part of the request.
        :param command:
        :param type: Device type can be gateway or driver.
        :param target: Can be nodes or nodeConfig
        :return: The response from the AWS server.
        """
        if body is None:
            body = {}

        #Builds the body for the request.
        payload = self.payload_gen(call, command, body, device_id, gateway_id, target)
        response_body = self.sync_request(payload)["body"]
        # status_error = f"Unexpected status - Expected status: {expected_status}, Actual: {response_body['status_code']}"
        # if type(expected_status) is int: expected_status = [expected_status]
        # assert response_body["status_code"] in expected_status, status_error

        return response_body