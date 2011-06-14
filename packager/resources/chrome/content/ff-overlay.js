%(slug)s.onFirefoxLoad = function(event) {
  document.getElementById("contentAreaContextMenu")
          .addEventListener("popupshowing", function (e){ %(slug)s.showFirefoxContextMenu(e); }, false);
};

%(slug)s.showFirefoxContextMenu = function(event) {
  // show or hide the menuitem based on what the context menu is on
  document.getElementById("context-%(slug)s").hidden = gContextMenu.onImage;
};

window.addEventListener("load", function () { %(slug)s.onFirefoxLoad(); }, false);

