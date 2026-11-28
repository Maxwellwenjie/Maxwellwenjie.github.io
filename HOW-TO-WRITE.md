# 怎么写一篇新文章

## 最短流程（3 步）

1. 复制任意分类目录下的 `_template.md`，改名为 `你的文章名.md`
2. 写内容，顶部保留 front matter（见下）
3. 上传到仓库对应分类目录

**完事。** `posts.json` 会自动生成，不用管。

---

## Front matter 格式

每篇文章开头必须有这三条横线包起来的一段：

```markdown
---
title: 8155 休眠唤醒
date: 2026-11-24
summary: 一句话摘要，会显示在列表卡片上。
tags: 8155, Sleep/Wake, CAN-FD
---

正文从这里开始……
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | 建议 | 文章标题。不写则取正文第一个 `# 标题`，再不行就用文件名 |
| `date` | 建议 | `YYYY-MM-DD`。列表按它倒序排列，不写会沉到最后 |
| `summary` | 建议 | 列表卡片上的描述。不写则自动取正文第一段 |
| `tags` | 可选 | 逗号分隔，显示成小标签 |
| `draft` | 可选 | 写 `true` 则这篇文章不进列表（但仍可直接访问） |

**只有 `title` 和 `date` 是强烈建议写**，其他都能自动兜底。

---

## 图片怎么插

### 方式一：Obsidian 语法（推荐，直接粘）

```markdown
![[Pasted image 20251216092417.png]]
```

把图片上传到仓库根目录的 `images/` 文件夹，文件名保持一致即可。
渲染器会自动转成 `/images/Pasted%20image%2020251216092417.png`。

带说明文字的写法：

```markdown
![[diagram.png|CAN 拓扑图]]
```

### 方式二：标准 Markdown

```markdown
![CAN 拓扑图](/images/diagram.png)
```

两种都支持，混用也没问题。

---

## 目录结构

```
automotive/          ← 分类目录
  article.html       ← 文章渲染页（不要动）
  index.html         ← 分类列表页（不要动）
  posts.json         ← 自动生成（不要手动改）
  _template.md       ← 模板，复制它来写新文章
  你的文章.md         ← 你写的文章

images/              ← 所有图片放这里
scripts/build-index.py   ← 生成 posts.json 的脚本
.github/workflows/build-index.yml  ← 自动化配置
```

分类目录：`automotive`、`ai`、`travel`、`photography`、`notes`

---

## 添加新分类

如果需要一个新的分类（比如 `reading`）：

1. 建一个目录，例如 `reading/`
2. 从 `automotive/` 复制 `index.html` 和 `article.html` 进去
3. 改 `index.html` 里的标题和导航高亮
4. 放一个 `.md` 进去
5. 在**其他所有页面的导航栏**里加一行 `<a href="/reading/">Reading</a>`

第 5 步比较烦，因为导航栏是每页手写的。如果分类要加很多，建议改成 JS 动态生成导航。

---

## 自动化原理

`.github/workflows/build-index.yml` 在你每次推送 `.md` 文件时：

1. 跑 `scripts/build-index.py`
2. 扫描每个含 `article.html` 的目录
3. 读所有 `.md` 的 front matter
4. 生成排序好的 `posts.json`
5. 如果有变化，自动 commit 回去

提交信息里带 `[skip ci]`，所以不会无限循环。

**注意**：如果 workflow 运行失败，站点不会挂（旧的 `posts.json` 还在），只是新文章不出现在列表里。去仓库的 **Actions** 标签看报错。

---

## 常见问题

**文章不出现在列表里？**
- 检查 front matter 是不是从第 1 行开始写的（前面不能有空行）
- 检查文件是不是以 `_` 开头（会被当成模板跳过）
- 检查 `draft: true` 有没有误加
- 去 Actions 看 workflow 是否成功

**页面显示 503 或空白？**
- `.md` 文件由 jsDelivr CDN 提供，如果 CDN 抽风会失败
- 打开浏览器控制台看 Network，确认 `cdn.jsdelivr.net` 的请求状态

**图片显示不出来？**
- 确认图片在 `images/` 目录下
- 确认文件名和 md 里写的一致（**空格和大小写都要一致**）
- 中文文件名也可以，会自动编码

**改了 md 但页面没更新？**
- jsDelivr 有缓存，大约 12 小时
- 强制刷新（Ctrl+Shift+R），或加 `?v=2` 测试

---

## 更新豆瓣书影音数据

`/douban/` 页面的数据是本地导出的快照，不会自动跟随豆瓣更新。有新标记时：

**第一步：电影页跑一次**
打开 `https://movie.douban.com/people/你的ID/collect`，F12 → Console，粘贴 `scripts/douban-console.js`，回车。
会下载 `douban-movie-*.json` 和 `douban-tv-*.json` 两个文件。

**第二步：书籍页跑一次**
打开 `https://book.douban.com/people/你的ID/collect`，同样粘贴运行，下载 `douban-book-*.json`。

> 控制台如果拦截粘贴，改用 Sources → Snippets → New snippet，粘进去按 Ctrl+Enter。

**第三步：重建并推送**

```bash
python scripts/update-douban.py --push
```

脚本会自动从下载目录里挑最新的三个文件、重建 `data/douban.json`、提交并推送。不加 `--push` 就只重建不提交，方便先看数字对不对。

**注意**：控制台脚本每次都会重新抓全量（不是增量），所以三个文件必须都是新的。只跑书籍页会导致影视数据丢失 —— 脚本检测到缺文件会直接报错退出，不会写出残缺数据。

**影视没有年份**是正常现象：豆瓣电影列表页不提供上映年份，只有书籍页有「作者/出版社/年份」。

---

## 评论区（giscus）

评论由 [giscus](https://giscus.app) 提供，数据存在本仓库的 GitHub Discussions 里 —— 没有第三方服务器，也不会随服务关停而消失。

### 为什么不用默认的 pathname 匹配

所有分类共用同一个 `article.html`，文章靠 `?p=文件名.md` 选择，所以 `location.pathname` 对同分类下每篇文章都一样。如果按 pathname 建话题，一个分类的所有文章会挤进同一个评论区。

因此 `assets/post.js` 传的是 `.md` 的仓库相对路径作为 `specific` term，例如 `/travel/葡萄牙之行.md`。

**代价：改文件名 = 换新话题，旧评论留在原话题里。** 分类文件夹改名同理。所以文章定稿后尽量别再改文件名。

### 关掉某篇文章的评论

在 front matter 里加一行：

```markdown
---
title: 某篇不想开评论的文章
date: 2026-11-26
comments: false
---
```

### 首次配置

1. 仓库 Settings → General → Features → 勾上 **Discussions**
2. 到 <https://github.com/apps/giscus> 安装到本仓库
3. 打开 <https://giscus.app>，填仓库名，分类选 **Announcements**（只有维护者能建话题，避免有人随手开串），
   把生成代码里的 `data-category-id` 填进 `assets/comments.js` 的 `categoryId`

配色主题在 `assets/giscus-theme.css`，由 giscus 官方 light 主题改写而来，只换了色值，想调就改里面的变量。
