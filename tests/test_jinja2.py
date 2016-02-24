import os
import pwd
import grp
import unittest
import mock
from tempfile import TemporaryDirectory

from jinja2 import Template, DictLoader, TemplateNotFound

from charms.templating.jinja2 import render


class TestJinja2(unittest.TestCase):
    def setUp(self):
        self.tmpl_dir = os.path.join(os.path.dirname(__file__), 'data')

        config_p = mock.patch('charmhelpers.core.hookenv.config')
        self.config = {}
        config_m = config_p.start()
        config_m.side_effect = lambda: self.config
        self.addCleanup(config_p.stop)

        charmdir_p = mock.patch('charmhelpers.core.hookenv.charm_dir')
        charmdir_m = charmdir_p.start()
        charmdir_m.return_value = self.tmpl_dir
        self.addCleanup(charmdir_p.stop)

    def test_missing(self):
        with mock.patch('charmhelpers.core.hookenv.log') as mlog:
            self.assertRaises(TemplateNotFound, render, 'missing', templates_dir='dir')
            mlog.assert_called_once_with('Could not load template missing from dir.', level=mock.ANY)

    def test_basic(self):
        self.config = {'cfg-name': 'cfg-value'}
        output = render('basic.j2', context={'name': 'value'})
        self.assertEqual(output, 'name=value\n'
                                 'cfg-name=cfg-value')

        output = render(template='{{ config["cfg-name"] }}')
        self.assertEqual(output, 'cfg-value')

        output = render(template=Template('{{ config["cfg-name"] }}'))
        self.assertEqual(output, 'cfg-value')

    def test_filters(self):
        filters = {'test': 'test({})'.format}
        output = render('filters.j2', filters=filters)
        self.assertEqual(output, 'test(value)\n'
                                 'fm-value1,fm-value2')
        self.assertEqual(render(template='{{"value"|test}}', filters=filters),
                         'test(value)')

    def test_tests(self):
        tests = {'test': lambda s: s == 'foo'}
        self.assertEqual(render('tests.j2', context={'foo': 'foo'}, tests=tests), 'Yep')
        self.assertEqual(render('tests.j2', context={'foo': 'bar'}, tests=tests), 'Nope')

        tmpl = '{% if foo is test %}Yep{% else %}Nope{% endif %}'
        self.assertEqual(render(template=tmpl, context={'foo': 'foo'}, tests=tests), 'Yep')
        self.assertEqual(render(template=tmpl, context={'foo': 'bar'}, tests=tests), 'Nope')

    def test_dir(self):
        output = render('test.j2',
                        templates_dir=os.path.join(self.tmpl_dir, 'templates/nested'))
        self.assertEqual(output, 'test')

    def test_loader(self):
        output = render('loading.j2',
                        template_loader=DictLoader({
                            'loading.j2': 'test',
                        }))
        self.assertEqual(output, 'test')

    @mock.patch('charmhelpers.core.host.log', mock.Mock())
    def test_write(self):
        with TemporaryDirectory() as tmpdir:
            uid = os.geteuid()
            user = pwd.getpwuid(uid).pw_name
            gid = os.getegid()
            group = grp.getgrgid(gid).gr_name
            out_dir = os.path.join(tmpdir, 'test')
            out_file = os.path.join(out_dir, 'output.txt')
            render('nested/test.j2', out_file,
                   owner=user, group=group, perms=0o400)
            with open(out_file) as of:
                self.assertEqual(of.read(), 'test')
            dir_stat = os.stat(out_dir)
            self.assertEqual(dir_stat.st_mode & 0o777, 0o700)
            self.assertEqual(dir_stat.st_uid, uid)
            self.assertEqual(dir_stat.st_gid, gid)
            file_stat = os.stat(out_file)
            self.assertEqual(file_stat.st_mode & 0o777, 0o400)
            self.assertEqual(file_stat.st_uid, uid)
            self.assertEqual(file_stat.st_gid, gid)
