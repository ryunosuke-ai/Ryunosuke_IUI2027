#!/usr/bin/env python3
"""
Export Overleaf review comments without manually transcribing them.

Design goals
------------
- Reuse an authenticated Chromium profile; no password is stored in this script.
- Capture comment/review-related JSON returned by the Overleaf web app.
- Fall back to DOM-based extraction when structured network data is unavailable.
- Save diagnostics so the extractor can be adapted without manually copying comments.

Usage
-----
  python export_comments.py "https://www.overleaf.com/project/PROJECT_ID"

First run:
  A Chromium window opens. Log into Overleaf yourself if necessary.
  Open the target project and wait until comments/review information is visible.
  The script then exports JSON/Markdown and diagnostics.

Important:
  Overleaf does not document a public comments export API. Its internal UI/API can change.
  This exporter therefore uses several non-destructive discovery strategies and never
  resolves, edits, or deletes comments.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

from playwright.async_api import async_playwright, Page, Response

RELEVANT_URL_RE = re.compile(
    r"(comment|comments|review|reviews|thread|threads|change|changes|track[-_]?change)",
    re.IGNORECASE,
)

DEFAULT_DOM_SELECTORS = [
    '[data-testid*="comment" i]',
    '[data-testid*="review" i]',
    '[aria-label*="comment" i]',
    '[aria-label*="review" i]',
    '[class*="comment" i]',
    '[class*="review" i]',
    '[class*="thread" i]',
]

TEXT_KEYS = {
    "comment", "comments", "content", "body", "text", "message", "reply",
    "replies", "thread", "threads", "review", "reviews",
}
META_KEYS = {
    "id", "_id", "thread_id", "threadId", "comment_id", "commentId",
    "author", "user", "name", "email", "created_at", "createdAt",
    "updated_at", "updatedAt", "resolved", "status", "file", "filename",
    "path", "doc", "doc_id", "docId", "range", "position", "offset",
    "from", "to", "anchor", "selection",
}


@dataclass
class ExtractedComment:
    source: str
    text: str
    author: str | None = None
    resolved: bool | None = None
    file: str | None = None
    anchor_text: str | None = None
    created_at: str | None = None
    raw_hint: dict[str, Any] | None = None


def norm_text(s: Any) -> str:
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def looks_like_comment_text(s: str) -> bool:
    s = norm_text(s)
    if len(s) < 2:
        return False
    # Avoid obvious UI labels.
    bad = {
        "comment", "comments", "review", "reviews", "resolve", "resolved",
        "reply", "edit", "delete", "more", "add comment", "track changes",
    }
    return s.lower() not in bad


def safe_json(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def walk_objects(obj: Any) -> Iterable[dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk_objects(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_objects(v)


def first_scalar(d: dict[str, Any], keys: Iterable[str]) -> Any:
    for k in keys:
        if k in d and isinstance(d[k], (str, int, float, bool)):
            return d[k]
    return None


def candidate_text_from_dict(d: dict[str, Any]) -> str:
    # Prefer strongly named fields.
    for key in ("comment", "body", "message", "text", "content"):
        v = d.get(key)
        if isinstance(v, str) and looks_like_comment_text(v):
            return norm_text(v)

    # Some APIs nest comment content.
    for key in ("comment", "message", "content", "body"):
        v = d.get(key)
        if isinstance(v, dict):
            for subkey in ("text", "body", "content", "value"):
                sv = v.get(subkey)
                if isinstance(sv, str) and looks_like_comment_text(sv):
                    return norm_text(sv)
    return ""


def author_from_dict(d: dict[str, Any]) -> str | None:
    v = d.get("author") or d.get("user")
    if isinstance(v, str):
        return norm_text(v) or None
    if isinstance(v, dict):
        for key in ("name", "display_name", "displayName", "email", "username"):
            if isinstance(v.get(key), str) and norm_text(v[key]):
                return norm_text(v[key])
    name = first_scalar(d, ("author_name", "authorName", "user_name", "userName", "name"))
    return norm_text(name) or None if name is not None else None


def resolved_from_dict(d: dict[str, Any]) -> bool | None:
    for key in ("resolved", "isResolved", "is_resolved"):
        if isinstance(d.get(key), bool):
            return d[key]
    status = d.get("status")
    if isinstance(status, str):
        st = status.lower()
        if "resolved" in st or "closed" in st:
            return True
        if "open" in st or "unresolved" in st:
            return False
    return None


def file_from_dict(d: dict[str, Any]) -> str | None:
    for key in ("file", "filename", "path", "docName", "documentName"):
        v = d.get(key)
        if isinstance(v, str) and v.strip():
            return norm_text(v)
    doc = d.get("doc") or d.get("document")
    if isinstance(doc, dict):
        for key in ("name", "path", "filename"):
            v = doc.get(key)
            if isinstance(v, str) and v.strip():
                return norm_text(v)
    return None


def anchor_from_dict(d: dict[str, Any]) -> str | None:
    for key in ("anchor_text", "anchorText", "selectedText", "selectionText", "quote"):
        v = d.get(key)
        if isinstance(v, str) and v.strip():
            return norm_text(v)
    for key in ("anchor", "selection", "range"):
        v = d.get(key)
        if isinstance(v, dict):
            for subkey in ("text", "quote", "selectedText", "content"):
                sv = v.get(subkey)
                if isinstance(sv, str) and sv.strip():
                    return norm_text(sv)
    return None


def comment_from_dict(d: dict[str, Any], source: str) -> ExtractedComment | None:
    text = candidate_text_from_dict(d)
    if not text:
        return None
    created = first_scalar(d, ("created_at", "createdAt", "timestamp", "time"))
    hint = {k: safe_json(v) for k, v in d.items() if k in META_KEYS}
    return ExtractedComment(
        source=source,
        text=text,
        author=author_from_dict(d),
        resolved=resolved_from_dict(d),
        file=file_from_dict(d),
        anchor_text=anchor_from_dict(d),
        created_at=norm_text(created) or None if created is not None else None,
        raw_hint=hint or None,
    )


def dedupe(comments: list[ExtractedComment]) -> list[ExtractedComment]:
    out: list[ExtractedComment] = []
    seen: set[tuple[str, str | None, str | None]] = set()
    for c in comments:
        key = (norm_text(c.text).lower(), c.file, c.anchor_text)
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


async def click_reviewish_buttons(page: Page) -> None:
    """Best-effort only. Failure is harmless."""
    labels = [
        "Review", "Reviews", "Comments", "Comment", "Show comments",
        "Open review panel", "Review panel",
    ]
    for label in labels:
        try:
            loc = page.get_by_role("button", name=re.compile(re.escape(label), re.I))
            if await loc.count() > 0:
                await loc.first.click(timeout=1500)
                await page.wait_for_timeout(500)
        except Exception:
            pass


async def scroll_possible_review_areas(page: Page) -> None:
    # Scroll likely sidebars/panels several times to force lazy-loaded threads into DOM.
    await page.evaluate(
        """async () => {
          const sleep = ms => new Promise(r => setTimeout(r, ms));
          const els = Array.from(document.querySelectorAll(
            '[data-testid*="review" i], [data-testid*="comment" i], [class*="review" i], [class*="comment" i], [class*="sidebar" i], [role="dialog"]'
          ));
          const scrollables = els.filter(el => {
            const s = getComputedStyle(el);
            return (el.scrollHeight > el.clientHeight + 20) &&
                   ['auto','scroll'].includes(s.overflowY);
          });
          for (const el of scrollables) {
            let prev = -1;
            for (let i=0; i<30; i++) {
              el.scrollTop = el.scrollHeight;
              await sleep(120);
              if (el.scrollHeight === prev) break;
              prev = el.scrollHeight;
            }
            el.scrollTop = 0;
          }
        }"""
    )


async def dom_extract(page: Page) -> list[ExtractedComment]:
    rows = await page.evaluate(
        """(selectors) => {
          const seen = new Set();
          const out = [];
          for (const sel of selectors) {
            for (const el of document.querySelectorAll(sel)) {
              if (!el || !el.innerText) continue;
              const txt = el.innerText.replace(/\\s+/g, ' ').trim();
              if (!txt || seen.has(txt)) continue;
              seen.add(txt);

              const attrs = {};
              for (const a of el.attributes || []) attrs[a.name] = a.value;

              // Try to keep a relatively compact candidate container.
              out.push({
                selector: sel,
                text: txt,
                tag: el.tagName,
                attrs,
              });
            }
          }
          return out;
        }""",
        DEFAULT_DOM_SELECTORS,
    )

    comments: list[ExtractedComment] = []
    for row in rows:
        txt = norm_text(row.get("text"))
        if not looks_like_comment_text(txt):
            continue

        # DOM containers can include author/UI text plus multiple replies.
        # Keep them as candidates; network extraction is preferred when available.
        if len(txt) > 5000:
            continue
        comments.append(
            ExtractedComment(
                source="dom",
                text=txt,
                raw_hint={
                    "selector": row.get("selector"),
                    "tag": row.get("tag"),
                    "attrs": row.get("attrs"),
                },
            )
        )
    return comments


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_url", help="Overleaf project URL, e.g. https://www.overleaf.com/project/<id>")
    ap.add_argument("--out-dir", default="docs/overleaf_review", help="Output directory")
    ap.add_argument("--profile-dir", default=".overleaf_playwright_profile", help="Persistent Chromium profile")
    ap.add_argument("--wait", type=int, default=0, help="Seconds to wait automatically. Default 0 = wait until you press Enter.")
    ap.add_argument("--headless", action="store_true", help="Run headless (not recommended for first run)")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    profile_dir = Path(args.profile_dir).expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    captured_payloads: list[dict[str, Any]] = []
    captured_urls: list[str] = []

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=args.headless,
            viewport={"width": 1500, "height": 1000},
        )

        page = context.pages[0] if context.pages else await context.new_page()

        async def on_response(resp: Response) -> None:
            url = resp.url
            if not RELEVANT_URL_RE.search(url):
                return
            captured_urls.append(url)
            try:
                ctype = (resp.headers.get("content-type") or "").lower()
                if "json" in ctype:
                    payload = await resp.json()
                    captured_payloads.append({"url": url, "payload": payload})
            except Exception:
                pass

        page.on("response", on_response)

        print(f"[1/5] Opening {args.project_url}")
        await page.goto(args.project_url, wait_until="domcontentloaded", timeout=120_000)

        if not args.headless:
            if args.wait > 0:
                print(
                    f"[2/5] Browser is open. If login is required, log in yourself.\n"
                    f"      Open the Review/Comments panel if it is not already visible.\n"
                    f"      Waiting {args.wait} seconds..."
                )
                await page.wait_for_timeout(args.wait * 1000)
            else:
                print(
                    "[2/5] Browser is open.\n"
                    "      1) Log into Overleaf if necessary.\n"
                    "      2) Open the target project.\n"
                    "      3) Open the Review/Comments panel and make sure comments are visible.\n"
                    "      4) Return to this terminal and press Enter.\n"
                    "      There is NO time limit while waiting for Enter."
                )
                await asyncio.to_thread(input, "\nPress Enter when Overleaf is ready... ")
        else:
            if args.wait <= 0:
                print("ERROR: --headless requires --wait > 0", file=sys.stderr)
                await context.close()
                return 2
            await page.wait_for_timeout(args.wait * 1000)

        print("[3/5] Trying to open/scroll review UI...")
        await click_reviewish_buttons(page)
        await page.wait_for_timeout(1500)
        await scroll_possible_review_areas(page)
        await page.wait_for_timeout(1000)

        # Diagnostics first: these are useful even if extraction fails.
        html_path = out_dir / "overleaf_page_snapshot.html"
        html_path.write_text(await page.content(), encoding="utf-8")
        await page.screenshot(path=str(out_dir / "overleaf_page_snapshot.png"), full_page=True)

        (out_dir / "captured_relevant_urls.txt").write_text(
            "\n".join(sorted(set(captured_urls))), encoding="utf-8"
        )
        (out_dir / "captured_network_payloads.json").write_text(
            json.dumps(captured_payloads, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print("[4/5] Extracting comment candidates...")
        comments: list[ExtractedComment] = []

        # Prefer structured network payloads.
        for item in captured_payloads:
            url = item["url"]
            for d in walk_objects(item["payload"]):
                c = comment_from_dict(d, source=f"network:{url}")
                if c:
                    comments.append(c)

        # Add DOM candidates as fallback.
        comments.extend(await dom_extract(page))
        comments = dedupe(comments)

        # Save all candidates; we do not modify Overleaf.
        json_path = out_dir / "overleaf_review_comments.json"
        json_path.write_text(
            json.dumps([asdict(c) for c in comments], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        md_lines = [
            "# Overleaf Review Comments",
            "",
            f"- Exported: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- Project: `{args.project_url}`",
            f"- Extracted candidates: **{len(comments)}**",
            "",
            "> This file is generated automatically. Network-derived entries are generally",
            "> more reliable than DOM-derived candidates.",
            "",
        ]
        for i, c in enumerate(comments, 1):
            md_lines += [
                f"## Comment {i}",
                "",
                f"- Source: `{c.source}`",
            ]
            if c.author:
                md_lines.append(f"- Author: {c.author}")
            if c.file:
                md_lines.append(f"- File: `{c.file}`")
            if c.resolved is not None:
                md_lines.append(f"- Resolved: `{c.resolved}`")
            if c.created_at:
                md_lines.append(f"- Created: {c.created_at}")
            if c.anchor_text:
                md_lines += ["", "**Anchor text**", "", f"> {c.anchor_text}"]
            md_lines += ["", "**Comment**", "", c.text, ""]
        (out_dir / "overleaf_review_comments.md").write_text(
            "\n".join(md_lines), encoding="utf-8"
        )

        await context.close()

    print("[5/5] Done.")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {out_dir / 'overleaf_review_comments.md'}")
    print(f"  Diagnostics: {html_path}, overleaf_page_snapshot.png")
    if not comments:
        print(
            "\nNo comment candidates were detected. This does NOT mean the comments are unavailable.\n"
            "Send me the generated overleaf_page_snapshot.html and/or captured_network_payloads.json;\n"
            "I can adapt the extractor to the current Overleaf UI without you transcribing comments."
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
