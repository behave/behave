# -*- coding: UTF-8 -*-
# pylint: disable=redundant-u-string-prefix,super-with-arguments
"""
Contains the core functionality, value objects and processor(s),
for collection a summary counts of a test run.

.. note:: USED BY: :class:`behave.reporter.summary:SummaryReporter`
"""
# pylint: disable=useless-object-inheritance, consider-using-f-string

from __future__ import absolute_import, print_function
from collections import Counter, OrderedDict
import six

from behave._types import require_type
from behave.model_type import Status
from behave.model_visitor import ModelVisitor


# -----------------------------------------------------------------------------
# PYTHON VERSION COMPATIBILITY
# -----------------------------------------------------------------------------
def _patch(target, name, new_value):
    setattr(target, name, new_value)


# -- MONKEY-PATCHES:
if not hasattr(Counter, "total"):
    # -- HINT: Counter.total() (since: Python 3.10)
    def _Counter_total(self):  # pylint: disable=invalid-name
        return sum(self.values())

    _patch(Counter, "total", _Counter_total)


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
STATUS_ORDER = (Status.passed,
                Status.failed, Status.error,
                Status.hook_error, Status.cleanup_error,
                Status.skipped,
                # -- STEPS-SPECIFIC (Part 1):
                Status.pending, Status.pending_warn,
                Status.undefined,
                # -- COMMON: Initial state
                Status.untested,
                # -- STEPS-SPECIFIC (Part 2):
                Status.untested_pending, Status.untested_undefined)


