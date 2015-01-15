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
