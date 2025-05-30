# -*- coding: utf-8 -*-
"""
Use behave4cmd0 step library (predecessor of behave4cmd).
"""

from __future__ import absolute_import

# -- REGISTER-STEPS FROM STEP-LIBRARY:
# import behave4cmd0.__all_steps__
import behave4cmd0.command_steps
import behave4cmd0.environment_steps
import behave4cmd0.filesystem_steps
import behave4cmd0.workdir_steps
import behave4cmd0.log_steps

import behave4cmd0.failing_steps
import behave4cmd0.passing_steps
import behave4cmd0.note_steps
