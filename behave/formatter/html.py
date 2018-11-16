# -*- coding: utf-8 -*-
"""
HTML formatter for behave.
Writes a single-page HTML file for test run with all features/scenarios.


IMPROVEMENTS:
  + Avoid to use lxml.etree, use xml.etree.ElementTree instead (bundled w/ Python)
  + Add pretty_print functionality to provide lxml goodie.
  + Stylesheet should be (easily) replacable
  + Simplify collapsable-section usage:
    => Only JavaScript-call: onclick = Collapsible_toggle('xxx')
    => Avoid code duplications, make HTML more readable
  + Expand All / Collapse All: Use <a> instead of <span> element
    => Make active logic (actions) more visible
  * Support external stylesheet ?!?
  * Introduce (Html)Page class to simplify extension and replacements
  * Separate business layer (HtmlFormatter) from technology layer (Page).
  * Correct Python2 constructs: map()/reduce()
  * end() or stream.close() handling is missing
  * steps: text, table parts are no so easily detectable
  * CSS: stylesheet should contain logical "style" classes.
    => AVOID using combination of style attributes where style is better.

TODO:
  * Embedding only works with one part ?!?
  * Even empty embed elements are contained ?!?
"""

from behave.formatter.base import Formatter
from behave.compat.collections import Counter
# XXX-JE-OLD: import lxml.etree as ET
import xml.etree.ElementTree as ET
import six
# XXX-JE-NOT-USED: import os.path


def _valid_XML_char_ordinal(i):
    return (  # conditions ordered by presumed frequency
        0x20 <= i <= 0xD7FF
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
    )

# XXX-JE-FIRST-IDEA:
# def html_prettify(elem):
#     """Return a pretty-printed XML string for the Element."""
#     rough_string = ET.tostring(elem, "utf-8") # XXX, method="html")
#     reparsed = minidom.parseString(rough_string)
#     return reparsed.toprettyxml(indent="  ")

