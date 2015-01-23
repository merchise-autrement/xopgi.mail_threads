#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.mail_server
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
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

from openerp.osv.orm import Model


neither = lambda *args: all(not a for a in args)


def get_kwargs(func):
    from xoutil.inspect import getfullargspec
    spec = getfullargspec(func)
    return (spec.varkw or []).extend(spec.kwonlyargs or [])


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
            from .transports import MailTransportRouter as transports
            mail_server_id = kw.get('mail_server_id', None)
            smtp_server = kw.get('smtp_server', None)
            context = kw.pop('context', {})
            if neither(mail_server_id, smtp_server):
                transport = transports.select(
                    self, cr, uid, message, context=context
                )
                delivered, data = False, {}
                if transport:
                    with transport:
                        message, data = transport.prepare_message(
                            self, cr, uid, message, context=context
                        )
                        delivered = transport.deliver(
                            self, cr, uid, message, data,
                            context=context
                        )
                if delivered:
                    return delivered
                elif data:
                    context.update(data.pop('context', {}))
                    valid = get_kwargs(_super)
                    kw.update((key, val) for key, val in data.items()
                              if key in valid)
                    kw['context'] = context
        return _super(cr, uid, message, **kw)

    def send_without_transports(self, cr, uid, message, **kw):
        '''Send a message without using third-party transports.'''
        with execution_context(DIRECT_SEND_CONTEXT):
            self.send_email(cr, uid, message, **kw)


DIRECT_SEND_CONTEXT = object()
