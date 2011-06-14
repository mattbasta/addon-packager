import nose
import os
import packager.main as p


def test_resourcepath():
    """Make sure the resource path is valid."""

    assert os.path.exists(p.RESOURCES_PATH)


def test_get_resource():
    """Test that resources are properly fetched."""

    rpath = p.RESOURCES_PATH
    p.RESOURCES_PATH = "tests/resources"

    nose.tools.eq_(p._get_resource("test.txt"), "{foo}")
    nose.tools.eq_(p._get_resource("test.txt", {"foo": "bar"}), "bar")

    p.RESOURCES_PATH = rpath


def test_write_resource():
    """Test that data is properly written to the XPI manager."""

    rpath = p.RESOURCES_PATH
    p.RESOURCES_PATH = "tests/resources"

    # Test that files with associated data are routed through _get_resource
    mx = MockXPI("test.txt", "bar")
    p._write_resource("test.txt", mx, {"foo": "bar"})

    # Test that files without associated data are written with write_file
    mx = MockXPI("test.txt", p._get_path("test.txt"))
    p._write_resource("test.txt", mx)

    p.RESOURCES_PATH = rpath


class MockXPI():
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

