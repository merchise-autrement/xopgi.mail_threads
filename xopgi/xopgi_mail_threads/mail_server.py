#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''General outgoing server selection.

Allow to specify rules about which outgoing SMTP server to choose.  Actually,
simply ensures that mail-sending facilities of OpenERP check for more options
when the "default" server is to be chosen.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


# TODO: Review with gevent-based model.
from xoutil.context import context as execution_context
from xoutil import logger as _logger

from xoeuf.models import Model
from xoeuf import api

import logging
logger = logging.getLogger(__name__)
del logging


class MailServer(Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email(self, message, **kw):
        '''Sends an email.

        Overrides the basic OpenERP's sending to allow transports to kick in.
        Basically it selects a transport and delivers the email with it if
        possible.

        The transport may choose to deliver the email by itself.  In this case
        the basic OpenERP is not used (unless the transport uses the provided
        `direct_send`:func: function).

        Otherwise, the transport may change the message to be deliver and the
        connection data.

        It is strongly suggested that transport only change headers and
        connection data.

        '''
        _super = super(MailServer, self).send_email
        if DIRECT_SEND_CONTEXT not in execution_context:
            logger.debug('Sending email with available transports.')
            transport = None
            try:
                from .transports import MailTransportRouter as transports
                mail_server_id = kw.get('mail_server_id', None)
                smtp_server = kw.get('smtp_server', None)
                if neither(mail_server_id, smtp_server):
                    transport, querydata = transports.select(
                        self, message
                    )
                    if transport:
                        logger.debug('Selected transport: %r.', transport)
                        with transport:
                            message, conndata = transport.prepare_message(
                                self, message,
                                data=querydata,
                            )
                            return transport.deliver(
                                self, message, conndata, **kw
                            )
            except Exception as e:
                from openerp.addons.base.ir.ir_mail_server import \
                    MailDeliveryException
                if not isinstance(e, MailDeliveryException):
                    _logger.exception(
                        'Transport %s failed. Falling back',
                        transport,
                        extra=dict(message_from=message.get('From'),
                                   message_to=message.get('To'),
                                   message_cc=message.get('Cc'),
                                   message_subject=message.get('Subject'))
                    )
                else:
                    raise
        return _super(message, **kw)

    @api.model
    def send_without_transports(self, message, **kw):
        '''Send a message without using third-party transports.'''
        with execution_context(DIRECT_SEND_CONTEXT):
            self.send_email(message, **kw)


DIRECT_SEND_CONTEXT = object()
neither = lambda *args: all(not a for a in args)
