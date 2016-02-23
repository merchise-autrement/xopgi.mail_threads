# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# mail_messages
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-06-20

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


from xoutil.string import safe_encode
from xoeuf.osv.orm import get_modelname

from openerp.osv import fields
from openerp.osv.orm import AbstractModel, Model
from openerp.addons.mail.mail_message import mail_message as _base
from openerp.addons.mail.mail_thread import mail_thread as _base_mail_thread

from email.generator import Generator


#: The name of the field to store the raw email.
RAW_EMAIL_ATTR = 'raw_email'


class mail_message(Model):
    _name = get_modelname(_base)
    _inherit = _name

    _columns = {
        RAW_EMAIL_ATTR:
            fields.text('Raw Email',
                        help='The raw email message unprocessed.')
    }

    _defaults = {
        RAW_EMAIL_ATTR: ''
    }


# Since the mailgate program actually call mail_thread's `message_process`,
# that, in turn, call `message_parse` this is the place to make the raw_email
# stuff happen, not the `mail_message` object.
class mail_thread(AbstractModel):
    _name = get_modelname(_base_mail_thread)
    _inherit = _name

    def message_parse(self, cr, uid, message, save_original=False,
                      context=None):
        from email.message import Message
        from xoutil.string import safe_decode
        assert isinstance(message, Message)
        result = super(mail_thread, self).message_parse(
            cr, uid, message, save_original=save_original, context=context)
        from io import BytesIO
        buf = BytesIO()
        # Re-encode to the connection encoding
        gen = ReencodingGenerator(buf, mangle_from_=False,
                                  target_charset=cr._cnx.encoding)
        gen.flatten(message)
        message = safe_decode(buf.getvalue(), encoding=cr._cnx.encoding)
        result[RAW_EMAIL_ATTR] = message
        return result


SAME_AS_ORIGINAL = None
PREPEND_X = object()

HEADERS_TO_COPY = {
    str('Content-Disposition'): SAME_AS_ORIGINAL,
    str('Content-Type'): SAME_AS_ORIGINAL,
    str('Content-Id'): SAME_AS_ORIGINAL,
}


# TODO: Move to xoutil after thorough inspection.
class ReencodingGenerator(Generator):
    '''A generator that re-encodes text bodies to a given charset.

    A message with 'text/...' Content-Type will be re-encoded (if needed) to
    the target charset.

    :param chop: Indicates whether to remove non-textual parts in a MIME
                 message.  If False non-textual parts won't be removed.

    '''
    def __init__(self, outfp, mangle_from_=True, maxheaderlen=78,
                 target_charset='utf-8',
                 chop=True):
        from email.charset import Charset, QP
        self._target_charset = target_charset
        self.chop = chop
        self.charset = charset = Charset(target_charset)
        charset.body_encoding = QP
        Generator.__init__(
            self,
            outfp,
            mangle_from_=mangle_from_,
            maxheaderlen=maxheaderlen,
        )

    def clone(self, fp):
        result = Generator.clone(self, fp)
        result._target_charset = self._target_charset
        return result

    def _write(self, msg):
        encoded = self._reencode(msg)
        if encoded:
            return Generator._write(self, encoded)

    @staticmethod
    def _istext(msg):
        '''Whether the message (or part) is acceptable as text.'''
        ct = msg.get_content_type() or msg.get_default_type()
        types = ('text/', )
        return any(ct.startswith(t) for t in types)

    @staticmethod
    def _is_attachment(msg):
        disposition = msg['Content-Disposition']
        return disposition and disposition.startswith('attachment;')

    def _reencode(self, msg):
        from xoutil.string import safe_decode, safe_encode
        from copy import deepcopy
        if self._istext(msg) and not self._is_attachment(msg):
            from_charset = _get_content_chartset(msg, 'ascii')
            target = self._target_charset
            # The `decode` should handle the Content-Transfer-Encoding, thus
            # we removed the header from the resulting message so that
            # set_payload reintroduce the proper one if needed.
            payload = msg.get_payload(decode=True)
            if payload:
                result = deepcopy(msg)
                newpayload = safe_encode(
                    safe_decode(payload, encoding=from_charset),
                    encoding=target
                )
                result.set_payload(newpayload, self.charset)
                # MIME-Version can be introduced by set_payload, remove it if
                # the original message didn't have it.
                if 'MIME-Version' not in msg:
                    del result['MIME-Version']
            else:
                result = msg
            return result
        elif msg.is_multipart() or not self.chop:
            return msg
        else:
            # If the message is not a text message worth keeping return an
            # empty part.
            return _chopped(msg, self.charset)


def _chopped(msg, charset):
    from email.message import Message
    result = Message()
    for header, target in HEADERS_TO_COPY.items():
        if target is SAME_AS_ORIGINAL:
            target = safe_encode(header)
        elif target is PREPEND_X:
            target = str('X-{}').format(safe_encode(header))
        result[target] = msg[header]
    result.set_payload('[Removed part]', charset)
    if 'MIME-Version' not in msg:
        del result['MIME-Version']
    return result


def _get_content_chartset(msg, default='ascii'):
    '''Extract the content chartset of the message.

    '''
    from xoutil.string import cut_prefixes, cut_suffixes
    assert default
    return cut_suffixes(
        cut_prefixes(
            msg.get_content_charset(default),
            'charset=', '"', '\''
        ),
        '"', '\''
    )


class HeaderOnlyGenerator(Generator):
    '''A generator that only prints the headers.

    It makes sure the result is on a given charset.

    '''
    def __init__(self, outfp, mangle_from_=True, maxheaderlen=78,
                 target_charset='utf-8'):
        self._target_charset = target_charset
        Generator.__init__(
            self,
            outfp,
            mangle_from_=mangle_from_,
            maxheaderlen=maxheaderlen,
        )

    def clone(self, fp):
        result = Generator.clone(self, fp)
        result._target_charset = self._target_charset
        return result

    def _write(self, msg):
        from xoutil.string import safe_decode, safe_encode
        res = Generator._write_headers(self, msg)
        # Headers are supposed to be always in US-ASCII, so let's decode from
        # it and encode it to the target encoding.
        return safe_encode(
            safe_decode(res, encoding='ascii'),
            encoding=self._target_charset
        )
