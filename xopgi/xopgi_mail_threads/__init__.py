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
    try:
        from odoo.addons.mail import models as mail   # Odoo 10+
    except ImportError:
        try:
            from openerp.addons.mail import models as mail   # Odoo 9
        except ImportError:
            from openerp.addons import mail  # Odoo 8
    assert getattr(mail, 'xopgi', False), \
        'You must use a recent Odoo packaged by Merchise Autrement'
