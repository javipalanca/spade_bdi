=========
Spade-BDI
=========

.. image:: https://img.shields.io/pypi/v/spade_bdi.svg
        :target: https://pypi.python.org/pypi/spade

.. image:: https://img.shields.io/pypi/pyversions/spade_bdi.svg
    :target: https://pypi.python.org/pypi/spade_bdi

.. image:: https://img.shields.io/pypi/l/spade_bdi
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://pepy.tech/badge/spade_bdi
    :target: https://pepy.tech/project/spade_bdi
    :alt: Downloads

.. image:: https://readthedocs.org/projects/spade_bdi/badge/?version=latest
        :target: https://spade-bdi.readthedocs.io?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/format/spade_bdi.svg
    :target: https://pypi.python.org/pypi/spade_bdi


Create hybrid agents with a BDI layer for the SPADE MAS Platform.


* Free software: GNU General Public License v3
* Documentation: https://spade-bdi.readthedocs.io. (to be completed)


Features
--------

* Create agents that parse and execute an ASL file written in AgentSpeak.
* Supports Agentspeak-like BDI behaviours.
* Add custom actions and functions.
* Send TELL, UNTELL and ACHIEVE  KQML performatives.

Examples
--------

basic.py::

    import getpass
    from spade_bdi.bdi import BDIAgent

    server = input("Please enter the XMPP server address: ")
    password = getpass.getpass("Please enter the password: ")

    a = BDIAgent("BasicAgent@" + server, password, "basic.asl")
    a.start()

    a.bdi.set_belief("car", "blue", "big")
    a.bdi.print_beliefs()

    print(a.bdi.get_belief("car"))
    a.bdi.print_beliefs()

    a.bdi.remove_belief("car", 'blue', "big")
    a.bdi.print_beliefs()

    print(a.bdi.get_beliefs())
    a.bdi.set_belief("car", 'yellow')


basic.asl::

    !start.

    +!start <-
        +car(red);
        .a_function(3,W);
        .print("w =", W);
        literal_function(red,Y);
        .print("Y =", Y);
        .custom_action(8);
        +truck(blue).

    +car(Color)
     <- .print("The car is ",Color).


Examples
--------

basic.py::

    import getpass
    from spade_bdi.bdi import BDIAgent

    server = input("Please enter the XMPP server address: ")
    password = getpass.getpass("Please enter the password: ")

    a = BDIAgent("BasicAgent@" + server, password, "basic.asl")
    a.start()

    a.bdi.set_belief("car", "blue", "big")
    a.bdi.print_beliefs()

    print(a.bdi.get_belief("car"))
    a.bdi.print_beliefs()

    a.bdi.remove_belief("car", 'blue', "big")
    a.bdi.print_beliefs()

    print(a.bdi.get_beliefs())
    a.bdi.set_belief("car", 'yellow')


basic.asl::

    !start.

    +!start <-
        +car(red);
        .a_function(3,W);
        .print("w =", W);
        literal_function(red,Y);
        .print("Y =", Y);
        .custom_action(8);
        +truck(blue).

    +car(Color)
     <- .print("The car is ",Color).


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
