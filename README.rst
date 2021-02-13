Ella Admin
==========

Admin Interfaces for Ella

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


:License: MIT


About
-------

This is a series of admin interfaces for the Ella (code https://gitlab.com/alleles/ella) Clinical Genomics Portal.

This project is under development and NOT recommended for production use!

`Docs <https://dabble-of-devops-ella-admin-docs.s3.amazonaws.com/index.html>`_ are a WIP and are hosted on S3.

Commands
---------

Please see the Makefile for the full list of commands.

Bring up the Development Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This brings up the dev instance with an empty database. You will not be able to login to the UI until you add some users.

::

    make clean
    make dev

If you'd like to add in some demo gene panels + user data run the `make demo` command.

::

    make db

Add the Demo + Analysis Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This has an analysis complete for analysis_id 2, name brca_sample_1.HBOCUTV_v01.

You can login using testuser1 Password#123.

::

    make clean
    make load

Then open up http://localhost:5001. You may have to wait a few seconds for it to load.

Add the Demo Data - No Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This creates a "clean" Ella instance with only the demo data. If you look in the Makefile you will see how to load the data in using the Ella CLI.

::

    make demo

You'll have to refresh the user password too.

::

    make ella_user=testuser1 user_reset_password

Open up http://localhost:5001 and change the password for testuser1 from the password shown with `make ella_user=testuser1 user_reset_password` to your new password.

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

#TODO this is documentation from the django-cookiecutter

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ docker-compose -f local.yml exec django bash -c "python manage.py createsuperuser"

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ docker-compose -f local.yml exec django bash -c "mypy ella_admin"

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html


Deployment
----------

The following details how to deploy this application.



Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html



