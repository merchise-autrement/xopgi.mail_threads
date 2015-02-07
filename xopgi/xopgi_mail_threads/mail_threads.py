# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_mail_threads.threads
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
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
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from xoutil.objects import metaclass
from xoeuf.osv.orm import get_modelname

from openerp.release import version_info as VERSION_INFO
from openerp.osv.orm import AbstractModel
from openerp.addons.mail.mail_thread import mail_thread as _base_mail_thread

# Backwards-compatible fix.
from xoutil.deprecation import deprecated
from xoutil import logger as _logger

from .routers import MailRouter
MailRouter = deprecated(MailRouter)(MailRouter)

del deprecated, MailRouter


class mail_thread(AbstractModel):
    _name = get_modelname(_base_mail_thread)
    _inherit = _name

    def _customize_routes(self, cr, uid, message, routes):
        from .utils import is_router_installed
        from .routers import MailRouter
        for router in MailRouter.registry:
            try:
                if is_router_installed(cr, uid, router) and \
                   router.is_applicable(cr, uid, message):
                    router.apply(cr, uid, routes, message)
            except:
                _logger.exception('Router %s failed.', router)
        if not routes:
            from xoutil.string import safe_encode
            from xoutil import logger
            import email
            from email.message import Message
            if not isinstance(message, Message):
                message = email.message_from_string(safe_encode(message))
            logger.warn(
                "No routes found for message '%s' sent by '%s'",
                message.get('Message-Id', 'No ID!'),
                message.get('Sender', message.get('From', '<>'))
            )
        return routes

    if VERSION_INFO < (8, 0):
        def message_route(self, cr, uid, message, model=None, thread_id=None,
                          custom_values=None, context=None):
            _super = super(mail_thread, self).message_route
            result = _super(cr, uid, message, model=model, thread_id=thread_id,
                            custom_values=custom_values, context=context)
            return self._customize_routes(cr, uid, message, result)
    else:
        def message_route(self, cr, uid, rawmessage, message, model=None,
                          thread_id=None, custom_values=None, context=None):
            _super = super(mail_thread, self).message_route
            result = _super(cr, uid, rawmessage, message, model=model,
                            thread_id=thread_id,
                            custom_values=custom_values, context=context)
            return self._customize_routes(cr, uid, rawmessage, result)


del metaclass, get_modelname, AbstractModel
