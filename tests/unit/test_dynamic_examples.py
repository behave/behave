from behave.dynamic_examples import load_examples_from_csv
from behave.model import Feature, ScenarioOutline, Examples, Table


def test_load_examples_from_csv():
    feature = Feature(None, 'Test Feature')
    scenario = ScenarioOutline(feature, 'Test Scenario')
    examples = Examples(scenario, 'Examples', '', '', 1)
    examples.table = Table(['username', 'email', 'password'])
    examples.table.add_row(['.', '.', '.'])
    scenario.examples.append(examples)
    feature.scenarios.append(scenario)

    csv_file_path = 'tests/test_dynamic_examples.csv'
    load_examples_from_csv(feature, csv_file_path)

    assert len(examples.table.rows) == 2
    assert examples.table.rows[0].cells == ['rajan', 'rajan1@example.com', '1234raj']
    assert examples.table.rows[1].cells == ['kumar', 'kumar2@example.com', '3456kum']
