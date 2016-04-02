#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_mail_threads._release
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-04-24


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def read_terpfile():
    import os
    from os.path import join
    with open(join(os.path.dirname(__file__), '__openerp__.py'), 'rU') as fh:
        content = fh.read()
        # Don't use the ODOO_VERSION_INFO magic.
        return eval(content, {}, {})

_TERP = read_terpfile()
VERSION = _TERP['version']
