#!/usr/bin/env python3
"""Collect author-scoped Git evidence across a workspace of repositories.

The result is intended as evidence for an LLM-authored performance summary. It
reports work streams and statistics, but does not infer delivery timeliness,
incident severity, complaints, or AI efficiency from commit metadata alone.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SKIP_DIRECTORIES = {
    ".git",
    ".gradle",
    ".hvigor",
    ".idea",
    ".next",
    ".turbo",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "oh_modules",
    "vendor",
}


@dataclass(frozen=True)
class Commit:
    project: str
    sha: str
    date: str
    author_name: str
    author_email: str
    subject: str
    parent_count: int
    additions: int
    deletions: int
    files: int
    binaries: int


def run_git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def discover_repositories(workspace: Path) -> Iterable[Path]:
    """Yield repository roots once, pruning dependency and build directories."""
    for directory, child_directories, filenames in os.walk(workspace):
        current = Path(directory)
        if ".git" in child_directories or ".git" in filenames:
            yield current
            child_directories[:] = []
            continue
        child_directories[:] = [
            name for name in child_directories if name not in SKIP_DIRECTORIES
        ]


def parse_log(project: Path, author_email: str, since: str, until: str) -> list[Commit]:
    """Read reachable branch/tag commits while deliberately excluding stash refs."""
    result = run_git(
        project,
        "log",
        "--branches",
        "--remotes",
        "--tags",
        f"--author={author_email}",
        f"--since={since}",
        f"--until={until}",
        "--date=iso-strict",
        "--format=%x1e%H%x1f%ad%x1f%an%x1f%ae%x1f%s%x1f%P",
        "--numstat",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git log failed")

    commits: list[Commit] = []
    for block in result.stdout.split("\x1e"):
        if not block.strip():
            continue
        header, *statistics = block.splitlines()
        fields = header.split("\x1f")
        if len(fields) != 6:
            continue
        sha, date, author_name, found_email, subject, parents = fields
        additions = deletions = files = binaries = 0
        for row in statistics:
            values = row.split("\t")
            if len(values) != 3:
                continue
            added, removed, _path = values
            files += 1
            if added == "-" or removed == "-":
                binaries += 1
            else:
                additions += int(added)
                deletions += int(removed)
        commits.append(
            Commit(
                project=project.name,
                sha=sha,
                date=date,
                author_name=author_name,
                author_email=found_email,
                subject=subject,
                parent_count=len(parents.split()),
                additions=additions,
                deletions=deletions,
                files=files,
                binaries=binaries,
            )
        )
    return commits


def commit_prefix(subject: str) -> str:
    matched = re.match(r"([a-z]+)(?:\([^)]*\))?:", subject.lower())
    return matched.group(1) if matched else "other"


def project_summary(commits: list[Commit]) -> list[dict[str, object]]:
    by_project: dict[str, list[Commit]] = defaultdict(list)
    for commit in commits:
        by_project[commit.project].append(commit)

    projects: list[dict[str, object]] = []
    for project, rows in by_project.items():
        unique_subjects: list[str] = []
        seen_subjects: set[str] = set()
        for row in sorted(rows, key=lambda item: item.date, reverse=True):
            if row.subject not in seen_subjects:
                unique_subjects.append(row.subject)
                seen_subjects.add(row.subject)
        projects.append(
            {
                "project": project,
                "commits": len(rows),
                "non_merge_commits": sum(item.parent_count <= 1 for item in rows),
                "additions": sum(item.additions for item in rows),
                "deletions": sum(item.deletions for item in rows),
                "files": sum(item.files for item in rows),
                "period": {
                    "first": min(item.date for item in rows),
                    "last": max(item.date for item in rows),
                },
                "recent_unique_subjects": unique_subjects[:12],
            }
        )
    return sorted(projects, key=lambda item: (-int(item["commits"]), str(item["project"])))


def build_report(
    workspace: Path,
    author_email: str,
    since: str,
    until: str,
    repositories: list[Path],
    commits: list[Commit],
    failures: dict[str, str],
    include_commits: bool,
) -> dict[str, object]:
    non_merge = [commit for commit in commits if commit.parent_count <= 1]
    authors = Counter((commit.author_name, commit.author_email) for commit in commits)
    report: dict[str, object] = {
        "scope": {
            "workspace": str(workspace),
            "since": since,
            "until": until,
            "author_email": author_email,
            "repository_roots_scanned": len(repositories),
            "repositories_with_commits": len({commit.project for commit in commits}),
        },
        "author_identities": [
            {"name": name, "email": email, "commits": count}
            for (name, email), count in authors.most_common()
        ],
        "summary": {
            "commits": len(commits),
            "merge_commits": sum(commit.parent_count > 1 for commit in commits),
            "non_merge_commits": len(non_merge),
            "additions": sum(commit.additions for commit in commits),
            "deletions": sum(commit.deletions for commit in commits),
            "files": sum(commit.files for commit in commits),
            "monthly_non_merge_commits": dict(
                sorted(Counter(commit.date[:7] for commit in non_merge).items())
            ),
            "prefixes_non_merge": dict(
                Counter(commit_prefix(commit.subject) for commit in non_merge).most_common()
            ),
        },
        "projects": project_summary(commits),
        "collection_notes": [
            "仅采集 branches、remotes、tags 可达提交；未采集 stash 与未提交工作区变更。",
            "提交和代码变更可作为工作线索，不足以单独证明工时、提测时效、日报、故障等级、投诉、AI 使用时长或资源成本。",
        ],
        "repository_failures": failures,
    }
    if include_commits:
        report["commits"] = [asdict(commit) for commit in sorted(commits, key=lambda item: item.date)]
    return report


def render_markdown(report: dict[str, object]) -> str:
    scope = report["scope"]
    summary = report["summary"]
    assert isinstance(scope, dict) and isinstance(summary, dict)
    lines = [
        "# Git 周期贡献取证",
        "",
        f"- 工作区：`{scope['workspace']}`",
        f"- 周期：{scope['since']} 至 {scope['until']}",
        f"- 提交身份：`{scope['author_email']}`",
        f"- 扫描仓库：{scope['repository_roots_scanned']}；有提交项目：{scope['repositories_with_commits']}",
        "",
        "## 内部统计（非绩效结论）",
        "",
        f"- 提交：{summary['commits']}；非 merge：{summary['non_merge_commits']}；merge：{summary['merge_commits']}",
        f"- 变更：+{summary['additions']} / -{summary['deletions']}；文件：{summary['files']}",
        "",
        "## 活跃项目与提交主题",
        "",
        "| 项目 | 提交 | 活跃区间 | 最近主题 |",
        "|---|---:|---|---|",
    ]
    projects = report["projects"]
    assert isinstance(projects, list)
    for project in projects:
        assert isinstance(project, dict)
        period = project["period"]
        assert isinstance(period, dict)
        subjects = "；".join(project["recent_unique_subjects"][:3])
        lines.append(
            f"| {project['project']} | {project['commits']} | "
            f"{period['first'][:10]} ~ {period['last'][:10]} | {subjects} |"
        )
    lines.extend(
        [
            "",
            "## 使用提示",
            "",
            "以上数据用于提炼工作流和核验事实。撰写绩效总结时，应以业务交付、协同、质量治理和知识沉淀为主，不应以提交数量作为完成情况。",
        ]
    )
    return "\n".join(lines) + "\n"


def default_author_email() -> str | None:
    result = subprocess.run(
        ["git", "config", "--global", "--get", "user.email"],
        check=False,
        capture_output=True,
        text=True,
    )
    email = result.stdout.strip()
    return email if result.returncode == 0 and email else None


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect author-scoped Git contribution evidence across a workspace."
    )
    parser.add_argument("--workspace", default=".", help="Workspace containing Git projects.")
    parser.add_argument("--since", required=True, help="Git --since boundary, including timezone when relevant.")
    parser.add_argument("--until", required=True, help="Git --until boundary, including timezone when relevant.")
    parser.add_argument(
        "--author-email",
        default=default_author_email(),
        help="Author email; defaults to global Git user.email.",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", help="Optional output file; otherwise writes stdout.")
    parser.add_argument(
        "--include-commits",
        action="store_true",
        help="Include every parsed commit in JSON output; omitted by default to keep reports concise.",
    )
    arguments = parser.parse_args()
    if not arguments.author_email:
        parser.error("--author-email is required because global Git user.email is unavailable")
    return arguments


def main() -> int:
    arguments = parse_arguments()
    workspace = Path(arguments.workspace).expanduser().resolve()
    if not workspace.is_dir():
        print(f"Workspace does not exist: {workspace}", file=sys.stderr)
        return 2

    repositories = sorted(set(discover_repositories(workspace)))
    commits: list[Commit] = []
    failures: dict[str, str] = {}
    for repository in repositories:
        try:
            commits.extend(parse_log(repository, arguments.author_email, arguments.since, arguments.until))
        except RuntimeError as error:
            failures[str(repository.relative_to(workspace))] = str(error)

    report = build_report(
        workspace,
        arguments.author_email,
        arguments.since,
        arguments.until,
        repositories,
        commits,
        failures,
        arguments.include_commits,
    )
    content = (
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if arguments.format == "json"
        else render_markdown(report)
    )
    if arguments.output:
        destination = Path(arguments.output).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
