import copy
import csv
from behave.model import ScenarioOutline


def load_examples_from_csv(feature, csv_file_path):
    for scenario in feature.scenarios:
        if isinstance(scenario, ScenarioOutline) and 'dynamic' in scenario.tags:
            for example in scenario.examples:
                orig = copy.deepcopy(example.table.rows[0])
                example.table.rows = []
                with open(csv_file_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    for row in csv_reader:
                        new_row = copy.deepcopy(orig)
                        new_row.cells = [cell for cell in row]
                        example.table.rows.append(new_row)
