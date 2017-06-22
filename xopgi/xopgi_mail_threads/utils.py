#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.util
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
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

try:
    from odoo.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from openerp.release import version_info as ODOO_VERSION_INFO

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
    from odoo.addons.base.ir.ir_mail_server import encode_header
except ImportError:
    from openerp.addons.base.ir.ir_mail_server import encode_header

try:
    from odoo.tools.mail import decode_smtp_header
except ImportError:
    try:
        from openerp.addons.mail.mail_message \
            import decode as decode_smtp_header
    except ImportError:
        from openerp.addons.mail.models.mail_message \  # noqa
            import decode as decode_smtp_header         # noqa

try:
    from odoo.addons.base.ir.ir_mail_server \
        import encode_rfc2822_address_header
except ImportError:
    from openerp.addons.base.ir.ir_mail_server \
        import encode_rfc2822_address_header


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
        return (
            obj
            for obj in self.registry
            if is_object_installed(model, obj)
        )


try:
    from xoeuf.models import is_object_installed
except ImportError:
    def is_object_installed(self, object):
        from xoeuf.modules import get_object_module
        module = get_object_module(object)
        if module:
            mm = self.env['ir.module.module']
            query = [('state', '=', 'installed'), ('name', '=', module)]
            return bool(mm.search(query))
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
