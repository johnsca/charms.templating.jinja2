# Copyright 2014-2015 Canonical Limited.
#
# This file is part of charm-helpers.
#
# charm-helpers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3 as
# published by the Free Software Foundation.
#
# charm-helpers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with charm-helpers.  If not, see <http://www.gnu.org/licenses/>.

import os

from jinja2 import Template, FileSystemLoader, Environment, exceptions

from charmhelpers.core import host
from charmhelpers.core import hookenv


def render(source=None, target=None, context=None, template=None,
           owner='root', group='root', perms=0o444, encoding='UTF-8',
           filters=None, tests=None,
           templates_dir=None, template_loader=None):
    """
    Render a template.

    Example usages::

        render('app.conf.j2', '/etc/app.conf', {
            'my_var': 'my_val',
        })

        output = render(
            'tmpl.j2',
            tests={
                'isnumeric': lambda s: s.isnumeric(),
            })

        from jinja2 import Template
        output = render(
            template='{{ config["my-opt"]|my_upper }}',
            filters={
                'my_upper': lambda s: s.upper(),
            })

    :param str source: Template path, relative to ``templates_dir``.
    :param str target: Target path.  Should be absolute path, or ``None``
        (in which case the output will not be written, and only returned).
    :param dict context: Map of additional context variables to be passed
        to the template.  Templates will always be given the following
        variables:
          * ``config`` A mapping of all of the charm config options.
    :param str owner: Name of the user that should own the target file.
    :param str group: Name of the group that should own the target file.
    :param int perms: Permissions of the target file.
    :param dict filters: Custom filters to be given to the template.
        Templates will always be given the following filters:
          * ``map_format``
            Exactly the same as the built-in ``format`` filter, but
            with the order of the args rearranged to work with ``map``.
    :param str templates_dir: Directory in which to look for templates.
        Defaults to ``$CHARM_DIR/templates``.
    :param str encoding: Defaults to ``UTF-8``.
    :param class template_loader: Template loader class to use instead of
        ``FileSystemLoader``.

    :returns: The rendered template is returned as well as written to the
        target file (if not ``None``).
    """
    if not any([source, template]):
        raise TypeError('Either source or template argument must be provided')
    if all([source, template]):
        raise TypeError('Only one of source or template argument must be provided')

    if template_loader:
        template_env = Environment(loader=template_loader)
    else:
        if templates_dir is None:
            templates_dir = os.path.join(hookenv.charm_dir(), 'templates')
        template_env = Environment(loader=FileSystemLoader(templates_dir))
    template_env.tests.update(tests or {})
    template_env.filters.update(dict({
        'map_format': lambda v, p: p % v,
    }, **(filters or {})))
    if template and isinstance(template, Template):
        template = template
    elif template:
        template = template_env.from_string(template)
    else:
        try:
            source = source
            template = template_env.get_template(source)
        except exceptions.TemplateNotFound as e:
            hookenv.log('Could not load template %s from %s.' %
                        (source, templates_dir),
                        level=hookenv.ERROR)
            raise e
    context = dict({'config': hookenv.config()}, **(context or {}))
    content = template.render(context)
    if target:
        target_dir = os.path.dirname(target)
        if not os.path.exists(target_dir):
            # If we have to create the dir, make its perms equal to file perms,
            # but with X bits equal to the R bits and at least owner-writable.
            dir_perms = perms | 0o200 | (perms & 0o444) >> 2
            host.mkdir(os.path.dirname(target), owner, group, perms=dir_perms)
        host.write_file(target, content.encode(encoding), owner, group, perms)
    return content
