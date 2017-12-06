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

from xoeuf.odoo.addons.xopgi_mail_threads import MailTransportRouter


class TestTransport(MailTransportRouter):
    @classmethod
    def query(cls, obj, message):
        return False, None

    def prepare_message(self, obj, message, data=None):
        return super(TestTransport, self).prepare_message(
            obj,
            message,
            data=data
        )

    def deliver(self, obj, message, data, **kwargs):
        return super(TestTransport, self).deliver(obj, message, data, **kwargs)
