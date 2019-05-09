#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Appends raw email to 'mail.message' module.

.. note:: On using `store_original`.

   OpenERP's mail system may save the original email, but it does so as an
   attachment.  We feel this is mistaken, cause an attachment is an integral
   part of the message and thus it should not be "created" by technical
   reasons.  A valid scenario for automatically creating an attachment should
   be business-driven.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging

from xoutil.eight.string import force as force_str

from xoeuf import fields, api, models

from email import message_from_string
from email.generator import DecodedGenerator
from email.message import Message

try:
    from base64 import encodebytes
except ImportError:
    from base64 import encodestring as encodebytes


#: The name of the field to store the raw email.
RAW_EMAIL_ATTR = 'raw_email'


logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    raw_email = fields.Binary('Raw Email',
                              default=b'',
                              help='The raw email message unprocessed.')


# Since the mailgate program actually call mail_thread's `message_process`,
# that, in turn, call `message_parse` this is the place to make the raw_email
# stuff happen, not the `mail_message` object.
class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_parse(self, message, save_original=False):
        if not isinstance(message, Message):
            message = force_str(message)
            message = message_from_string(message)
        result = super(MailThread, self).message_parse(
            message, save_original=save_original
        )
        try:
            from io import BytesIO
            buf = BytesIO()
            gen = DecodedGenerator(buf, mangle_from_=False)
            gen.flatten(message)
            result[RAW_EMAIL_ATTR] = encodebytes(buf.getvalue())
        except Exception:  # noqa
            # Should any error happen while reencoding; it's not worthy to
            # stop the message from being created.  Just log.
            logger.exception(
                'Error while re-encoding raw email.  Continuing normally'
            )
        return result
