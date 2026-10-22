/* Rosé OS — couche de compatibilité plateformes.
   Sur Android TV, l'objet "Android" est déjà fourni par l'appli : ce fichier ne fait rien.
   Sur webOS (LG), Tizen (Samsung) et navigateur, il fournit le même objet. */
(function () {
  if (window.Android && window.Android.open) return;

  var ua = navigator.userAgent || "";
  var isWebOS = /web0s|webos/i.test(ua) || typeof window.PalmServiceBridge !== "undefined";
  var isTizen = /tizen/i.test(ua) || typeof window.tizen !== "undefined";

  // Identifiants d'applications (au mieux : si l'appli est absente, on ouvre le site)
  var WEBOS = { netflix: "netflix", youtube: "youtube.leanback.v4", amazon: "amazon",
                primevideo: "amazon", disneyplus: "com.disney.disneyplus-prod", spotify: "spotify-beehive" };
  var TIZEN = { netflix: "3201907018807", youtube: "111299001912", primevideo: "3201512006785",
                amazon: "3201512006785", disneyplus: "3201901017640", spotify: "3201606009684" };

  function pick(map, host) {
    for (var k in map) if (host.indexOf(k) !== -1) return map[k];
    return null;
  }
  function hostOf(u) { try { return new URL(u).hostname; } catch (e) { return ""; } }

  function webOSLaunch(id, fallback) {
    try {
      var b = new window.PalmServiceBridge();
      b.onservicecallback = function (r) {
        try { if (JSON.parse(r).returnValue === false) fallback(); } catch (e) { fallback(); }
      };
      b.call("luna://com.webos.applicationManager/launch", JSON.stringify({ id: id }));
    } catch (e) { fallback(); }
  }
  function openWeb(url) {
    if (isTizen && window.tizen && tizen.application && tizen.ApplicationControl) {
      try {
        tizen.application.launchAppControl(
          new tizen.ApplicationControl("http://tizen.org/appcontrol/operation/view", url),
          null, function () {}, function () { window.open(url, "_blank"); });
        return;
      } catch (e) {}
    }
    window.open(url, "_blank", "noopener");
  }

  window.Android = {
    open: function (url) {
      var host = hostOf(url);
      var web = function () { openWeb(url); };
      if (isWebOS) { var w = pick(WEBOS, host); if (w) return webOSLaunch(w, web); }
      if (isTizen && window.tizen && tizen.application) {
        var t = pick(TIZEN, host);
        if (t) {
          try { return tizen.application.launch(t, function () {}, web); } catch (e) {}
        }
      }
      web();
    },
    stock: function () {
      try {
        if (isTizen) return tizen.application.getCurrentApplication().exit();
        if (isWebOS && window.webOS && webOS.platformBack) return webOS.platformBack();
        if (isWebOS) return webOSLaunch("com.webos.app.home", function () {});
      } catch (e) {}
      try { window.close(); } catch (e) {}
    }
  };

  // Touches Retour des télécommandes (webOS 461, Tizen 10009) -> Échap
  window.addEventListener("keydown", function (e) {
    if (e.keyCode === 461 || e.keyCode === 10009 || e.key === "XF86Back") {
      e.preventDefault();
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    }
  }, true);
})();
