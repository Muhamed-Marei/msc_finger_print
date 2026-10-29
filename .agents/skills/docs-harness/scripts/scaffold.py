#!/usr/bin/env python3
"""
docs-harness scaffolder.

Creates and extends a bilingual (EN/AR) phase-and-feature documentation tree
from data/file-registry.json + templates/.

    scaffold.py init        --root docs --project "Name" [--stack generic] [--phase 01:foundation:Foundation]
    scaffold.py add-phase   --root docs --num 02 --slug commerce --title "Commerce" [--title-ar "التجارة"]
    scaffold.py add-feature --root docs --phase 02 --code CART --slug shopping-cart --title "Shopping Cart"
    scaffold.py add-adr     --root docs --title "Use X for Y"

Never overwrites an existing file unless --force is passed.
Exit codes: 0 ok, 1 usage/validation error, 2 refused (would overwrite).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
DATA = BUNDLE / "data"
TEMPLATES = BUNDLE / "templates"
AR_SPLIT = "<!-- @@AR@@ -->"
TODAY = _dt.date.today().isoformat()


# --------------------------------------------------------------------------- io
def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def sha_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render(template: str, ctx: dict) -> str:
    out = (TEMPLATES / template).read_text(encoding="utf-8")
    for key, val in ctx.items():
        out = out.replace("{{%s}}" % key, str(val))
    return out


def ar_header(en_relname: str, en_body: str) -> str:
    return (
        "---\n"
        "lang: ar\n"
        f"source: {en_relname}\n"
        f"source_sha: {sha_of(en_body)}\n"
        f"translated: {TODAY}\n"
        "status: machine-skeleton  # replace with 'human-reviewed' once a person has read it\n"
        "---\n\n"
    )


def write(path: Path, body: str, force: bool, created: list, skipped: list) -> None:
    if path.exists() and not force:
        skipped.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    created.append(path)


def emit(root: Path, entry: dict, ctx: dict, force: bool, created: list, skipped: list) -> None:
    """Write one registry entry, splitting the template into EN + AR when mirrored."""
    rel = entry["path"].format(**ctx)
    target = root / rel
    raw = render(entry["template"], ctx)

    if entry["bilingual"] == "mirror":
        if AR_SPLIT not in raw:
            raise SystemExit(f"template {entry['template']} is mirror-mode but has no {AR_SPLIT} marker")
        en_body, ar_body = (part.strip() + "\n" for part in raw.split(AR_SPLIT, 1))
        write(target, en_body, force, created, skipped)
        ar_target = target.with_suffix("")
        ar_target = ar_target.with_name(ar_target.name + ".ar.md")
        write(ar_target, ar_header(target.name, en_body) + ar_body, force, created, skipped)
    else:
        write(target, raw.replace(AR_SPLIT, "").rstrip() + "\n", force, created, skipped)


def phase_dir(num: str, slug: str) -> str:
    return f"phase-{int(num):02d}-{slug}"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def stack_block(profiles: dict, key: str) -> dict:
    if key not in profiles["profiles"]:
        raise SystemExit(
            f"unknown stack '{key}'. Available: {', '.join(sorted(profiles['profiles']))}"
        )
    p = profiles["profiles"][key]
    return {
        "STACK_LABEL": p["label"],
        "STACK_LAYERS": p["layers"],
        "STACK_RULES": "\n".join(f"- {r}" for r in p["rules"]),
        "STACK_FITNESS": "\n".join(f"- {f}" for f in p["fitness"]),
    }


def report(created: list, skipped: list, root: Path) -> None:
    for p in created:
        print(f"  + {p.relative_to(root.parent) if root.parent != p else p}")
    if skipped:
        print(f"\n  {len(skipped)} file(s) already existed and were left alone "
              f"(pass --force to overwrite):")
        for p in skipped[:10]:
            print(f"    · {p.name}")
        if len(skipped) > 10:
            print(f"    · … and {len(skipped) - 10} more")
    print(f"\n{len(created)} file(s) written under {root}/")


# ----------------------------------------------------------------- subcommands
def cmd_init(a) -> int:
    reg, profiles = load("file-registry.json"), load("stack-profiles.json")
    root = Path(a.root)
    ctx = {"PROJECT": a.project, "DATE": TODAY, "ADR_NUM": "0001",
           "ADR_TITLE": "Adopt the docs harness", **stack_block(profiles, a.stack)}
    created: list = []
    skipped: list = []

    for entry in reg["static_tree"]:
        if entry["template"] == "meta-registry.json":
            write(root / entry["path"], json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
                  a.force, created, skipped)
            continue
        emit(root, entry, ctx, a.force, created, skipped)

    # make the project self-contained: the validator ships with the docs
    validator = root / "_meta" / "validate.py"
    if not validator.exists() or a.force:
        validator.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "validate.py", validator)
        created.append(validator)

    for spec in a.phase or []:
        _add_phase_files(root, reg, profiles, spec, ctx, a, created, skipped)

    report(created, skipped, root)
    print("\nNext: fill every <!-- FILL --> in AGENTS.md, then prd.md's anti-features list.")
    print(f"Then run: python {root}/_meta/validate.py {root}")
    return 0


def _add_phase_files(root, reg, profiles, spec, base_ctx, a, created, skipped):
    parts = spec.split(":")
    if len(parts) < 2:
        raise SystemExit(f"--phase expects NUM:slug[:Title], got '{spec}'")
    num, slug = parts[0], parts[1]
    title = parts[2] if len(parts) > 2 else slug.replace("-", " ").title()
    ctx = {**base_ctx, "PHASE_NUM": f"{int(num):02d}", "PHASE_SLUG": slug,
           "PHASE_TITLE": title, "phase_dir": phase_dir(num, slug)}
    for entry in reg["phase_tree"]:
        emit(root, entry, ctx, a.force, created, skipped)


def cmd_add_phase(a) -> int:
    reg, profiles = load("file-registry.json"), load("stack-profiles.json")
    root = Path(a.root)
    created: list = []
    skipped: list = []
    base = {"PROJECT": a.project or "", "DATE": TODAY, **stack_block(profiles, a.stack)}
    _add_phase_files(root, reg, profiles, f"{a.num}:{a.slug}:{a.title}", base, a, created, skipped)
    report(created, skipped, root)
    print(f"\nNow add a row for phase {int(a.num):02d} to {root}/03-phases/ROADMAP.md "
          f"(EN: {a.title}{' / AR: ' + a.title_ar if a.title_ar else ''}).")
    return 0


def cmd_add_feature(a) -> int:
    reg, profiles = load("file-registry.json"), load("stack-profiles.json")
    root = Path(a.root)
    matches = sorted((root / "03-phases").glob(f"phase-{int(a.phase):02d}-*"))
    if not matches:
        raise SystemExit(f"no phase folder matching phase-{int(a.phase):02d}-* under {root}/03-phases")
    pdir = matches[0].name
    if not re.fullmatch(r"[A-Z0-9]{2,12}", a.code):
        raise SystemExit(f"--code must be 2–12 uppercase letters/digits, got '{a.code}'")
    ctx = {"PROJECT": a.project or "", "DATE": TODAY,
           "PHASE_NUM": f"{int(a.phase):02d}", "phase_dir": pdir,
           "FEATURE_CODE": a.code, "FEATURE_SLUG": a.slug or slugify(a.title),
           "FEATURE_TITLE": a.title, "feature_slug": a.slug or slugify(a.title),
           **stack_block(profiles, a.stack)}
    created: list = []
    skipped: list = []
    for entry in reg["feature_tree"]:
        emit(root, entry, ctx, a.force, created, skipped)
    report(created, skipped, root)
    print(f"\nNow: add {a.code} to {root}/_meta/features-index.md and to "
          f"{root}/03-phases/{pdir}/plan.md, then open task ids T-{int(a.phase):02d}.{a.code}.NN "
          f"in that phase's tasks.md.")
    return 0


def cmd_add_adr(a) -> int:
    root = Path(a.root)
    dec = root / "01-architecture" / "decisions"
    dec.mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for p in dec.glob("[0-9][0-9][0-9][0-9]-*.md")
            if (m := re.match(r"(\d{4})-", p.name))]
    nxt = f"{max(nums) + 1 if nums else 1:04d}"
    ctx = {"PROJECT": a.project or "", "DATE": TODAY, "ADR_NUM": nxt, "ADR_TITLE": a.title}
    created: list = []
    skipped: list = []
    entry = {"path": f"01-architecture/decisions/{nxt}-{slugify(a.title)}.md",
             "template": "adr.md", "bilingual": "mirror"}
    emit(root, entry, ctx, a.force, created, skipped)
    report(created, skipped, root)
    print(f"\nNow add ADR {nxt} to {root}/01-architecture/decisions/INDEX.md. "
          f"Do not skip the rejected-alternatives table.")
    return 0


# ----------------------------------------------------------------------- entry
def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="scaffold.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, project_required=False):
        sp.add_argument("--root", default="docs", help="docs tree root (default: docs)")
        sp.add_argument("--project", required=project_required,
                        help="project name used in headings")
        sp.add_argument("--stack", default="generic", help="key from data/stack-profiles.json")
        sp.add_argument("--force", action="store_true", help="overwrite existing files")

    i = sub.add_parser("init", help="create the full tree")
    common(i, project_required=True)
    i.add_argument("--phase", action="append", metavar="NUM:slug[:Title]",
                   help="repeatable; e.g. --phase 01:foundation:Foundation")
    i.set_defaults(func=cmd_init)

    ap = sub.add_parser("add-phase", help="add a phase folder")
    common(ap)
    ap.add_argument("--num", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--title-ar", dest="title_ar")
    ap.set_defaults(func=cmd_add_phase)

    af = sub.add_parser("add-feature", help="add a feature slice inside a phase")
    common(af)
    af.add_argument("--phase", required=True, help="phase number, e.g. 02")
    af.add_argument("--code", required=True, help="stable feature code, e.g. CART")
    af.add_argument("--slug")
    af.add_argument("--title", required=True)
    af.set_defaults(func=cmd_add_feature)

    ad = sub.add_parser("add-adr", help="append the next numbered ADR")
    common(ad)
    ad.add_argument("--title", required=True)
    ad.set_defaults(func=cmd_add_adr)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
