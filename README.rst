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


.. _buildout: http://buildout.org/
.. _OpenERP/Odoo: Odoo_
.. _OpenERP: Odoo_
.. _Odoo: http://github.com/odoo/odoo
.. _xoeuf: http://github.com/merchise-autrement/xoeuf
