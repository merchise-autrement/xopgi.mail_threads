# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xopgi.xopgi_mail_threads.threads
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-06-18

'''Extends OpenERP mail detection strategies.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

import logging
_logger = logging.getLogger(__name__)

from xoeuf.osv.orm import get_modelname

from openerp.osv.orm import Model
from openerp.addons.mail.mail_thread import mail_thread as _base_mail_thread


class mail_thread(Model):
    _name = get_modelname(_base_mail_thread)
    _inherit = _name

    def message_route(self, cr, uid, message, model=None, thread_id=None,
                      custom_values=None, context=None):
        _logger.debug('Threading magic')
        _super = super(mail_thread, self).message_route
        return _super(cr, uid, message, model=model, thread_id=thread_id,
                      custom_values=custom_values, context=context)
