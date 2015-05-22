#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.routers
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-15

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import warnings
from xoutil.objects import metaclass

from .utils import RegisteredType


# The following is a trick to allow old routers to work for now.
class MailRouterType(RegisteredType):
    _new_api = {
        'is_applicable': ('obj', 'cr', 'uid', 'message'),
        'apply': ('obj', 'cr', 'uid', 'routes', 'message')
    }

    @classmethod
    def wrap(cls, clsname, name, clsmethod):
        '''Wrap a router method if old API.'''
        from functools import wraps
        from xoutil.inspect import getfullargspec
        args = getfullargspec(clsmethod.__func__)[0][1:]
        if len(args) != len(cls._new_api[name]):
            warnings.warn('The method %s of router %s uses a '
                          'deprecated API' % (name, clsname),
                          stacklevel=3)
            func = clsmethod.__func__

            @classmethod
            @wraps(func)
            def result(cls, obj, cr, uid, *a):
                return func(cls, cr, uid, *a)
            return result
        else:
            return clsmethod

    def __new__(cls, name, bases, attrs):
        attrs = {
            attr: (
                cls.wrap(name, attr, val)
                if attr in cls._new_api and isinstance(val, classmethod)
                else val
            )
            for attr, val in attrs.items()
        }
        return super(MailRouterType, cls).__new__(cls, name, bases, attrs)


# TODO: Check the metaclass reliability.
#
# I'm worried about how this classes are loaded in the OpenERP processes.
# Since the metaclass will register all classes derived from MailRouter, and
# those classes may actually be non-suitable to all databases, the cr and uid
# arguments were introduced for that reason.
class MailRouter(metaclass(MailRouterType)):
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
    def is_applicable(cls, obj, cr, uid, message):
        '''Return True if the router is applicable to the message.

        This is defined as weak test, but strong tests are encouraged.

        :param obj:  The mail.thread object.
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
    def apply(cls, obj, cr, uid, routes, message):
        '''Transform if needed the `routes` according to the message.

        :param routes: The routes as previously left by OpenERP and possible
                       other routers.
        :type routes: list

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
