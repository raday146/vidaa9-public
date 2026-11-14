// vidaa-launcher settings for couch-tv's TV home (see couch-tv docs/CONFIG.md for every key).
// Static, no-bridge VIDAA setup: no computer, no mock data.

// couch-tv's no-bridge mode: the home never calls a bridge and shows no "computer is off" note.
window.COUCH_STANDALONE = true;

window.COUCH_CONFIG = {
  // nobody configured: the Person 1 / Person 2 switch never shows
  people: [],
  home: {
    keep_watching: false,   // hide the Keep watching row
    dock_size: 11,          // our 11 apps, then Settings, then More
    now_playing: false      // standalone would poll the site's api/now, which this static setup has not got
  }
};

// &lighter=1: couch-tv's Lighter home (no blur, no soft shadows, a still photo)
if (/[?&]lighter=1(&|$)/.test(location.search)) window.COUCH_CONFIG.home.lighter = true;
