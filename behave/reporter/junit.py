import os.path
from xml.etree import ElementTree

from behave.reporter.base import Reporter


class JUnitReporter(Reporter):
    def feature(self, feature):
        filename = None
        for path in self.config.paths:
            if feature.filename.startswith(path):
                filename = feature.filename[len(path) + 1:]
                break
        if filename is None:
            filename = os.path.split(feature.filename)[1]
        filename = filename.rsplit('.', 1)[0]
        classname = filename = filename.replace('/', '.')
        filename = 'TESTS-%s.xml' % filename

        suite = ElementTree.Element('testsuite')
        suite.set('name', feature.name or feature.filename)

        tests = 0
        failed = 0
        skipped = 0

        for scenario in feature:
            tests += 1

            case = ElementTree.Element('testcase')
            case.set('class', classname)
            case.set('name', scenario.name or '')
            case.set('time', str(round(scenario.duration, 3)))

            if scenario.status == 'failed':
                failed += 1
                failure = ElementTree.Element('failure')

                for step in scenario:
                    if step.status == 'failed':
                        failure.set('type', step.exception.__class__.__name__)
                        failure.set('message', str(step.exception))
                        if not isinstance(step.exception, AssertionError):
                            failure.text = step.error_message
                        break

                case.append(failure)
            elif scenario.status in ('skipped', 'untested'):
                for step in scenario:
                    if step.status == 'undefined':
                        failed += 1
                        failure = ElementTree.Element('failure')
                        failure.set('type', 'undefined')
                        failure.set('message', '')
                        case.append(failure)
                        break

            suite.append(case)

        suite.set('tests', str(tests))
        suite.set('failures', str(failed))
        suite.set('skip', str(skipped))
        suite.set('time', str(round(feature.duration, 3)))

        if not os.path.exists(self.config.junit_directory):
            os.mkdir(self.config.junit_directory)

        tree = ElementTree.ElementTree(suite)
        report_filename = os.path.join(self.config.junit_directory, filename)
        tree.write(open(report_filename, 'w'), 'utf8')
