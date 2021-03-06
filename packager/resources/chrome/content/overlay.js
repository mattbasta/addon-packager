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
