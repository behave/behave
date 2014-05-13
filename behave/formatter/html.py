from behave.formatter.base import Formatter
import lxml.etree as ET
import base64
import os.path
from behave.compat.collections import Counter


def _valid_XML_char_ordinal(i):
    return (  # conditions ordered by presumed frequency
        0x20 <= i <= 0xD7FF
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
        )


class HTMLFormatter(Formatter):
    name = 'html'
    description = 'Very basic HTML formatter'

    def __init__(self, stream, config):
        super(HTMLFormatter, self).__init__(stream, config)

        self.html = ET.Element('html')

        head = ET.SubElement(self.html, 'head')
        ET.SubElement(head, 'title').text = u'Behave steps'
        ET.SubElement(head, 'meta', {'content': 'text/html;charset=utf-8'})
        ET.SubElement(head, 'style').text = """body{font-size:0;color:#fff;margin:0;
        padding:0}.behave,td,th{font:400 11px "Lucida Grande",Helvetica,sans-serif;
        background:#fff;color:#000}.behave #behave-header,td #behave-header,
        th #behave-header{background:#65c400;color:#fff;height:8em}.behave 
        #behave-header #expand-collapse p,td #behave-header #expand-collapse 
        p,th #behave-header #expand-collapse p{float:right;margin:0 0 0 10px}
        .background h3,.behave .scenario h3,td .scenario h3,th .scenario h3{
        font-size:11px;padding:3px;margin:0;background:#65c400;color:#fff;
        font-weight:700}.background h3{font-size:1.2em;background:#666}.behave 
        h1,td h1,th h1{margin:0 10px;padding:10px;font-family:"Lucida Grande",
        Helvetica,sans-serif;font-size:2em;position:absolute}.behave h4,td h4,
        th h4{margin-bottom:2px}.behave div.feature,td div.feature,th div.feature
        {padding:2px;margin:0 10px 5px}.behave div.examples,td div.examples,th 
        div.examples{padding:0 0 0 1em}.behave .stats,td .stats,th .stats{margin:2em}
        .behave .summary ul.features li,td .summary ul.features li,th .summary 
        ul.features li{display:inline}.behave .step_name,td .step_name,th .step_name
        {float:left}.behave .step_file,td .step_file,th .step_file{text-align:right;
        color:#999}.behave .step_file a,td .step_file a,th .step_file a{color:#999}.behave 
        .scenario_file,td .scenario_file,th .scenario_file{float:right;color:#999}.behave 
        .tag,td .tag,th .tag{font-weight:700;color:#246ac1}.behave .backtrace,td 
        .backtrace,th .backtrace{margin-top:0;margin-bottom:0;margin-left:1em;color:#000}
        .behave a,td a,th a{text-decoration:none;color:#be5c00}.behave a:hover,
        td a:hover,th a:hover{text-decoration:underline}.behave a:visited,td a:visited,
        th a:visited{font-weight:400}.behave a div.examples,td a div.examples,
        th a div.examples{margin:5px 0 5px 15px;color:#000}.behave .outline table,
        td .outline table,th .outline table{margin:0 0 5px 10px}.behave table,
        td table,th table{border-collapse:collapse}.behave table td,td table td,
        th table td{padding:3px 3px 3px 5px}.behave table td.failed,td table td.failed,
        th table td.failed{border-left:5px solid #c20000;border-bottom:1px solid 
        #c20000;background:#fffbd3;color:#c20000}.behave table td.passed,td table 
        td.passed,th table td.passed{border-left:5px solid #65c400;border-bottom:1px 
        solid #65c400;background:#dbffb4;color:#3d7700}.behave table td.skipped,td 
        table td.skipped,th table td.skipped{border-left:5px solid #0ff;border-bottom:1px 
        solid #0ff;background:#e0ffff;color:#011}.behave table td.pending,.behave table 
        td.undefined,td table td.pending,td table td.undefined,th table td.pending,th table 
        td.undefined{border-left:5px solid #faf834;border-bottom:1px solid #faf834;
        background:#fcfb98;color:#131313}.behave table td.message,td table td.message,th 
        table td.message{border-left:5px solid #0ff;border-bottom:1px solid #0ff;
        background:#e0ffff;color:#011}.behave ol,td ol,th ol{list-style:none;
        margin:0;padding:0}.behave ol li.step,td ol li.step,th ol li.step{
        padding:3px 3px 3px 18px;margin:5px 0 5px 5px}.behave ol li,td ol li,th 
        ol li{margin:0 0 0 1em;padding:0 0 0 .2em}.behave ol li span.param,td 
        ol li span.param,th ol li span.param{font-weight:700}.behave ol li.failed,td 
        ol li.failed,th ol li.failed{border-left:5px solid #c20000;border-bottom:1px 
        solid #c20000;background:#fffbd3;color:#c20000}.behave ol li.passed,td ol 
        li.passed,th ol li.passed{border-left:5px solid #65c400;border-bottom:1px 
        solid #65c400;background:#dbffb4;color:#3d7700}.behave ol li.skipped,td ol 
        li.skipped,th ol li.skipped{border-left:5px solid #0ff;border-bottom:1px 
        solid #0ff;background:#e0ffff;color:#011}.behave ol li.pending,.behave ol 
        li.undefined,td ol li.pending,td ol li.undefined,th ol li.pending,th ol 
        li.undefined{border-left:5px solid #faf834;border-bottom:1px solid 
        #faf834;background:#fcfb98;color:#131313}.behave ol li.message,td ol 
        li.message,th ol li.message{border-left:5px solid #0ff;border-bottom:1px 
        solid #0ff;background:#e0ffff;color:#011;margin-left:10px}.behave #summary,td 
        #summary,th #summary{margin:0;padding:5px 10px;text-align:right;top:0;
        right:0;float:right}.behave #summary p,td #summary p,th #summary 
        p{margin:0 0 0 2px}.behave #summary #totals,td #summary #totals,th 
        #summary #totals{font-size:1.2em}"""

        self.stream = self.open()
        body = ET.SubElement(self.html, 'body')
        self.suite = ET.SubElement(body, 'div', {'class': 'behave'})

        #Summary
        self.header = ET.SubElement(self.suite, 'div', id='behave-header')
        label = ET.SubElement(self.header, 'div', id='label')
        ET.SubElement(label, 'h1').text = u'Behave features'

        summary = ET.SubElement(self.header, 'div', id='summary')

        totals = ET.SubElement(summary, 'p', id='totals')

        self.current_feature_totals = ET.SubElement(totals, 'p', id='feature_totals')
        self.scenario_totals = ET.SubElement(totals, 'p', id='scenario_totals')
        self.step_totals = ET.SubElement(totals, 'p', id='step_totals')
        self.duration = ET.SubElement(summary, 'p', id='duration')

        expand_collapse = ET.SubElement(summary, 'div', id='expand-collapse')

        expander = ET.SubElement(expand_collapse, 'span', id='expander')
        expander.set('onclick',
                     "var ols=document.getElementsByClassName('scenario_steps');" +
                     "for (var i=0; i< ols.length; i++) {" +
                     "ols[i].style.display = 'block';" +
                     "}; " +
                     "return false")
        expander.text = u'Expand All'

        spacer = ET.SubElement(expand_collapse, 'span')
        spacer.text = u"  "

        collapser = ET.SubElement(expand_collapse, 'span', id='collapser')
        collapser.set('onclick',
                      "var ols=document.getElementsByClassName('scenario_steps');" +
                      "for (var i=0; i< ols.length; i++) {" +
                      "ols[i].style.display = 'none';" +
                      "}; " +
                      "return false")
        collapser.text = u'Collapse All'

        self.embed_id = 0
        self.embed_in_this_step = None
        self.embed_data = None
        self.embed_mime_type = None
        self.scenario_id = 0

    def feature(self, feature):
        if not hasattr(self, "all_features"):
            self.all_features = []
        self.all_features.append(feature)

        self.current_feature = ET.SubElement(self.suite, 'div', {'class': 'feature'})
        if feature.tags:
            tags_element = ET.SubElement(self.current_feature, 'span', {'class': 'tag'})
            tags_element.text = u'@' + reduce(lambda d, x: "%s, @%s" % (d, x), feature.tags)
        h2 = ET.SubElement(self.current_feature, 'h2')
        feature_element = ET.SubElement(h2, 'span', {'class': 'val'})
        feature_element.text = u'%s: %s' % (feature.keyword, feature.name)
        if feature.description:
            description_element = ET.SubElement(self.current_feature, 'pre', {'class': 'message'})
            description_element.text = reduce(lambda d, x: "%s\n%s" % (d, x), feature.description)

    def background(self, background):
        self.current_background = ET.SubElement(self.suite, 'div', {'class': 'background'})

        h3 = ET.SubElement(self.current_background, 'h3')
        ET.SubElement(h3, 'span', {'class': 'val'}).text = \
            u'%s: %s' % (background.keyword, background.name)

        self.steps = ET.SubElement(self.current_background, 'ol')

    def scenario(self, scenario):
        if scenario.feature not in self.all_features:
            self.all_features.append(scenario.feature)
        self.scenario_el = ET.SubElement(self.suite, 'div', {'class': 'scenario'})

        scenario_file = ET.SubElement(self.scenario_el, 'span', {'class': 'scenario_file'})
        scenario_file.text = "%s:%s" % (scenario.location.filename, scenario.location.line)

        if scenario.tags:
            tags = ET.SubElement(self.scenario_el, 'span', {'class': 'tag'})
            tags.text = u'@' + reduce(lambda d, x: "%s, @%s" % (d, x), scenario.tags)

        self.scenario_name = ET.SubElement(self.scenario_el, 'h3')
        span = ET.SubElement(self.scenario_name, 'span', {'class': 'val'})
        span.text = u'%s: %s' % (scenario.keyword, scenario.name)

        if scenario.description:
            description_element = ET.SubElement(self.scenario_el, 'pre', {'class': 'message'})
            description_element.text = reduce(lambda d, x: "%s\n%s" % (d, x), scenario.description)

        self.steps = ET.SubElement(self.scenario_el, 'ol',
                                   {'class': 'scenario_steps',
                                    'id': 'scenario_%s' % self.scenario_id})

        self.scenario_name.set('onclick',
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
        if match.location:
            self.location = "%s:%s" % (match.location.filename, match.location.line)
        else:
            self.location = "<unknown>"

    def step(self, step):
        self.arguments = None
        self.embed_in_this_step = None
        self.last_step = step

    def result(self, result):
        self.last_step = result
        step = ET.SubElement(self.steps, 'li', {'class': 'step %s' % result.status})
        step_name = ET.SubElement(step, 'div', {'class': 'step_name'})

        keyword = ET.SubElement(step_name, 'span', {'class': 'keyword'})
        keyword.text = result.keyword + u' '

        if self.arguments:
            text_start = 0
            for argument in self.arguments:
                step_text = ET.SubElement(step_name, 'span', {'class': 'step val'})
                step_text.text = result.name[text_start:argument.start]
                ET.SubElement(step_text, 'b').text = str(argument.value)
                text_start = argument.end
            step_text = ET.SubElement(step_name, 'span', {'class': 'step val'})
            step_text.text = result.name[self.arguments[-1].end:]
        else:
            step_text = ET.SubElement(step_name, 'span', {'class': 'step val'})
            step_text.text = result.name

        step_file = ET.SubElement(step, 'div', {'class': 'step_file'})
        ET.SubElement(step_file, 'span').text = self.location

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
            self.embed_id += 1
            link = ET.SubElement(step, 'a', {'class': 'message'})
            link.set("onclick",
                     "rslt=document.getElementById('embed_%s');" % self.embed_id +
                     "rslt.style.display =" +
                     "(rslt.style.display == 'none' ? 'block' : 'none');" +
                     "return false")
            link.text = u'Error message'

            embed = ET.SubElement(step, 'pre',
                                  {'id': "embed_%s" % self.embed_id,
                                  'style': 'display: none; white-space: pre-wrap;'})
            cleaned_error_message = ''.join(
                c for c in result.error_message if _valid_XML_char_ordinal(ord(c))
            )
            embed.text = cleaned_error_message
            embed.tail = u'    '

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
                          self.embed_data,
                          self.embed_caption)
            self.embed_in_this_step = None

    def _doEmbed(self, span, mime_type, data, caption):
        self.embed_id += 1

        link = ET.SubElement(span, 'a')
        link.set("onclick",
                 "embd=document.getElementById('embed_%s');" % self.embed_id +
                 "embd.style.display =" +
                 "(embd.style.display == 'none' ? 'block' : 'none');" +
                 "return false")

        if 'video/' in mime_type:
            if not caption:
                caption = u'Video'
            link.text = unicode(caption)

            embed = ET.SubElement(span, 'video',
                                  {'id': 'embed_%s' % self.embed_id,
                                   'style': 'display: none',
                                   'width': '320',
                                   'controls': ''})
            embed.tail = u'    '
            ET.SubElement(embed, 'source',{
                          'src': u'data:%s;base64,%s' % (mime_type, base64.b64encode(data)),
                          'type': '%s; codecs="vp8 vorbis"' % mime_type})

        if 'image/' in mime_type:
            if not caption:
                caption = u'Screenshot'
            link.text = unicode(caption)

            embed = ET.SubElement(span, 'img', {
                                  'id': 'embed_%s' % self.embed_id,
                                  'style': 'display: none',
                                  'src': u'data:%s;base64,%s' % (
                                      mime_type, base64.b64encode(data))})
            embed.tail = u'    '

        if 'text/' in mime_type:
            if not caption:
                caption = u'Data'
            link.text = unicode(caption)

            cleaned_data = ''.join(
                c for c in data if _valid_XML_char_ordinal(ord(c))
            )

            embed = ET.SubElement(span, 'pre',
                                  {'id': "embed_%s" % self.embed_id,
                                   'style': 'display: none'})
            embed.text = cleaned_data
            embed.tail = u'    '

    def embedding(self, mime_type, data, caption=None):
        if self.last_step.status == 'untested':
            # Embed called during step execution
            self.embed_in_this_step = True
            self.embed_mime_type = mime_type
            self.embed_data = data
            self.embed_caption = caption
        else:
            # Embed called in after_*
            self._doEmbed(self.last_step_embed_span, mime_type, data, caption)

    def close(self):
        if not hasattr(self, "all_features"):
            self.all_features = []
        self.duration.text =\
            u"Finished in %0.1f seconds" %\
            sum(map(lambda x: x.duration, self.all_features))

        # Filling in summary details
        result = []
        statuses = map(lambda x: x.status, self.all_features)
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.current_feature_totals.text = u'Features: %s' % ', '.join(result)

        result = []
        scenarios_list = map(lambda x: x.scenarios, self.all_features)
        scenarios = []
        if len(scenarios_list) > 0:
            scenarios = reduce(lambda a, b: a + b, scenarios_list)
        statuses = map(lambda x: x.status, scenarios)
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.scenario_totals.text = u'Scenarios: %s' % ', '.join(result)

        result = []
        step_list = map(lambda x: x.steps, scenarios)
        steps = []
        if step_list:
            steps = reduce(lambda a, b: a + b, step_list)
        statuses = map(lambda x: x.status, steps)
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.step_totals.text = u'Steps: %s' % ', '.join(result)

        # Sending the report to stream
        if len(self.all_features) > 0:
            self.stream.write(ET.tostring(self.html, pretty_print = True))
