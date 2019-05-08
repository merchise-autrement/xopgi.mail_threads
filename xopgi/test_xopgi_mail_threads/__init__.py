#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from .model import *  # noqa
from .router import TestRouter  # noqa
from .transport import TestTransport  # noqa


def _assert_test_mode(cr, registry, *args):
    from xoeuf import odoo
    if not odoo.tools.config['test_enable']:
        raise RuntimeError(
            'You cannot install a test addon in a production DB'
        )
