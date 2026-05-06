"""
Regression tests for issue #1320:
Auto-promote raw ``bool`` provider values to :class:`BoolValueObject`.

Without auto-promotion, ``ActiveTagMatcher`` wraps a raw ``bool`` in the base
``ValueObject``, which compares with ``operator.eq``. Tag values from a
feature file are always strings, so ``operator.eq(True, "true")`` is ``False``
and bool active-tag matching silently never matches.
"""

import pytest

from behave.tag_matcher import (
    ActiveTagMatcher,
    BoolValueObject,
    ValueObject,
    setup_active_tag_values,
)


class TestIssue1320BoolAutoPromotion:
    @pytest.mark.parametrize(
        "provider_value, tag_value, expected_enabled",
        [
            (True, "true", True),
            (True, "false", False),
            (False, "true", False),
            (False, "false", True),
            # BoolValueObject.to_bool also accepts these spellings.
            (True, "yes", True),
            (True, "on", True),
            (False, "no", True),
            (False, "off", True),
        ],
    )
    def test_use_with_bool_provider_value(
        self, provider_value, tag_value, expected_enabled
    ):
        provider = {"flag": "undefined"}
        matcher = ActiveTagMatcher(provider)
        setup_active_tag_values(provider, {"flag": provider_value})

        tag = matcher.make_category_tag("flag", tag_value)
        # `should_skip_with_tags` is the inverse of "enabled".
        assert matcher.should_skip_with_tags([tag]) is (not expected_enabled)

    def test_explicit_bool_value_object_still_works(self):
        """Users who already wrap in BoolValueObject must not regress."""
        provider = {"flag": "undefined"}
        matcher = ActiveTagMatcher(provider)
        setup_active_tag_values(provider, {"flag": BoolValueObject(True)})

        tag = matcher.make_category_tag("flag", "true")
        assert matcher.should_skip_with_tags([tag]) is False

    def test_string_provider_value_unchanged(self):
        """Non-bool provider values still go through the plain ValueObject path."""
        provider = {"name": "undefined"}
        matcher = ActiveTagMatcher(provider)
        setup_active_tag_values(provider, {"name": "alice"})

        assert matcher.should_skip_with_tags([matcher.make_category_tag("name", "alice")]) is False
        assert matcher.should_skip_with_tags([matcher.make_category_tag("name", "bob")]) is True


class TestIssue1320ValueObjectFromRaw:
    def test_from_raw_promotes_bool(self):
        wrapped = ValueObject.from_raw(True)
        assert type(wrapped) is BoolValueObject
        assert wrapped.value is True

    def test_from_raw_leaves_strings_alone(self):
        wrapped = ValueObject.from_raw("alice")
        assert type(wrapped) is ValueObject
        assert wrapped.value == "alice"

    def test_from_raw_does_not_promote_int(self):
        # bool is a subclass of int -- make sure plain ints stay as ValueObject
        # so we don't accidentally change number-handling semantics.
        wrapped = ValueObject.from_raw(42)
        assert type(wrapped) is ValueObject
        assert wrapped.value == 42
