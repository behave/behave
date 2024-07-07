from __future__ import absolute_import, print_function
import copy
import csv
import os


def load_dynamic_examples_from_csv(example, file_path):
    if os.path.exists(file_path):
        orig = copy.deepcopy(example.table.rows[0])  # Make a deep copy of the original header row
        example.table.rows = []  # Clear existing rows
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                new_row = copy.deepcopy(orig)
                new_row.cells = [str(cell) for cell in row]
                example.table.rows.append(new_row)
    else:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
