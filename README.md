# kiku-skills

个人私有 AI Skills 仓库。

## 安装

使用 [`skills`](https://github.com/vercel-labs/skills) CLI 全局安装本仓库的全部 Skills：

```bash
npx skills add josonchou/kiku-skills -g
```

仅安装指定 Skill：

```bash
npx skills add josonchou/kiku-skills@half-year-work-summary -g
```

移除 `-g` 可将 Skill 安装到当前项目，而非用户全局目录；添加 `-y` 可跳过交互确认。

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