# -----------------------------------------------------------------------------
# COUNTS VALUE OBJECTS
# -----------------------------------------------------------------------------
class StatusCounts(Counter):  # pylint: disable=abstract-method
    """
    ValueObject that stores the counts related to one category:

    * features
    * rules
    * scenarios
    * steps
    """
    # NOSTEP_ORDER = [status for status in STATUS_ORDER
    #                 if status != Status.undefined]
    ORDER = STATUS_ORDER
    ZERO = {
        Status.passed: 0,
        Status.failed: 0,
        Status.error: 0,
        Status.hook_error: 0,
        Status.cleanup_error: 0,
        Status.skipped: 0,
        Status.pending: 0,
        Status.pending_warn: 0,
        Status.undefined: 0,
        Status.untested: 0,
        Status.untested_pending: 0,
        Status.untested_undefined: 0,
    }

    def __init__(self, data=None, **kwargs):
        data = self.make_data(data, **kwargs)
        Counter.__init__(self, data)

    # -- CONSTRUCTOR-METHODS:
    @classmethod
    def from_counts(cls, passed=0, failed=0, error=0,
                    skipped=0, untested=0,
                    pending=0, pending_warn=0, untested_pending=0,
                    undefined=0, untested_undefined=0,
                    hook_error=0, cleanup_error=0):
        data = {
            Status.passed: passed,
            Status.failed: failed,
            Status.error: error,
            Status.hook_error: hook_error,
            Status.cleanup_error: cleanup_error,
            Status.skipped: skipped,
            Status.pending: pending,
            Status.pending_warn: pending_warn,
            Status.untested_pending: untested_pending,
            Status.untested: untested,
            Status.undefined: undefined,
            Status.untested_undefined: untested_undefined,
        }
        return cls(data)
        # -- OLD:
        # return cls(passed=passed, failed=failed, skipped=skipped,
        #            untested=untested, undefined=undefined)

    @classmethod
    def from_dict(cls, data):
        require_type(data, dict)
        return cls.from_counts(**data)

    # -- CLASS-METHODS and STATIC-METHODS:
    @classmethod
    def make_data(cls, data=None, **kwargs):
        """
        Creates data for this class and checks that:

        * only Status values are used
        * converts "status.name" to "status" (from-string conversion)

        :param data:  Dict-like object.
        :param kwargs:  Optional key-value pairs (dict-like).
        :return: Dict object (for this class).
        """
        this_data = cls.ZERO.copy()
        if data is None:
            data = {}
        data.update(**kwargs)

        for key, value in data.items():
            status = key
            if isinstance(key, six.string_types):
                status = Status.from_name(key)
            elif not isinstance(key, Status):
                raise TypeError("other.item.key: %r (expect: Status)" % key)
            this_data[status] = value
        return this_data

    # -- INSTANCE-METHODS:
    @property
    def all(self):
        """Computes the sum of all counts.

        :return: Sum of all counts.
        """
        # -- SINCE Python 3.10: Counter.total()
        # OLD: return sum(self.values())
        return self.total()

    def reset(self):
        """Reset all counters to zero (and keep the counters)."""
        for status in self.keys():
            self[status] = 0

    def increment(self, status=Status.passed, delta=1):
        """Increment one of the counters by a delta value."""
        if not isinstance(status, Status):
            raise TypeError("%r (expected: Status)" % status)
        self[status] += delta

    def as_dict(self):
        """Convert into a dictionary with string keys (instead of: Status).
        This simplifies conversion to JSON or similar formats.
        """
        this_data = OrderedDict()
        for status, value in self.items():
            this_data[status.name] = value
        return this_data

    def get(self, key, default=None):
        if key == "all":
            return self.all
        return super(StatusCounts, self).get(key, default)

    def __getitem__(self, key):
        if key == "all":
            return self.all
        return super(StatusCounts, self).__getitem__(key)

    def __str__(self):
        parts = ["all: %d" % self.all]
        for status in self.ORDER:
            counts = self.get(status, 0)
            if counts:
                parts.append("%s: %d" % (status.name, counts))
        return ", ".join(parts)

    def __repr__(self):
        parts_text = str(self)
        return "<%s: %s>" % (self.__class__.__name__, parts_text)

    def __eq__(self, other):
        if not isinstance(other, (StatusCounts, Counter, dict)):
            raise TypeError("%r (expected: StatusCounts)" % other)

        # -- NORMAL CASE:
        # return list(self.items()) == list(other.items())
        is_same = self.items() == other.items()
        return is_same

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.all > 0

    if six.PY2:
        def __nonzero__(self):
            return self.__bool__()

    # -- ALREADY, SEE: Counter
    # def __iadd__(self, other):
    #     """Adds other to this object.
    #
    #     EXAMPLE::
    #
    #         # Add status_counts2 to status_counts1
    #         status_counts1 = StatusCounts.from_counts(passed=3, failed=1)
    #         status_counts2 = StatusCounts.from_counts(failed=4, skipped=1)
    #         status_counts1 += status_count2
    #         expected = StatusCounts.from_counts(passed=3, failed=5, skipped=1)
    #         assert status_counts1 == expected
    #     """
    #     this_class = self.__class__
    #     if not isinstance(other, this_class):
    #         raise TypeError("%r (expected: %s)" % (other, this_class.__name__))
    #
    #     for status, value in other.items():
    #         self[status] += value
    #
    # def __add__(self, other):
    #     """Adds two objects together.
    #
    #     EXAMPLE::
    #
    #         # Add status_counts2 to status_counts1
    #         status_counts1 = StatusCounts.from_counts(passed=3, failed=1)
    #         status_counts2 = StatusCounts.from_counts(failed=2, skipped=1)
    #         status_counts3 = status_counts1 + status_count2
    #         expected = StatusCounts.from_counts(passed=3, failed=3, skipped=1)
    #         assert status_counts3 == expected
    #     """
    #     counts = self.__class__(self.items())
    #     counts += other
    #     return counts


