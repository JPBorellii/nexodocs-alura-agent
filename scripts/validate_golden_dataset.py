#!/usr/bin/env python3
"""Validate the static structure of the NexoDocs RAG golden dataset."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

DATASET = Path("tests/rag_golden_dataset_v1.csv")

REQUIRED_COLUMNS = {
    "case_id",
    "dataset_version",
    "document_id",
    "document_version",
    "category",
    "question",
    "expected_status",
    "expected_answer",
    "source_section",
    "criticality",
    "expected_facts",
    "forbidden_facts",
    "notes",
}

VALID_STATUS = {"ANSWERED", "NOT_FOUND", "SAFE_HANDOFF"}
VALID_CRITICALITY = {"P0", "P1"}
VALID_CATEGORIES = {
    "literal",
    "semantic",
    "policy_reasoning",
    "contact_routing",
    "safe_handoff",
    "unanswerable",
    "adversarial",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    if not DATASET.exists():
        fail(f"arquivo não encontrado: {DATASET}")

    with DATASET.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            fail("CSV sem cabeçalho")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            fail("colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))

        rows = list(reader)

    if len(rows) < 20:
        fail(f"dataset pequeno demais: {len(rows)} casos")

    ids = [row["case_id"].strip() for row in rows]
    if len(ids) != len(set(ids)):
        fail("case_id duplicado")

    for index, row in enumerate(rows, start=2):
        case_id = row["case_id"].strip() or f"linha {index}"

        for required in ("question", "expected_status", "expected_answer", "source_section"):
            if not row[required].strip():
                fail(f"{case_id}: campo obrigatório vazio: {required}")

        if row["expected_status"] not in VALID_STATUS:
            fail(f"{case_id}: expected_status inválido: {row['expected_status']}")

        if row["criticality"] not in VALID_CRITICALITY:
            fail(f"{case_id}: criticality inválida: {row['criticality']}")

        if row["category"] not in VALID_CATEGORIES:
            fail(f"{case_id}: category inválida: {row['category']}")

        if row["document_id"] != "CH-MAN-001":
            fail(f"{case_id}: document_id inesperado")

        if row["document_version"] != "1.0":
            fail(f"{case_id}: document_version inesperada")

    status_counts = Counter(row["expected_status"] for row in rows)
    category_counts = Counter(row["category"] for row in rows)
    p0_count = sum(row["criticality"] == "P0" for row in rows)

    if status_counts["NOT_FOUND"] < 4:
        fail("são necessários pelo menos 4 casos NOT_FOUND")

    if status_counts["SAFE_HANDOFF"] < 3:
        fail("são necessários pelo menos 3 casos SAFE_HANDOFF")

    if category_counts["adversarial"] < 2:
        fail("são necessários pelo menos 2 casos adversariais")

    print("Golden Dataset: PASS")
    print(f"Casos totais: {len(rows)}")
    print(f"Casos P0: {p0_count}")
    print("Status:", dict(sorted(status_counts.items())))
    print("Categorias:", dict(sorted(category_counts.items())))


if __name__ == "__main__":
    main()
