var %(slug)s = {
  onLoad: function() {
    // initialization code
    this.initialized = true;
    this.strings = document.getElementById("%(slug)s-strings");
  },

  onMenuItemCommand: function(e) {
    var promptService = Components.classes["@mozilla.org/embedcomp/prompt-service;1"]
                                  .getService(Components.interfaces.nsIPromptService);
    promptService.alert(window, this.strings.getString("helloMessageTitle"),
                                this.strings.getString("helloMessage"));
  },

  onToolbarButtonCommand: function(e) {
    // just reuse the function above.  you can change this, obviously!
    %(slug)s.onMenuItemCommand(e);
  }
};

window.addEventListener("load", function () { %(slug)s.onLoad(); }, false);


%(slug)s.onFirefoxLoad = function(event) {
  document.getElementById("contentAreaContextMenu")
          .addEventListener("popupshowing", function (e) {
    %(slug)s.showFirefoxContextMenu(e);
  }, false);
};

%(slug)s.showFirefoxContextMenu = function(event) {
  // show or hide the menuitem based on what the context menu is on
  document.getElementById("context-%(slug)s").hidden = gContextMenu.onImage;
};

window.addEventListener("load", function () { %(slug)s.onFirefoxLoad(); }, false);
