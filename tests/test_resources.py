import copy
import os

from mock import Mock, patch
from nose.tools import eq_
from pyquery import PyQuery as pq

import packager.main as p
from packager.main import escape_all, FIREFOX_GUID

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')

data = {
    'id': 'slap@tickle.me<script>',
    'version': '1.0<script>',
    'name': 'Wamp Wamp<script>',
    'description': 'descrrrrrr<script>',
    'author_name': 'me<script>',
    'contributors': 'mr. bean <mr@bean.com>\nmrs. bean <script>',
    'targetapplications': [
        {
            'guid': '%s<script>' % FIREFOX_GUID,
            'min_ver': '3.0<script>',
            'max_ver': '8.*<script>'
        }
    ],
    'slug': 'sllllllug<script>'
}

features = ('preferences_dialog', 'about_dialog')


def test_installrdf():
    # Since `build_installrdf` will sanitize the dict above, send a copy of
    # `data` so we can compare the escaped text output to the original `data`.
    content = p.build_installrdf(copy.deepcopy(data), features)

    # PyQuery thinks colons are pseudo-selectors, so we do this.
    content = content.replace('em:', 'em_')
    doc = pq(content, parser='html_fragments')

    tag = lambda t: doc('rdf > description > %s' % t)

    eq_(tag('em_type').text(), '2')
    eq_(tag('em_id').text(), data['id'])
    eq_(tag('em_version').text(), data['version'])
    eq_(tag('em_name').text(), data['name'])
    eq_(tag('em_description').text(), data['description'])
    eq_(tag('em_creator').text(), data['author_name'])

    contributors = data['contributors'].split('\n')
    for c_xml, c_data in zip(tag('em_contributor'), contributors):
        eq_(pq(c_xml).text(), c_data)

    apps = data['targetapplications']
    eq_(tag('em_targetapplication').length, len(apps))
    eq_(tag('em_targetapplication description').length, 1)
    for app_xml, app in zip(tag('em_targetapplication description'), apps):
        app_tag = pq(app_xml)
        eq_(app_tag('em_id').text(), app['guid'])
        eq_(app_tag('em_minversion').text(), app['min_ver'])
        eq_(app_tag('em_maxversion').text(), app['max_ver'])

    path = 'chrome://%s/content/' % data['slug']
    if 'preferences_dialog' in features:
        eq_(tag('em_optionsurl').text(), path + 'options.xul')
    if 'about_dialog' in features:
        eq_(tag('em_abouturl').text(), path + 'about.xul')


def test_default_prefs():
    data = {'slug': 'my_addon'}
    fn = 'defaults/preferences/prefs.js'
    mx = MockXPI(fn)
    p._write_resource(fn, mx, data)
    mx.assert_file(fn)

    # Ensure that the correct output got written.
    output = p._get_resource(fn, data)
    expected = open(p._get_path(fn)).read().replace('%(slug)s', data['slug'])
    eq_(output.strip(), expected.strip())

    # Ensure that the file got written correctly to the XPI.
    mx.assert_data(fn, expected)


@patch('validator.xpi.XPIManager.write')
@patch('packager.main._write_resource')
def test_ff_overlay(_write_resource, write):
    """The files `ff-overlay.xul` and `ff-overlay.js` should appear in
    the package if Firefox is a target application.

    """
    data_ = copy.deepcopy(data)
    data_['targetapplications'][0]['guid'] = FIREFOX_GUID

    fn = 'some_file.zip'
    p.packager(data_, fn, features)

    # Ensure that `xpi.write(...)` was called with `ff-overlay.xul`.
    called_name, called_data = write.call_args_list[-1][0]
    eq_(called_name, 'chrome/content/ff-overlay.xul')

    # Ensure that `_write_resource(...)` was called with `ff-overlay.js`.
    called_name, xpi_obj, called_data = _write_resource.call_args_list[-1][0]
    eq_(called_name, 'chrome/content/ff-overlay.js')
    eq_(called_data, data_)

    os.unlink(fn)


@patch('validator.xpi.XPIManager.write')
@patch('packager.main._write_resource')
def test_non_ff_overlay(_write_resource, write):
    """The files `ff-overlay.xul` and `ff-overlay.js` should not appear
    in the package if Firefox isn't one of the target applications.

    """
    fn = 'some_file.zip'
    p.packager(data, fn, features)

    # Ensure that `xpi.write(...)` was not called with 'ff-overlay.xul'.
    called_name, called_data = write.call_args_list[-1][0]
    assert called_name != 'chrome/content/ff-overlay.xul', (
        'Package incorrectly included ff-overlay.xul for a non-Firefox add-on')

    # Ensure that `_write_resource(...)` was not called with 'ff-overlay.js'.
    called_name, xpi_obj, called_data = _write_resource.call_args_list[-1][0]
    assert called_name != 'chrome/content/ff-overlay.js', (
        'Package incorrectly included ff-overlay.js for a non-Firefox add-on')

    os.unlink(fn)


def test_resourcepath():
    """Make sure the resource path is valid."""
    assert os.path.exists(p.RESOURCES_PATH), (
        'Resource path %r could be not found' % p.RESOURCES_PATH)


def test_get_resource():
    """Test that resources are properly fetched."""
    rpath = p.RESOURCES_PATH
    p.RESOURCES_PATH = RESOURCES_PATH

    fn = 'test.txt'
    eq_(p._get_resource(fn), '{foo}')
    eq_(p._get_resource(fn, {'foo': 'bar'}), 'bar')

    p.RESOURCES_PATH = rpath


def test_write_resource():
    """Test that data is properly written to the XPI manager."""
    rpath = p.RESOURCES_PATH
    p.RESOURCES_PATH = RESOURCES_PATH
    fn = 'test.txt'

    # Test that files with associated data are routed through _get_resource.
    mx = MockXPI(fn)
    p._write_resource(fn, mx, {'foo': 'bar'})
    mx.assert_file(fn)

    # Test that files without associated data are written with write_file.
    mx = MockXPI(fn)
    p._write_resource(fn, mx)
    mx.assert_file(fn)

    p.RESOURCES_PATH = rpath


class MockXPI(object):
    """Mock the XPI object in order to make assertions on the data that
    is saved to the output package.

    """

    def __init__(self, filename):
        self.filename = filename
        self.contents = {}

    def assert_file(self, filename):
        assert filename in self.contents, (
            'File %r does not appear in mock XPI' % filename)

    def assert_data(self, filename, data):
        eq_(self.contents[filename].strip(), data.strip())

    def write(self, filename, data):
        self.contents[filename] = data

    def write_file(self, filename, external_file):
        self.write(filename, external_file)
