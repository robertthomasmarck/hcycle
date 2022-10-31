from datetime import datetime, timedelta
from time import sleep

import click

from api_utils.site_controller import SiteController
from utils.csv_manager import CSVManager
from utils.cycle_helper import tint_selector, build_data_row
from utils.gwctl_manager import GWCTLManager


def call_cycles(env,
                site,
                group,
                cycles,
                cycle_period,
                check_rate,
                energy_manager,
                rand,
                start_level,
                file,
                debug=False,
                wait_to_start=0):
    # setup an interface to control the windows
    site_controller = SiteController(env, site)
    out_file = make_test_file_name(env, site, group, file)
    csv_manager = CSVManager(out_file, debug)
    print(f"Cycles will start in {wait_to_start} seconds")
    sleep(wait_to_start)
    group_gateways = site_controller.get_group_gateways(group)
    gwctl_manager = GWCTLManager(group_gateways, site_controller.site_id)
    if energy_manager:
        group_energy_managers = site_controller.get_group_ems(group)
    window_list = site_controller.get_group_window_list(group)
    # start the cycle counter
    cycle_count = 0
    check_count = 0
    while cycle_count <= cycles:
        start_time = datetime.now()

        tint_level = tint_selector(rand, cycle_count, start_level)
        site_controller.send_tint_to_group(group, tint_level)

        loop = True
        while loop:
            click.echo(f"Env:{env} Site:{site} Group:{group} Cycles:{cycle_count}/{cycles}")
            check_count += 1
            tint_data = site_controller.get_live_tint_data_for_group(group)
            window_faults = site_controller.get_group_fault_data(group_name=group)
            if energy_manager:
                em_faults = gwctl_manager.get_energy_manager_faults(group_energy_managers)
                em_data = gwctl_manager.get_energy_manager_info(group_energy_managers, "node getDriverInfo")

                window_data = build_data_row(check_count,
                                             tint_data,
                                             window_list,
                                             tint_level,
                                             window_faults,
                                             em_faults,
                                             em_data)
            else:
                window_data = build_data_row(check_count, tint_data, window_list, tint_level, window_faults)
            csv_manager.write_line(line=window_data)
            if datetime.now() >= start_time + timedelta(minutes=cycle_period):
                loop = False
            sleep(check_rate)
        cycle_count += 1
    click.echo("Cycles Complete")
    csv_manager.close_writer()


def make_test_file_name(env, site, group, file):
    group_file_name = group.replace(" ", "").replace(":", "")
    date = datetime.now().strftime("%Y%m%d%H%M")
    if file is None:
        out_file = f"{env}{site}{group_file_name}{date}"
    else:
        out_file = file + f"{env}{site}{group_file_name}{date}"
    return out_file
