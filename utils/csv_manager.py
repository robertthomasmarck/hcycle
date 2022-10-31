import csv
import json
import sys
from datetime import datetime
from os.path import exists
from time import sleep

import click

import paths


class CSVManager:

    def __init__(self, file_name, testing):
        self.file_loc = f"test_data/{file_name}.csv"
        if not testing:
            self.check_for_file(self.file_loc)
        self.data_file = open(paths.get_paths(self.file_loc), 'w', newline='')
        self.writer = csv.writer(self.data_file)

    def write_line(self, line):
        jsondata = json.loads(json.dumps(line))

        for count, data in jsondata.items():
            if count == "1":
                self.writer.writerow(data.keys())
            self.writer.writerow(data.values())

    def close_writer(self):
        self.data_file.close()
        click.echo(f"File available: {paths.get_paths(self.file_loc)}".replace("/", "\\"))

    def check_for_file(self, file):
        if exists(paths.get_paths(file)):
            answer = input("File already exists. Do you want to overwrite it? y/n: ")
            if answer == "y" or answer == "Y":
                pass
            elif answer == "n" or answer == "N":
                sys.exit()
            else:
                print("Please select y or n.")
                self.check_for_file(file)




