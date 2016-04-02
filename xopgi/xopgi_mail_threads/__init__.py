# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_mail_threads
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2014-06-18

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from . import mail_messages  # noqa
from . import mail_threads  # noqa
from . import mail_server  # noqa


from .routers import MailRouter  # noqa
from .transports import TransportRouteData, MailTransportRouter  # noqa


def post_load_hook():
    # Ensure your are running a patched Odoo.  I don't really like this, but
    # Odoo's current inheritance mechanics leaves no (good) choice:  Either
    #
    # - we figure out how to monkey patch the models that inherit from
    #   mail.thread after they are load, or
    #
    # - we change the inheriting mechanism in Odoo (i.e patching Odoo), or
    #
    # - we patch Odoo's mail addon to have our code.
    #
    # We're choosing the last one.
    #
    from openerp.addons import mail
    assert getattr(mail, 'xopgi', False), \
        'You must use a recent Odoo packaged by Merchise Autrement'