class HookErrorCounts(Counter):
    """Counters class for keep track of:

    * hook.errors: Any other Exception is raised
    * hook.failed: AssertionError is raised
    """
    # pylint: disable=W0223
    # -- DETAIL: W0223: Method 'fromkeys' is abstract in class 'Counter'
    #    but is not overridden in child class 'HookErrorCounts' (abstract-method)
    ORDER = ["on_feature", "on_rule", "on_scenario", "on_step"]
    ZERO = {
        "on_feature": 0,
        "on_rule": 0,
        "on_scenario": 0,
        "on_step": 0,
    }

    def __init__(self, data=None, **kwargs):
        the_data = self.make_data(data, **kwargs)
        Counter.__init__(self, the_data)

    # -- CONSTRUCTOR-METHODS:
    @classmethod
    def from_counts(cls, on_feature=0, on_rule=0, on_scenario=0, on_step=0):
        return cls(on_feature=on_feature,
                   on_rule=on_rule,
                   on_scenario=on_scenario,
                   on_step=on_step)

    @classmethod
    def from_dict(cls, data):
        require_type(data, dict)
        return cls.from_counts(**data)

    # -- CLASS-METHODS:
    @classmethod
    def make_data(cls, data=None, **kwargs):
        if data is None:
            data = {}
        else:
            data = data.copy()
        data.update(kwargs)
        this_data = cls.ZERO.copy()
        for name in cls.ORDER:
            this_data[name] = data.get(name, 0)
        return this_data

    # -- INSTANCE-METHODS:
    @property
    def all(self):
        return self.total()

    def increment(self, name, delta=1):
        if name not in self.keys():
            raise KeyError(name)
        self[name] += delta

    def items(self):
        for name in self.ORDER:
            value = self.get(name, 0)
            yield name, value

    def as_dict(self):
        return OrderedDict(self.items())

    def get(self, key, default=None):
        if key == "all":
            return self.all
        return super(HookErrorCounts, self).get(key, default)

    def __getitem__(self, key):
        if key == "all":
            return self.all
        return super(HookErrorCounts, self).__getitem__(key)

    def __eq__(self, other):
        if not isinstance(other, (HookErrorCounts, Counter, dict)):
            return False
        if len(self) != len(other):
            return False

        # -- NORMAL CASE:
        for name, value in self.items():
            other_value = other.get(name, None)
            if value != other_value:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return self.items()

    def __str__(self):
        parts = ["all: %s" % self.all]
        for name in self.ORDER:
            counts = self.get(name, 0)
            if counts:
                parts.append("%s: %d" % (name, counts))
        return ", ".join(parts)

    def __repr__(self):
        parts_text = str(self)
        return "<%s: %s>" % (self.__class__.__name__, parts_text)

    def __bool__(self):
        return self.all > 0

    if six.PY2:
        def __nonzero__(self):
            return self.__bool__()

    # -- ALREADY, SEE: Counter
    # def __iadd__(self, other):
    #     require_type(other, (HookErrorCounts, Counter, dict))
    #     for name in self.ORDER:
    #         self[name] += other.get(name, 0)
    #     return self
    #
    # def __add__(self, other):
    #     require_type(other, (HookErrorCounts, Counter, dict))
    #     the_sum = self.__class__(self.items())
    #     the_sum += other
    #     return the_sum


class SummaryCounts(object):
    """Composite value object that contains the counter objects related to:

    * features
    * rules
    * scenarios
    * steps
    * hook_errors (on which level; condition: AssertionError/Exception was raised)
    """
    COUNTERS_CLASS_MAP = {
        "hook_errors": HookErrorCounts,
    }
    ORDER = (
        "features", "rules", "scenarios", "steps", "hook_errors",
    )
    PREFIX = "  "

    def __init__(self):
        self.features = StatusCounts()
        self.rules = StatusCounts()
        self.scenarios = StatusCounts()
        self.steps = StatusCounts()
        self.hook_errors = HookErrorCounts()

    # -- CONSTRUCTOR-METHODS:
    @classmethod
    def from_counts(cls, strict=True, **kwargs):
        other = cls()
        for name in cls.ORDER:
            counts = kwargs.pop(name, None)
            counters_class = cls.COUNTERS_CLASS_MAP.get(name, StatusCounts)
            if counts is not None:
                if not isinstance(counts, counters_class):
                    message = "%r (expected: %s)" % (counts, counters_class)
                    raise TypeError(message)
                setattr(other, name, counts)

        if strict and kwargs:
            bad_params = kwargs.keys()
            raise ValueError("UNEXPECTED: %s" % ", ".join(bad_params))
        return other

    @classmethod
    def from_dict(cls, data, strict=False):
        require_type(data, dict)
        return cls.from_counts(strict=strict, **data)

    # -- INSTANCE-METHOS:
    def items(self):
        for name in self.ORDER:
            value_object = getattr(self, name)
            yield name, value_object

    def as_dict(self, nested=False):
        """Converts into dictionary with string-keys (supports: JSON)."""
        the_data = OrderedDict()
        for name, value_object in self.items():
            if nested:
                # -- USE NESTED DICTS (replace: Counter objects)
                value_object = value_object.as_dict()
            the_data[name] = value_object
        return the_data

    def get(self, key, default=None):
        if key == "all":
            return self.all
        return super(SummaryCounts, self).get(key, default)

    def __len__(self):
        """Returns number of counter categories."""
        return len(self.ORDER)

    def __getitem__(self, key):
        if key == "all":
            return self.all
        return super(SummaryCounts, self).__getitem__(key)

    def __iter__(self):
        """Returns an iterator over the counter categories."""
        return self.items()

    def __bool__(self):
        return any((counts.all > 0) for _, counts in self.items())

    def __eq__(self, other):
        if isinstance(other, dict):
            return other == self.as_dict()
        if not isinstance(other, SummaryCounts):
            return False

        # -- NORMAL CASE:
        return ((self.features == other.features) and
                (self.rules == other.rules) and
                (self.scenarios == other.scenarios) and
                (self.steps == other.steps) and
                (self.hook_errors == other.hook_errors))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iadd__(self, other):
        """Implements inplace-addition: ``self += other``"""
        if isinstance(other, dict):
            this_class = self.__class__
            other = this_class.from_counts(**other)

        for name, value in self.items():
            other_value = getattr(other, name, 0)
            value += other_value
        return self

    def __add__(self, other):
        """Implements addition: ``self + other``"""
        counts_sum = self.__class__(self.items())
        counts_sum += other
        return counts_sum

    def __str__(self):
        """Converts this object into string representation."""
        schema = "{name: >9s}: {value}"
        parts = []
        for name, value in self.items():
            if value.all and name != "features":
                # -- SHOW ONLY: NON-ZERO parts (information compression).
                text = schema.format(name=name, value=value)
                parts.append(text)
        line_seperator = u"\n%s" % self.PREFIX
        return line_seperator.join(parts)

    def __repr__(self):
        text = str(self).replace("\n", ";\n  ").strip()
        return "<%s: %s>" % (self.__class__.__name__, text)

    if six.PY2:
        def __nonzero__(self):
            return self.__bool__()


