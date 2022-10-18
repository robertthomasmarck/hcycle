import csv
import json
import sys
from os.path import exists

import click

import paths


class CSVManager:

    def __init__(self, file_name, testing):
        if not testing:
            self.check_for_file(file_name)
        self.file = file_name
        self.data_file = open(paths.get_paths(file_name), 'w', newline='')
        self.writer = csv.writer(self.data_file)

    def write_line(self, line):
        jsondata = json.loads(json.dumps(line))

        for count, data in jsondata.items():
            if count == "1":
                self.writer.writerow(data.keys())
            self.writer.writerow(data.values())

    def close_writer(self):
        self.data_file.close()
        click.echo(f"File available: {paths.get_paths(self.file)}\{self.file}.")

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


