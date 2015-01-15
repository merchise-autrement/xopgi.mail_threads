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

from xoutil.objects import metaclass, classproperty

from .utils import RegisteredType


class MailTransportRouter(metaclass(RegisteredType)):
    '''Mail transport routers decide how to deliver outgoing messages.

    When OpenERP needs to send an email, registered transport router are run
    one after the other to find any transport router that can/must deliver the
    message.

    When consulted the transport may respond that:

    - It *cannot* deliver the message.
    - It *can* deliver the message.
    - It *should* deliver the message.

    Transports that cannot deliver a message are not disturbed any further.

    '''

    CANNOT = 0
    CAN = 1
    SHOULD = 2
    MUST = 3

    @classmethod
    def query(self, cr, uid, message, context=None):
        '''Respond if the transport router can or must deliver the provided
        message.'''
        if self is MailTransportRouter:
            raise NotImplemented()


    @classmethod
    def deliver(self, cr, uid, message, context=None):
        '''Deliver if possible the message.

        Return False if the delivery was not possible.  Return True if the
        delivery was successful.  The last case means only that the transport
        could properly deliver the message to next hop in the chain not that
        message was actually delivered to its final destination.

        '''
        raise NotImplemented()

    @classmethod
    def prepare_message(self, cr, uid, message, context=None):
        '''Prepares the message to be delivered.

        Returns a tuple with ``(direct, message, kwargs)``.  If ``direct`` is
        True you should use the `deliver`:meth: method to actually deliver the
        message.  (See the `server` module).  In this case both ``message``
        and ``data`` will be None.

        If ``direct`` is False, ``message`` contains the message that OpenERP
        will actually send, while ``kwargs`` will be used to instruct the
        ``send_email`` method of ``ir.mail_server`` how to send it.

        For instance, transports may choose not to deliver the message but to
        modify its headers, and to provide the ``smtp_*`` keyword arguments.

        .. warning:: Although, transports may modify the `message` argument it
           is recommended to use the returned value.

        '''
        return False, message, {}


def is_router_installed(self, cr, uid, router):
    from xoeuf.modules import get_object_module
    module = get_object_module(router)
    if module:
        mm = self.pool['ir.module.module']
        query = [('state', '=', 'installed'), ('name', '=', module)]
        return bool(mm.search(cr, uid, query))
    else:
        return False


def proper_transport(self, cr, uid, message, context=None):
    '''Select the "best" transport for a message.'''
    candidates = [router for router in MailTransportRouter.registry
                  if is_router_installed(self, cr, uid, router)]
    found = False
    transport, level = None, MailTransportRouter.CANNOT
    while not found and candidates:
        current = candidates.pop(0)
        res = current.query(cr, uid, message, context=context)
        if res > level:
            transport, level = current, res
            found = res == MailTransportRouter.MUST
    return transport

del metaclass
