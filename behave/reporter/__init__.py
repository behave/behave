from behave.importer import load_class
from behave.reporter.base import Reporter


def load_reporter_class(repoter_scoped_class_name):
    error_message = 'reporter=%s is unknown' % repoter_scoped_class_name
    try:
        reporter_class = load_class(repoter_scoped_class_name)
        if not issubclass(reporter_class, Reporter):
            raise Exception(error_message)
        return reporter_class
    except ImportError:
        raise Exception(error_message)
