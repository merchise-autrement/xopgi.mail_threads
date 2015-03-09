#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.mail_threads.ir_model_access
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-02-09

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import tools
from openerp.osv.orm import browse_record, Model
from openerp.addons.base.ir.ir_model import ir_model_access as base

from xoeuf.osv.orm import get_modelname


class ir_model_access(Model):
    _name = get_modelname(base)
    _inherit = _name

    @tools.ormcache()
    def check(self, cr, uid, model, mode='read', raise_exception=True,
              context=None):
        '''Allow to anyone can `read` from any mail_threads inherited models.

        '''
        if mode == 'read':
            if isinstance(model, browse_record):
                model_name = model.model
            else:
                model_name = model
            models = self.pool['mail.thread'].message_capable_models(cr, uid)
            if models and model_name in models.keys():
                return True
        return super(ir_model_access, self).check(cr, uid, model, mode,
                                                  raise_exception, context)
