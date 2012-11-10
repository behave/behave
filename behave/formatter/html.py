from behave.formatter.base import Formatter
from xml.etree import cElementTree as ET
import base64
import os.path


class HTMLFormatter(Formatter):
    name = 'html'
    description = 'Very basic HTML formatter'

    def __init__(self, stream, config):
        super(HTMLFormatter, self).__init__(stream, config)

        self.html = ET.Element('html')

        head = ET.SubElement(self.html, 'head')
        ET.SubElement(head, 'title').text = 'Behave steps'
        ET.SubElement(head, 'meta', {'content': 'text/html;charset=utf-8'})
        ET.SubElement(head, 'style').text =\
            open(os.path.join(os.path.dirname(__file__), ("report.css")),
                'r').read()

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
            self._doEmbed(self.last_step_embed_span,
                          self.embed_mime_type,
                          self.embed_data)
            self.embed_in_this_step = None

    def _doEmbed(self, span, mime_type, data):
        self.embed_id += 1

        link = ET.SubElement(span, 'a')
        link.set("onclick", \
                 "embd=document.getElementById('embed_%s');" % self.embed_id +
                 "embd.style.display =" +
                 "(embd.style.display == 'none' ? 'block' : 'none');" +
                 "return false")

        if 'image/' in mime_type:
            link.text = 'Screenshot'

            embed = ET.SubElement(span, 'img',
                {'id': 'embed_%s' % self.embed_id,
                 'style': 'display: none',
                 'src': 'data:%s;base64,%s' % (mime_type, base64.b64encode(data))
                })
            embed.tail = '    '

        if 'text/' in mime_type:
            link.text = 'Data'

            embed = ET.SubElement(span, 'pre',
                {'id': "text_%s" % self.embed_id,
                 'style': 'display: none'})
            embed.text = data
            embed.tail = '    '

    def embedding(self, mime_type, data):
        if self.last_step.status == 'untested':
            # Embed called during step execution
            self.embed_in_this_step = True
            self.embed_mime_type = mime_type
            self.embed_data = data
        else:
            # Embed called in after_*
            self._doEmbed(self.last_step_embed_span, mime_type, data)

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
