from __future__ import absolute_import
from behave.formatter.base import Formatter
from xml.etree import ElementTree as ET


class HTMLFormatter(Formatter):
    name = 'html'
    description = 'Very basic HTML formatter'

    def __init__(self, stream, config):
        super(HTMLFormatter, self).__init__(stream, config)

        self.steps = []
        self.show_timings = config.show_timings

        self.html = ET.Element('html')

        head = ET.SubElement(self.html, 'head')

        ET.SubElement(head, 'title').text = 'Behave steps'

        ET.SubElement(head, 'meta').set('content', 'text/html;charset=utf-8')

        style = ET.SubElement(head, 'style')
        style.text = """
            body {
              font-size: 0px;
              color: white;
              margin: 0px;
              padding: 0px;
            }

            .behave, td, th {
              font: normal 11px "Lucida Grande", Helvetica, sans-serif;
              background: white;
              color: black;
            }
            .behave #behave-header, td #behave-header, th #behave-header {
              background: #65c400;
              color: white;
              height: 6em;
            }
            .behave #behave-header #expand-collapse p, td #behave-header #expand-collapse p, th #behave-header #expand-collapse p {
              float: right;
              margin: 0 0 0 10px;
            }
            .behave .scenario h3, td .scenario h3, th .scenario h3, .background h3 {
              font-size: 11px;
              padding: 3px;
              margin: 0;
              background: #65c400;
              color: white;
              font-weight: bold;
            }

            .background h3 {
              font-size: 1.2em;
              background: #666;
            }

            .behave h1, td h1, th h1 {
              margin: 0px 10px 0px 10px;
              padding: 10px;
              font-family: "Lucida Grande", Helvetica, sans-serif;
              font-size: 2em;
              position: absolute;
            }
            .behave h4, td h4, th h4 {
              margin-bottom: 2px;
            }
            .behave div.feature, td div.feature, th div.feature {
              padding: 2px;
              margin: 0px 10px 5px 10px;
            }
            .behave div.examples, td div.examples, th div.examples {
              padding: 0em 0em 0em 1em;
            }
            .behave .stats, td .stats, th .stats {
              margin: 2em;
            }
            .behave .summary ul.features li, td .summary ul.features li, th .summary ul.features li {
              display: inline;
            }
            .behave .step_name, td .step_name, th .step_name {
              float: left;
            }
            .behave .step_file, td .step_file, th .step_file {
              text-align: right;
              color: #999999;
            }
            .behave .step_file a, td .step_file a, th .step_file a {
              color: #999999;
            }
            .behave .scenario_file, td .scenario_file, th .scenario_file {
              float: right;
              color: #999999;
            }
            .behave .tag, td .tag, th .tag {
              font-weight: bold;
              color: #246ac1;
            }
            .behave .backtrace, td .backtrace, th .backtrace {
              margin-top: 0;
              margin-bottom: 0;
              margin-left: 1em;
              color: black;
            }
            .behave a, td a, th a {
              text-decoration: none;
              color: #be5c00;
            }
            .behave a:hover, td a:hover, th a:hover {
              text-decoration: underline;
            }
            .behave a:visited, td a:visited, th a:visited {
              font-weight: normal;
            }
            .behave a div.examples, td a div.examples, th a div.examples {
              margin: 5px 0px 5px 15px;
              color: black;
            }
            .behave .outline table, td .outline table, th .outline table {
              margin: 0px 0px 5px 10px;
            }
            .behave table, td table, th table {
              border-collapse: collapse;
            }
            .behave table td, td table td, th table td {
              padding: 3px 3px 3px 5px;
            }
            .behave table td.failed, .behave table td.passed, .behave table td.skipped, .behave table td.pending, .behave table td.undefined, td table td.failed, td table td.passed, td table td.skipped, td table td.pending, td table td.undefined, th table td.failed, th table td.passed, th table td.skipped, th table td.pending, th table td.undefined {
              padding-left: 18px;
              padding-right: 10px;
            }
            .behave table td.failed, td table td.failed, th table td.failed {
              border-left: 5px solid #c20000;
              border-bottom: 1px solid #c20000;
              background: #fffbd3;
              color: #c20000;
            }
            .behave table td.passed, td table td.passed, th table td.passed {
              border-left: 5px solid #65c400;
              border-bottom: 1px solid #65c400;
              background: #dbffb4;
              color: #3d7700;
            }
            .behave table td.skipped, td table td.skipped, th table td.skipped {
              border-left: 5px solid aqua;
              border-bottom: 1px solid aqua;
              background: #e0ffff;
              color: #001111;
            }
            .behave table td.pending, td table td.pending, th table td.pending {
              border-left: 5px solid #faf834;
              border-bottom: 1px solid #faf834;
              background: #fcfb98;
              color: #131313;
            }
            .behave table td.undefined, td table td.undefined, th table td.undefined {
              border-left: 5px solid #faf834;
              border-bottom: 1px solid #faf834;
              background: #fcfb98;
              color: #131313;
            }
            .behave table td.message, td table td.message, th table td.message {
              border-left: 5px solid aqua;
              border-bottom: 1px solid aqua;
              background: #e0ffff;
              color: #001111;
            }
            .behave ol, td ol, th ol {
              list-style: none;
              margin: 0px;
              padding: 0px;
            }
            .behave ol li.step, td ol li.step, th ol li.step {
              padding: 3px 3px 3px 18px;
              margin: 5px 0px 5px 5px;
            }
            .behave ol li, td ol li, th ol li {
              margin: 0em 0em 0em 1em;
              padding: 0em 0em 0em 0.2em;
            }
            .behave ol li span.param, td ol li span.param, th ol li span.param {
              font-weight: bold;
            }
            .behave ol li.failed, td ol li.failed, th ol li.failed {
              border-left: 5px solid #c20000;
              border-bottom: 1px solid #c20000;
              background: #fffbd3;
              color: #c20000;
            }
            .behave ol li.passed, td ol li.passed, th ol li.passed {
              border-left: 5px solid #65c400;
              border-bottom: 1px solid #65c400;
              background: #dbffb4;
              color: #3d7700;
            }
            .behave ol li.skipped, td ol li.skipped, th ol li.skipped {
              border-left: 5px solid aqua;
              border-bottom: 1px solid aqua;
              background: #e0ffff;
              color: #001111;
            }
            .behave ol li.pending, td ol li.pending, th ol li.pending {
              border-left: 5px solid #faf834;
              border-bottom: 1px solid #faf834;
              background: #fcfb98;
              color: #131313;
            }
            .behave ol li.undefined, td ol li.undefined, th ol li.undefined {
              border-left: 5px solid #faf834;
              border-bottom: 1px solid #faf834;
              background: #fcfb98;
              color: #131313;
            }
            .behave ol li.message, td ol li.message, th ol li.message {
              border-left: 5px solid aqua;
              border-bottom: 1px solid aqua;
              background: #e0ffff;
              color: #001111;
              margin-left: 10px;
            }
            .behave #summary, td #summary, th #summary {
              margin: 0px;
              padding: 5px 10px;
              text-align: right;
              top: 0px;
              right: 0px;
              float: right;
            }
            .behave #summary p, td #summary p, th #summary p {
              margin: 0 0 0 2px;
            }
            .behave #summary #totals, td #summary #totals, th #summary #totals {
              font-size: 1.2em;
            }
        """

        body = ET.SubElement(self.html, 'body')

        self.suite = ET.SubElement(body, 'div')
        self.suite.set('class', 'behave')

        #Summary
        header = ET.SubElement(self.suite, 'div')
        header.set('id', 'behave-header')

        label = ET.SubElement(header, 'div')
        label.set('id', 'label')

        ET.SubElement(label, 'h1').text = 'Behave features'

        summary = ET.SubElement(header, 'div')
        summary.set('id', 'summary')

        self.totals = ET.SubElement(summary, 'p')
        self.totals.set('id', 'totals')

        self.duration = ET.SubElement(summary, 'p')
        self.duration.set('id', 'duration')

        expand_collapse = ET.SubElement(summary, 'div')
        expand_collapse.set('id', 'expand-collapse')

        expander = ET.SubElement(expand_collapse, 'div')
        expander.set('id', 'expander')
        expander.text = 'Expand All'

        collapser = ET.SubElement(expand_collapse, 'div')
        collapser.set('id', 'collapser')
        collapser.text = 'Collapse All'

    def feature(self, feature):
        self.feature = ET.SubElement(self.suite, 'div')
        self.feature.set('class', 'feature')

        h2 = ET.SubElement(self.feature, 'h2')
        span = ET.SubElement(h2, 'span')
        span.set('class', 'val')
        span.text = u'%s: %s\n' % (feature.keyword, feature.name)

    def background(self, background):
        self.background = ET.SubElement(self.suite, 'div')
        self.background.set('class', 'background')

        h3 = ET.SubElement(self.background, 'h3')
        span = ET.SubElement(h3, 'span')
        span.set('class', 'val')
        span.text = u'%s: %s\n' % (background.keyword, background.name)

        self.steps = ET.SubElement(self.scenario, 'ol')

    def scenario(self, scenario):
        self.scenario = ET.SubElement(self.suite, 'div')
        self.scenario.set('class', 'scenario')

        scenario_file = ET.SubElement(self.scenario, 'span')
        scenario_file.set('class', 'scenario_file')
        scenario_file.text = scenario.location

        tags = ET.SubElement(self.scenario, 'span')
        tags.set('class', 'tag')
        tags.text = '@' + reduce(lambda d, x: "%s, @%s" % (d, x), scenario.tags)

        h3 = ET.SubElement(self.scenario, 'h3')
        span = ET.SubElement(h3, 'span')
        span.set('class', 'val')
        span.text = u'%s: %s\n' % (scenario.keyword, scenario.name)

        self.steps = ET.SubElement(self.scenario, 'ol')

    def scenario_outline(self, outline):
        self.scenario_outline = ET.SubElement(self.suite, 'div')
        self.scenario_outline.set('class', 'scenario outline')

        h3 = ET.SubElement(self.scenario_outline, 'h3')
        span = ET.SubElement(h3, 'span')
        span.set('class', 'val')
        span.text = u'%s: %s\n' % (outline.keyword, outline.name)

        self.steps = ET.SubElement(self.scenario, 'ol')

    def step(self, step):
        pass

    def result(self, result):
        step = ET.SubElement(self.steps, 'li')
        step.set('class', 'step %s' % result.status)

        step_name = ET.SubElement(step, 'div')
        step_name.set('class', 'step_name')

        keyword = ET.SubElement(step_name, 'span')
        keyword.set('class', 'keyword')
        keyword.text = result.keyword + ' '

        keyword = ET.SubElement(step_name, 'span')
        keyword.set('class', 'step val')
        keyword.text = result.name

        step_file = ET.SubElement(step, 'div')
        step_file.set('class', 'step_file')
        span = ET.SubElement(step_file, 'span')
        span.text = result.location

        if result.error_message:
            message = ET.SubElement(step, 'div')
            message.set('class', 'message')

            pre = ET.SubElement(message, 'pre')
            pre.text = result.error_message

    def close(self):
        self.stream.write(unicode(ET.tostring(self.html, encoding='utf-8')))
