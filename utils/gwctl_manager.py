import ast
import json
import os
import subprocess
from datetime import datetime
from time import sleep

import click

import paths

root = paths.get_paths("")
new_gwctl = f"{root}gwctl-1.1.0.exe"
old_gwctl = f"{root}gwctl-0.45.0.exe"
config_files = f"{root}gwctl_config_files"


class GWCTLManager:
    def __init__(self, gateway_list, siteId):
        self.config_list = {}
        for gateway_cloud_id, gateway_hardware_id in gateway_list.items():
            self.config_list.update({gateway_cloud_id: self.generate_config(gateway_hardware_id, siteId,
                                                                            f"config_{gateway_hardware_id}.json")})

    def generate_config(self, target_gateway, site_id, file_name):
        file = f"{config_files}\\{file_name}"
        if os.path.exists(file):
            return file
        else:
            base_config = f"--config {root}\westwallglarecontroltest.json"
            admin_keys = f"--api {root}\\api.json"
            admin_command = "admin ctlCfgGen"
            targets = f"{target_gateway[-4:]} {site_id} '{file_name}' '{config_files}'"
            command = f"{old_gwctl} {base_config} {admin_keys} {admin_command} {targets}"
            r = self.run_command(command)
            config_text = r[r.find("generated") + 10:r.find("site") + 100]
            with open(file, 'w', encoding='utf-8') as c:
                c.write(config_text)
            c.close()
            return file

    def get_energy_manager_faults(self, em_list):
        em_faults = {}
        for gateway_id, config_file in self.config_list.items():
            for em_gateway_id, em_id in em_list.items():
                if gateway_id == em_gateway_id:
                    target_site = f"{new_gwctl} --config '{config_file}'"
                    em_command = f"{target_site} node remoteSerialCommand {em_id} ".replace("'", "")
                    p = self.run_command(em_command + "\"batmon faults\"")
                    now = datetime.now().strftime("%H:%M:%S")
                    # if "overtemperature during charge" in p:
                    #     click.echo("Energy manager over temp. Pausing script.")
                    #     sleep(2000)
                    if "no faults" in p:
                        em_faults[now] = {
                            "em_id": em_id,
                            "faults": "No Faults"
                        }
                    else:
                        em_faults[now] = {
                            "em_id": em_id,
                            "faults": p
                        }

        return em_faults

    def get_energy_manager_info(self, em_list, base_command, r_serial_command=""):
        info = {}
        for gateway_id, config_file in self.config_list.items():
            for em_gateway_id, em_id in em_list.items():
                if gateway_id == em_gateway_id:
                    target_site = f"{new_gwctl} --config '{config_file}'"
                    em_command = f"{target_site} {base_command} {em_id} ".replace("'", "")
                    #Get the response and turn it into a string
                    p = str(subprocess.check_output(em_command + f"{r_serial_command}"))
                    #Get the useful data, remove the formatting commands, and add a unique character to help with parsing
                    p = p[p.find("Info called") + 11: len(p)].replace("\\n\\t", "~").replace("\\n", "").split("~")
                    a = self.cleaner_upper(p, delimiter=" = ")
                    a["netstats"] = a["netstats"].replace("map[", "").replace("]", "").replace(" ", "~").split('~')
                    a = self.cleaner_upper(a["netstats"], delimiter=":", add_to=a)
                    emi = a["emi"]
                    cv = emi[emi.find("cv:"):emi[:-1].find("]")+1]
                    emi = emi.replace(cv, "").replace("map[", "").replace("]", "").replace(" ", "~").split('~')
                    a = self.cleaner_upper(emi, delimiter=":", add_to=a)
                    cv = cv.replace("cv:[", "").replace("]", "").split(' ')
                    count = 1
                    for v in cv:
                        el = "{" + f"\"cv-{count}\": \"{v}\"" + "}"
                        a.update(json.loads(el))
                        count += 1
                    remove = ['emi', 'flt', 'lockout', 'mac', 'utc',
                              'visible', 'name', 'netstats', 'dstatus',
                              'state', 'entry_type', 'last_step_id', 'igu-id',
                              'archItemId', 'ip', 'version', 'groups',
                              'real_window', 'configHash', 'devicetype', 'drives',
                              'gateway', 'hv', 'id', 'site', 'ula', 'id']
                    for k in remove:
                        a.pop(k, None)
                    a = dict(sorted(a.items()))
                    info.update({em_id: a})
        return info

    def cleaner_upper(self, raw_response, delimiter, add_to=None):
        if add_to == None:
            clean_data = {}
        else:
            clean_data = add_to
        for element in raw_response:

            # Add the characters needs to make each element a json object
            element = "{\"" + element + "\"}"
            element = element.replace(f"{delimiter}", "\": \"")
            try:
                clean_data.update(json.loads(element))
            except:
                pass
        return clean_data

    @staticmethod
    def run_command(command):
        try:
            p = subprocess.check_output(command, timeout=90, shell=True)
            response = p.decode("utf-8")
            return response
        except Exception as e:
            print(e)
            return e
