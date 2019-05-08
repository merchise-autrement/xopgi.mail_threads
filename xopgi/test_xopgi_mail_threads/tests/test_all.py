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

from xoeuf import MAJOR_ODOO_VERSION
from xoeuf.odoo.tests.common import TransactionCase, at_install, post_install
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


if MAJOR_ODOO_VERSION < 12:
    class RouterCase(TransactionCase):
        # So that routers are actually installed, otherwise they are 'to
        # install'
        post_install = True
        at_install = not post_install

    def at_install(flag):        # noqa
        return lambda obj: obj

    post_install = at_install   # noqa
else:
    RouterCase = TransactionCase


class TransportCase(RouterCase):
    def setUp(self):
        super(TransportCase, self).setUp()
        # The addon 'mail' patches 'send_mail'; we need to revert that or
        # else our transport are not called.
        self._unpatch_send_email()

    def _unpatch_send_email(self):
        # The pair of methods _patch_method and _revert_method are
        # ill-defined.  In this case: the tests of the addon 'mail' patch
        # the ir.mail_server, and revert, this causes the Model Class to
        # be modified with by setting the 'origin' code of in the Model
        # Class.  The Model Class should be empty: so we simply remove the
        # send_email method and allow the MRO to execute smoothly.
        try:
            del type(self.env['ir.mail_server']).mro()[0].send_email
        except:  # noqa
            pass


@patch.object(TestRouter, 'query', return_value=NO)
@patch.object(TestRouter, 'apply')
@at_install(False)
@post_install(True)
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
@at_install(False)
@post_install(True)
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
@at_install(False)
@post_install(True)
class TestSendingMessagesFalsyTransport(TransportCase):
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
@at_install(False)
@post_install(True)
class TestSendingMessagesTruishTransport(TransportCase):
    def test_calls_transport_prep_and_deliver(self, query, prepare_message,
                                              deliver):
        message = email.message_from_string(MESSAGE)
        self.env['ir.mail_server'].send_email(message)
        self.assertTrue(query.called)
        self.assertTrue(prepare_message.called)
        self.assertTrue(deliver.called)
