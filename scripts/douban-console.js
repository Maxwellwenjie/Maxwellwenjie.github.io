/* ===========================================================
   douban-console.js — scrape your own Douban records from the
   browser console. No extension, no third-party service.

   HOW TO USE
   1. Log in at www.douban.com
   2. Open your collect page, e.g.
        https://movie.douban.com/people/YOUR_ID/collect
        https://book.douban.com/people/YOUR_ID/collect
   3. F12 -> Console -> paste this whole file -> Enter
      (if paste is blocked: Sources -> Snippets -> New snippet)
   4. It downloads douban-movie-*.json / douban-book-*.json

   Run once on movie.douban.com (films + series) and once on
   book.douban.com (books).

   Handles both layouts Douban serves:
     new  <ul class="interest-list"><li class="subject-item">
     old  <div class="item">  /  <ul class="list-view"><li class="item">
   Page size is read from "1-15 / 154" instead of being assumed.
   =========================================================== */

(async () => {
  const DELAY = 1200;

  const uid = (location.pathname.match(/\/people\/([^/]+)\//) || [])[1];
  if (!uid) {
    console.error('请先打开你的"我看过的"页面，URL 里必须包含 /people/你的ID/');
    return;
  }

  const host = location.hostname;
  const baseType = host.startsWith('book') ? 'book'
                 : host.startsWith('music') ? 'music' : 'movie';

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const txt = (el, sel) => {
    const n = el.querySelector(sel);
    return n ? n.textContent.replace(/\s+/g, ' ').trim() : '';
  };

  function pickItems(doc) {
    const sets = [
      'li.subject-item',
      'ul.interest-list > li',
      '.grid-view .item',
      'ul.list-view > li.item',
      '.item',
    ];
    for (const sel of sets) {
      const found = doc.querySelectorAll(sel);
      if (found.length) return { nodes: found, sel };
    }
    return { nodes: [], sel: null };
  }

  function pageInfo(doc) {
    const el = doc.querySelector('.subject-num, .num, .paginator .thispage');
    if (el) {
      const m = el.textContent.match(/(\d+)\s*[-\u2013]\s*(\d+)\s*\/\s*(\d+)/);
      if (m) return { size: Number(m[2]) - Number(m[1]) + 1, total: Number(m[3]) };
    }
    return { size: 0, total: 0 };
  }

  function parsePage(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const { nodes, sel } = pickItems(doc);
    const rows = [];

    nodes.forEach((el) => {
      const a = el.querySelector('.info h2 a') ||
                el.querySelector('.info .title a') ||
                el.querySelector('h2 a') ||
                el.querySelector('.title a');
      if (!a) return;

      let rating = 0;
      const rEl = el.querySelector('span[class*="rating"]');
      if (rEl) {
        const m = (rEl.className || '').match(/rating(\d)/);
        if (m) rating = Number(m[1]);
      }

      const dateRaw = txt(el, '.date');
      const date = (dateRaw.match(/\d{4}-\d{2}-\d{2}/) || [''])[0];

      const rec = {
        title: (a.getAttribute('title') || a.textContent).replace(/\s+/g, ' ').trim(),
        link: a.href,
        rating,
        date,
      };

      const comment = txt(el, 'p.comment') || txt(el, '.comment');
      if (comment) rec.comment = comment.slice(0, 280);

      const pub = txt(el, '.pub') || txt(el, '.intro') || txt(el, '.meta');
      if (pub) rec.pub = pub.slice(0, 160);

      const tagsRaw = txt(el, '.tags');
      if (tagsRaw) {
        const t = tagsRaw.replace(/^标签[:：]\s*/, '')
          .split(/[\s,，、/]+/).filter(Boolean).slice(0, 8);
        if (t.length) rec.tags = t;
      }

      rows.push(rec);
    });

    return { rows, sel, info: pageInfo(doc) };
  }

  async function collect(type, label) {
    const out = [];
    let start = 0;
    let size = 0;
    let total = 0;

    for (let page = 0; page < 200; page++) {
      const url = `${location.origin}/people/${uid}/collect?start=${start}` +
                  `&sort=time&rating=all&filter=all&mode=grid` +
                  (type === 'tv' ? '&type=tv' : '');

      let res;
      try {
        res = await fetch(url, { credentials: 'include' });
      } catch (e) {
        console.error(`${label} 请求失败：${e.message}`);
        break;
      }
      if (!res.ok) {
        console.warn(`${label} HTTP ${res.status}，停止于 start=${start}`);
        break;
      }

      const html = await res.text();
      const { rows, sel, info } = parsePage(html);

      if (!rows.length) {
        if (page === 0) {
          console.error(`${label}：解析不到条目。` +
            `页面含 subject 链接 ${(html.match(/\/subject\//g) || []).length} 个，` +
            `命中的选择器：${sel || '无'}`);
          console.log('请把下面这段 HTML 发给我，我来适配：');
          console.log(html.slice(0, 1500));
        }
        break;
      }

      out.push(...rows);
      if (!size) size = info.size || rows.length;
      if (info.total) total = info.total;

      console.log(`${label}: ${out.length}${total ? '/' + total : ''} 条 (start=${start})`);

      if (total && out.length >= total) break;
      start += size;
      await sleep(DELAY);
    }

    const seen = new Set();
    return out.filter((r) => {
      const k = r.link || r.title;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  }

  function download(type, items) {
    if (!items.length) {
      console.warn(type + '：没有抓到条目，未生成文件。');
      return;
    }
    const payload = { type, user: uid, count: items.length, items };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `douban-${type}-${items.length}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    console.log(`已下载 douban-${type}-${items.length}.json`);
  }

  console.log(`开始抓取，用户 ${uid}，站点 ${host}`);
  const jobs = baseType === 'movie'
    ? [['movie', '电影'], ['tv', '剧集']]
    : [[baseType, baseType === 'book' ? '书籍' : '音乐']];

  for (const [type, label] of jobs) {
    const items = await collect(type, label);
    items.forEach((r) => { r.kind = type; });
    console.log(`—— ${label} 完成：${items.length} 条`);
    download(type, items);
    await sleep(DELAY);
  }
  console.log('全部完成。把下载的 json 文件发给我即可。');
})();
