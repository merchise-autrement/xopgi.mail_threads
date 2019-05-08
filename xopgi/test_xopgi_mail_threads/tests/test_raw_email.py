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

from xoeuf.modules import get_caller_addon
from xoeuf.odoo.modules.module import get_resource_path
from xoeuf.odoo.tests.common import TransactionCase


class TestRawEmail(TransactionCase):
    def test_attachment_without_a_content_type_with_NUL(self):
        path = get_resource_path(
            get_caller_addon(),
            'data',
            'invalid-ct-with-nuls.txt'
        )
        with open(path, 'rb') as f:
            self.env['mail.thread'].message_process(
                'bouncer',
                f.read()
            )
