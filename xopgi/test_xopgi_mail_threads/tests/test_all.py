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

YES = (True, None)
NO = (False, None)


class RouterCase(TransactionCase):
    # So that routers are actually installed, otherwise they are 'to install'
    post_install = True
    at_install = not post_install


@patch.object(TestRouter, 'query', return_value=NO)
@patch.object(TestRouter, 'apply')
class TestReceivingMailsFalsyQuery(RouterCase):
    def test_calls_router_query(self, apply, query):
        Mailer = self.env['mail.thread']
        Mailer.message_process(
            'bouncer',
            MESSAGE,
            save_original=False,
            strip_attachments=False,
        )
        self.assertTrue(query.called)
        self.assertFalse(apply.called)


@patch.object(TestRouter, 'query', return_value=YES)
@patch.object(TestRouter, 'apply')
class TestReceivingMailsTruishQuery(RouterCase):
    def test_calls_router_apply(self, apply, query):
        Mailer = self.env['mail.thread']
        Mailer.message_process(
            'bouncer',
            MESSAGE,
            save_original=False,
            strip_attachments=False,
        )
        self.assertTrue(query.called)
        self.assertTrue(apply.called)



@patch.object(TestTransport, 'query', return_value=NO)
@patch.multiple(TestTransport, prepare_message=DEFAULT, deliver=DEFAULT)
class TestSendingMessagesFalsyTransport(RouterCase):
    def test_calls_transport_query(self, query, prepare_message, deliver):
        message = email.message_from_string(MESSAGE)
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertFalse(prepare_message.called)
        self.assertFalse(deliver.called)


PREPARED_MESSAGE = TransportRouteData(email.message_from_string(MESSAGE), {})


@patch.object(TestTransport, 'deliver')
@patch.object(TestTransport, 'prepare_message', return_value=PREPARED_MESSAGE)
@patch.object(TestTransport, 'query', return_value=YES)
class TestSendingMessagesTruishTransport(RouterCase):
    def test_calls_transport_prep_and_deliver(self, query, prepare_message,
                                              deliver):
        message = email.message_from_string(MESSAGE)
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertTrue(prepare_message.called)
        self.assertTrue(deliver.called)
