# -*- coding: UTF-8 -*-
"""
This module provides the abstract base classes and core concepts
for the model elements in behave.
"""

import os.path
import sys
import six
from behave.capture import Captured
from behave.textutil import text as _text
from enum import Enum


PLATFORM_WIN = sys.platform.startswith("win")


def posixpath_normalize(path):
    return path.replace("\\", "/")


def make_relpath_if_possible(filename, base_directory=None):
    if base_directory is None:
        base_directory = os.getcwd()

    try:
        # -- NEEDS: abspath?
        filename = os.path.relpath(filename, base_directory)
    except ValueError:
        # -- WINDOWS: Different drives used for filename, base_directory
        # RELATED TO: Issue #599
        # MAYBE: filename = os.path.abspath(filename)
        pass
    return filename


# -----------------------------------------------------------------------------
# GENERIC MODEL CLASSES:
# -----------------------------------------------------------------------------
class Status(Enum):
    """Provides the (test-run) status of a model element.
    Features and Scenarios use: untested, skipped, passed, failed.
    Steps may use all enum-values.

    Enum values:
    * untested (initial state):

        Defines the initial state before a test-run.
        Sometimes used to indicate that the model element was not executed
        during a test run.

    * skipped:

        A model element is skipped because it should not run.
        This is caused by filtering mechanisms, like tags, active-tags,
        file-location arg, select-by-name, etc.

    * passed: Model element is executed and passed (without failures).
    * failed: Model element is executed and assert-condition failed.
    * error:  Model element is executed and raised an exception (unexpected).
    * hook_error:    Failure occured while executing a hook.
    * pending:       Pending step that leads to an error.
    * pending_warn:  Pending step that leads is accepted/passed.
    * undefined:     If a step does not exist (no step implementation was found).
    * untested_pending:   RESERVED: If a pending step is untested (in dry-run mode).
    * untested_undefined: If an undefined step is untested (in dry-run mode).
    * executing: Marks the steps during execution (used in a formatter)

    .. versionadded:: 1.2.6
        Supersedes string-based status values.
    """
    unknown = 0         # RESERVED: For special cases.
    untested = 1
    executing = 2       # Used while executing a model element.
    skipped = 10
    passed = 11
    xfailed = 12        # RESERVED: Used if expected to fail (marked with: @xfail tag)
    xpassed = 13        # RESERVED: Used if xfailed model-element passes.
    failed = 20         # If assertion fails (and currently: exception occurs)
    error = 21          # If unexpected exception occurs.
    hook_error = 22     # If a hook has failed.
    cleanup_error = 23  # RESERVED: If exception occurs in cleanup-phase/cleanup-function.
    # -- FOR STEPS:
    undefined = 30          # If a step is undefined/unregistered (results in error).
    pending = 31            # Pending-step (registered but not implemented; results in error)
    pending_warn = 32       # Pending step that is gracefully accepted
    untested_pending = 33   # RESERVED: Pending step as untested step (in dry-run mode)
    untested_undefined = 34 # Undefined steps as untested step (in dry-run mode).

    @property
    def normalized_name(self):
        if self is Status.untested_undefined:
            return Status.undefined.name
        elif self in (Status.pending_warn, Status.untested_pending):
            return Status.pending.name
        return self.name

    def __eq__(self, other):
        """Comparison operator equals-to other value.
        Supports other enum-values and string (for backward compatibility).

        EXAMPLES::

            status = Status.passed
            assert status == Status.passed
            assert status == "passed"
            assert status != "failed"

        :param other:   Other value to compare (enum-value, string).
        :return: True, if both values are equal. False, otherwise.
        """
        if isinstance(other, six.string_types):
            # -- CONVENIENCE: Compare with string-name (backward-compatible)
            return self.name == other
        return super(Status, self).__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def has_failed(self):
        return self.is_error() or self.is_failure()

    def is_passed(self):
        return self in (Status.passed, Status.xfailed, Status.xpassed,
                        Status.pending_warn)

    def is_failure(self):
        return self is Status.failed

    def is_error(self):
        return self in (Status.error, Status.hook_error, Status.cleanup_error,
                        Status.undefined, Status.pending)

    def is_untested(self):
        return self in (Status.untested,
                        Status.untested_undefined,
                        Status.untested_pending)

    def is_pending(self):
        return self in (Status.pending, Status.pending_warn, Status.untested_pending)

    def is_undefined(self):
        return self in (Status.undefined, Status.untested_undefined)

    def is_final(self):
        """
        Indicates that this status is a final-status.
        """
        return self in (Status.skipped, Status.passed,
                        Status.xfailed, Status.xpassed,
                        Status.failed, Status.error,
                        Status.hook_error,
                        # -- USED FOR: STEP is not found/registered
                        Status.undefined, Status.untested_undefined,
                        # -- USED FOR: Registered step -- NotImplementedStep/PendingStep
                        Status.pending, Status.pending_warn)

    def to_status_v0(self):
        # -- BACKWARD COMPATIBLE STATUS: Convert new enum-values to old ones.
        cls = self.__class__
        status_v0_values = [
            cls.untested,
            cls.skipped,
            cls.passed,
            cls.failed,
            cls.undefined,
            cls.executing,
        ]
        if self.is_error():
            return Status.failed
        elif self.is_pending():
            return Status.undefined
        elif self in status_v0_values:
            return self
        assert False, "OOPS: status=%s" % self
        return Status.unknown

    @classmethod
    def from_name(cls, name):
        """Select enumeration value by using its name.

        :param name:    Name as key to the enum value (as string).
        :return: Enum value (instance)
        :raises: LookupError, if status name is unknown.
        """
        # pylint: disable=no-member
        enum_value = cls.__members__.get(name, None)
        if enum_value is None:
            known_names = ", ".join(cls.__members__.keys())
            raise LookupError("%s (expected: %s)" % (name, known_names))
        return enum_value


