#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Transient models used as default route for incoming messages with no route.

Bounce is needed for cases when notification of no valid address must reach
sender.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, models

import logging

_logger = logging.getLogger(__name__)
del logging


class NoRouteBounce(models.TransientModel):
    _name = 'noroute.bounce.model'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        '''Create a bounce to notify sender.

        When a router can't find a route for the message, a default one will
        be created using this model. Anyway, in some cases, a bounce it's
        needed for that the sender can be notified about the message not
        delivered to the recipient because no valid address was given.

        '''
        bounce_body_html = """<div> <p>Hello,</p> <p>The following email sent
        to %s was not delivered because no valid address was given.</p>
        </div><blockquote>%s</blockquote>""" % (msg_dict.get('to'),
                                                msg_dict.get('body'))
        MailThread = self.env['mail.thread']
        MailThread._routing_create_bounce_email(msg_dict.get('from'),
                                                bounce_body_html,
                                                custom_values['message'])

        return False

    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        # Conceptually this is not needed, cause its purpose is to update the
        # object record from an email data.  Being a 'helper' model we mustn't
        # modify any record for that sort of thing.
        return False

    @api.multi
    def message_post(self, **kwargs):
        return False


class NoRouteIgnore(models.TransientModel):
    _name = 'mail.ignore.model'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        ''' Message with default route.

        When a router can't find a route for the message, a default one will
        be created using this model. This way all incoming messages will be
        processed in a proper manner.

        '''
        return False

    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        # Conceptually this is not needed, cause its purpose is to update the
        # object record from an email data.  Being a 'helper' model  we mustn't
        # modify any record for that sort of thing.
        return False

    @api.multi
    def message_post(self, **kwargs):
        return False
