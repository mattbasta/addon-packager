import os
from xml.sax.saxutils import escape


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")

def packager(data, xpi_path):
    """
    Package an add-on from input data. The resulting package will be saved as
    xpi_path.

    Format:
        - uid : <em:id> value
        - version : <em:version>
        - name : <em:name>
        - description : <em:description>
        - author_name : <em:author>
        - contributors : /n-delimited list of contributors
        - platforms : List containing values from zamboni's amo.PLATFORMS
        - targetapplications : Dict in the form of:
            {
            "min_ver": "3.6",
            "max_ver": "6.0a1",
            "guid": "...",
            "enabled": True # Must be True!
            }
        - uuid : A UUID value that is unique to this package
        - slug : A slug value based on the name which will be used as a package
                 identifier.

    xpi_path should be the file path to build the XPI at.

    features should be a set containing string names of each of the features to
        include.
    """

    # Instantitate the XPI Manager
    from validator.xpi import XPIManager
    xpi = XPIManager(xpi_path, mode="w")

    xpi.write("install.rdf", build_installrdf(data))
    _write_resource("chrome.manifest", xpi, data)
    _write_resource("defaults/preferences/prefs.js", xpi, data)
    _write_resource("chrome/content/overlay.js", xpi, data)
    _write_resource("chrome/skin/overlay.css", xpi, data)
    _write_resource("chrome/locale/en-US/overlay.dtd", xpi, data)
    _write_resource("chrome/locale/en-US/overlay.properties", xpi, data)

    if "about" in features:
        _write_resource("chrome/content/about.xul", xpi, data)
        _write_resource("chrome/locale/en-US/about.dtd", xpi)

    if "options" in features:
        _write_resource("chrome/content/options.xul", xpi, data)
        _write_resource("chrome/locale/en-US/options.dtd", xpi)

    xpi.zf.close()
    return xpi_path


def _get_path(filename):
    """A shortcut to get the path to a resource."""
    return os.path.join(RESOURCES_PATH, filename)


def _get_resource(filename, data=None):
    """
    A shortcut to get the contents of a file.

    If data is specified, each of the keys will be replaced (in the format of
    %key% from the contents of the file) with the value from data.
    """
    resource = open(_get_path(filename))
    output = resource.read()

    if data:
        for key in data.keys():
            if key in output:
                output = output.replace("%%%s%%" % key, data[key])

    resource.close()
    return output


def _write_resource(filename, xpi, data=None):
    """A shortcut to write a resource to an XPI."""
    if not data:
        xpi.write_file(filename, _get_path(filename))
    else:
        xpi.write(filename, _get_resource(filename, data))


def build_installrdf(data):

    # Build the install.rdf file

    rdf_description = (
            ("<em:description>%s</em:description>" %
                 escape(data["description"])) if
            data["description"] else "")

    rdf_contributors = "\n".join([
            "<em:contributor>%s</em:contributor>" % escape(c.strip()) for
            c in
            data["contributors"].split("\n") if
            c])

    # Target platforms are disabled because they're exclusive, not inclusive.
    # Enabling them will take some time to iron out, and they're not supported
    # by the validator now, anyway.

    # # 54 minutes were spent trying to find the OS_TARGET for Maemo. Turns out
    # # it doesn't matter anyway (and there's no way to target it with
    # # <em:targetPlatform>), so it doesn't matter one way or another.
    # platform_ref = {"linux": "Linux",
    #                 "mac": "Darwin",
    #                 "windows": "WINNT",
    #                 "android": "Android",
    #                 "maemo": "Linux"} # TODO: LOLWUT? A big F.U. to OS_TARGET.
    #
    # # Just ignore the All Platforms and All Mobile Platforms boxes. The
    # # <em:targetPlatform> field is used to narrow support, not broaden it.
    # rdf_targetplatforms = "\n".join([
    #         "<em:targetPlatform>%s</em:targetPlatform>" % platform_ref[p] for
    #         p in
    #         data["platforms"] if
    #         (p in platform_ref)])

    rdf_targetapplications = []
    for app in data["targetapplications"]:
        rdf_targetapplications.append("""
        <em:targetApplication>
        <Description>
            <em:id>%s</em:id>
            <em:minVersion>%s</em:minVersion>
            <em:maxVersion>%s</em:maxVersion>
        </Description>
        </em:targetApplication>
        """ % map(escape, (app["guid"], app["min_ver"], app["max_ver"])))

    rdf_targetapplications = "\n".join(rdf_targetapplications)

    install_rdf = _get_resource("install.rdf")
    return install_rdf % (
            escape(data["uid"]),
            escape(data["version"]),
            escape(data["name"]),
            rdf_description,
            escape(data["author_name"]),
            rdf_contributors,
            "", # rdf_targetplatforms,
            rdf_targetapplications)


def build_chrome_manifest(data):

    chrome_manifest = [_get_resource("chrome.manifest", data)]
    if any(app["guid"] == "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}" for
           app in data["targetapplications"]):
        chrome_manifest.append("/n")
        chrome_manifest.append(("overlay\t"
                                "chrome://browser/content/browser.xul\t"
                                "chrome://%s/content/ff-overlay.xul") %
                                   data["slug"])

    return "\n".join(chrome_manifest)

