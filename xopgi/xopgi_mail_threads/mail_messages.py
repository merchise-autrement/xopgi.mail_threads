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

from xoutil.eight.string import force as force_str
from xoutil.future.codecs import safe_encode, safe_decode

from xoeuf import fields, api, models

from email import message_from_string
from email.generator import DecodedGenerator
from email.message import Message


#: The name of the field to store the raw email.
RAW_EMAIL_ATTR = 'raw_email'


class MailMessage(models.Model):
    _inherit = 'mail.message'

    raw_email = fields.Binary('Raw Email',
                              default=b'',
                              help='The raw email message unprocessed.')


# Since the mailgate program actually call mail_thread's `message_process`,
# that, in turn, call `message_parse` this is the place to make the raw_email
# stuff happen, not the `mail_message` object.
class MailThread(models.AbstractModel):
    _name = 'mail.thread'
    _inherit = _name

    @api.model
    def message_parse(self, message, save_original=False):
        if not isinstance(message, Message):
            message = force_str(message)
            message = message_from_string(message)
        result = super(MailThread, self).message_parse(
            message, save_original=save_original
        )
        from io import BytesIO
        buf = BytesIO()
        # Re-encode to the connection encoding
        gen = ReencodingGenerator(buf, mangle_from_=False,
                                  target_charset=self._cr._cnx.encoding)
        gen.flatten(message)
        message = safe_decode(buf.getvalue(), encoding=self._cr._cnx.encoding)
        result[RAW_EMAIL_ATTR] = message
        return result


# TODO: When we are in Python 3, this won't be needed: we'll be able to use
# DecodedGenerator directly.
class ReencodingGenerator(DecodedGenerator):
    '''A generator that re-encodes text bodies to a given charset.

    A message with 'text/...' Content-Type will be re-encoded (if needed) to
    the target charset.

    '''
    def __init__(self, outfp, mangle_from_=True, maxheaderlen=78,
                 target_charset='utf-8'):
        from email.charset import Charset, QP
        self._target_charset = target_charset
        self.charset = charset = Charset(target_charset)
        charset.body_encoding = QP
        DecodedGenerator.__init__(
            self,
            outfp,
            mangle_from_=mangle_from_,
            maxheaderlen=maxheaderlen,
        )

    def clone(self, fp):
        result = DecodedGenerator.clone(self, fp)
        result._target_charset = self._target_charset
        return result

    def write(self, s):
        DecodedGenerator.write(self, safe_encode(s, self._target_charset))

    # Internal API for Python 3.

    def _new_buffer(self):
        from io import BytesIO
        return BytesIO()

    def _encode(self, s):
        return safe_encode(s, self._target_charset)
