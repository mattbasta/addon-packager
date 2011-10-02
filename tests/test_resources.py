import os

from nose.tools import eq_
from pyquery import PyQuery as pq

import packager.main as p

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')


def test_installrdf():
    data = {
        'id': 'slap@tickle.me',
        'version': '1.0',
        'name': 'Wamp Wamp',
        'description': 'descrrrrrr',
        'author_name': 'me',
        'contributors': 'mr. bean\nmrs. bean',
        'targetapplications': [
            {
                'guid': '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}',
                'min_ver': '3.0',
                'max_ver': '8.*'
            }
        ],
        'slug': 'sllllllug'
    }
    features = ('preferences_dialog', 'about_dialog')

    content = p.build_installrdf(data, features).replace('em:', 'em_')
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


def test_resourcepath():
    """Make sure the resource path is valid."""
    assert os.path.exists(p.RESOURCES_PATH), (
        'Resource path %r could be not found' % p.RESOURCES_PATH)


def test_get_resource():
    """Test that resources are properly fetched."""
    rpath = p.RESOURCES_PATH
    p.RESOURCES_PATH = RESOURCES_PATH

    eq_(p._get_resource("test.txt"), "{foo}")
    eq_(p._get_resource("test.txt", {"foo": "bar"}), "bar")

    p.RESOURCES_PATH = rpath


def test_write_resource():
    """Test that data is properly written to the XPI manager."""
    rpath = p.RESOURCES_PATH
    p.RESOURCES_PATH = RESOURCES_PATH

    # Test that files with associated data are routed through _get_resource.
    mx = MockXPI("test.txt", "bar")
    p._write_resource("test.txt", mx, {"foo": "bar"})

    # Test that files without associated data are written with write_file.
    mx = MockXPI("test.txt", p._get_path("test.txt"))
    p._write_resource("test.txt", mx)

    p.RESOURCES_PATH = rpath


class MockXPI(object):
    """
    Mock the XPI object in order to make assertions on the data that is saved
    to the output package.
    """

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def write(self, filename, data):
        assert filename == self.filename
        assert data == self.data

    def write_file(self, filename, external_file):
        self.write(filename, external_file)
