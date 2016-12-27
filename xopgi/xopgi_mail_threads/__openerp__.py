# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_mail_threads
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11
# flake8: noqa


# We must not use the ODOO_VERSION_INFO magic provide by Merchise's
# distribution of Odoo.
{
    "name": "Mail Threads (xopgi)",
    "version": "4.0",
    "post_load": "post_load_hook",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_mail_threads",
    'category': 'Social Network',
    "description": "Improves OpenERP's basic mail management.",
    "depends": ['mail'],
    "data": [
        "views/transitional.xml"
    ],
    "demo_xml": [],
    "application": False,
    "auto_install": True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': ((8, 0) <= ODOO_VERSION_INFO < (10, 0))
}
