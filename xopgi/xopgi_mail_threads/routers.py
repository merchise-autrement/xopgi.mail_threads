#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from xoutil.eight.meta import metaclass
except ImportError:
    from xoutil.objects import metaclass
from .utils import RegisteredType


class MailRouter(metaclass(RegisteredType)):
    '''A router for mail to objects inside OpenERP.

    A router is an "after the fact" mechanism for the routing mechanism
    implemented by the `mail` module of OpenERP.  OpenERP apply only three
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

    .. warning::

       All methods defined in a mail router are automatically converted to
       hybrid methods, this is, they are exposed as class methods as well as
       instance methods.

    '''

    @classmethod
    def query(cls, obj, message):
        '''Return if the router is applicable to the message.

        This is defined as weak test, but strong tests are encouraged.

        :param obj:  The ``mail.thread`` object.
        :param cr: The OpenERP cursor for the database.
        :param uid: The UID of the user.

        :param message: The email to be routed inside OpenERP.
        :type message: :class:`email.message.Message`.

        :returns: A tuple of ``(valid, data)``.  `valid` must be True is the
                  router can process the message.  `data` is anything that
                  will be passed as the `data` keyword argument to the `apply`
                  method.

                  You may also simply return a single boolean value, in that
                  case data will be None.

        The cursor is provided so that different databases could be configured
        to use or not the router.  The `uid` is provided so that routers may
        call ORM methods.

        .. versionchanged:: 3.0 Changed the name to the method to `query` so
           that is more consistent with `MailTransportRouter`:class:

        .. versionchanged:: 4.0 No more old API signature.

        '''
        if cls is MailRouter:  # avoid failing when super()
            raise NotImplementedError()

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        '''Transform if needed the `routes` according to the message.

        :param routes: The routes as previously left by OpenERP and possible
                       other routers.
        :type routes: list

        Each route must have the form::

           (model, thread_id, custom_values, user_id, alias_id)

        .. versionchanged:: 4.0 No more old API signature.

        '''
        if cls is MailRouter:
            raise NotImplementedError()

    @classmethod
    def find_route(cls, routes, pred=None):
        '''Yields pairs of `(position, route)` of routes that match the
        predicated `pred`.

        '''
        return ((i, route) for i, route in enumerate(routes)
                if not pred or pred(route))


del metaclass
