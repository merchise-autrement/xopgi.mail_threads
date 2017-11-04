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

import email
try:
    from unittest.mock import patch, DEFAULT, create_autospec
except ImportError:
    from mock import patch, DEFAULT, create_autospec
from xoeuf.odoo.tests.common import TransactionCase
from xoeuf.odoo.addons.xopgi_mail_threads import TransportRouteData

from ..router import TestRouter
from ..transport import TestTransport

MESSAGE = '''Delivered-To: default-xopgi-mailthread-model@localhost
To: default-xopgi-mailthread-model@localhost
From: someone@localhost
Subject: Incomming Message

This is a message.

'''

TRUISH_ROUTER_QUERY = create_autospec(
    TestRouter.query,
    return_value=(True, None),
)
FALSY_ROUTER_QUERY = create_autospec(
    TestRouter.query,
    return_value=(False, None),
)


class RouterCase(TransactionCase):
    # So that routers are actually installed, otherwise they are 'to install'
    post_install = True
    at_install = not post_install


@patch.multiple(TestRouter, query=FALSY_ROUTER_QUERY, apply=DEFAULT)
class TestReceivingMailsFalsyQuery(RouterCase):
    def test_calls_router_query(self, query, apply):
        Mailer = self.env['mail.thread']
        Mailer.message_process(
            'bouncer',
            MESSAGE,
            save_original=False,
            strip_attachments=False,
        )
        self.assertTrue(query.called)
        self.assertFalse(apply.called)


@patch.multiple(TestRouter, query=TRUISH_ROUTER_QUERY, apply=DEFAULT)
class TestReceivingMailsTruishQuery(RouterCase):
    def test_calls_router_apply(self, query, apply):
        Mailer = self.env['mail.thread']
        Mailer.message_process(
            'bouncer',
            MESSAGE,
            save_original=False,
            strip_attachments=False,
        )
        self.assertTrue(query.called)
        self.assertTrue(apply.called)


TRUISH_TRANSP_QUERY = create_autospec(
    TestTransport.query,
    return_value=(True, None)
)
FALSY_TRANSP_QUERY = create_autospec(
    TestTransport.query,
    return_value=(False, None)
)
PREPARE_MESSAGE = create_autospec(
    TestTransport.prepare_message,
    return_value=TransportRouteData(email.message_from_string(MESSAGE), {})
)


@patch.multiple(TestTransport, query=FALSY_TRANSP_QUERY,
                prepare_message=DEFAULT, deliver=DEFAULT)
class TestSendingMessagesFalsyTransport(RouterCase):
    def test_calls_transport_query(self, query, prepare_message, deliver):
        message = email.message_from_string(MESSAGE)
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertFalse(prepare_message.called)
        self.assertFalse(deliver.called)


@patch.multiple(TestTransport, query=TRUISH_TRANSP_QUERY,
                prepare_message=PREPARE_MESSAGE, deliver=DEFAULT)
class TestSendingMessagesTruishTransport(RouterCase):
    def test_calls_transport_prep_and_deliver(self, query, prepare_message,
                                              deliver):
        message = email.message_from_string(MESSAGE)
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertTrue(prepare_message.called)
        self.assertTrue(deliver.called)
