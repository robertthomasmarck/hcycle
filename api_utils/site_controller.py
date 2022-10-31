import json
from datetime import datetime

import click
from requests import api

from api_utils.api_client_config import ApiCliConfig

request_config = ApiCliConfig()


class SiteController:
    def __init__(self, environment, site_name):
        self.env = environment
        request_config.set_request_config(self.env)
        self.url = request_config.server
        self.base_url = f"{self.url}/v3/sites/"
        self.site_list = self.get_sites()
        self.site_name = site_name
        self.site_id = self.get_site_id_by_name(site_name)
        self.gateways = self.get_gateways()
        self.driver_list = self.get_drivers()

    def make_target_url(self, target):
        url = self.base_url + self.site_id + "/" + target
        return url

    def get_sites(self):
        response = api.get(self.base_url, headers=request_config.headers).json()
        sites_raw = response['results']
        sites_raw.sort(key=lambda x: x["name"])
        return sites_raw

    def get_site_id_by_name(self, name):
        site_id = ""
        for site_raw in self.site_list:
            if site_raw['name'] == name:
                site_id = site_raw['id']
        if site_id == "":
            raise NameError("Site does not exist, check spelling.")
        else:
            return site_id

    # Gateways

    def get_gateways(self, echo=False):
        url = self.make_target_url(target='gateways')
        response = api.get(url, headers=request_config.headers).json()
        gateways_raw = response['results']
        gateways_raw.sort(key=lambda x: x["name"])
        gateway_dict = {}
        for gwy in gateways_raw:
            if "hardwareId" in gwy:
                gateway_dict[gwy['name']] = {"hardwareId": gwy['hardwareId'], "id": gwy['id'], "nodeId": gwy["nodeId"]}
            if echo: click.echo(
                f"{gwy['name']} - Cloud Id: {gwy['nodeId']}  Hardward Id: {gwy['parts'][0]['hardwareId']}")
        return gateway_dict

    def get_gateway_id_by_name(self, gateway_name):
        return self.gateways[gateway_name]

    # Drivers

    def get_drivers(self):
        driver_dict = {}
        for gwy_id in self.gateways.values():
            url = self.make_target_url(f'gateways/{gwy_id}/nodes')
            raw_node_response = api.get(url, headers=request_config.headers).json()
            for raw_node in raw_node_response['results']:
                if raw_node['type'] == 'ecdriver':
                    driver_dict[raw_node['name']] = raw_node['nodeId']
        return driver_dict

    def get_driver_id_by_name(self, driver_name):
        if driver_name in self.driver_list:
            return self.driver_list[driver_name]
        else:
            return None

    def build_driver_map(self):
        """
        This is hacky and stupid. The gateways/[gatewayId]/nodes endpoint does not work.
        So I can put anything in as the gateway Id and it will return all nodes for the site.
        :return:
        """
        driver_map = {}
        url = self.make_target_url(target=f'gateways/123/nodes')
        node_list = api.get(url, headers=request_config.headers).json()['results']
        for gwy, gwy_ids in self.gateways.items():
            for node in node_list:
                if gwy_ids['nodeId'] == node['gatewayId'] and node['type'] == 'ecdriver':
                    driver_map[node['name']] = {'gatewayCloudId': gwy_ids['id'],
                                                'gatewayHardwareId': gwy_ids['hardwareId'],
                                                'driverHardwareId': node['nodeId'],
                                                'driverCloudId': node['id']
                                                }
        return driver_map

    # Group Calls

    def get_group_info(self, name):
        group_id = self.get_group_id_by_name(name)
        url = f"{self.make_target_url(target='groups')}/{group_id}"
        group_map = api.get(url, headers=request_config.headers).json()
        return group_map

    def get_groups(self):
        url = self.make_target_url(target='groups')
        response = api.get(url, headers=request_config.headers).json()
        groups_raw = response['results']
        groups_raw.sort(key=lambda x: x["name"])
        gateway_dict = {}
        for group in groups_raw:
            gateway_dict[group['name']] = group['id']
        return gateway_dict

    def get_group_drivers(self, target_group_name):
        groups = self.get_groups()
        for group_name, group_id in groups.items():
            if group_name == target_group_name:
                target_group_id = group_id
        url = self.make_target_url(target='groups')
        response = api.get(f"{url}/{target_group_id}", headers=request_config.headers).json()
        windows = response['results']['windows']
        window_dict = {}
        for window in windows:
            if "hardwareId" in window:
                window_dict[window['name']] = window['hardwareId']
            else:
                click.echo(f"{window['name']} does not have a hardwareId; cannot be tested.")
        return window_dict

    def get_group_gateways(self, group):
        driver_map = self.build_driver_map()
        group_drivers = self.get_group_drivers(group)
        gwy_id_list = {}
        for gdriver in group_drivers:
            for driver, related_ids in driver_map.items():
                if gdriver == driver and related_ids["gatewayCloudId"] not in driver_map.keys():
                    gwy_id_list.update({related_ids["gatewayCloudId"]: related_ids["gatewayHardwareId"]})
        return gwy_id_list

    def get_group_id_by_name(self, group_name):
        group_list = self.get_groups()
        for group, group_id in group_list.items():
            if group_name == group:
                return group_id

    def send_tint_to_group(self, group, level):
        url = self.make_target_url(target='groups')
        group_id = self.get_group_id_by_name(group_name=group)
        tint_group_ept = f"{url}/{group_id}/tint"
        api.post(tint_group_ept, headers=request_config.headers, json={"level": level})
        click.echo(f"Tint sent to site: {self.site_name}, group: {group}, target level this cycle: {level}")

    def get_live_tint_data_for_group(self, group):
        group_id = self.get_group_id_by_name(group)
        url = f"{self.make_target_url(target='groups')}/{group_id}/live-tint-data"
        live_data = api.get(url, headers=request_config.headers).json()["results"]
        live_data.sort(key=lambda x: x["windowId"])
        return live_data

    def get_group_window_list(self, group_name):
        group_data = self.get_group_info(group_name)["results"]["windows"]
        group_data.sort(key=lambda x: x["id"])
        window_list = {}
        for window in group_data:
            window_list.update({window["id"]: window["name"]})
        return window_list

    def get_group_fault_data(self, group_name):
        group_data = self.get_group_info(group_name)["results"]["windows"]
        group_data.sort(key=lambda x: x["id"])
        fault_data = {}
        for window in group_data:
            now = datetime.now().strftime("%H:%M:%S")
            if window["meta"]["driver"]["fault_states"] != {}:
                fault_data[now] = {
                    "name": window["name"],
                    "firmware_version": window["meta"]["driver"]["firmware"],
                    "fault_states": window["meta"]["driver"]["fault_states"]
                }
            else:
                fault_data[now] = {
                    "name": window["name"],
                    "firmware_version": window["meta"]["driver"]["firmware"],
                    "fault_states": "No Faults"
                }
        return fault_data


    def get_group_ems(self, group):
        gateways = self.get_group_gateways(group)
        site_ems = self.build_energy_manger_map()
        group_ems = {}
        for em, ids in site_ems.items():
            if ids["gatewayCloudId"] in gateways.keys() and ids["emHardwareId"] not in group_ems:
                group_ems.update({ids['gatewayCloudId']: ids["emHardwareId"]})
        return group_ems

    # Energy Managers
    def build_energy_manger_map(self):
        em_map = {}
        for gwy, gwy_ids in self.gateways.items():
            url = self.make_target_url(target=f'gateways/{gwy_ids["id"]}/nodes')
            response = api.get(url, headers=request_config.headers).json()
            for node in response['results']:
                if node['type'] == 'eman':
                    em_map[node['name']] = {'gatewayCloudId': gwy_ids['id'],
                                            'gatewayHardwareId': gwy_ids['hardwareId'],
                                            'emHardwareId': node['nodeId'],
                                            'emCloudId': node['id']}
        return em_map
