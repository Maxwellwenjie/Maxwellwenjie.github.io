/* ===========================================================
   list.js — renders the post list on a category index page
   from that folder's posts.json.

   posts.json format:

   [
     {
       "file": "can-topology.md",
       "title": "CAN Topology Walkthrough",
       "date": "2026-10-10",
       "summary": "Reading a vehicle CAN topology diagram...",
       "tags": ["CAN", "CAN-FD"]
     }
   ]

   Sort order: newest first by `date`. Missing dates sink to the
   bottom. Nothing else needs editing to add an article.
   =========================================================== */

(function () {
  'use strict';

  /* ---------- config ---------- */

  // Same repo as post.js. posts.json IS served by GitHub Pages, so we
  // try the local copy first (fast, same-origin) and only fall back to
  // the CDN if that request fails.
  var REPO_OWNER = 'Maxwellwenjie';
  var REPO_NAME = 'maxwellwenjie.github.io';
  var REPO_BRANCH = 'master';
  var CDN = 'https://cdn.jsdelivr.net/gh/' + REPO_OWNER + '/' + REPO_NAME + '@' + REPO_BRANCH + '/';

  var mount = document.getElementById('post-list');
  if (!mount) return;

  // Category folder = current path, e.g. /automotive/
  var base = window.location.pathname.replace(/[^/]*$/, '');
  var relPath = base.replace(/^\/+/, '') + 'posts.json';

  fetchJson([base + 'posts.json', CDN + encodeURI(relPath)])
    .then(function (posts) {
      if (!Array.isArray(posts) || posts.length === 0) {
        mount.innerHTML =
          '<div class="empty-state"><p>No posts yet. Add a .md file and list it in posts.json.</p></div>';
        return;
      }

      posts.sort(function (a, b) {
        var da = a.date ? new Date(a.date).getTime() : 0;
        var db = b.date ? new Date(b.date).getTime() : 0;
        return db - da;
      });

      var html = posts
        .map(function (post) {
          var href = 'article.html?p=' + encodeURIComponent(post.file || '');
          var tags = (post.tags || [])
            .map(function (t) {
              return '<span class="tag">' + escapeHtml(t) + '</span>';
            })
            .join('');

          return (
            '<a class="post-card" href="' + href + '">' +
            (post.date
              ? '<div class="post-date">' + escapeHtml(formatDate(post.date)) + '</div>'
              : '') +
            '<h4>' + escapeHtml(post.title || post.file || 'Untitled') + '</h4>' +
            (post.summary ? '<p>' + escapeHtml(post.summary) + '</p>' : '') +
            (tags ? '<div class="post-tags">' + tags + '</div>' : '') +
            '</a>'
          );
        })
        .join('');

      mount.innerHTML = '<div class="post-list">' + html + '</div>';
    })
    .catch(function (err) {
      mount.innerHTML =
        '<div class="empty-state"><p>Could not load posts.json (' +
        escapeHtml(err.message) +
        ').</p></div>';
    });

  /* ---------- helpers ---------- */

  // Try each URL in order; resolve with the parsed JSON of the first
  // one that answers 200 with valid JSON.
  function fetchJson(urls) {
    return urls.reduce(function (chain, url) {
      return chain.catch(function () {
        return fetch(url, { cache: 'no-cache' }).then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json();
        });
      });
    }, Promise.reject(new Error('no source'))).catch(function () {
      throw new Error('neither the local copy nor the CDN responded');
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatDate(d) {
    var parsed = new Date(d);
    if (isNaN(parsed.getTime())) return d;
    return parsed.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }
})();
