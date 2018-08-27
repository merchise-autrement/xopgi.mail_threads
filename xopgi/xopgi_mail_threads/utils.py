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

from xoeuf import SUPERUSER_ID

from email.utils import getaddresses, formataddr
from xoeuf.odoo.addons.base.ir.ir_mail_server import encode_header  # noqa
from xoeuf.odoo.addons.base.ir.ir_mail_server import encode_rfc2822_address_header  # noqa

from .stdroutes import BOUNCE_ROUTE_MODEL, IGNORE_MESSAGE_ROUTE_MODEL


try:
    # Odoo 10
    from odoo.tools.mail import decode_message_header as decode_header
except ImportError:
    try:
        # Odoo 8
        from openerp.addons.mail.mail_thread import decode_header
    except ImportError:
        # Odoo 9 fallback
        from openerp.addons.mail.models.mail_thread import decode_header

try:
    from odoo.tools.mail import decode_smtp_header
except ImportError:
    try:
        from openerp.addons.mail.mail_message import decode as decode_smtp_header  # noqa
    except ImportError:
        from openerp.addons.mail.models.mail_message import decode as decode_smtp_header  # noqa


class RegisteredType(type):
    '''A metaclass that registers all its instances.

    Create a new instance of a registered type (take note of the Python 2/3
    difference for metaclasses)::

        >>> class Foo(object):
        ...   __metaclass__ = RegisteredType


    The subclassess of ``Foo`` will be registered::

        >>> class Bar(Foo):
        ...    pass

        >>> Bar in Foo.registry
        True

    The method `get_installed_objects`:meth: requires model (new API
    recordset).  Return a subset of the registered subclasses that are defined
    in module that belongs to an addon which is installed in the DB related
    with the given model.

    '''

    def __new__(cls, name, bases, attrs):
        res = super(RegisteredType, cls).__new__(cls, name, bases, attrs)
        root = res.mro()[-2]  # up two levels in the MRO must be the base
        registry = getattr(root, 'registry', None)
        if registry is not None:
            registry.add(res)
        else:
            root.registry = set()
        return res

    def get_installed_objects(self, model):
        '''Return a list of all registered objects which are installed in the
        DB given by `model`.

        Return a iterable (not necessarily a list).

        '''
        from xoeuf.modules import is_object_installed
        return (
            obj
            for obj in self.registry
            if is_object_installed(model, obj)
        )


# TODO: Move these to xoutil.  For that I need first to port the
# `decode_header` from future email.
def set_message_address_header(message, header, value, address_only=False):
    if address_only:
        previous = decode_header(message, header)
        previous = getaddresses([previous])
        names = [name for name, _ in previous]
    else:
        names = []
    replacements = getaddresses([value])
    if names:
        from six.moves import zip
        from itertools import cycle
        addresses = list(
            zip(names, cycle(email for _, email in replacements))
        )
    else:
        addresses = replacements
    value = encode_rfc2822_address_header(
        ', '.join(formataddr(address) for address in addresses)
    )
    if header in message:
        message.replace_header(header, value)
    else:
        message[header] = value


def set_message_sender(message, sender, address_only=False):
    '''Set or replace the message's sender header.

    If `sender` contains both the name and address both are changed unless
    `address_only` is True, in which case the name of the sender in the
    message survives.

    '''
    set_message_address_header(message, 'Sender', sender,
                               address_only=address_only)


def set_message_from(message, addresses, address_only=False):
    '''Set or replace the message's From header.

    :type addresses: string

    :param addresses: The addresses Can contain several email addresses (with
                      or without names).  It can be a single address and all
                      authors will be replaced.

    '''
    set_message_address_header(message, 'From', addresses,
                               address_only=address_only)


def get_addresses_headers(message, headers):
    '''Get all the addresses in messages according to given headers.

    :param headers: The name of headers to get.  It's expected such headers,
                    contain just email addresses.

    :returns: a list of 2-tuples with name, email address.

    '''
    result = []
    get = message.get_all
    for header in headers:
        result.extend(getaddresses(get(header, [])))
    return result


def get_recipients(message):
    'Return a list pairs with the names and emails of the recipients.'
    return get_addresses_headers(message, ['To', 'Cc', 'Bcc'])


def create_bounce_route(original_message, **custom_values):
    '''Return the standard bounce route.

    Routers that create this route will emit a bounce to the message's
    Return-Path.

    :param original_message: The email.Message that we're bouncing.

    '''
    return (
        BOUNCE_ROUTE_MODEL,
        False,
        dict(custom_values, original_message=original_message),
        SUPERUSER_ID,
        None
    )


def create_ignore_route(original_message, **custom_values):
    '''Return the standard ignore route.

    Routers that create this route will simply accept and ignore the message.

    :param original_message: The email.Message that we're accepting and
                             ignoring.

    '''
    return (
        IGNORE_MESSAGE_ROUTE_MODEL,
        False,
        dict(custom_values, original_message=original_message),
        SUPERUSER_ID,
        None
    )
