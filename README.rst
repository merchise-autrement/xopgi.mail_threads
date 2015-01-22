=======================================================
 Merchise's General Extensions to OpenERP Mail Threads
=======================================================

Overview
========

Generalizes how OpenERP searches for incoming message's threads.  Several mail
implementations (like that of Evaneos) don't include the "References:" and
"In-Reply-To:", different strategies are needed for these cases.

This addons allows to register different strategies.

Also allows to register `transports` for outgoing messages.  Transports allow
to deliver message using different mechanisms.  A simple application of
transports is to choose one of several SMTP servers to send a given message
based on some conditions.  Another application can be to use LMTP instead of
SMTP, or some other sort of bridge.


Note about installation
=======================

We are using buildout_ to deploy our of OpenERP servers.  We also developed a
framework-level package for `OpenERP/Odoo`_ called xoeuf_.  Xoeuf allows
addons to be installed like true Python distributions instead of just copying
them to a directory.

Nevertheless you may just copy ``xopgi_mail_threads`` to your addons
directory.

This addons does not use features not in the core OpenERP_.


Usage
=====

Mail routers
------------

Mail routers are Python new-style classes that inherit from ``MailRouter``.
They must implement the ``is_applicable()`` class method to test whether a
message should be routed using this router, and the class method ``apply()``
to actually do the routing.

::

   from openerp.addons.xopgi_mail_threads import MailRouter

   class MyRouter(MailRouter):
       @classmethod
       def is_applicable(cls, cr, uid, message):
          return False

       @classmethod
       def apply(cls, cr, uid, routes, message):
           return routes


Mail transports
---------------

Mail transports are Python new-style classes that inherit from
``MailTransportRouter``.  Transports must implement the following methods:

``query(cr, uid, message, context=None)``

   Called to know whether this transport can deliver a `message`.  It return
   value indicates whether the transport can or cannot deliver the message.

``prepare_message(cr, uid, message, context=None)``

   This is called for the *selected* transport that will deliver the message.

   Allows to change the message before delivery and the connection data.

   Return a named tuple ``(message, connection_data)`` that indicates the
   message that should be sent and the connection data that should be used as
   arguments for the ``send_email`` method of ``ir.mail_server``.


``deliver(cr, uid, message, data, context=None)``

   Deliver the message if possible.

   Return False to fallback to OpenERP's default implementation.

   Inside this method the ``send_email`` method of the ``ir.mail_server``
   object can be used and the transport won't be re-elected but another one
   will.  This allows for several transports to kick in and do their magic as
   pipeline.  Notice this may, however, slow the delivery.  Transports are not
   meant for the unwary users, but for system designers.  Furthermore, the
   order in which they will be elected is not totally defined.


.. _buildout: http://buildout.org/
.. _OpenERP/Odoo: Odoo_
.. _OpenERP: Odoo_
.. _Odoo: http://github.com/odoo/odoo
.. _xoeuf: http://github.com/merchise-autrement/xoeuf
