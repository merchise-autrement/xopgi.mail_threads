#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

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

from xoutil.eight.meta import metaclass
from xoutil.future.codecs import safe_encode

from xoeuf import api
from xoeuf.models import AbstractModel

import logging
logger = logging.getLogger(__name__)
del logging


class MailThread(AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _customize_routes(self, message, routes):
        from .routers import MailRouter
        logger.debug('Processing incomming message with custom routers')
        for router in MailRouter.get_installed_objects(self):
            # Since a router may fail after modifying `routes` somehow, let's
            # keep it safe here to restore if needed.
            routes_copy = routes[:]
            try:
                result = router.query(self, message)
                if isinstance(result, tuple):
                    valid, data = result
                else:
                    valid, data = result, None
                if valid:
                    logger.debug('Processing message using router %r', router)
                    router.apply(self, routes, message, data=data)
            except Exception:
                logger.exception('Router %s failed.  Ignoring it.', router)
                routes = routes_copy
        if not routes:
            import email
            from email.message import Message
            if not isinstance(message, Message):
                message = email.message_from_string(safe_encode(message))
            logger.warn(
                "No routes found for message coming from %r.",
                message.get('Sender', message.get('From', '<>')),
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
        else:
            logger.debug(
                "Message accepted, coming from %r",
                message.get('Sender', message.get('From', '<>')),
            )
        return routes

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None,
                      custom_values=None):
        result = []
        error_before_custom_routes = None
        try:
            _super = super(MailThread, self).message_route
            result = _super(message, message_dict, model=model,
                            thread_id=thread_id,
                            custom_values=custom_values)
        except (AssertionError, ValueError) as error:
            # super's message_route method may raise a ValueError if it finds
            # no route, we want to wait to see if we can find a custom route
            # before raising the ValueError.
            #
            # In Odoo 9 super's message_route may raise an AssertionError if
            # the fallback model (i.e crm.lead) is not installed.
            error_before_custom_routes = error
        result = self._customize_routes(message, result or [])
        if result:
            return result
        elif error_before_custom_routes:
            raise error_before_custom_routes
        else:
            return []


del metaclass, AbstractModel
