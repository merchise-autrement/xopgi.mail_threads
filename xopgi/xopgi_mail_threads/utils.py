#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.util
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
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


from email.utils import getaddresses, formataddr

from openerp.addons.mail.mail_thread import decode_header
from openerp.addons.base.ir.ir_mail_server import \
    encode_rfc2822_address_header as _address_header


class RegisteredType(type):
    '''A metaclass that registers all its instances.'''

    def __new__(cls, name, bases, attrs):
        res = super(RegisteredType, cls).__new__(cls, name, bases, attrs)
        root = res.mro()[-2]
        registry = getattr(root, 'registry', None)
        if registry is not None:
            registry.add(res)
        else:
            root.registry = set()
        return res


def is_router_installed(cr, uid, router):
    from xoeuf.osv.registry import Registry
    from xoeuf.modules import get_object_module
    module = get_object_module(router)
    if module:
        db = Registry(cr.dbname)
        with db() as cr:
            mm = db.models['ir.module.module']
            query = [('state', '=', 'installed'), ('name', '=', module)]
            return bool(mm.search(cr, uid, query))
    else:
        return False


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
    value = _address_header(
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
