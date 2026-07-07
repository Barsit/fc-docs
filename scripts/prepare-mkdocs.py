#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_SRC = ROOT / "_mkdocs_src"
SITE_DIR = ROOT / "_site"
CONFIG_PATH = ROOT / "mkdocs.generated.yml"

def main() -> None:
    reset_build_dirs()
    copy_content()
    nav = build_nav()
    write_config(nav)


def reset_build_dirs() -> None:
    for path in (DOCS_SRC, SITE_DIR):
        if path.exists():
            shutil.rmtree(path)
    DOCS_SRC.mkdir(parents=True)


def copy_content() -> None:
    shutil.copy2(ROOT / "README.md", DOCS_SRC / "index.md")
    english_readme = (ROOT / "README.en-US.md").read_text(encoding="utf-8")
    english_readme = english_readme.replace("(README.md)", "(index.md)")
    (DOCS_SRC / "README.en-US.md").write_text(english_readme, encoding="utf-8")

    for name in ("docs", "assets"):
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, DOCS_SRC / name)

    license_file = ROOT / "LICENSE"
    if license_file.exists():
        shutil.copy2(license_file, DOCS_SRC / "LICENSE")


def build_nav() -> list[dict[str, str | list]]:
    nav: list[dict[str, str | list]] = [
        {"首页": "index.md"},
        {"English": "README.en-US.md"},
    ]

    docs_nav: list[dict[str, str | list]] = []
    zh_nav = nav_for_directory(DOCS_SRC / "docs" / "zh-CN")
    en_nav = nav_for_directory(DOCS_SRC / "docs" / "en-US")
    if zh_nav:
        docs_nav.append({"中文文档": zh_nav})
    if en_nav:
        docs_nav.append({"English Docs": en_nav})
    if docs_nav:
        nav.append({"文档": docs_nav})

    return nav


def nav_for_directory(directory: Path) -> list[dict[str, str | list]]:
    entries: list[dict[str, str | list]] = []
    if not directory.exists():
        return entries

    directories = sorted(
        [path for path in directory.iterdir() if path.is_dir()],
        key=sort_path,
    )
    files = sorted(
        [path for path in directory.iterdir() if path.is_file() and path.suffix == ".md"],
        key=sort_path,
    )

    for file_path in files:
        label = extract_title(file_path.read_text(encoding="utf-8")) or clean_label(file_path.stem)
        entries.append({label: relative_docs_path(file_path)})

    for child_dir in directories:
        child_entries = nav_for_directory(child_dir)
        if child_entries:
            entries.append({clean_label(child_dir.name): child_entries})

    return entries


def write_config(nav: list[dict[str, str | list]]) -> None:
    CONFIG_PATH.write_text(
        "\n".join(
            [
                "site_name: 阿里云函数计算官方文档",
                "site_url: https://aliyun-fc.github.io/fc-docs/",
                "repo_url: https://github.com/aliyun-fc/fc-docs",
                "repo_name: aliyun-fc/fc-docs",
                "docs_dir: _mkdocs_src",
                "site_dir: _site",
                "use_directory_urls: true",
                "theme:",
                "  name: material",
                "  language: zh",
                "  features:",
                "    - navigation.instant",
                "    - navigation.tracking",
                "    - navigation.sections",
                "    - navigation.indexes",
                "    - navigation.top",
                "    - toc.follow",
                "    - search.suggest",
                "    - search.highlight",
                "  palette:",
                "    - scheme: default",
                "      primary: blue",
                "      accent: light blue",
                "plugins:",
                "  - search:",
                "      lang:",
                "        - zh",
                "        - en",
                "markdown_extensions:",
                "  - admonition",
                "  - attr_list",
                "  - md_in_html",
                "  - tables",
                "  - toc:",
                "      permalink: true",
                "  - pymdownx.details",
                "  - pymdownx.superfences",
                "nav:",
                render_nav_yaml(nav, indent=2),
                "",
            ]
        ),
        encoding="utf-8",
    )


def render_nav_yaml(items: list[dict[str, str | list]], indent: int) -> str:
    lines: list[str] = []
    prefix = " " * indent
    for item in items:
        for label, value in item.items():
            if isinstance(value, list):
                lines.append(f"{prefix}- {yaml_string(label)}:")
                lines.append(render_nav_yaml(value, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_string(label)}: {yaml_string(value)}")
    return "\n".join(lines)


def relative_docs_path(path: Path) -> str:
    return path.relative_to(DOCS_SRC).as_posix()


def extract_title(text: str) -> str | None:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def clean_label(value: str) -> str:
    value = re.sub(r"^\d+[.、_-]*", "", value)
    return value.replace("_", " ").strip() or "Untitled"


def sort_path(path: Path) -> tuple[str, ...]:
    return tuple(path.relative_to(DOCS_SRC).parts)


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


if __name__ == "__main__":
    main()
