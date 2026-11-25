/* ===========================================================
   Books & Films — renders data/douban.json into /douban/
   Generated data, no dependencies. See scripts/build-douban.py
   =========================================================== */

(function () {
  var DATA_URL = "/data/douban.json";

  function $(id) { return document.getElementById(id); }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function avg(list) {
    var rated = list.filter(function (r) { return r.rating > 0; });
    if (!rated.length) return 0;
    var sum = rated.reduce(function (a, r) { return a + r.rating; }, 0);
    return sum / rated.length;
  }

  function yearsOf(list) {
    return list.map(function (r) { return parseInt((r.date || "").slice(0, 4), 10); })
               .filter(function (y) { return y > 1900; });
  }

  function statCard(label, value, sub) {
    return '<div class="db-stat"><div class="db-stat-label">' + esc(label) + "</div>" +
           '<div class="db-stat-value">' + value +
           (sub ? '<span class="db-stat-sub">' + esc(sub) + "</span>" : "") + "</div></div>";
  }

  function ratingBars(list, label) {
    var counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
    list.forEach(function (r) { if (r.rating >= 1 && r.rating <= 5) counts[r.rating]++; });
    var max = Math.max(1, counts[5], counts[4], counts[3], counts[2], counts[1]);
    var rated = list.filter(function (r) { return r.rating > 0; }).length;

    var rows = [5, 4, 3, 2, 1].map(function (star) {
      var n = counts[star];
      var pct = Math.round((n / max) * 100);
      return '<div class="db-bar-row">' +
             '<span class="db-bar-key">' + star + "★</span>" +
             '<div class="db-bar-track"><div class="db-bar-fill db-fill-' + star +
             '" style="width:' + pct + '%"></div></div>' +
             '<span class="db-bar-num">' + n + "</span></div>";
    }).join("");

    return '<div class="db-block"><h3>' + esc(label) + "</h3>" +
           '<p class="db-block-note">' + rated + " 条评分，平均 " +
           avg(list).toFixed(2) + " 星</p>" + rows + "</div>";
  }

  function yearChart(list) {
    var counts = {};
    yearsOf(list).forEach(function (y) { counts[y] = (counts[y] || 0) + 1; });
    var years = Object.keys(counts).map(Number).sort();
    if (!years.length) return "";

    var last = years[years.length - 1];
    var span = [];
    for (var y = last - 9; y <= last; y++) span.push(y);
    var max = Math.max.apply(null, span.map(function (y) { return counts[y] || 0; }).concat([1]));

    var bars = span.map(function (y) {
      var n = counts[y] || 0;
      var h = Math.round((n / max) * 100);
      return '<div class="db-year-col" title="' + y + "：" + n + ' 部">' +
             '<div class="db-year-bar-wrap"><div class="db-year-bar" style="height:' +
             (n ? Math.max(4, h) : 0) + '%"></div></div>' +
             '<div class="db-year-num">' + (n || "") + "</div>" +
             '<div class="db-year-label">' + String(y).slice(2) + "</div></div>";
    }).join("");

    return '<div class="db-block db-block-wide"><h3>年度分布</h3>' +
           '<p class="db-block-note">近十年标记数量（部 / 本）</p>' +
           '<div class="db-years">' + bars + "</div></div>";
  }

  function topList(list, emptyText) {
    var seen = {};
    var top = list.filter(function (r) { return r.rating >= 4; })
      .sort(function (a, b) { return (b.date || "").localeCompare(a.date || ""); })
      .filter(function (r) {
        if (seen[r.title]) return false;
        seen[r.title] = true;
        return true;
      })
      .slice(0, 6);

    if (!top.length) return '<p class="db-block-note">' + esc(emptyText) + "</p>";

    return '<ol class="db-top">' + top.map(function (r) {
      var meta = [];
      if (r.year) meta.push(r.year);
      if (r.author) meta.push(r.author);
      var stars = "";
      for (var i = 0; i < 5; i++) stars += i < r.rating ? "★" : "☆";
      return '<li><span class="db-top-title" title="' + esc(r.title) + '">' +
             esc(r.title) + "</span>" +
             (meta.length ? '<span class="db-top-meta">' + esc(meta.join(" · ")) + "</span>" : "") +
             '<span class="db-top-stars">' + stars + "</span></li>";
    }).join("") + "</ol>";
  }

  function render(data) {
    var movies = data.movies || [];
    var books = data.books || [];
    var all = movies.concat(books);

    var movieYears = yearsOf(movies).concat(yearsOf(books));
    var from = movieYears.length ? Math.min.apply(null, movieYears) : null;
    var to = movieYears.length ? Math.max.apply(null, movieYears) : null;

    var header = $("db-link");
    if (header) {
      if (data.profile && data.profile.url) {
        header.href = data.profile.url;
        header.style.display = "";
      } else {
        header.style.display = "none";
      }
    }

    $("db-stats").innerHTML =
      statCard("电影 / 剧集", movies.length, "部") +
      statCard("书籍", books.length, "本") +
      statCard("平均评分", avg(all).toFixed(2), "星") +
      statCard("时间跨度", from && to ? (to - from + 1) : "—", from && to ? "年" : "");

    $("db-ratings").innerHTML =
      ratingBars(movies, "电影评分分布") + ratingBars(books, "书籍评分分布");

    $("db-years").innerHTML = yearChart(all);

    $("db-top").innerHTML =
      '<div class="db-block"><h3>近期高分 · 影视</h3>' +
      '<p class="db-block-note">4 星以上，按标记时间倒序</p>' +
      topList(movies, "还没有 4 星以上的影视。") + "</div>" +
      '<div class="db-block"><h3>近期高分 · 书籍</h3>' +
      '<p class="db-block-note">4 星以上，按标记时间倒序</p>' +
      topList(books, "还没有 4 星以上的书。") + "</div>";

    var synced = (data.profile && data.profile.synced) || "未知";
    $("db-synced").textContent = "最近同步 " + synced;
  }

  function fail(msg) {
    var el = $("db-stats");
    if (el) el.innerHTML = '<div class="db-empty">' + esc(msg) + "</div>";
  }

  fetch(DATA_URL, { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(render)
    .catch(function (e) {
      fail("数据还没生成：运行 python scripts/build-douban.py 你的导出文件.xlsx（" + e.message + "）");
    });
})();
