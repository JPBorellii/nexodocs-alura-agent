#!/usr/bin/env python3
"""
Build a searchable, professional PDF from the NexoDocs corporate knowledge-base Markdown.

Usage:
    py scripts\build_knowledge_pdf.py
or:
    python scripts/build_knowledge_pdf.py

Default input:
    knowledge-base/manual_corporativo_clinica_horizonte_v1.0.md

Default output:
    knowledge-base/manual_corporativo_clinica_horizonte_v1.0.pdf
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


DOC_ID = "CH-MAN-001"
DOC_VERSION = "1.0"
DOC_SHORT_NAME = "Manual Corporativo - Clinica Horizonte"


def normalize_text(text: str) -> str:
    """Normalize a few Markdown/Unicode characters for reliable PDF rendering."""
    replacements = {
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def inline_markdown(text: str) -> str:
    """Convert a minimal, safe Markdown subset into ReportLab Paragraph markup."""
    text = normalize_text(text)
    text = html.escape(text)

    # Inline code first so later substitutions do not touch it.
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)

    # Bold.
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)

    # Italic (minimal support).
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)

    return text


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="NexoTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            alignment=TA_CENTER,
            spaceAfter=7 * mm,
            textColor=colors.HexColor("#15233C"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            spaceAfter=4 * mm,
            textColor=colors.HexColor("#4B5563"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            textColor=colors.HexColor("#15233C"),
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoH3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
            textColor=colors.HexColor("#334155"),
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.8,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=2.7 * mm,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoBullet",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.8,
            leading=14,
            leftIndent=6 * mm,
            firstLineIndent=-3 * mm,
            spaceAfter=1.5 * mm,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            leftIndent=5 * mm,
            rightIndent=5 * mm,
            spaceAfter=1.5 * mm,
            textColor=colors.HexColor("#334155"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoNote",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.2,
            leading=13,
            leftIndent=5 * mm,
            rightIndent=5 * mm,
            borderColor=colors.HexColor("#CBD5E1"),
            borderWidth=0.7,
            borderPadding=5,
            backColor=colors.HexColor("#F8FAFC"),
            textColor=colors.HexColor("#334155"),
            spaceBefore=2 * mm,
            spaceAfter=4 * mm,
        )
    )

    return styles


def add_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4

    header = f"NexoDocs | {DOC_SHORT_NAME} | {DOC_ID} v{DOC_VERSION}"
    footer = f"Pagina {doc.page}"

    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, height - 14 * mm, width - 18 * mm, height - 14 * mm)
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(18 * mm, height - 10.5 * mm, header)

    footer_width = stringWidth(footer, "Helvetica", 7.5)
    canvas.drawString((width - footer_width) / 2, 8.5 * mm, footer)

    canvas.restoreState()


def markdown_to_story(markdown_text: str):
    styles = build_styles()
    story = []

    lines = markdown_text.splitlines()
    paragraph_buffer: list[str] = []
    seen_title = False
    metadata_block = True

    def flush_paragraph():
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        text = " ".join(part.strip() for part in paragraph_buffer if part.strip())
        paragraph_buffer = []
        if text:
            story.append(Paragraph(inline_markdown(text), styles["NexoBody"]))

    for raw in lines:
        line = raw.rstrip()

        if not line.strip():
            flush_paragraph()
            continue

        if line.strip() == "---":
            flush_paragraph()
            story.append(Spacer(1, 2 * mm))
            metadata_block = False
            continue

        if line.startswith("# "):
            flush_paragraph()
            if seen_title:
                story.append(PageBreak())
            story.append(Spacer(1, 8 * mm))
            story.append(Paragraph(inline_markdown(line[2:].strip()), styles["NexoTitle"]))
            seen_title = True
            continue

        if line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line[3:].strip()), styles["NexoH2"]))
            metadata_block = False
            continue

        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line[4:].strip()), styles["NexoH3"]))
            continue

        if line.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line[2:].strip()), styles["NexoNote"]))
            continue

        if line.startswith("- "):
            flush_paragraph()
            item = inline_markdown(line[2:].strip())
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{item}", styles["NexoBullet"]))
            continue

        # The document's metadata section uses Markdown bold labels such as
        # **Versão:** 1.0. Keep each metadata field on its own line.
        if metadata_block and re.match(r"^\*\*[^*]+:\*\*\s*", line):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line), styles["NexoMeta"]))
            continue

        paragraph_buffer.append(line)

    flush_paragraph()

    return story


def build_pdf(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {input_path}")

    markdown_text = input_path.read_text(encoding="utf-8")

    if not markdown_text.strip():
        raise ValueError("O arquivo Markdown esta vazio.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="NexoDocs - Manual Corporativo da Clinica Horizonte",
        author="NexoDocs - Challenge Alura Agentes",
        subject="Base de conhecimento corporativa ficticia para sistema RAG",
        creator="NexoDocs PDF Builder",
    )

    story = markdown_to_story(markdown_text)

    doc.build(
        story,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Gera o PDF pesquisavel da base de conhecimento NexoDocs.")
    parser.add_argument(
        "--input",
        default="knowledge-base/manual_corporativo_clinica_horizonte_v1.0.md",
        help="Caminho do Markdown de entrada.",
    )
    parser.add_argument(
        "--output",
        default="knowledge-base/manual_corporativo_clinica_horizonte_v1.0.pdf",
        help="Caminho do PDF de saida.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    build_pdf(input_path, output_path)

    print("PDF gerado com sucesso:")
    print(output_path.resolve())


if __name__ == "__main__":
    main()
