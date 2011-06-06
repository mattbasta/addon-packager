import nose
import packager.main as p


def test_apply_data():
    """Test that data gets applied properly."""

    data = {"foo": "test",
            "bar": "mozilla"}

    nose.tools.eq_(p._apply_data("i %foo% at %bar%", data),
                   "i test at mozilla")

