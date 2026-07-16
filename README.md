# kiku-skills

个人私有 AI Skills 仓库。

## 安装

使用 [`skills`](https://github.com/vercel-labs/skills) CLI 安装指定 Skill：

```bash
npx skills add https://github.com/josonchou/kiku-skills --skill half-year-work-summary
```

安装其他 Skill 时替换 `--skill` 参数，例如：

```bash
npx skills add https://github.com/josonchou/kiku-skills --skill mise-python2
```

## Skills

- `half-year-work-summary`：从多个 Git 项目的周期提交中整理工作总结、KPI 自评和飞书绩效文档。
- `mise-python2`：在 Apple Silicon Mac 上通过 Rosetta 2 和 mise 安装 Python 2.7。

## 可复用脚本

`half-year-work-summary/scripts/collect_git_contributions.py` 可跨项目归集指定周期内、指定 Git 身份的提交证据。示例：

```bash
python3 half-year-work-summary/scripts/collect_git_contributions.py \
  --workspace ~/Workspace/douyu \
  --since '2026-01-01 00:00:00 +0800' \
  --until '2026-06-30 23:59:59 +0800' \
  --format json \
  --output ./git-evidence-2026-h1.json
```
