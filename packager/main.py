import os
from xml.sax.saxutils import escape


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")

def packager(data, xpi_path, features):
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
    xpi.write("chrome.manifest",
              build_chrome_manifest(data, features, is_firefox))
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

    if "button" in features:
        _write_resource("chrome/skin/toolbar-button.png", xpi)

    if "sidebar" in features:
        _write_resource("chrome/content/ff-sidebar.js", xpi)
        _write_resource("chrome/content/ff-sidebar.xul", xpi)

    # Multiple features require ff-overlay.xul
    if any(feature in features for feature in ("button",
                                               "contextmenu",
                                               "mainmenu",
                                               "sidebar")):
        xpi.write("chrome/content/ff-overlay.xul",
                  _build_ffoverlay_xul(data, features, is_firefox))
        _write_resource("chrome/content/ff-overlay.js", xpi, data)

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
    output = _apply_data(resource.read(), data)

    resource.close()
    return output.strip()


def _apply_data(blob, data=None):
    """Apply a dict of variables to the file as a basic template."""

    if data:
        for key in data:
            template_key = "%%%s%%" % key
            if template_key in blob:
                blob = blob.replace(template_key, data[key])

    return blob


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
        """ % (escape(app["guid"]),
               escape(app["min_ver"]),
               escape(app["max_ver"])))

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


def build_chrome_manifest(data, features, is_firefox=False):

    chrome_manifest = [_get_resource("chrome.manifest", data)]
    if is_firefox:
        chrome_manifest.append(("overlay\t"
                                "chrome://browser/content/browser.xul\t"
                                "chrome://%s/content/ff-overlay.xul") %
                                   data["slug"])

    if "button" in features:
        chrome_manifest.append(
                ("overlay\t"
                 "chrome://global/content/customizeToolbar.xul\t"
                 "chrome://%s/skin/overlay.css") % data["slug"])


    return "\n".join(chrome_manifest)


def build_ffoverlay_xul(data, features, is_firefox=False):
    """Build the ff-overlay.xul file."""

    ffoverlay = _get_resource("chrome/content/ff-overlay.xul", data=data)

    extra = []
    if "button" in features:
        extra.append(_apply_data("""
        <toolbarpalette id="BrowserToolbarPalette">
            <toolbarbutton id="%slug%-toolbar-button" class="toolbarbutton-1 chromeclass-toolbar-additional"
                label="&%slug%ToolbarButton.label;" tooltiptext="&%slug%ToolbarButton.tooltip;"
                oncommand="%slug%.onToolbarButtonCommand()"/>
        </toolbarpalette>""", data=data))

    if "contextmenu" in features:
        extra.append(_apply_data("""
        <popup id="contentAreaContextMenu">
            <menuitem id="context-%slug%" label="&%slug%Context.label;"
                accesskey="&%slug%Context.accesskey;"
                insertafter="context-stop"
                oncommand="%slug%.onMenuItemCommand(event)"/>
        </popup>""", data=data))

    if "mainmenu" in features:
        extra.append(_apply_data("""
        <menupopup id="menu_ToolsPopup">
            <menuitem id="%slug%-hello" label="&%slug%.label;"
                oncommand="%slug%.onMenuItemCommand(event);"/>
        </menupopup>
        """, data=data))

    if "sidebar" in features:
        extra.append(_apply_data("""
        <menupopup id="viewSidebarMenu">
            <menuitem observes="viewSidebar_%slug%" />
        </menupopup>
        <broadcasterset id="mainBroadcasterSet">
            <broadcaster id="viewSidebar_%slug%"
                 label="&%slug%Sidebar.label;"
                 autoCheck="false"
                 type="checkbox"
                 group="sidebar"
                 sidebarurl="chrome://%slug%/content/ff-sidebar.xul"
                 sidebartitle="&%slug%Sidebar.label;"
                 oncommand="toggleSidebar('viewSidebar_%slug%');" />
        </broadcasterset>
        """, data=data))

    if "toolbar" in features:
        extra.append(_apply_data("""
        <toolbox id="navigator-toolbox">
            <toolbar class="chromeclass-toolbar" toolbarname="&%slug%Toolbar.name;" customizable="true" id="%slug%-toolbar">
                <label value="&%slug%Toolbar.label;"/>
            </toolbar>
        </toolbox>
        """, data=data))

    return ffoverlay % "\n".join(extra)

