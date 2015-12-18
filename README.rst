=======================================================
 Merchise's General Extensions to OpenERP Mail Threads
=======================================================

Overview
========

Generalizes how OpenERP searches the thread for an incoming message.  Several
mail implementations (like that of Evaneos) don't include the "References:"
and "In-Reply-To:".  Different strategies are needed for these cases.

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

Mail routers are used whenever an email reaches the Odoo.  Its job is to
perform an action in response to an email.  Normally the action performed is
to create a new object or place the email inside an existing thread.

Odoo has a limited way to treat incoming messages.  Mail routers allow you to
extend Odoo's capabilities.

Mail routers are implemented with Python new-style classes that inherit from
``MailRouter``.

They must implement following methods:

- ``query(cls, obj, cr, uid, message, context=None)``

  A class method to test whether a message should be routed using this
  router.  It must return either:

  - A single boolean value to indicate whether the router can route the
    message or not.

  - A tuple ``(routeable, data)`` whose first component is the same boolean
    value as before and the second component is an opaque object that is
    passed to the `apply` method as the `data` keyword argument.

  The `obj` argument will be the ``mail.thread`` object.  `message` is the
  parsed message being received.

- ``apply(cls, obj, cr, uid, routes, message, data=None, context=None):``

  A class method that will only called if `query` returned True or ``(True,
  data)``.

  `routes` will be previously detected routes by standard Odoo routing
  mechanisms or possible other routes.

  You must change `routes` in place to either remove or add routes.


Mail transports
---------------

Mail transports are involved whenever an email needs to be sent.  An outgoing
email may be both transformed before delivery and delivered using non-standard
ways.

Mail transports are implemented with Python new-style classes that inherit
from ``MailTransportRouter``.  Transports must implement the following
methods:

``query(obj, cr, uid, message, context=None)``

   This is a classmethod.

   Called to know whether this transport can deliver a `message`.  It returns
   whether the transport can or cannot deliver the message.

   The `obj` is the `ir.mail_server` object.  Useful to access the `pool` so
   that consulting the DB can be done in the same cursor.

   The result must be either a single boolean value indicating if the
   transport can deliver the message, or a tuple ``(deliverable, data)`` whose
   first component is the same boolean value, and the second is an opaque
   object that is going to be passed as the keyword argument `data` of
   `prepare_message`.


``prepare_message(obj, cr, uid, message, data=None, context=None)``

   This is called for the *selected* transport that will deliver the message.

   Allows to change the message before delivery and the connection data.

   Return a named tuple ``(message, connection_data)`` that indicates the
   message that should be sent and the connection data that should be used as
   arguments for the ``send_email`` method of ``ir.mail_server``.

   The `data` keyword argument is the second component of the return value of
   `query`.


``deliver(obj, cr, uid, message, data, context=None)``

   Deliver the message if possible.

   Return False to indicate the message was not sent.

   .. note:: Before 3.0 False would indicate to fallback to OpenERP's default.
      This is no longer true.  We will only fallback if the transport fails
      with an exception other than ``MailDeliveryException``.

   Inside this method you may call the ``send_email`` method of the
   ``ir.mail_server`` object and the current transport won't be re-elected but
   another one will.  This allows for several transports to kick in and do
   their magic as a pipeline.  Notice this may, however, slows the delivery.
   Transports are not meant for the unwary users, but for system designers.
   Furthermore, the order in which they will be elected is not totally
   defined.  The default implementation the `delivery` method simply calls
   ``send_mail``.


Changes in 3.0
==============

The old API was dropped:

- MailRouter now must implement a `query` method instead of the old
  `is_applicable`.

- Routers and transporters are now required to accept the `obj` argument as
  the first positional argument.

- Routers and transporters are required to accept the `data` keyword
  argument.

.. _buildout: http://buildout.org/
.. _OpenERP/Odoo: Odoo_
.. _OpenERP: Odoo_
.. _Odoo: http://github.com/odoo/odoo
.. _xoeuf: http://github.com/merchise-autrement/xoeuf

..
   Local Variables:
   ispell-dictionary: "en"
   End:
