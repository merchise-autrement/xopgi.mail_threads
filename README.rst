=======================================================
 Merchise's General Extensions to OpenERP Mail Threads
=======================================================

Overview
========

Generalizes how OpenERP searches for incoming message's threads.  Several mail
implementations (like that of Evaneos) don't include the "References:" and
"In-Reply-To:", different strategies are needed for these cases.

This addons allows to register different strategies.


Note about installation
=======================

We are using buildout_ to deploy several configurations of OpenERP.  We also
developed a framework-level package for `OpenERP/Odoo`_ called xoeuf_.  Xoeuf
allows addons to be installed like true Python packages instead of just
copying them to a directory.

Nevertheless, you may just copy the ``xopgi_mail_threads`` to your addons
directory.

This addons does not use features not in the core OpenERP_.


Usage
=====

Mail routers are Python new-style classes that inherit from ``MailRouter``.
They must implement the ``is_applicable()`` to test whether a message should
be routed using this router, and the method ``apply()`` to actually do the
routing.

::

   from openerp.addons.xopgi_mail_threads import MailRouter


   class MyRouter(MailRouter):
       @classmethod
       def is_applicable(cls, cr, uid, message):
          return False

       @classmethod
       def apply(cls, cr, uid, routes, message):
           return routes



.. _buildout: http://buildout.org/
.. _OpenERP/Odoo: Odoo_
.. _OpenERP: Odoo_
.. _Odoo: http://github.com/odoo/odoo
.. _xoeuf: http://github.com/merchise-autrement/xoeuf
