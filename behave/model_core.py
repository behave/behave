# -*- coding: UTF-8 -*-
"""
This module provides the abstract base classes and core concepts
for the model elements in behave.
"""

import os.path
import sys
import six
from behave.capture import ManyCaptured, CaptureSinkAsCollector
from behave.constant import CAPTURE_SINK_STORE_CAPTURED_ON_SUCCESS
from behave.model_type import (
    FileLocation, Status,
    make_relpath_if_possible,
)


# -----------------------------------------------------------------------------
# ABSTRACT MODEL CLASSES (and concepts):
# -----------------------------------------------------------------------------
class BasicStatement(object):
    STORE_CAPTURED_ON_SUCCESS = CAPTURE_SINK_STORE_CAPTURED_ON_SUCCESS

    def __init__(self, filename, line, keyword, name):
        if not isinstance(keyword, six.text_type):
            raise TypeError("keyword: {type_}:{value} (expected: {text_type})".format(
                type_=type(keyword).__name__, value=keyword,
                text_type=six.text_type.__name__
            ))
        if not isinstance(name, six.text_type):
            raise TypeError("name: {type_}:{value} (expected: {text_type})".format(
                type_=type(name).__name__, value=name,
                text_type=six.text_type.__name__
            ))

        filename = filename or '<string>'
        filename = make_relpath_if_possible(filename, os.getcwd())   # -- NEEDS: abspath?
        self.location = FileLocation(filename, line)
        self.keyword = keyword
        self.name = name
        # -- SINCE: 1.2.6 as Captured
        # CHANGED IN: 1.2.7 from Captured to ManyCaptured
        # NOTE: Protect against assignment.
        self._captured = ManyCaptured()
        self._capture_sink = CaptureSinkAsCollector(self._captured)
        self._capture_sink.store_on_success = self.STORE_CAPTURED_ON_SUCCESS
        # -- ERROR CONTEXT INFO:
        self.exception = None
        self.exc_traceback = None
        self.error_message = None

    @property
    def captured(self):
        return self._captured

    @property
    def capture_sink(self):
        return self._capture_sink

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
        if not isinstance(other, BasicStatement):
            raise TypeError("other: {!r} (expected: BasicStatement)".format(other))
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
    def inherited_tags(self):
        """
        Compute the inherited tags of this entity (if any exist).

        :return: Set of inherited tags

        .. versionadded:: 1.2.7
        """
        if not self.parent:
            return set()

        # -- RECURSION CHAIN: self.parent ...
        return self.parent.effective_tags

    @property
    def effective_tags(self):
        """
        Compute effective tags of this entity.
        This includes the own tags and the inherited tags from the parents.

        :return: Set of effective tags

        .. versionadded:: 1.2.7
        """
        tags = set(self.tags)
        tags.update(self.inherited_tags)
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
        if value is Status.cleanup_error:
            if self._cached_status is Status.hook_error:
                # -- IGNORE: Status.cleanup_error
                return
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