class ScenarioStatus(object):
    """
    Utility class that computes the Scenario status from one of its steps.
    """
    @staticmethod
    def from_step_status(step_status, dry_run=False):
        assert isinstance(step_status, Status)
        other_status_values = (Status.skipped, )
        if step_status.is_error():
            # -- CASE 1: hook_error, pending-step, undefined-step as error
            return Status.error
        elif step_status.is_failure():
            return Status.failed
        elif step_status.is_untested():
            # -- SPECIAL CASE: In dry-run with undefined-step discovery
            #    Undefined steps should not cause failed scenario.
            return Status.untested
        elif step_status is Status.pending_warn:
            # -- IGNORE: pending-step (as passed in CASE 1)
            step_status = Status.passed
        elif step_status != Status.passed:
            assert step_status in other_status_values, "status=%s" % step_status
            return step_status
        return Status.passed

    @classmethod
    def from_step(cls, step, dry_run=False):
        return cls.from_step_status(step.status, dry_run=dry_run)


class OuterStatus(object):
    """
    Used for feature(s) and rule(s) to derive their status
    from one of its contained model-elements (like: scenarios).
    """

    @staticmethod
    def from_inner_status(status):
        assert isinstance(status, Status)
        if status.is_error():
            return Status.error
        elif status.is_failure():
            return Status.failed
        elif status is Status.pending_warn:
            # -- FOR: Scenario.status based on contained step(s)
            return Status.passed
        # -- OTHERWISE:
        return status

    @classmethod
    def from_inner_model_element(cls, model_element):
        return cls.from_inner_status(model_element.status)


class Argument(object):
    """An argument found in a *feature file* step name.

    The attributes are:

    .. attribute:: original

       The actual text matched in the step name.

    .. attribute:: value

       The potentially type-converted value of the argument.

    .. attribute:: name

       The name of the argument.
       This will be None if the parameter is anonymous.

    .. attribute:: start

       The start index in the step name of the argument. Used for display.

    .. attribute:: end

       The end index in the step name of the argument. Used for display.
    """
    def __init__(self, start, end, original, value, name=None):
        self.start = start
        self.end = end
        self.original = original
        self.value = value
        self.name = name


