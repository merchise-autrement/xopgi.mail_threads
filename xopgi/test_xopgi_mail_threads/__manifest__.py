#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    "name": "Test Mail Threads (xopgi)",
    "version": "4.1",
    "author": "Merchise Autrement",
    "depends": ['mail', 'xopgi_mail_threads'],
    "data": ['data/alias.xml'],
    "application": False,
    "auto_install": False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': True,

    'post_init_hook': '_assert_test_mode',
}
