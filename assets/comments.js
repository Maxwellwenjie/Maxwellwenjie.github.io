/* ===========================================================
   comments.js — giscus comment thread under each article

   Why the term is not the pathname:
   Every category reuses one template, /<category>/article.html, and the
   article is selected by the ?p= query string. window.location.pathname
   is therefore identical for every article in a category, so giscus'
   default pathname mapping would put all of them into one thread.
   post.js instead passes the repo-relative .md path (e.g.
   "/travel/葡萄牙之行.md") as a "specific" term, which gives each article
   its own discussion.

   Consequence worth knowing: renaming an .md file starts a new thread.
   Renaming a category folder does the same.

   Loading: the giscus iframe is only injected once the reader scrolls
   within 800px of the comment section, so it costs nothing on first paint.

   Setup (one time):
     1. Repo → Settings → General → Features → tick "Discussions"
     2. Create a category, suggested name "Comments", type "Announcements"
        (Announcements means only maintainers can open threads)
     3. Open https://giscus.app, enter the repo, pick that category,
        copy the two id values into CONFIG below.
   =========================================================== */

(function () {
  'use strict';

  var CONFIG = {
    repo: 'Maxwellwenjie/Maxwellwenjie.github.io',
    repoId: 'MDEwOlJlcG9zaXRvcnkxOTQ2MTIyMDE=',

    // Fill these two from giscus.app after Discussions is enabled.
    category: 'Comments',
    categoryId: '',

    reactions: '1',
    inputPosition: 'top',
    lang: 'zh-CN',
    theme: 'https://maxwellwenjie.github.io/assets/giscus-theme.css'
  };

  var mounted = false;

  window.mountComments = function (term) {
    var section = document.getElementById('comments');
    var host = document.getElementById('comments-body');

    if (!section || !host || mounted) return;

    if (!CONFIG.categoryId) {
      console.warn(
        '[comments] categoryId is empty, thread skipped. ' +
        'Fill it in from https://giscus.app — see assets/comments.js.'
      );
      return;
    }

    mounted = true;
    section.hidden = false;

    function inject() {
      var s = document.createElement('script');
      s.src = 'https://giscus.app/client.js';
      s.async = true;
      s.crossOrigin = 'anonymous';
      s.setAttribute('data-repo', CONFIG.repo);
      s.setAttribute('data-repo-id', CONFIG.repoId);
      s.setAttribute('data-category', CONFIG.category);
      s.setAttribute('data-category-id', CONFIG.categoryId);
      s.setAttribute('data-mapping', 'specific');
      s.setAttribute('data-term', term);
      s.setAttribute('data-reactions-enabled', CONFIG.reactions);
      s.setAttribute('data-emit-metadata', '0');
      s.setAttribute('data-input-position', CONFIG.inputPosition);
      s.setAttribute('data-theme', CONFIG.theme);
      s.setAttribute('data-lang', CONFIG.lang);
      s.setAttribute('data-loading', 'lazy');
      host.appendChild(s);
    }

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        io.disconnect();
        inject();
      }, { rootMargin: '800px 0px' });
      io.observe(section);
    } else {
      inject();
    }
  };
})();
