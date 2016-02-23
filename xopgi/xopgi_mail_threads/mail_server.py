#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.mail_server
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-15

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

from openerp.osv.orm import Model


neither = lambda *args: all(not a for a in args)


def get_kwargs(func):
    from xoutil.inspect import getfullargspec
    spec = getfullargspec(func)
    argsspec = spec.args
    if argsspec and spec.defaults:
        argsspec = argsspec[-len(spec.defaults):]
    else:
        argsspec = []
    argsspec.extend(spec.kwonlyargs or [])
    return argsspec


class MailServer(Model):
    _inherit = 'ir.mail_server'

    def send_email(self, cr, uid, message, **kw):
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
            transport = None
            try:
                from .transports import MailTransportRouter as transports
                mail_server_id = kw.get('mail_server_id', None)
                smtp_server = kw.get('smtp_server', None)
                context = kw.pop('context', {})
                if neither(mail_server_id, smtp_server):
                    transport, querydata = transports.select(
                        self, cr, uid, message, context=context
                    )
                    if transport:
                        with transport:
                            message, conndata = transport.prepare_message(
                                self, cr, uid, message,
                                data=querydata,
                                context=context
                            )
                            return transport.deliver(
                                self, cr, uid, message, conndata,
                                context=context
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
        return _super(cr, uid, message, **kw)

    def send_without_transports(self, cr, uid, message, **kw):
        '''Send a message without using third-party transports.'''
        with execution_context(DIRECT_SEND_CONTEXT):
            self.send_email(cr, uid, message, **kw)


DIRECT_SEND_CONTEXT = object()
