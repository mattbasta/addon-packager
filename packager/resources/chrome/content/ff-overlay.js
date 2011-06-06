%slug%.onFirefoxLoad = function(event) {
  document.getElementById("contentAreaContextMenu")
          .addEventListener("popupshowing", function (e){ %slug%.showFirefoxContextMenu(e); }, false);
};

%slug%.showFirefoxContextMenu = function(event) {
  // show or hide the menuitem based on what the context menu is on
  document.getElementById("context-%slug%").hidden = gContextMenu.onImage;
};

window.addEventListener("load", function () { %slug%.onFirefoxLoad(); }, false);

