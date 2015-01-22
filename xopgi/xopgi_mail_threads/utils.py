#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.util
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