# @total_ordering
# class FileLocation(unicode):
class FileLocation(object):
    """
    Provides a value object for file location objects.
    A file location consists of:

      * filename
      * line (number), optional

    LOCATION SCHEMA:
      * "{filename}:{line}" or
      * "{filename}" (if line number is not present)
    """

    def __init__(self, filename, line=None):
        if PLATFORM_WIN:
            filename = posixpath_normalize(filename)
        self.filename = filename
        self.line = line

    def get(self):
        return self.filename

    def abspath(self):
        return os.path.abspath(self.filename)

    def basename(self):
        return os.path.basename(self.filename)

    def dirname(self):
        return os.path.dirname(self.filename)

    def relpath(self, start=os.curdir):
        """Compute relative path for start to filename.

        :param start: Base path or start directory (default=current dir).
        :return: Relative path from start to filename
        """
        return make_relpath_if_possible(self.filename, start)

    def exists(self):
        return os.path.exists(self.filename)

    def _line_lessthan(self, other_line):
        if self.line is None:
            # return not (other_line is None)
            return other_line is not None
        elif other_line is None:
            return False
        else:
            return self.line < other_line

    def __eq__(self, other):
        if isinstance(other, FileLocation):
            return self.filename == other.filename and self.line == other.line
        elif isinstance(other, six.string_types):
            return self.filename == other
        else:
            raise TypeError("Cannot compare FileLocation with %s:%s" % \
                            (type(other), other))

    def __ne__(self, other):
        # return not self == other    # pylint: disable=unneeded-not
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, FileLocation):
            if self.filename < other.filename:
                return True
            elif self.filename > other.filename:
                return False
            else:
                assert self.filename == other.filename
                return self._line_lessthan(other.line)

        elif isinstance(other, six.string_types):
            return self.filename < other
        else:
            raise TypeError("Cannot compare FileLocation with %s:%s" % \
                            (type(other), other))

    def __le__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # return not other < self     # pylint unneeded-not
        return other >= self

    def __gt__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        if isinstance(other, FileLocation):
            return other < self
        else:
            return self.filename > other

    def __ge__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # return not self < other
        return not self.__lt__(other)

    def __repr__(self):
        return u'<FileLocation: filename="%s", line=%s>' % \
               (self.filename, self.line)

    def __str__(self):
        filename = self.filename
        if isinstance(filename, six.binary_type):
            filename = _text(filename, "utf-8")
        if self.line is None:
            return filename
        return u"%s:%d" % (filename, self.line)

    if six.PY2:
        __unicode__ = __str__
        __str__ = lambda self: self.__unicode__().encode("utf-8")

    @classmethod
    def for_function(cls, func, curdir=None):
        """Extracts the location information from the function and builds
        the location string (schema: "{source_filename}:{line_number}").

        :param func: Function whose location should be determined.
        :return: FileLocation object
        """
        func = unwrap_function(func)
        function_code = six.get_function_code(func)
        filename = function_code.co_filename
        line_number = function_code.co_firstlineno

        curdir = curdir or os.getcwd()
        filename = make_relpath_if_possible(filename, curdir)
        return cls(filename, line_number)


