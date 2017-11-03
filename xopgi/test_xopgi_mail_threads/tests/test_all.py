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
    from unittest.mock import patch, DEFAULT
except ImportError:
    from mock import patch, DEFAULT
from xoeuf.odoo.tests.common import TransactionCase

from ..router import TestRouter
from ..transport import TestTransport

MESSAGE = '''Delivered-To: default-xopgi-mailthread-model@localhost
To: default-xopgi-mailthread-model@localhost
From: someone@localhost
Subject: Incomming Message

This is a message.

'''


class RouterCase(TransactionCase):
    # So that routers are actually installed, otherwise they are 'to install'
    post_install = True
    at_install = not post_install

    def setUp(self):
        super(RouterCase, self).setUp()
        self.alias = self.env['mail.alias'].create({
            'alias_name': 'default-xopgi-mailthread-model',
            'alias_model_id': self.env.ref('test_xopgi_mail_threads.model_test_xopgi_thread_model').id
        })

    def tearDown(self):
        self.alias.unlink()
        super(RouterCase, self).tearDown()


@patch.multiple(TestRouter, query=DEFAULT, apply=DEFAULT)
class TestReceivingMails(RouterCase):
    def test_calls_router_query(self, query, apply):
        Mailer = self.env['mail.thread']
        message = MESSAGE
        Mailer.message_process(
            'bouncer',
            message,
            save_original=False,
            strip_attachments=False,
        )
        self.assertTrue(query.called)
        self.assertFalse(apply.called)

    def test_calls_router_apply(self, query, apply):
        Mailer = self.env['mail.thread']
        message = 'X-Passing: Ok\nX-Passing-Payload: Payload\n'
        message += MESSAGE
        Mailer.message_process(
            'bouncer',
            message,
            save_original=False,
            strip_attachments=False,
        )
        self.assertTrue(query.called)
        self.assertTrue(apply.called)


@patch.multiple(TestTransport,
                query=DEFAULT, prepare_message=DEFAULT, deliver=DEFAULT)
class TestSendingMessages(RouterCase):
    def test_calls_transport_query(self, query, prepare_message, deliver):
        message = email.message_from_string(MESSAGE)
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertFalse(prepare_message.called)
        self.assertFalse(deliver.called)

    def test_calls_transport_prepare_and_deliver(self, query, prepare_message, deliver):
        message = email.message_from_string(
            'X-Passing: Ok\nX-Passing-Payload: Payload\n' + MESSAGE
        )
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertTrue(prepare_message.called)
        self.assertTrue(deliver.called)
