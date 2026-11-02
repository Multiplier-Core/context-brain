"""cb-eval: validate the test sets and run baselines against them."""

import argparse
import json
import sys
from pathlib import Path

from . import DEFAULT_ROOT, classification, retrieval
from .data import CATEGORIES, QUESTION_TYPES, load_items, load_notes, load_questions
from .org import Org
from .validate import validate


def pct(x: float | None) -> str:
    return "—" if x is None else f"{x:.1%}"


def table(header: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def cmd_validate(args) -> int:
    errors = validate(args.root)
    for e in errors:
        print(e)
    print(f"{len(errors)} problem(s)" if errors else "All test sets are consistent.")
    return 1 if errors else 0


def cmd_classify(args) -> int:
    org = Org.load(args.root)
    items = load_items(args.root)
    clf = classification.CLASSIFIERS[args.classifier](org)
    slices, predictions = classification.evaluate(clf, items)

    print(f"# Classification: `{args.classifier}` on {len(items)} items\n")
    print("## Gate 1 (criteria 1–4)\n")
    rows = []
    for name, (value, ok) in classification.gate_1(slices).items():
        target = classification.GATE_1[name]
        shown = value if name == "leaks" else pct(value)
        want = (
            f"= {target}"
            if name == "leaks"
            else (f"≤ {target:.0%}" if name == "prompt_rate" else f"≥ {target:.0%}")
        )
        rows.append([name, shown, want, "pass" if ok else "**fail**"])
    print(table(["Criterion", "Value", "Target", "Result"], rows))

    print("\n## By slice\n")
    rows = []
    for name, s in slices.items():
        rows.append(
            [
                name,
                s.n,
                pct(s.accuracy),
                len(s.leaks),
                len(s.secrets_stored),
                pct(s.precision),
                pct(s.coverage),
                pct(s.prompt_rate),
                len(s.wrong_group),
            ]
        )
    print(
        table(
            [
                "Slice",
                "Items",
                "Accuracy",
                "Leaks",
                "Secrets stored",
                "Precision",
                "Coverage",
                "Prompt rate",
                "Wrong group",
            ],
            rows,
        )
    )

    print("\n## Confusion matrix (all items; rows expected, columns predicted)\n")
    conf = slices["all"].confusion
    print(
        table(
            ["expected \\ predicted", *CATEGORIES],
            [[e, *(conf[(e, p)] for p in CATEGORIES)] for e in CATEGORIES],
        )
    )

    leaks = slices["all"].leaks
    if leaks:
        print("\n## Leaks\n")
        by_id = {i.id: (i, p) for i, p in predictions}
        for item_id in leaks:
            i, p = by_id[item_id]
            print(f"- `{i.id}` expected {i.category}, shared to {p.group} ({p.reason}): {i.text}")

    if args.out:
        write_json(
            args.out,
            {
                "classifier": args.classifier,
                "slices": {
                    k: {
                        "n": s.n,
                        "accuracy": s.accuracy,
                        "leaks": s.leaks,
                        "secrets_stored": s.secrets_stored,
                        "precision": s.precision,
                        "coverage": s.coverage,
                        "prompt_rate": s.prompt_rate,
                        "wrong_group": s.wrong_group,
                    }
                    for k, s in slices.items()
                },
                "predictions": [
                    {"id": i.id, "category": p.category, "group": p.group, "reason": p.reason}
                    for i, p in predictions
                ],
            },
        )
    return 0


def cmd_retrieve(args) -> int:
    org = Org.load(args.root)
    notes = load_notes(org.vaults)
    questions = load_questions(args.root)
    whole = retrieval.evaluate(org, retrieval.WholeVault(notes), questions, 0)
    names = args.retriever or list(retrieval.RETRIEVERS)
    budgets = args.budget or [500, 1500, 3000]

    print(f"# Retrieval on {len(questions)} questions, {len(notes)} notes\n")
    print("Answerable: every gold string is in the returned context (an upper bound on accuracy).")
    print("Tokens are approximate (4 characters per token).\n")
    runs = []
    for name in names:
        retriever = retrieval.RETRIEVERS[name](notes)
        for budget in [0] if name == "whole" else budgets:
            s = whole if name == "whole" else retrieval.evaluate(org, retriever, questions, budget)
            runs.append((name, budget, s))

    rows = []
    for name, budget, s in runs:
        answer_qs = [r for r in s.results if r.question.type != "access"]
        access_qs = s.of("access")
        rows.append(
            [
                name,
                budget or "none",
                pct(s.rate(answer_qs, "answerable")),
                pct(s.rate(answer_qs, "evidence_found")),
                f"{s.mean_tokens:.0f}",
                pct(s.mean_tokens / whole.mean_tokens if whole.mean_tokens else None),
                f"{sum(not r.access_leak for r in access_qs)}/{len(access_qs)}",
                len(s.leaks),
            ]
        )
    print(
        table(
            [
                "Retriever",
                "Budget",
                "Answerable",
                "Evidence found",
                "Mean tokens",
                "vs whole",
                "Access passed",
                "Leaks",
            ],
            rows,
        )
    )

    print("\n## Answerable by question type\n")
    types = [t for t in QUESTION_TYPES if t != "access"]
    print(
        table(
            ["Retriever", "Budget", *types],
            [
                [n, b or "none", *(pct(s.rate(s.of(t), "answerable")) for t in types)]
                for n, b, s in runs
            ],
        )
    )

    if args.out:
        write_json(
            args.out,
            {
                "runs": [
                    {
                        "retriever": n,
                        "budget": b,
                        "results": [
                            {
                                "id": r.question.id,
                                "tokens": r.tokens,
                                "answerable": r.answerable,
                                "evidence_found": r.evidence_found,
                                "access_leak": r.access_leak,
                            }
                            for r in s.results
                        ],
                    }
                    for n, b, s in runs
                ]
            },
        )
    return 1 if any(s.leaks for _, _, s in runs) else 0


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\nWrote {path}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cb-eval", description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="the eval/ directory")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="check the test sets are consistent")

    p = sub.add_parser("classify", help="run a classifier on the classification set")
    p.add_argument("--classifier", choices=list(classification.CLASSIFIERS), default="rules")
    p.add_argument("--out", type=Path, help="also write results as JSON")

    p = sub.add_parser("retrieve", help="run retrievers on the retrieval set")
    p.add_argument("--retriever", action="append", choices=list(retrieval.RETRIEVERS))
    p.add_argument("--budget", action="append", type=int, help="token budget (repeatable)")
    p.add_argument("--out", type=Path, help="also write results as JSON")

    args = parser.parse_args(argv)
    return {"validate": cmd_validate, "classify": cmd_classify, "retrieve": cmd_retrieve}[
        args.command
    ](args)


if __name__ == "__main__":
    sys.exit(main())
