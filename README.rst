charms.templating.jinja2 |badge|
--------------------------------

.. |badge| image:: https://travis-ci.org/juju-solutions/charms.templating.jinja2.svg
    :target: https://travis-ci.org/juju-solutions/charms.templating.jinja2

Helper for rendering Jinja2 templates with charms


Usage
-----

.. code-block:: python

    from charms.templating.jinja2 import render

    render('app.conf.j2', '/etc/app.conf', {
        'my_var': 'my_val',
    })

    output = render(
        'tmpl.j2',
        tests={
            'isnumeric': lambda s: s.isnumeric(),
        })

    output = render(
        template='{{ config["my-opt"]|my_upper }}',
        filters={
            'my_upper': lambda s: s.upper(),
        })

The full documentation is available at http://pythonhosted.org/charms.templating.jinja2/