# -----------------------------------------------------------------------------
# ABSTRACT MODEL CLASSES (and concepts):
# -----------------------------------------------------------------------------
class BasicStatement(object):
    def __init__(self, filename, line, keyword, name):
        filename = filename or '<string>'
        filename = make_relpath_if_possible(filename, os.getcwd())   # -- NEEDS: abspath?
        self.location = FileLocation(filename, line)
        assert isinstance(keyword, six.text_type), "ACTUAL: %s:%r" % (type(keyword), keyword)
        assert isinstance(name, six.text_type), "ACTUAL: %s:%r" % (type(keyword), keyword)
        self.keyword = keyword
        self.name = name
        # -- SINCE: 1.2.6
        self.captured = Captured()
        # -- ERROR CONTEXT INFO:
        self.exception = None
        self.exc_traceback = None
        self.error_message = None

    @property
    def filename(self):
        # return os.path.abspath(self.location.filename)
        return self.location.filename

    @property
    def line(self):
        return self.location.line

    def reset(self):
        # -- RESET: Captured output data
        self.captured.reset()
        # -- RESET: ERROR CONTEXT INFO
        self.exception = None
        self.exc_traceback = None
        self.error_message = None

    def store_exception_context(self, exception):
        self.exception = exception
        self.exc_traceback = sys.exc_info()[2]

    def __hash__(self):
        # -- NEEDED-FOR: PYTHON3
        # return id((self.keyword, self.name))
        return id(self)

    def __eq__(self, other):
        # -- PYTHON3 SUPPORT, ORDERABLE:
        # NOTE: Ignore potential FileLocation differences.
        return (self.keyword, self.name) == (other.keyword, other.name)

    def __lt__(self, other):
        # -- PYTHON3 SUPPORT, ORDERABLE:
        # NOTE: Ignore potential FileLocation differences.
        return (self.keyword, self.name) < (other.keyword, other.name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # return not other < self
        return other >= self

    def __gt__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        assert isinstance(other, BasicStatement)
        return other < self

    def __ge__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        # OR: return self >= other
        return not self < other     # pylint: disable=unneeded-not

    # def __cmp__(self, other):
    #     # -- NOTE: Ignore potential FileLocation differences.
    #     return cmp((self.keyword, self.name), (other.keyword, other.name))


class TagStatement(BasicStatement):

    def __init__(self, filename, line, keyword, name, tags):
        if tags is None:
            tags = []
        super(TagStatement, self).__init__(filename, line, keyword, name)
        self.tags = tags

    def should_run_with_tags(self, tag_expression):
        """Determines if statement should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if examples should run. False, otherwise (skip it).
        """
        return tag_expression.check(self.tags)


class TagAndStatusStatement(BasicStatement):
    """Base class for statements with:

    * tags (as: taggable statement)
    * status (has a result after a test run)
    """

    def __init__(self, filename, line, keyword, name, tags, parent=None):
        super(TagAndStatusStatement, self).__init__(filename, line, keyword, name)
        self.parent = parent    # Container for this entity; None for feature.
        self.tags = tags
        self.should_skip = False
        self.skip_reason = None
        self._cached_status = Status.untested

    @property
    def effective_tags(self):
        """Compute effective tags of this entity.
        This is includes the own tags and the inherited tags from the parents.

        :return: Set of effective tags

        .. versionadded:: 1.2.7
        """
        tags = set(self.tags)
        if self.parent:
            # -- INHERIT TAGS: From parent(s), recursively
            inherited_tags = self.parent.effective_tags
            tags.update(inherited_tags)
        return tags

    def should_run_with_tags(self, tag_expression):
        """Determines if statement should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if this statement should run. False, otherwise (skip it).
        """
        return tag_expression.check(self.effective_tags)

    @property
    def status(self):
        if not self._cached_status.is_final():
            # -- RECOMPUTE: As long as final status is not reached.
            self._cached_status = self.compute_status()
        return self._cached_status

    def set_status(self, value):
        if isinstance(value, six.string_types):
            value = Status.from_name(value)
        self._cached_status = value

    def clear_status(self):
        self._cached_status = Status.untested

    def reset(self):
        self.should_skip = False
        self.skip_reason = None
        self.clear_status()

    def compute_status(self):
        raise NotImplementedError()


class Replayable(object):
    type = None

    def replay(self, formatter):
        getattr(formatter, self.type)(self)


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def unwrap_function(func, max_depth=10):
    """Unwraps a function that is wrapped with :func:`functools.partial()`"""
    iteration = 0
    wrapped = getattr(func, "__wrapped__", None)
    while wrapped and iteration < max_depth:
        func = wrapped
        wrapped = getattr(func, "__wrapped__", None)
        iteration += 1
    return func
