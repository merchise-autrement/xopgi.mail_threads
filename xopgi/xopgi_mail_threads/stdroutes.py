#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Standard routes for bounces and ignores.

See `create_ignore_route` and `create_bounce_route` in the `utils` module.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.objects import get_first_of
from xoeuf import api, models

import logging

_logger = logging.getLogger(__name__)
del logging


BOUNCE_ROUTE_MODEL = 'xopgi.mail_threads.bounce'
IGNORE_MESSAGE_ROUTE_MODEL = 'xopgi.mail_threads.ignore'


class _Base(object):
    # None of the models below actually update or post nothing.
    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        return False

    @api.multi
    def message_post(self, **kwargs):
        # WARNING: Odoo calls this method always (even after calling
        # message_new) and it this method is expected to return a
        # 'mail.message' object.  Odoo 10 and 11 call .write() on the result
        # of this method, but they don't test is actually a message.  Our
        # version of `write` is quite forgiving.
        return self

    @api.multi
    def write(self, vals):
        return True


class SendBounce(_Base, models.TransientModel):
    _name = BOUNCE_ROUTE_MODEL

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        '''Create a bounce to notify sender.

        The original message (`email.Message`:class:) must be passed in the
        'original_message' of `custom_values`.

        '''
        custom_values = custom_values or {}
        bounce_body_html = custom_values.get('bounce_body_html')
        if not bounce_body_html:
            bounce_body_html = """<div> <p>Hello,</p> <p>The following email sent
            to %s was not delivered because no valid address was given.</p>
            </div><blockquote>%s</blockquote>""" % (msg_dict.get('to'),
                                                    msg_dict.get('body'))
        MailThread = self.env['mail.thread']
        # _routing_create_bounce_email DO try to get the 'Return-Path' and
        # falls back to the argument, so we look for the Sender and fall-back
        # to From.
        sender = get_first_of((msg_dict, ), 'Sender', 'From')
        MailThread._routing_create_bounce_email(
            sender,
            bounce_body_html,
            custom_values['original_message'],
        )
        return self.create({}).id


class Ignore(_Base, models.TransientModel):
    _name = IGNORE_MESSAGE_ROUTE_MODEL

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        '''Ignore the message.

        '''
        return self.create({}).id