# -----------------------------------------------------------------------------
# PROCESSOR(s)
# -----------------------------------------------------------------------------
class SummaryCollector(ModelVisitor):
    """Collect summary counts information from feature(s).

    EXAMPLE:

    .. code-block:: py

        from behave.summary import SummaryCounts, SummaryProcessor

        features = ...  # OUT_OF_SCOPE
        summary_counts = SummaryCounts()
        collector = SummaryCollector(summary_counts)
        collector.visit_many(features)
        print(summary_counts)
        # OR: collector.visit_feature(feature)
        # OR: collector.visit_scenario(scenario)
    """

    def __init__(self, summary_counts=None):
        super(SummaryCollector, self).__init__(visitor=self)
        if summary_counts is None:
            summary_counts = SummaryCounts()
        self.summary_counts = summary_counts
        self.duration = 0.0
        self.failed_features = []
        self.failed_scenarios = []
        self.errored_features = []
        self.errored_scenarios = []
        self.pending_features = []
        self.pending_scenarios = []

    def reset(self):
        self.summary_counts.reset()
        self.duration = 0.0
        self.failed_features = []
        self.failed_scenarios = []
        self.errored_features = []
        self.errored_scenarios = []

    def has_failures_or_errors(self):
        return (bool(self.failed_features) or bool(self.failed_scenarios) or
                bool(self.errored_features) or bool(self.errored_scenarios))

    # -- IMPLEMENT API FOR: IModelVisitor
    def on_feature(self, feature):
        if feature.status == Status.failed:
            self.failed_features.append(feature)
        elif feature.status == Status.error:
            self.errored_features.append(feature)

        self.duration += feature.duration
        self.summary_counts.features.increment(feature.status)
        if feature.hook_failed:
            self.summary_counts.hook_errors.increment("on_feature")

    def on_rule(self, rule):
        self.summary_counts.rules.increment(rule.status)
        if rule.hook_failed:
            self.summary_counts.hook_errors.increment("on_rule")

    def on_scenario(self, scenario):
        if scenario.status == Status.failed:
            self.failed_scenarios.append(scenario)
        elif scenario.status == Status.error:
            self.errored_scenarios.append(scenario)

        self.summary_counts.scenarios.increment(scenario.status)
        if scenario.hook_failed:
            self.summary_counts.hook_errors.increment("on_scenario")

    def on_step(self, step):
        self.summary_counts.steps.increment(step.status)
        if step.hook_failed:
            self.summary_counts.hook_errors.increment("on_step")
