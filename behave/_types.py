# -*- coding: UTF-8 -*-
"""Basic types (helper classes)."""


class Unknown(object):
    """Placeholder for unknown/missing information, distinguishable from None.

    .. code-block:: python

        data = {}
        value = data.get("name", Unknown)
        if value is Unknown:
            # -- DO SOMETHING
            ...
    """
