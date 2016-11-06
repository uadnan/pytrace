
PyTrace is written on the top of `Bdb <https://docs.python.org/2/library/bdb.html>`_ that will execute small python programs within a sandbox environment and collects heap & stack information on each setup.
Collected information can be later used to demonstrate program execution on GUI. Thanks for checking it out.

--------------
 Installation
--------------
::

   pip install git+https://github.com/uadnan/pytrace

-------
 Usage
-------
.. code:: python

    import pytrace
    traces = pytrace.trace("<PYTHON SCRIPT TO VISUALIZE>")
    print(traces)

Returned traces can't be directly converted to JSON using ``json.dumps``, instead use ``pytrace.json.dumps``

.. code:: python

     from pytrace.json import dumps
     traces_json = dumps(traces)
     print(traces_json)

