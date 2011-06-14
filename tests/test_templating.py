import nose
import packager.main as p


def test_apply_data_empty():
    """Test that applying no data with _apply_data does nothing."""

    nose.tools.eq_(p._apply_data("I {heart} you", "foo.xul"), "I {heart} you")
    nose.tools.eq_(p._apply_data("I %(heart)s you", "foo.js"),
                   "I %(heart)s you")


def test_apply_data():
    """Test that data gets applied properly."""

    data = {"foo": "test",
            "bar": "mozilla"}

    nose.tools.eq_(p._apply_data("i {foo} at {bar}", "foo.xul", data),
                   "i test at mozilla")

def test_apply_js_data():
    """Test that data gets applied properly for JS files."""

    data = {"foo": "test",
            "bar": "mozilla"}

    nose.tools.eq_(p._apply_data("i %(foo)s at %(bar)s", "foo.js", data),
                   "i test at mozilla")

