# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xopgi.xopgi_mail_threads.threads
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
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

from openerp.osv.orm import AbstractModel
from openerp.addons.mail.mail_thread import mail_thread as _base_mail_thread


class _MailRouterType(type):
    _base = None

    def __new__(cls, name, bases, attrs):
        res = super(_MailRouterType, cls).__new__(cls, name, bases, attrs)
        if not cls._base:
            cls._base = res
            res.registry = set()
        else:
            registry = cls._base.registry
            registry.add(res)
        return res


# TODO: Check the metaclass reliability.
#
# I'm worried about how this classes are loaded in the OpenERP processes.
# Since the metaclass will register all classes derived from MailRouter, and
# those classes may actually be non-suitable to all databases, the cr and uid
# arguments were introduced for that reason.

class MailRouter(metaclass(_MailRouterType)):
    '''A router for mail to objects inside OpenERP.

    A router is an "after the fact" mechanism for the routing mechanism
    implemented by the `mail` module of OpenERP.  This module apply only three
    rules:

    a) Based on the "References" and "In-Reply-To" if and only if they match
       the regular expression for OpenERP-generated "Message-Id".

    b) Based on the registered mail aliases on the system.

    c) Defaults provided to the `message_route` method.

    Notice that only the first two actually use the message.

    These rules are enough for most cases.  But sometimes they fail to
    integrate well with other systems.

    Mail routers are allowed to change the routes previously detected by
    OpenERP and other routers.  They way mail routers are chained is
    undefined.  So, mail routers are encouraged to implement op-out features.

    '''
    @classmethod
    def is_applicable(cls, cr, uid, message):
        '''Return True if the router is applicable to the message.

        This is defined as weak test, but strong tests are encouraged.

        :param cr: The OpenERP cursor for the database.
        :param uid: The UID of the user.

        :param message: The email to be routed inside OpenERP.
        :type message: :class:`email.message.Message`.

        The cursor is provided so that different databases could be configured
        to use or not the router.  The `uid` is provided so that routers may
        call ORM methods.

        '''
        if cls is MailRouter:  # avoid failing when super()
            raise NotImplementedError()

    @classmethod
    def apply(cls, cr, uid, routes, message):
        '''Transform if needed the `routes` according to the message.

        :param routes: The routes as previously left by OpenERP and possible
                       other routers.
        :type routes: list

        '''
        if cls is MailRouter:
            raise NotImplementedError()


class mail_thread(AbstractModel):
    _name = get_modelname(_base_mail_thread)
    _inherit = _name

    def message_route(self, cr, uid, message, model=None, thread_id=None,
                      custom_values=None, context=None):
        _super = super(mail_thread, self).message_route
        result = _super(cr, uid, message, model=model, thread_id=thread_id,
                        custom_values=custom_values, context=context)
        for router in MailRouter.registry:
            if router.is_applicable(cr, uid, message):
                router.apply(cr, uid, result, message)
        return result


del metaclass, get_modelname, AbstractModel
