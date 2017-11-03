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

from xoeuf.odoo.addons.xopgi_mail_threads import MailRouter


class TestRouter(MailRouter):
    @classmethod
    def query(cls, obj, message):
        return bool(message['X-Passing']), message['X-Passing-Payload']

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        # Keep the routes.  Only here to watch if called or not
        return routes
