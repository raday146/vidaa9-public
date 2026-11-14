// vidaa-launcher: our dock apps and More-menu entries, read by app.js through window.VIDAA.
// "url" stays empty until discovery finds how each one opens on the TV.
(function () {
  "use strict";
  var LOGOS = "../../remote/src/app-logos/";

  // the dock, in order (Settings and More follow, added by app.js)
  var apps = [
    { id: "youtube", label: "YouTube", icon: LOGOS + "com.google.android.youtube.tv.png", url: "" },
    { id: "netflix", label: "Netflix", icon: LOGOS + "com.netflix.ninja.png", url: "" },
    { id: "disney-plus", label: "Disney+", icon: LOGOS + "com.disney.disneyplus.png", url: "" },
    { id: "prime-video", label: "Prime Video", icon: LOGOS + "com.amazon.amazonvideo.livingroom.png", url: "" },
    { id: "apple-tv", label: "Apple TV", icon: LOGOS + "com.apple.atve.androidtv.appletv.png", url: "" },
    { id: "hbo-max", label: "HBO Max", icon: LOGOS + "com.wbd.stream.png", url: "" },
    { id: "partner-tv", label: "Partner TV", icon: null, url: "" },
    { id: "browser", label: "Browser", icon: null, url: "" },
    { id: "spotify", label: "Spotify", icon: LOGOS + "com.spotify.tv.android.png", url: "" },
    { id: "vidaa-store", label: "VIDAA Store", icon: null, url: "" },
    { id: "jellyfin", label: "Jellyfin", icon: null, url: "" }
  ];

  // the "..." (More) tile's menu
  var more = [
    { id: "hdmi1", label: "HDMI 1", icon: null, url: "" },
    { id: "hdmi2", label: "HDMI 2", icon: null, url: "" },
    { id: "hdmi3", label: "HDMI 3", icon: null, url: "" },
    { id: "airplay", label: "AirPlay", icon: null, url: "" },
    { id: "screen-mirroring", label: "Screen Mirroring", icon: null, url: "" },
    { id: "av", label: "AV", icon: null, url: "" },
    { id: "content-sharing", label: "Content Sharing", icon: null, url: "" },
    { id: "network", label: "Network/Wi-Fi", icon: null, url: "" }
  ];

  var byId = {};
  apps.forEach(function (a) { byId[a.id] = a; });

  window.VIDAA = {
    more: more,
    // couch-tv's app shape; "vidaa" carries our entry
    apps: apps.map(function (a) { return { kind: "app", name: a.label, package: a.id, vidaa: a }; }),
    // null: couch-tv's built-in fallback (the app's name on a plain tile)
    icon: function (id) { return byId[id] ? byId[id].icon : null; },
    // OK on an app or a More entry; returns the note to show
    open: function (entry) {
      if (!entry.url) return entry.label + " is not connected yet";
      // TODO: launch method, once discovery shows how VIDAA opens entry.url
      return entry.label + ": launch method not set yet";
    }
  };
})();
