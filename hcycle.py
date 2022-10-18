import sys
from datetime import datetime, timedelta
from time import sleep

import click

import paths
from api_utils.site_controller import SiteController
from utils.csv_manager import CSVManager
from utils.cycle_helper import tint_selector, build_data_row
from utils.gwctl_manager import GWCTLManager


@click.group()
def cli():
    click.echo("Halio Cycle Tester Version: 0.0.1")


@cli.command()
@click.option("-env", is_flag=False, flag_value="stage", default="stage",
              type=click.Choice(['stage', 'prod'], case_sensitive=False))
@click.option('-s', '--site', required=True)
@click.option('-gr', '--group', required=True)
@click.option('-cy', '--cycles', required=True, type=int)
@click.option('-w', "--wait", required=True, type=float)
@click.option('-cr', '--check-rate', required=True, type=int)
@click.option('-em/-em-off', '--energy-manager/--energy-manager-off', default=False, help="Include energy manager data")
@click.option('-rnd/-full', '--rand/--full', default=False, help="Randomize tint levels")
@click.option('-sl', '--start-level', default=0, type=int)
@click.option('-f', '--file', required=True, type=str)
@click.option('--testing/--not-testing', default=False)
def cycle_test(env, site, group, cycles, wait, check_rate, energy_manager, rand, start_level, file, testing):
    # setup an interface to control the windows
    site_controller = SiteController(env, site)
    csv_manager = CSVManager(file, testing)
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
            if datetime.now() >= start_time + timedelta(minutes=wait):
                loop = False
            sleep(check_rate)
        cycle_count += 1
    click.echo("Cycles Complete")
    csv_manager.close_writer()


@cli.command()
@click.option('-gid', '--gateway_id', required=True)
@click.option('-sid', '--site_id', required=True)
@click.option('-fn', '--file_name', required=True)
def gen_config(gateway_id, site_id, file_name):
    gwctl_manager = GWCTLManager({}, site_id)
    gwctl_manager.generate_config(gateway_id, site_id, file_name)
    click.echo(file_name)




@cli.command()
@click.option("-env", is_flag=False, flag_value="stage", default="stage",
              type=click.Choice(['stage', 'prod'], case_sensitive=False))
@click.option('-s', '--site', required=True)
@click.option('-gr', '--group', required=True)
def group_info(env, site, group):
    site_controller = SiteController(env, site)
    r = site_controller.get_live_tint_data_for_group(group)
    click.echo(r)


@cli.command()
def is_this_thing_on():
    site_controller = SiteController("stage", "GlareControlTestSLC")
    test_group = "West Wall"
    a = site_controller.get_group_ems(test_group)
    pass
