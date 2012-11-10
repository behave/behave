from behave.formatter.base import Formatter
from xml.etree import cElementTree as ET
import base64


class HTMLFormatter(Formatter):
    name = 'html'
    description = 'Very basic HTML formatter'

    def __init__(self, stream, config):
        super(HTMLFormatter, self).__init__(stream, config)

        self.html = ET.Element('html')

        head = ET.SubElement(self.html, 'head')
        ET.SubElement(head, 'title').text = 'Behave steps'
        ET.SubElement(head, 'meta', {'content': 'text/html;charset=utf-8'})
        ET.SubElement(head, 'style').text = """
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
              height: 8em;
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
        self.suite = ET.SubElement(body, 'div', {'class': 'behave'})

        #Summary
        self.header = ET.SubElement(self.suite, 'div', id='behave-header')
        label = ET.SubElement(self.header, 'div', id='label')
        ET.SubElement(label, 'h1').text = 'Behave features'

        summary = ET.SubElement(self.header, 'div', id='summary')

        totals = ET.SubElement(summary, 'p', id='totals')

        self.feature_totals = ET.SubElement(totals, 'p', id='feature_totals')
        self.scenario_totals = ET.SubElement(totals, 'p', id='scenario_totals')
        self.step_totals = ET.SubElement(totals, 'p', id='step_totals')
        self.duration = ET.SubElement(summary, 'p', id='duration')

        expand_collapse = ET.SubElement(summary, 'div', id='expand-collapse')

        expander = ET.SubElement(expand_collapse, 'div', id='expander')
        expander.set('onclick', \
                     "var ols=document.getElementsByClassName('scenario_steps');" +
                     "for (var i=0; i< ols.length; i++) {" +
                         "ols[i].style.display = 'block';" +
                     "}; " +
                     "return false")
        expander.text = 'Expand All'

        collapser = ET.SubElement(expand_collapse, 'div', id='collapser')
        collapser.set('onclick', \
                     "var ols=document.getElementsByClassName('scenario_steps');" +
                     "for (var i=0; i< ols.length; i++) {" +
                         "ols[i].style.display = 'none';" +
                     "}; " +
                     "return false")
        collapser.text = 'Collapse All'

        self.embed_id = 0
        self.embed_in_this_step = None
        self.embed_data = None
        self.embed_description = None
        self.embed_mime_type = None

        self.scenario_id = 0
        self.all_features = []

    def feature(self, feature):
        self.all_features.append(feature)

        self.feature = ET.SubElement(self.suite, 'div', {'class': 'feature'})
        h2 = ET.SubElement(self.feature, 'h2')
        ET.SubElement(h2, 'span', {'class': 'val'}).text = \
            u'%s: %s' % (feature.keyword, feature.name)

    def background(self, background):
        self.background = ET.SubElement(self.suite, 'div', {'class': 'background'})

        h3 = ET.SubElement(self.background, 'h3')
        ET.SubElement(h3, 'span', {'class': 'val'}).text = \
            u'%s: %s' % (background.keyword, background.name)

        self.steps = ET.SubElement(self.background, 'ol')

    def scenario(self, scenario):
        self.scenario_el = ET.SubElement(self.suite, 'div', {'class': 'scenario'})

        scenario_file = ET.SubElement(self.scenario_el, 'span', {'class': 'scenario_file'})
        scenario_file.text = scenario.location

        if scenario.tags:
            tags = ET.SubElement(self.scenario_el, 'span', {'class': 'tag'})
            tags.text = '@' + reduce(lambda d, x: "%s, @%s" % (d, x), scenario.tags)

        self.scenario_name = ET.SubElement(self.scenario_el, 'h3')
        span = ET.SubElement(self.scenario_name, 'span', {'class': 'val'})
        span.text = u'%s: %s' % (scenario.keyword, scenario.name)

        self.steps = ET.SubElement(self.scenario_el, 'ol',
            {'class': 'scenario_steps',
             'id': 'scenario_%s' % self.scenario_id})

        self.scenario_name.set('onclick', \
                     "ol=document.getElementById('scenario_%s');" % self.scenario_id +
                     "ol.style.display =" +
                     "(ol.style.display == 'none' ? 'block' : 'none');" +
                     "return false")
        self.scenario_id += 1

    def scenario_outline(self, outline):
        self.scenario(self, outline)
        self.scenario_el.set('class', 'scenario outline')

    def match(self, match):
        self.arguments = match.arguments

    def step(self, step):
        self.arguments = None
        self.embed_in_this_step = None
        self.last_step = step

    def result(self, result):
        self.last_step = result
        step = ET.SubElement(self.steps, 'li', {'class': 'step %s' % result.status})
        step_name = ET.SubElement(step, 'div', {'class': 'step_name'})

        keyword = ET.SubElement(step_name, 'span', {'class': 'keyword'})
        keyword.text = result.keyword + ' '

        step_text = ET.SubElement(step_name, 'span', {'class': 'step val'})
        if self.arguments:
            for argument in self.arguments:
                step_text.text = result.name.split(argument.value)[0]
                bold = ET.SubElement(step_text, 'b')
                bold.text = argument.value
                bold.tail = result.name.split(argument.value)[1]
        else:
            step_text.text = result.name

        step_file = ET.SubElement(step, 'div', {'class': 'step_file'})
        ET.SubElement(step_file, 'span').text = result.location

        self.last_step_embed_span = ET.SubElement(step, 'span')
        self.last_step_embed_span.set('class', 'embed')

        if result.text:
            message = ET.SubElement(step, 'div', {'class': 'message'})
            pre = ET.SubElement(message, 'pre', {'style': 'white-space: pre-wrap;'})
            pre.text = result.text

        if result.table:
            table = ET.SubElement(step, 'table')
            tr = ET.SubElement(table, 'tr')
            for heading in result.table.headings:
                ET.SubElement(tr, 'th').text = heading

            for row in result.table.rows:
                tr = ET.SubElement(table, 'tr')
                for cell in row.cells:
                    ET.SubElement(tr, 'td').text = cell

        if result.error_message:
            message = ET.SubElement(step, 'div', {'class': 'message'})
            pre = ET.SubElement(message, 'pre', {'style': 'white-space: pre-wrap;'})
            pre.text = result.error_message

        if result.status == 'failed':
            style = 'background: #C40D0D; color: #FFFFFF'
            self.scenario_name.set('style', style)
            self.header.set('style', style)

        if result.status == 'undefined':
            style = 'background: #FAF834; color: #000000'
            self.scenario_name.set('style', style)
            self.header.set('style', style)

        if hasattr(self, 'embed_in_this_step') and self.embed_in_this_step:
            self._doEmbed(self.last_step_embed_span, self.embed_mime_type,
                          self.embed_data, self.embed_description)
            self.embed_in_this_step = None

    def _doEmbed(self, span, mime_type, data, description):
        self.embed_id += 1

        link = ET.SubElement(span, 'a')
        link.set("onclick", \
                 "embd=document.getElementById('embed_%s');" % self.embed_id +
                 "embd.style.display =" +
                 "(embd.style.display == 'none' ? 'block' : 'none');" +
                 "return false")
        if self.embed_description:
            link.text = self.embed_description

        if 'image/' in mime_type:
            if self.embed_description is None:
                link.text = 'Screenshot'

            embed = ET.SubElement(span, 'img',
                {'id': 'embed_%s' % self.embed_id,
                 'style': 'display: none',
                 'src': 'data:%s;base64,%s' % (mime_type, base64.b64encode(data))
                })
            embed.tail = '    '

        if 'text/' in mime_type:
            if self.embed_description is None:
                link.text = 'Data'

            embed = ET.SubElement(span, 'pre',
                {'id': "text_%s" % self.embed_id,
                 'style': 'display: none'})
            embed.text = data
            embed.tail = '    '

    def embedding(self, mime_type, data, description=None):
        if self.last_step.status == 'untested':
            # Embed called during step execution
            self.embed_in_this_step = True
            self.embed_mime_type = mime_type
            self.embed_data = data
            self.embed_description = description
        else:
            # Embed called in after_*
            self._doEmbed(self.last_step_embed_span, mime_type, data, description)

    def close(self):
        self.duration.text =\
            "Finished in %0.1f seconds" %\
                sum(map(lambda x: x.duration, self.all_features))

        # Filling in summary details
        result = []
        statuses = map(lambda x: x.status, self.all_features)
        from collections import Counter
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.feature_totals.text = 'Features: ' + ', '.join(result)

        result = []
        scenarios = reduce(lambda a, b: a + b,
                           map(lambda x: x.scenarios, self.all_features))
        statuses = map(lambda x: x.status, scenarios)
        from collections import Counter
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.scenario_totals.text = 'Scenarios: ' + ', '.join(result)

        result = []
        steps = reduce(lambda a, b: a + b,
                           map(lambda x: x.steps, scenarios))
        statuses = map(lambda x: x.status, steps)
        from collections import Counter
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.step_totals.text = 'Steps: ' + ', '.join(result)

        # Sending the report to stream
        self.stream.write(unicode(ET.tostring(self.html, encoding='utf-8')))
