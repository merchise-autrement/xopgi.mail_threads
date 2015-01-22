#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.transports
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-15

'''Transports for outgoing emails.

Transports allow to fully override OpenERP's internal mechanisms for send
emails.  Once an email needs to be sent a transport may choose to either
further instruct how to send it by the OpenERP internal mail_server or to
deliver itself.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.collections import namedtuple
from xoutil.objects import metaclass, classproperty
from xoutil import logger as _logger

from .utils import RegisteredType

TransportRouteData = namedtuple('TransportRouteData',
                                'message, connection_data')


# A sentinel for transports execution context.
WITH_TRANSPORT = object()


class MailTransportRouter(metaclass(RegisteredType)):
    '''Mail transport routers decide how to deliver outgoing messages.

    When OpenERP needs to send an email, registered transport router are
    consulted to find a transport router that can deliver the message.

    '''

    @classmethod
    def select(cls, cr, uid, message, context=None):
        '''Select a registered transport that can deliver the message.

        No order is warranted about how to select any transport that can
        deliver a message.

        '''
        from .utils import is_router_installed
        from xoutil.context import context
        candidates = (router for router in MailTransportRouter.registry
                      if is_router_installed(cr, uid, router)
                      if router.context_name not in context)
        found, transport = False, None
        candidate = next(candidates, None)
        while not found and candidate:
            found = candidate.query(cr, uid, message, context=context)
            if found:
                transport = candidate
            else:
                candidate = next(candidates, None)
        return transport() if transport else None

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

    def query(self, cr, uid, message, context=None):
        '''Respond if the transport router can deliver the message.

        Returns True if the transport can deliver the message and False,
        otherwise.

        '''
        raise NotImplemented()

    def deliver(self, cr, uid, message, data, context=None):
        '''Deliver if possible the message.

        Return False if the transport won't do the delivery directly.  This
        will delegate the delivery to OpenERP's ``send_email`` method.

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
        return False

    def prepare_message(self, cr, uid, message, context=None):
        '''Prepares the message to be delivered.

        Returns a named tuple with ``(message, connection_data)``.

        The ``message`` attribute is the message that OpenERP will actually
        send, while ``connection_data`` will be used to instruct the
        ``send_email`` method of ``ir.mail_server`` how to send it if the
        `deliver`:func: indicates it.

        '''
        return TransportRouteData(message, {})


del metaclass, classproperty, RegisteredType, namedtuple
