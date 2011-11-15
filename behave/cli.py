import os
import os.path
import sys

import yaml

from behave import parser
from behave.configuration import Configuration
from behave.formatter.pretty_formatter import PrettyFormatter

TAG_HELP = """
Scenarios inherit tags declared on the Feature level. The simplest
TAG_EXPRESSION is simply a tag:

--tags @dev

When a tag in a tag expression starts with a ~, this represents boolean NOT:

--tags ~@dev

A tag expression can have several tags separated by a comma, which represents
logical OR:

--tags @dev,@wip

The --tags option can be specified several times, and this represents logical
AND, for instance this represents the boolean expression
(@foo || !@bar) && @zap:

--tags @foo,~@bar --tags @zap.

Beware that if you want to use several negative tags to exclude several tags
you have to use logical AND:

--tags ~@fixme --tags ~@buggy.

Positive tags can be given a threshold to limit the number of occurrences. Which
can be practical if you are practicing Kanban or CONWIP. This will fail if there
are more than 3 occurrences of the @qa tag:

--tags @qa:3
""".strip()

class Language(object):
    @classmethod
    def load(cls, language_name, default_language_name="en"):
        directory, _f = os.path.split(os.path.abspath(__file__))
        language_path = os.path.join(directory, 'languages.yml')
        languages = yaml.load(open(language_path))
        if language_name not in languages:
            return None
        return cls(languages[language_name], languages[default_language_name])
    
    def __init__(self, mappings, default_mappings=None):
        self.mappings = mappings
        self.default_mappings = default_mappings
    
    def words(self, key):
        """
        Give all the synonymns of a word in the requested language 
        (or the default language if no word is available).
        """
        if self.default_mappings is not None and key not in self.mappings:
            return self.default_mappings[key].encode('utf').split("|")
        else:
            return self.mappings[key].encode('utf').split("|")

def feature_files(paths):
    files = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.feature'):
                        files.append(os.path.join(dirpath, filename))
        elif path.startswith('@'):
            files.extend([filename.strip() for filename in open(path)])
        elif os.path.exists(path):
            files.append(path)
        else:
            raise Exception("Can't find path: " + path)
    return files
    
def main():
    config = Configuration()
        
    if config.tags and config.tags[0] == 'help':
        print TAG_HELP
        sys.exit(0)
    
    if not config.paths:
        config.paths = ['features']
    
    for filename in feature_files(config.paths):
        feature = parser.parse_file(os.path.abspath(filename), Language.load('en'))
        formatter = PrettyFormatter(sys.stdout, False, False)
        formatter.uri(filename)
        formatter.feature(feature)
        if feature.has_background():
            formatter.background(feature.background)
        for s in feature.iter_scenarios():
            if isinstance(s, parser.Scenario):
                formatter.scenario(s)
            else:
                formater.scenario_outline(s)
            for scenario in s.iterate():
                for step in scenario.iter_steps():
                    formatter.step(step)
        formatter.eof()
                    
        print ''