"""
This module provides `JSON`_ formatters for :mod:`behave`:

* json: Generates compact JSON output
* json.pretty: Generates readable JSON output

.. _JSON: https://json.org
"""

import base64
import json
from behave.formatter.base import Formatter
from behave.model_type import Status


# -----------------------------------------------------------------------------
# CLASS: JSONFormatter
# -----------------------------------------------------------------------------
class JSONFormatter(Formatter):
    name = "json"
    description = "JSON dump of test run"
    dumps_kwargs = {}
    split_text_into_lines = True   # EXPERIMENT for better readability.

    json_number_types = (int, float)
    json_scalar_types = json_number_types + (str, bool, type(None))

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    def reset(self):
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    # -- FORMATTER API:
    def uri(self, uri):
        pass

    def feature(self, feature):
        self.reset()
        self.current_feature = feature
        self.current_feature_data = {
            "keyword": feature.keyword,
            "name": feature.name,
            "tags": list(feature.tags),
            "location": str(feature.location),
            "status": None,     # Not known before feature run.
        }
        element = self.current_feature_data
        if feature.description:
            element["description"] = feature.description

    def background(self, background):
        element = self.add_feature_element({
            "type": "background",
            "keyword": background.keyword,
            "name": background.name,
            "location": str(background.location),
            "steps": [],
        })
        if background.name:
            element["name"] = background.name
        self._step_index = 0

        # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
        for step_ in background.steps:
            self.step(step_)

    def scenario(self, scenario):
        self.finish_current_scenario()
        self.current_scenario = scenario

        element = self.add_feature_element({
            "type": "scenario",
            "keyword": scenario.keyword,
            "name": scenario.name,
            "tags": scenario.tags,
            "location": str(scenario.location),
            "steps": [],
            "status": None,
        })
        if scenario.description:
            element["description"] = scenario.description
        self._step_index = 0

    @classmethod
    def make_table(cls, table):
        table_data = {
            "headings": table.headings,
            "rows": [list(row) for row in table.rows]
        }
        return table_data

    def step(self, step):
        s = {
            "keyword": step.keyword,
            "step_type": step.step_type,
            "name": step.name,
            "location": str(step.location),
        }

        if step.text:
            text = step.text
            if self.split_text_into_lines and "\n" in text:
                text = text.splitlines()
            s["text"] = text
        if step.table:
            s["table"] = self.make_table(step.table)
        element = self.current_feature_element
        element["steps"].append(s)

    def match(self, match):
        args = []
        matched_arguments = match.arguments or []
        for argument in matched_arguments:
            argument_value = argument.value
            if not isinstance(argument_value, self.json_scalar_types):
                # -- OOPS: Avoid invalid JSON format w/ custom types.
                # Use raw string (original) instead.
                argument_value = argument.original
            assert isinstance(argument_value, self.json_scalar_types)
            arg = {
                "value": argument_value,
            }
            if argument.name:
                arg["name"] = argument.name
            if argument.original != argument_value:
                # -- REDUNDANT DATA COMPRESSION: Suppress for strings.
                arg["original"] = argument.original
            args.append(arg)

        match_data = {
            "location": str(match.location) or "",
            "arguments": args,
        }
        if match.location:
            # -- NOTE: match.location=None occurs for undefined steps.
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["match"] = match_data

    # -- CAPTURED OUTPUT: Streams provided as JSON "result" fields.
    CAPTURED_OUTPUT_NAMES = ("stdout", "stderr", "log")

    @classmethod
    def _format_text(cls, text):
        """Split multi-line text into a list of lines (for readability)."""
        if cls.split_text_into_lines and "\n" in text:
            return text.splitlines()
        return text

    @classmethod
    def make_captured_output(cls, captured, exclude_text=None):
        """Build the JSON "result" fields for the captured output of a step.

        SINCE behave v1.2.7, captured output is stored on the model element
        (in ``step.captured``) instead of being inlined into the step's
        ``error_message``. This exposes it as dedicated JSON fields so that
        JSON reports retain the captured stdout/stderr/log (esp. the
        "Captured logging" of a failed step).

        :param captured: Captured output (value object), see :class:`Captured`.
        :param exclude_text:
            Optional text to omit. For a failed step, the error message is also
            stored in the captured stderr (see ``Step._process_error``); passing
            ``step.error_message`` avoids duplicating it as ``captured_stderr``.
        :return: Dict with ``captured_<name>`` fields (may be empty).

        .. seealso:: https://github.com/behave/behave/issues/1323
        """
        captured_fields = {}
        if not (captured and captured.has_output()):
            return captured_fields
        for name in cls.CAPTURED_OUTPUT_NAMES:
            captured_text = getattr(captured, name, "")
            if not captured_text or captured_text == exclude_text:
                continue
            captured_fields["captured_" + name] = cls._format_text(captured_text)
        return captured_fields

    def result(self, step):
        steps = self.current_feature_element["steps"]
        result_element = {
            "status": step.status.name,
            "duration": step.duration,
        }
        steps[self._step_index]["result"] = result_element
        if step.error_message and step.status == Status.failed:
            # -- OPTIONAL: Provided for failed steps.
            result_element["error_message"] = self._format_text(step.error_message)
        result_element.update(
            self.make_captured_output(step.captured, exclude_text=step.error_message)
        )
        self._step_index += 1

    def embedding(self, mime_type, data):
        step = self.current_feature_element["steps"][self._step_index]
        if "embeddings" not in step:
            step["embeddings"] = []
        step["embeddings"].append({
            "mime_type": mime_type,
            "data": base64.b64encode(data).decode(self.stream.encoding or "utf-8"),
        })

    def eof(self):
        """
        End of feature
        """
        if not self.current_feature_data:
            return

        # -- NORMAL CASE: Write collected data of current feature.
        self.finish_current_scenario()
        self.update_status_data()

        if self.feature_count == 0:
            # -- FIRST FEATURE:
            self.write_json_header()
        else:
            # -- NEXT FEATURE:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.reset()
        self.feature_count += 1

    def close(self):
        if self.feature_count == 0:
            # -- FIRST FEATURE: Corner case when no features are provided.
            self.write_json_header()
        self.write_json_footer()
        self.close_stream()

    # -- JSON-DATA COLLECTION:
    def add_feature_element(self, element):
        assert self.current_feature_data is not None
        if "elements" not in self.current_feature_data:
            self.current_feature_data["elements"] = []
        self.current_feature_data["elements"].append(element)
        return element

    @property
    def current_feature_element(self):
        assert self.current_feature_data is not None
        return self.current_feature_data["elements"][-1]

    def update_status_data(self):
        assert self.current_feature
        assert self.current_feature_data
        self.current_feature_data["status"] = self.current_feature.status.name

    def finish_current_scenario(self):
        if self.current_scenario:
            status_name = self.current_scenario.status.name
            self.current_feature_element["status"] = status_name

    # -- JSON-WRITER:
    def write_json_header(self):
        self.stream.write("[\n")

    def write_json_footer(self):
        self.stream.write("\n]\n")

    def write_json_feature(self, feature_data):
        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        self.stream.write(",\n\n")


# -----------------------------------------------------------------------------
# CLASS: PrettyJSONFormatter
# -----------------------------------------------------------------------------
class PrettyJSONFormatter(JSONFormatter):
    """
    Provides readable/comparable textual JSON output.
    """
    name = "json.pretty"
    description = "JSON dump of test run (human readable)"
    dumps_kwargs = {"indent": 2, "sort_keys": True}
