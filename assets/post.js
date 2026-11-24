/* ===========================================================
   post.js — renders a Markdown article into article.html

   URL form:  /<category>/article.html?p=<filename>.md

   The .md file may optionally start with front matter:

       ---
       title: My Article
       date: 2026-11-24
       summary: One line shown on the list page.
       tags: CAN, Diagnostics
       ---

   Front matter is optional; if absent, the first "# heading"
   becomes the title and the first paragraph the summary.
   =========================================================== */

(function () {
  'use strict';

  var params = new URLSearchParams(window.location.search);
  var mdPath = params.get('p');

  var $title = document.getElementById('post-title');
  var $meta = document.getElementById('post-meta');
  var $body = document.getElementById('post-body');
  var $back = document.getElementById('back-link');

  function fail(msg) {
    $body.innerHTML = '<div class="empty-state"><p>' + msg + '</p></div>';
    $title.textContent = 'Not found';
    $meta.textContent = '';
  }

  if (!mdPath) {
    fail('No article specified.');
    return;
  }

  // Resolve the .md relative to the current folder (e.g. /automotive/article.html?p=foo.md)
  // so a category page keeps clean, short URLs.
  var base = window.location.pathname.replace(/[^/]*$/, '');

  fetch(base + mdPath, { cache: 'no-cache' })
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    })
    .then(function (raw) {
      var parsed = splitFrontMatter(raw);
      var data = parsed.data;
      var body = parsed.body;

      // Title: front matter first, else first H1 in the body (and strip it)
      var title = data.title;
      if (!title) {
        var m = body.match(/^\s*#\s+(.+)$/m);
        if (m) {
          title = m[1];
          body = body.replace(m[0], '');
        } else {
          title = mdPath.replace(/\.md$/, '');
        }
      }

      document.title = title + ' — Wenjie Liu';
      $title.textContent = title;

      var metaBits = [];
      if (data.date) metaBits.push(formatDate(data.date));
      if (data.readtime) metaBits.push(data.readtime);
      $meta.textContent = metaBits.join(' · ');

      if ($back && data.category !== false) {
        $back.href = base;
      }

      marked.setOptions({ gfm: true, breaks: false });
      $body.innerHTML = marked.parse(body);

      // Add language class + copy-friendly wrapping to code blocks
      Array.prototype.forEach.call($body.querySelectorAll('pre'), function (pre) {
        pre.setAttribute('tabindex', '0');
      });

      // Make external links open in a new tab
      Array.prototype.forEach.call($body.querySelectorAll('a'), function (a) {
        var href = a.getAttribute('href') || '';
        if (/^https?:\/\//.test(href) && href.indexOf(location.hostname) === -1) {
          a.setAttribute('target', '_blank');
          a.setAttribute('rel', 'noopener');
        }
      });
    })
    .catch(function (err) {
      fail('Could not load <code>' + mdPath + '</code> (' + err.message + ').');
    });

  /* ---------- helpers ---------- */

  // Minimal YAML-ish front matter parser: key: value, tags as a comma list.
  function splitFrontMatter(text) {
    var fm = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;
    var m = text.match(fm);
    if (!m) return { data: {}, body: text };

    var data = {};
    m[1].split(/\r?\n/).forEach(function (line) {
      var idx = line.indexOf(':');
      if (idx === -1) return;
      var key = line.slice(0, idx).trim();
      var val = line.slice(idx + 1).trim();
      // strip surrounding quotes
      val = val.replace(/^['"]|['"]$/g, '');
      if (key) data[key] = val;
    });

    return { data: data, body: text.slice(m[0].length) };
  }

  function formatDate(d) {
    var parsed = new Date(d);
    if (isNaN(parsed.getTime())) return d;
    return parsed.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  }
})();
