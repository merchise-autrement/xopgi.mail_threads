# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_mail_threads.threads
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-06-18

'''Extends OpenERP mail detection strategies.

Odoo's mail addon has only four strategies to select a message's thread id or
create a new one.

Those strategies work for most cases, but some fail.  At the same time, those
are packed into a single method ``message_route`` which is responsible to
select the messages several targets (threads).  This makes harder to extend
how those strategies apply.

Our current solution is two folded:

- First allow OpenERP to select their targets.

- Then allow other `Mail Routers <MailRouter>`:class: to process the results
  as they see fit.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from xoutil.eight.meta import metaclass
except ImportError:
    from xoutil.objects import metaclass

from xoutil import logger as _logger
from xoutil.string import safe_encode

from openerp.osv.orm import AbstractModel


class MailThread(AbstractModel):
    _inherit = 'mail.thread'

    def _customize_routes(self, cr, uid, message, routes, context=None):
        from .utils import is_router_installed
        from .routers import MailRouter
        for router in MailRouter.registry:
            # Since a router may fail after modifying `routes` somehow, let's
            # keep it safe here to restore if needed.
            routes_copy = routes[:]
            try:
                if is_router_installed(cr, uid, router):
                    result = router.query(self, cr, uid, message,
                                          context=context)
                    if isinstance(result, tuple):
                        valid, data = result
                    else:
                        valid, data = result, None
                    if valid:
                        router.apply(self, cr, uid, routes, message,
                                     data=data, context=context)
            except:
                _logger.exception('Router %s failed.  Ignoring it.', router)
                routes = routes_copy
        if not routes:
            from xoutil import logger
            import email
            from email.message import Message
            if not isinstance(message, Message):
                message = email.message_from_string(safe_encode(message))
            logger.warn(
                "No routes found for message.",
                extra=dict(
                    message_id=message.get('Message-Id', '<>'),
                    sender=message.get('Sender', message.get('From', '<>')),
                    recipients=[
                        message.get('To'),
                        message.get('Delivered-To'),
                        message.get('Cc'),
                    ]
                )
            )
        return routes

    def message_route(self, cr, uid, rawmessage, message, model=None,
                      thread_id=None, custom_values=None, context=None):
        _super = super(MailThread, self).message_route
        result = []
        error = None
        try:
            result = _super(cr, uid, rawmessage, message, model=model,
                            thread_id=thread_id,
                            custom_values=custom_values,
                            context=context)
        except (AssertionError, ValueError) as error:
            # super's message_route method may raise a ValueError if it finds
            # no route, we want to wait to see if we can find a custom route
            # before raising the ValueError.
            #
            # In Odoo 9 super's message_route may raise an AssertionError if
            # the fallback model (i.e crm.lead) is not installed.
            pass
        result = self._customize_routes(cr, uid, rawmessage, result or [],
                                        context=context)
        if result:
            return result
        elif error:
            raise error
        else:
            return []

del metaclass, AbstractModel
