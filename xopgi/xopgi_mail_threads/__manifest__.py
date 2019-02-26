#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    "name": "Mail Threads (xopgi)",
    "version": "4.1",
    "post_load": "post_load_hook",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_mail_threads",
    'category': 'Social Network',
    "description": "Improves OpenERP's basic mail management.",
    "depends": ['mail'],
    "data": [
        "views/transitional.xml"
    ],
    "application": False,
    "auto_install": True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': 10 <= MAJOR_ODOO_VERSION < 13,  # noqa
}
