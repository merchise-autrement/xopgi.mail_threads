#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# post-001-cleanup-raw-emails
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-04-21

'''Removes the bulk of raw_emails and leave only the headers.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging
import email
from io import BytesIO

from xoutil.string import safe_decode, safe_encode
from xoutil.modules import modulemethod

from xopgi.xopgi_mail_threads.mail_messages import HeaderOnlyGenerator

from openerp import SUPERUSER_ID
from xoeuf.osv.model_extensions import search_browse


logger = logging.getLogger('openerp.modules')


@modulemethod
def migrate(self, cr, version):
    from openerp.modules.registry import RegistryManager as manager
    try:
        pool = manager.get(cr.dbname)
        Message = pool['mail.message']
        count = Message.search_count(cr, SUPERUSER_ID, [])
        logger.info('Processing %d emails', count)
        offset = 0
        limit = 5000
        while offset < count:
            messages = search_browse(Message, cr, SUPERUSER_ID, [],
                                     offset=offset, limit=limit)
            batch = len(messages)
            offset += batch
            logger.info('Processing batch of %d.  Remaining %d',
                        batch, count - offset)
            for message in messages:
                if message.raw_email:
                    values = {}
                    buf = BytesIO()
                    # Re-encode to the connection encoding
                    gen = HeaderOnlyGenerator(buf, mangle_from_=False,
                                              target_charset=cr._cnx.encoding)
                    gen.flatten(email.message_from_string(
                        safe_encode(message.raw_email)))
                    rawemail = safe_decode(buf.getvalue(),
                                           encoding=cr._cnx.encoding)
                    values['raw_email'] = rawemail
                    Message.write(cr, SUPERUSER_ID, [message.id], values)
    except:
        logger.exception('Bad thing happened')
        raise
