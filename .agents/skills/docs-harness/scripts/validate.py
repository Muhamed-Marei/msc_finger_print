#!/usr/bin/env python3
"""
docs-harness validator.

    python validate.py [docs_root] [--strict] [--quiet]

Checks, in order of how much damage they prevent:
  1. secrets       — a credential value committed under docs/            (ERROR)
  2. translation   — Arabic mirror missing, stale, or orphaned            (ERROR)
  3. task DAG      — duplicate ids, unknown deps, cycles, illegal starts  (ERROR)
  4. structure     — required files missing, routing links broken         (ERROR)
  5. budgets       — a file past its token ceiling                        (WARN, ERROR at 130%)
  6. hygiene       — >1 task in progress, [!]/[~] with no reason          (WARN)

Rewrites <root>/_meta/translation-status.md on every run.
Exit: 0 clean · 1 errors (or warnings with --strict).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

TASK_RE = re.compile(r"^\s*-\s*\[([ x/!~])\]\s*(T-\d{2}\.[A-Z0-9]{2,12}\.\d{2})\s*(.*)$")
DEPS_RE = re.compile(r"<!--\s*deps:\s*([^>]*?)\s*(?:\||-->)")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"`(docs/[^`]+?\.md)`|\]\(([^)]+?\.md)\)")

SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}"), "Stripe-style secret key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{35}"), "Google API key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"\bey[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "JWT"),
    (re.compile(r"(?i)[A-Z0-9_]*(?:password|passwd|secret|api_?key|[A-Z0-9]_?key|token|credential)"
                r"\s*[:=]\s*[\"']?[^\s\"'<>|]{8,}"),
     "assigned credential value"),
]
# A placeholder is not a secret. These keep the scan usable on a template tree.
SECRET_ALLOW = re.compile(r"(?i)<!--|FILL|xxx+|\.\.\.|_{4,}|\byour[-_]|example|placeholder|"
                          r"<[a-z_ -]+>|\bNAME\b|\bvalue\b")

ERRORS: list[str] = []
WARNINGS: list[str] = []
NOTES: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ------------------------------------------------------------------ utilities
def est_tokens(text: str) -> int:
    """Rough token count. Arabic is token-dense, so non-ASCII costs more per char."""
    ascii_n = sum(1 for c in text if ord(c) < 128)
    return int(ascii_n / 4 + (len(text) - ascii_n) / 2)


def sha_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.split("#", 1)[0].strip()
    return out


def load_registry(root: Path) -> dict:
    local = root / "_meta" / "file-registry.json"
    bundled = Path(__file__).resolve().parent.parent / "data" / "file-registry.json"
    src = local if local.exists() else bundled
    if not src.exists():
        err(f"no file-registry.json found (looked in {local} and {bundled})")
        return {}
    return json.loads(src.read_text(encoding="utf-8"))


def md_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if "/assets/" not in p.as_posix())


# -------------------------------------------------------------------- checks
def check_secrets(root: Path) -> None:
    for p in md_files(root) + sorted(root.rglob("*.json")):
        text = p.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            if SECRET_ALLOW.search(line):
                continue
            for pat, label in SECRET_PATTERNS:
                if pat.search(line):
                    err(f"SECRET  {p.relative_to(root)}:{line_no} looks like a {label}. "
                        f"Remove it, rotate the credential, then re-run.")
                    break


def check_translation(root: Path, reg: dict) -> list[tuple[str, str, str]]:
    """Returns rows for translation-status.md."""
    rows: list[tuple[str, str, str]] = []
    mirror_en: set[Path] = set()

    patterns = [e for e in reg.get("static_tree", []) if e["bilingual"] == "mirror"]
    mirror_names = {Path(e["path"]).name for e in patterns}
    mirror_names |= {Path(e["path"]).name for e in reg.get("phase_tree", []) if e["bilingual"] == "mirror"}
    mirror_names |= {Path(e["path"]).name for e in reg.get("feature_tree", []) if e["bilingual"] == "mirror"}
    # ADRs are mirror-mode by convention
    adr_dir = root / "01-architecture" / "decisions"

    for p in md_files(root):
        if p.name.endswith(".ar.md"):
            continue
        is_mirror = p.name in mirror_names or (p.parent == adr_dir and re.match(r"\d{4}-", p.name))
        if not is_mirror:
            continue
        mirror_en.add(p)
        en_body = p.read_text(encoding="utf-8")
        ar = p.with_name(p.stem + ".ar.md")
        rel = p.relative_to(root).as_posix()
        if not ar.exists():
            err(f"TRANSLATION  {rel} has no Arabic mirror ({ar.name}).")
            rows.append((rel, "—", "MISSING"))
            continue
        fm = frontmatter(ar.read_text(encoding="utf-8"))
        recorded = fm.get("source_sha", "")
        if not recorded:
            err(f"TRANSLATION  {ar.relative_to(root).as_posix()} has no source_sha in its frontmatter.")
            rows.append((rel, ar.name, "NO-HASH"))
        elif recorded != sha_of(en_body):
            err(f"TRANSLATION  {ar.relative_to(root).as_posix()} is STALE — "
                f"{rel} changed since translation. Retranslate and update source_sha.")
            rows.append((rel, ar.name, "STALE"))
        else:
            state = "in-sync"
            if fm.get("status") == "machine-skeleton":
                warn(f"translation  {ar.relative_to(root).as_posix()} is still a machine skeleton; "
                     f"a person has not reviewed the Arabic.")
                state = "in-sync (unreviewed)"
            rows.append((rel, ar.name, state))

    for p in md_files(root):
        if not p.name.endswith(".ar.md"):
            continue
        en = p.with_name(p.name[: -len(".ar.md")] + ".md")
        if not en.exists():
            err(f"TRANSLATION  {p.relative_to(root).as_posix()} is an ORPHAN — "
                f"its English source {en.name} is gone.")
            rows.append(("—", p.relative_to(root).as_posix(), "ORPHAN"))
    return rows


def check_tasks(root: Path) -> None:
    ledgers = sorted((root / "03-phases").glob("phase-*/tasks.md"))
    if not ledgers:
        NOTES.append("no phase ledgers yet — add one with `scaffold.py add-phase`")
        return

    all_ids: dict[str, tuple[Path, str, int]] = {}
    deps: dict[str, list[str]] = {}

    for led in ledgers:
        rel = led.relative_to(root).as_posix()
        in_progress = []
        for line_no, line in enumerate(led.read_text(encoding="utf-8").splitlines(), 1):
            m = TASK_RE.match(line)
            if not m:
                continue
            mark, tid, rest = m.group(1), m.group(2), m.group(3)
            if "XXXX" in tid:
                continue
            dup = tid in all_ids
            if dup:
                prev = all_ids[tid]
                err(f"TASKS  duplicate id {tid} — "
                    f"{prev[0].relative_to(root).as_posix()}:{prev[2]} and {rel}:{line_no}. "
                    f"Ids are assigned once and never reused.")
            else:
                all_ids[tid] = (led, mark, line_no)

            dm = DEPS_RE.search(rest)
            raw = dm.group(1) if dm else ""
            dl = [d.strip() for d in re.split(r"[,\s]+", raw)
                  if d.strip() and d.strip() not in {"—", "-", "none"}]
            if not dup:  # keep the first declaration so a duplicate cannot hide a cycle
                deps[tid] = dl

            if mark == "/":
                in_progress.append(tid)
            if mark in "!~" and len(rest.split("<!--")[0].strip()) < 12:
                warn(f"tasks  {rel}:{line_no} {tid} is [{mark}] with no stated reason. "
                     f"A blocked task with no reason is a task nobody can unblock.")
        if len(in_progress) > 1:
            warn(f"tasks  {rel} has {len(in_progress)} tasks in progress "
                 f"({', '.join(in_progress)}). One per session keeps the ledger truthful.")

    for tid, dl in deps.items():
        for d in dl:
            if d not in all_ids:
                err(f"TASKS  {tid} depends on {d}, which does not exist.")
            elif all_ids[tid][1] in "/x" and all_ids[d][1] != "x":
                err(f"TASKS  {tid} is [{all_ids[tid][1]}] but its dependency {d} "
                    f"is [{all_ids[d][1]}]. A task MUST NOT start before its deps are done.")

    # cycle detection
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(n: str) -> None:
        if state.get(n) == 2:
            return
        if state.get(n) == 1:
            cyc = " -> ".join(stack[stack.index(n):] + [n])
            err(f"TASKS  dependency cycle: {cyc}")
            return
        state[n] = 1
        stack.append(n)
        for d in deps.get(n, []):
            if d in deps:
                visit(d)
        stack.pop()
        state[n] = 2

    for tid in list(deps):
        visit(tid)

    ready = [t for t in deps
             if all_ids[t][1] == " "
             and all(all_ids.get(d, (None, "", 0))[1] == "x" for d in deps[t])]
    done = sum(1 for v in all_ids.values() if v[1] == "x")
    NOTES.append(f"tasks: {len(all_ids)} total · {done} done · {len(ready)} ready to start"
                 + (f" (next: {', '.join(ready[:5])})" if ready else ""))


def check_structure(root: Path, reg: dict) -> None:
    for entry in reg.get("static_tree", []):
        p = root / entry["path"]
        if not p.exists():
            err(f"STRUCTURE  required file missing: {entry['path']}")

    agents = root / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = m.group(1) or m.group(2)
            cand = Path(target)
            resolved = cand if cand.is_absolute() else (
                root.parent / cand if cand.parts and cand.parts[0] == root.name else root / cand
            )
            if resolved.suffix == ".md" and not resolved.exists() and "<" not in target:
                err(f"STRUCTURE  AGENTS.md routes to {target}, which does not exist.")
        if "FILL" in text:
            warn("structure  AGENTS.md still contains <!-- FILL --> placeholders. "
                 "An unfilled router sends agents guessing.")


def check_budgets(root: Path, reg: dict) -> None:
    budgets: dict[str, int] = {}
    for group in ("static_tree", "phase_tree", "feature_tree"):
        for e in reg.get(group, []):
            budgets[Path(e["path"]).name] = e["token_budget"]

    total = 0
    always = 0
    for p in md_files(root):
        text = p.read_text(encoding="utf-8")
        n = est_tokens(text)
        total += n
        base = p.name[:-len(".ar.md")] + ".md" if p.name.endswith(".ar.md") else p.name
        budget = budgets.get(base)
        if p.name == "AGENTS.md":
            always += n
        if budget is None:
            continue
        rel = p.relative_to(root).as_posix()
        if n > budget * 1.3:
            err(f"BUDGET  {rel} is ~{n} tokens against a {budget} ceiling (>130%). "
                f"Split it or move detail to a linked file.")
        elif n > budget:
            warn(f"budget  {rel} is ~{n} tokens against a {budget} ceiling. Prune before it grows.")

    NOTES.append(f"token footprint: ~{total} across the tree · ~{always} always-loaded (AGENTS.md)")
    if always > 2000:
        warn(f"budget  the always-loaded layer is ~{always} tokens. Past ~2000 the "
             f"load-bearing lines start getting lost in the middle.")


def write_status(root: Path, rows: list[tuple[str, str, str]]) -> None:
    meta = root / "_meta"
    if not meta.exists():
        return
    out = ["# Translation Status — generated", "",
           "<!-- Written by validate.py. Do not hand-edit; fix the source and re-run. -->", "",
           f"Last run: {_dt.datetime.now().isoformat(timespec='seconds')}", "",
           "| File | Arabic mirror | State |", "|---|---|---|"]
    for a, b, c in sorted(rows) or [("—", "—", "no mirrored files found")]:
        out.append(f"| `{a}` | `{b}` | {c} |")
    out += ["", "States: `in-sync` · `in-sync (unreviewed)` · `STALE` · `MISSING` · `NO-HASH` · `ORPHAN`",
            "", "STALE, MISSING and NO-HASH fail the docs check. Bilingual coverage counts only when verified."]
    (meta / "translation-status.md").write_text("\n".join(out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------- entry
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="validate.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default="docs")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--quiet", action="store_true", help="print only failures")
    a = ap.parse_args(argv)

    root = Path(a.root)
    if not root.is_dir():
        print(f"no docs tree at {root}", file=sys.stderr)
        return 1

    reg = load_registry(root)
    check_secrets(root)
    rows = check_translation(root, reg) if reg else []
    check_tasks(root)
    if reg:
        check_structure(root, reg)
        check_budgets(root, reg)
    write_status(root, rows)

    if ERRORS:
        print(f"\n{len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  ✗ {e}")
    if WARNINGS and not a.quiet:
        print(f"\n{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print(f"  ! {w}")
    if NOTES and not a.quiet:
        print()
        for n in NOTES:
            print(f"  · {n}")

    if ERRORS:
        print(f"\nFAIL — {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        return 1
    if WARNINGS and a.strict:
        print(f"\nFAIL (strict) — {len(WARNINGS)} warning(s)")
        return 1
    print(f"\nOK — 0 errors, {len(WARNINGS)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
