#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Transports for outgoing emails.

Transports allow to fully override OpenERP's internal mechanisms for send
emails.  Once an email needs to be sent a transport may choose to either
further instruct how to send it by the OpenERP internal mail_server or to
deliver itself.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.future.collections import namedtuple
from xoutil.eight.meta import metaclass
from xoutil.objects import classproperty

from .utils import RegisteredType

import logging
_logger = logging.getLogger(__name__)
del logging


TransportRouteData = namedtuple('TransportRouteData',
                                'message, connection_data')


# A sentinel for transports execution context.
WITH_TRANSPORT = object()


class MailTransportRouter(metaclass(RegisteredType)):
    '''Mail transport routers decide how to deliver outgoing messages.

    When OpenERP needs to send an email, registered transport router are
    consulted to find a transport router that can deliver the message.

    '''

    def __new__(cls, *args, **kwargs):
        res = getattr(cls, '__singleton__', None)
        if not res:
            res = object.__new__(cls, *args, **kwargs)
            setattr(cls, '__singleton__', res)
        return res

    @classmethod
    def select(cls, obj, message):
        '''Select a registered transport that can deliver the message.

        No order is warranted about how to select any transport that can
        deliver a message.

        Return a tuple of ``(transport, query_data)`` where `transport` if an
        instance of the selected transport and `query_data` is data returned
        by the `query` method of the transport selected or None.

        '''
        from xoutil.context import Context
        candidates = (
            transport
            for transport in MailTransportRouter.get_installed_objects(obj)
            if transport.context_name not in Context
        )
        found, transport, data = False, None, None
        candidate = next(candidates, None)
        while not found and candidate:
            try:
                res = candidate.query(obj, message)
            except Exception:
                _logger.exception(
                    'Candidate transport %s failed. Proceeding with another',
                    candidate,
                    extra=dict(
                        message_to=message['To'],
                        message_from=message['From'],
                        message_delivered_to=message['Delivered-To'],
                        message_subject=message['Subject'],
                        message_return_path=message['Return-Path'],
                        message_as_string=message.as_string()
                    )
                )
                res = False
            if isinstance(res, tuple):
                found, data = res
            else:
                found, data = res, None
            if found:
                transport = candidate
            else:
                candidate = next(candidates, None)
        return (transport(), data) if transport else (None, None)

    @classproperty
    def context_name(cls):
        from xoutil.names import nameof
        return (WITH_TRANSPORT, nameof(cls, inner=True, full=True))

    @property
    def context(self):
        from xoutil.context import context
        return context(self.context_name)

    def __enter__(self):
        _logger.debug("Entering context for %s", self.context_name)
        return self.context.__enter__()

    def __exit__(self, *args):
        _logger.debug("Exiting context for %s", self.context_name)
        return self.context.__exit__(*args)

    @classmethod
    def query(cls, obj, message):
        '''Respond if the transport router can deliver the message.

        Return True if the transport can deliver the message and False,
        otherwise.

        .. versionchanged:: 2.5 You may also return a tuple of ``(result,
           data)``.  The first component should be the boolean value as
           before.  The ``data`` part is an object that will be passed as the
           ``data`` keyword argument of the `prepare_message`:meth: method.

        This is useful to avoid computing things twice in `query` and in
        `prepare_message`:meth:.

        .. versionchanged:: 4.0 No more old API signature.

        '''
        raise NotImplementedError()

    def deliver(self, server, message, data, **kwargs):
        '''Deliver if possible the message.

        Return the Message-Id string if the delivery was successful.  This
        only means that the transport could properly deliver the message to
        next hop in the chain not that message was actually delivered to its
        final destination.

        You should pass both the ``message`` and ``connection_data`` objects
        returned by `prepare_message`:func:.

        Inside this method the ``send_email`` method of the ``ir.mail_server``
        object can be used and the transport won't be re-elected but another
        one will.  This allows for several transports to kick in and do their
        magic as a pipeline.  Notice this may, however, slow the delivery.

        Transports are not meant for the unwary users, but for system
        designers.  Furthermore, the order in which they will be elected is
        not defined.

        '''
        try:
            from odoo.addons.base.ir.ir_mail_server import IrMailServer
        except ImportError:
            # Odoo 12
            from odoo.addons.base.models.ir_mail_server import IrMailServer

        kwargs.update(dict(data or {}))
        try:
            return server.send_email(message, **kwargs)
        except AssertionError as error:
            if error.message == IrMailServer.NO_VALID_RECIPIENT:
                _logger.info(
                    "No valid recipients for message %s: %s",
                    message.get('Message-Id'), message.get('To')
                )
            else:
                raise

    def prepare_message(self, obj, message, data=None):
        '''Prepares the message to be delivered.

        Returns a named tuple TransportRouteData with ``(message,
        connection_data)``.

        The ``message`` attribute is the message that OpenERP will actually
        send, while ``connection_data`` will be used to instruct the
        ``send_email`` method of ``ir.mail_server`` how to send it if the
        `deliver`:func: indicates it.

        The ``data`` keyword argument is the second component if the return
        value of the `query`:meth: method.  You may use that data to avoid
        redoing stuff you did in the `query` method.

        .. versionchanged:: 2.5  Added the `data` argument.

        '''
        return TransportRouteData(message, {})

    @classmethod
    def get_message_objects(cls, obj, message):
        '''Get the mail.message browse record for the `message` .

        :returns: A tuple ``(msg, refs)`` where the `msg` is the mail.message
           browse record and the refs is a list of mail.message browse records
           of the references in the `message`.

        If the message's Message-Id is not found `msg` is set to None.  If any
        of references is not found it won't be included the `refs` list.

        '''
        message_id = message['Message-Id']
        references = tuple(
            ref.strip()
            for ref in message.get('References', '').split(',')
        )
        Messages = obj.env['mail.message']
        msg = Messages.search([('message_id', '=', message_id)])
        if not msg:
            msg = None  # convert the null-record to None
        if references:
            refs = Messages.search([('message_id', 'in', references)])
        else:
            refs = Messages  # the empty recordset
        return msg, refs


del metaclass, classproperty, RegisteredType, namedtuple