def ET_tostring(elem, pretty_print=False):
    """Render an HTML element(tree) and optionally pretty-print it."""

    text = ET.tostring(elem, "unicode")   # XXX, method="html")
    if pretty_print:
        # -- RECIPE: For pretty-printing w/ xml.etree.ElementTree.
        # SEE: http://pymotw.com/2/xml/etree/ElementTree/create.html
        from xml.dom import minidom
        import re
        declaration_len = len(minidom.Document().toxml())
        reparsed = minidom.parseString(text)
        text = reparsed.toprettyxml(indent="  ")[declaration_len:]
        text_re = re.compile(r'>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
        text = text_re.sub(r'>\g<1></', text)
    return text

class JavascriptLibrary(object):
    collapsible = """
function Collapsible_toggle(id)
{
    var elem = document.getElementById(id);
    elem.style.display = (elem.style.display == 'none' ? 'block' : 'none');
    return false;
}

function Collapsible_expandAll(className)
{
    var elems = document.getElementsByClassName(className);
    for (var i=0; i < elems.length; i++) {
        elems[i].style.display = 'block';
    }
}

function Collapsible_collapseAll(className)
{
    var elems = document.getElementsByClassName(className);
    for (var i=0; i < elems.length; i++) {
        elems[i].style.display = 'none';
    }
}

function Collapsible_expandAllFailed()
{
    var elems = document.getElementsByClassName('failed');
    for (var i=0; i < elems.length; i++) {
        var elem = elems[i];
        if (elem.nodeName == 'H3'){
            elem.parentElement.getElementsByTagName('ol')[0].style.display = 'block';
        }
    }
}
"""


class BasicTheme(object):
    stylesheet_text = """
body{font-size:0;color:#fff;margin:0;
padding:0}.behave,td,th{font:400 11px "Lucida Grande",Helvetica,sans-serif;
background:#fff;color:#000}.behave #behave-header,td #behave-header,
th #behave-header{background:#65c400;color:#fff;height:8em}.behave
#behave-header #expand-collapse p,td #behave-header #expand-collapse
p,th #behave-header #expand-collapse p{float:right;margin:0 0 0 10px}
.background h3,.behave .scenario h3,td .scenario h3,th .scenario h3{
font-size:11px;padding:3px;margin:0;background:#65c400;color:#fff;
font-weight:700}.background h3{font-size:1.2em;background:#666}.behave
h1,td h1,th h1{margin:0 10px;padding:10px;font-family:'Lucida Grande',
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
#summary #totals{font-size:1.2em} h3.failed,#behave-header.failed{background:
#c40d0d !important} h3.undefined,#behave-header.undefined{background:#faf834
 !important; color:#000 !important} #behave-header.failed a{color:#fff} pre {
 white-space: pre-wrap}
"""


class Page(object):
    """
    Provides a HTML page construct (as technological layer).
    XXX
    """
    theme = BasicTheme

    def __init__(self, title=None):
        pass


class HTMLFormatter(Formatter):
    """Provides a single-page HTML formatter
    that writes the result of a  test run.
    """
    name = 'html'
    description = 'Very basic HTML formatter'
    title = u"Behave Test Report"

    def __init__(self, stream, config):
        super(HTMLFormatter, self).__init__(stream, config)

        # -- XXX-JE-PREPARED-BUT-DISABLED:
        # XXX Seldom changed value.
        # XXX Should only be in configuration-file in own section "behave.formatter.html" ?!?
        # XXX Config support must be provided.
        # XXX REASON: Don't clutter behave config-space w/ formatter/plugin related config data.
        # self.css = self.default_css
        # if config.css is not None:
        #    self.css = config.css
        self.html = ET.Element('html')
        head = ET.SubElement(self.html, 'head')
        ET.SubElement(head, 'title').text = self.title
        ET.SubElement(head, 'meta', {'http-equiv': 'Content-Type', 'content': 'text/html;charset=utf-8'})
        style = ET.SubElement(head, 'style', type=u"text/css")
        style.append(ET.Comment(Page.theme.stylesheet_text))
        script = ET.SubElement(head, 'script', type=u"text/javascript")
        script_text = ET.Comment(JavascriptLibrary.collapsible)
        script.append(script_text)

        self.stream = self.open()
        body = ET.SubElement(self.html, 'body')
        self.suite = ET.SubElement(body, 'div', {'class': 'behave'})

        #Summary
        self.header = ET.SubElement(self.suite, 'div', id='behave-header')
        label = ET.SubElement(self.header, 'div', id='label')
        ET.SubElement(label, 'h1').text = self.title

        summary = ET.SubElement(self.header, 'div', id='summary')

        totals = ET.SubElement(summary, 'p', id='totals')

        self.current_feature_totals = ET.SubElement(totals, 'p', id='feature_totals')
        self.scenario_totals = ET.SubElement(totals, 'p', id='scenario_totals')
        self.step_totals = ET.SubElement(totals, 'p', id='step_totals')
        self.duration = ET.SubElement(summary, 'p', id='duration')

        # -- PART: Expand/Collapse All
        expand_collapse = ET.SubElement(summary, 'div', id='expand-collapse')
        expander = ET.SubElement(expand_collapse, 'a', id='expander', href="#")
        expander.set('onclick', "Collapsible_expandAll('scenario_steps')")
        expander.text = u'Expand All'
        cea_spacer = ET.SubElement(expand_collapse, 'span')
        cea_spacer.text = u" | "
        collapser = ET.SubElement(expand_collapse, 'a', id='collapser', href="#")
        collapser.set('onclick', "Collapsible_collapseAll('scenario_steps')")
        collapser.text = u'Collapse All'
        cea_spacer = ET.SubElement(expand_collapse, 'span')
        cea_spacer.text = u" | "
        expander = ET.SubElement(expand_collapse, 'a', id='failed_expander', href="#")
        expander.set('onclick', "Collapsible_expandAllFailed()")
        expander.text = u'Expand All Failed'


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
            tags_element.text = u'@' + ', @'.join(feature.tags)
        h2 = ET.SubElement(self.current_feature, 'h2')
        feature_element = ET.SubElement(h2, 'span', {'class': 'val'})
        feature_element.text = u'%s: %s' % (feature.keyword, feature.name)
        if feature.description:
            description_element = ET.SubElement(self.current_feature, 'pre', {'class': 'message'})
            description_element.text = '\n'.join(feature.description)

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
            tags.text = u'@' + ', @'.join(scenario.tags)

        self.scenario_name = ET.SubElement(self.scenario_el, 'h3')
        span = ET.SubElement(self.scenario_name, 'span', {'class': 'val'})
        span.text = u'%s: %s' % (scenario.keyword, scenario.name)

        if scenario.description:
            description_element = ET.SubElement(self.scenario_el, 'pre', {'class': 'message'})
            description_element.text = '\n'.join(scenario.description)

        self.steps = ET.SubElement(self.scenario_el, 'ol',
                                   {'class': 'scenario_steps',
                                    'id': 'scenario_%s' % self.scenario_id})

        self.scenario_name.set('onclick',
                "Collapsible_toggle('scenario_%s')" % self.scenario_id)
        self.scenario_id += 1

        self.first_step = None
        self.current = None
        self.actual = None

    def scenario_outline(self, outline):
        self.scenario(self, outline)
        self.scenario_el.set('class', 'scenario outline')

    def step(self, step):

        cur = {}

        if self.first_step == None:
            self.first_step = cur
        else:
            self.current['next_step'] = cur

        cur['name'] = step.name
        cur['next_step'] = None
        cur['keyword'] = step.keyword

        self.current = cur

    def match(self, match):
        if self.actual == None:
            self.actual = self.first_step
        else:
            self.actual = self.actual['next_step']

        step_el = ET.SubElement(self.steps, 'li')
        step_name = ET.SubElement(step_el, 'div', {'class': 'step_name'})

        keyword = ET.SubElement(step_name, 'span', {'class': 'keyword'})
        keyword.text = self.actual['keyword'] + u' '

        step_text = ET.SubElement(step_name, 'span', {'class': 'step val'})

        step_file = ET.SubElement(step_el, 'div', {'class': 'step_file'})

        self.actual['act_step_embed_span'] = ET.SubElement(step_el, 'span')
        self.actual['act_step_embed_span'].set('class', 'embed')

        self.actual['step_el'] = step_el

        if match.arguments:
            text_start = 0
            for argument in match.arguments:
                step_part = ET.SubElement(step_text, 'span')
                step_part.text = self.actual['name'][text_start:argument.start]
                if isinstance(argument.value, six.integer_types):
                    argument.value = str(argument.value)
                ET.SubElement(step_text, 'b').text = argument.value
                text_start = argument.end
            step_part = ET.SubElement(step_text, 'span')
            step_part.text = self.actual['name'][match.arguments[-1].end:]
        else:
            step_text.text = self.actual['name']

        if match.location:
            location = "%s:%s" % (match.location.filename, match.location.line)
        else:
            location = "<unknown>"
        ET.SubElement(step_file, 'span').text = location

    def result(self, result):

        self.actual['step_el'].set('class', 'step %s' % result.status.name)

        if result.text:
            message = ET.SubElement(self.actual['step_el'], 'div', {'class': 'message'})
            pre = ET.SubElement(message, 'pre')
            pre.text = result.text

        if result.table:
            table = ET.SubElement(self.actual['step_el'], 'table')
            tr = ET.SubElement(table, 'tr')
            for heading in result.table.headings:
                ET.SubElement(tr, 'th').text = heading

            for row in result.table.rows:
                tr = ET.SubElement(table, 'tr')
                for cell in row.cells:
                    ET.SubElement(tr, 'td').text = cell

        if result.error_message:
            self.embed_id += 1
            link = ET.SubElement(self.actual['step_el'], 'a', {'class': 'message'})
            link.set("onclick",
                    "Collapsible_toggle('embed_%s')" % self.embed_id)
            link.text = u'Error message'

            embed = ET.SubElement(self.actual['step_el'], 'pre',
                                  {'id': "embed_%s" % self.embed_id,
                                   'style': 'display: none'})
            cleaned_error_message = ''.join(
                c for c in result.error_message if _valid_XML_char_ordinal(ord(c))
            )
            embed.text = cleaned_error_message
            embed.tail = u'    '

        if result.status == 'failed':
            self.scenario_name.set('class', 'failed')
            self.header.set('class', 'failed')

        if result.status == 'undefined':
            self.scenario_name.set('class', 'undefined')
            self.header.set('class', 'undefined')


    def _doEmbed(self, span, mime_type, data, caption):
        self.embed_id += 1

        link = ET.SubElement(span, 'a')
        link.set("onclick", "Collapsible_toggle('embed_%s')" % self.embed_id)

        if 'video/' in mime_type:
            if not caption:
                caption = u'Video'
            link.text = six.u(caption)

            embed = ET.SubElement(span, 'video',
                                  {'id': 'embed_%s' % self.embed_id,
                                   'style': 'display: none',
                                   'width': '320',
                                   'controls': ''})
            embed.tail = u'    '
            ET.SubElement(embed, 'source',{
                          'src': u'data:%s;base64,%s' % (mime_type, data),
                          'type': mime_type})

        if 'image/' in mime_type:
            if not caption:
                caption = u'Screenshot'
            link.text = six.u(caption)

            embed = ET.SubElement(span, 'img', {
                                  'id': 'embed_%s' % self.embed_id,
                                  'style': 'display: none',
                                  'src': u'data:%s;base64,%s' % (
                                      mime_type, data)})
            embed.tail = u'    '

        if 'text/' in mime_type:
            if not caption:
                caption = u'Data'
            link.text = six.u(caption)

            cleaned_data = ''.join(
                c for c in data if _valid_XML_char_ordinal(ord(c))
            )

            embed = ET.SubElement(span, 'pre',
                                  {'id': "embed_%s" % self.embed_id,
                                   'style': 'display: none'})
            embed.text = six.u(cleaned_data)
            embed.tail = u'    '

    def embedding(self, mime_type, data, caption=None):
        self._doEmbed(self.actual['act_step_embed_span'], mime_type, data, caption)

    def close(self):
        if not hasattr(self, "all_features"):
            self.all_features = []
        self.duration.text =\
            u"Finished in %0.1f seconds" %\
            sum([x.duration for x in self.all_features])

        # Filling in summary details
        result = []
        statuses = [x.status.name for x in self.all_features]
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.current_feature_totals.text = u'Features: %s' % ', '.join(result)

        result = []
        scenarios_list = [x.scenarios for x in self.all_features]
        scenarios = []
        if len(scenarios_list) > 0:
            scenarios = [x for subl in scenarios_list for x in subl]
        statuses = [x.status.name for x in scenarios]
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.scenario_totals.text = u'Scenarios: %s' % ', '.join(result)

        result = []
        step_list = [x.steps for x in scenarios]
        steps = []
        if step_list:
            steps = [x for subl in step_list for x in subl]
        statuses = [x.status.name for x in steps]
        status_counter = Counter(statuses)
        for k in status_counter:
            result.append('%s: %s' % (k, status_counter[k]))
        self.step_totals.text = u'Steps: %s' % ', '.join(result)

        # Sending the report to stream
        if len(self.all_features) > 0:
            self.stream.write(u"<!DOCTYPE HTML>\n")
            self.stream.write(ET_tostring(self.html, pretty_print=True))
