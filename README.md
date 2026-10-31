# Zhenyu Zhang 个人学术主页

一个单页静态网站，用 GitHub Pages 托管，不需要任何构建工具。

## 文件结构

```
index.html              ← 网站本身（由 build.py 生成，不要直接改）
template.html           ← 页面模板：简介、Research、经历、经费、报告、服务都在这里改
data/publications.csv   ← 论文列表（用 Excel 编辑，no 列决定顺序；作者后加 * 表示通讯作者）
data/topics.csv         ← 论文的分类（目前 3 类）
build.py                ← 读 CSV + 模板，生成 index.html
make_thumbs.py          ← 把 thumbs_raw/ 里的截图处理成缩略图（用法见 更新论文.md）
thumbs_raw/             ← 放原始截图（不用上传）
assets/css/style.css    ← 样式（颜色在文件最上面）
assets/img/             ← 头像、研究主题图；论文配图放 assets/img/papers/
assets/papers/          ← 论文 PDF
assets/files/           ← 放 CV 的 PDF
```

## 第一次上线（只需做一次）

1. 在 GitHub 新建一个**公开**仓库，名字必须是 `zhangzhy-geo.github.io`（和 GitHub 用户名完全一致，加 `.github.io`）。
2. 把本文件夹里的所有文件上传到仓库根目录（网页上 "Add file → Upload files" 拖进去即可，包括 `.nojekyll`）。
3. 仓库 **Settings → Pages**：Source 选 "Deploy from a branch"，Branch 选 `main`，文件夹选 `/ (root)`，保存。
4. 1–2 分钟后访问 `https://zhangzhy-geo.github.io`。

## 上线前要补的东西

| 内容 | 放到哪里 |
|---|---|
| 头像（正方形，≥ 400×400） | `assets/img/profile.jpg` |
| 三个研究主题的代表图（16:9） | `assets/img/research/coupled.jpg`、`agro.jpg`、`hydroclimate.jpg` |
| CV 的 PDF | `assets/files/CV_Zhenyu_Zhang.pdf` |

图片没放之前，页面会自动显示占位图，不会出现破图。

## 以后怎么更新论文

见本地文件 **`更新论文.md`**（只在自己电脑上，不上传）。简单说：用 Excel 改 `data/publications.csv`（保存为 CSV UTF-8），然后运行 `python3 build.py`。
论文按 `no` 列的数字从大到小排列，编号由你自己定。PDF 放 `assets/papers/`，论文配图（jpg/png/gif/mp4）放 `assets/img/papers/`，表格里只填文件名。

## 改其他内容

简介、Research interests、经历、Research 卡片、报告、服务、左栏信息都在 `template.html` 里，改完运行 `python3 build.py`。
每种常见改动的具体写法和可复制的模板见本地文件 **`更新其他内容.md`**（只在自己电脑上，不上传）。

## 访客地图（左栏底部）

1. 打开 https://mapmyvisitors.com （免费；也可以用 https://clustrmaps.com ），用你的网站地址 `https://zhangzhy-geo.github.io` 注册，选 **Globe**（3D 地球）或 **Map**（平面地图）。
2. 复制它给你的那段代码（通常是一行 `<script ...></script>`）。
3. 在 `template.html` 里搜 `PASTE BELOW`，把代码粘贴在 `PASTE BELOW` 和 `PASTE ABOVE` 两行之间，运行 `python3 build.py`。

没粘贴代码之前，这一块会自动隐藏。
