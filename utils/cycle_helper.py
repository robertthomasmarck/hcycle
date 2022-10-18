import random
from datetime import datetime

import click


def tint_selector(rand, cycles, start_level):
    if cycles == 0:
        return start_level
    else:
        if rand:
            tint_level = random.randint(1, 100)
        elif start_level < 50:
            tint_level = cycles % 2 * 100
        elif start_level >= 50:
            tint_level = abs(cycles % 2 - 1) * 100
        return tint_level


def build_data_row(count, tint_data, window_list, tint_level, window_faults, em_faults=None, em_data=None):
    now = datetime.now().strftime("%H:%M:%S")
    window_data = {}
    window_data[count] = {"Time": now}
    for window in tint_data:
        if window["windowId"] in window_list:
            win_name = window_list[window["windowId"]]
            window_data[count].update({win_name+" Level": window["results"]["level"]})
    window_data[count].update({"Target Level": str(tint_level)})
    click.echo(f"{window_data[count]}".translate({ord(i): None for i in '{}[]\''}))
    for time, win_fault in window_faults.items():
        click.echo(f"Windows: {win_fault['fault_states']}".translate({ord(i): None for i in '{}[]\''}))
        if win_fault["fault_states"] == "No Faults":
            window_data[count].update({f"{win_fault['name']} Faults": f"{win_fault['fault_states']}"})
        else:
            window_data[count].update({f"{win_fault['name']} Faults": f"{win_fault['fault_states']} :: {win_fault['firmware_version']}"})
    if em_faults is not None:
        for time, em_fault in em_faults.items():
            click.echo(f"Energy Managers: {em_fault['faults']}".translate({ord(i): None for i in '{}[]\''}))
            window_data[count].update({f"EM Faults: {em_fault['em_id']}": f"{em_fault['faults']}"})
    if em_data is not None:
        for em, data in em_data.items():
            for data_name, data_point in data.items():
                # if data_name not in ["emi", "netstats"]:
                window_data[count].update({f"{em[-4:]}::{data_name}": f"{data_point}"})
    return window_data
