#!/usr/bin/env python3
"""
Build and validate a searchable PDF from the NexoDocs corporate knowledge-base Markdown.

Usage:
    py scripts\build_knowledge_pdf.py

Default input:
    knowledge-base/manual_corporativo_clinica_horizonte_v1.0.md

Default output:
    knowledge-base/manual_corporativo_clinica_horizonte_v1.0.pdf

The builder intentionally supports the Markdown subset used by the project:
- H1/H2/H3 headings
- bold and italic text
- unordered lists using "-", "*" or "+"
- Markdown links, including mailto links
- front-matter-style bold metadata labels
- paragraphs and blockquotes

After generation, the PDF is automatically validated with pypdf.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


DOC_ID = "CH-MAN-001"
DOC_VERSION = "1.0"
DOC_SHORT_NAME = "Manual Corporativo - Clínica Horizonte"

REQUIRED_TEXT_MARKERS = (
    "10 minutos",
    "24 horas",
    "Camila Ribeiro",
    "Regra de fonte de verdade",
)

FORBIDDEN_TEXT_MARKERS = (
    "mailto:",
    "](",
)


class DeterministicCanvas(pdf_canvas.Canvas):
    """Create byte-for-byte reproducible PDFs for the same source content."""

    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        super().__init__(*args, **kwargs)


def normalize_text(text: str) -> str:
    """Normalize punctuation that can cause inconsistent PDF rendering."""
    replacements = {
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
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
    """Convert the project's inline Markdown subset to ReportLab Paragraph markup."""
    text = normalize_text(text)

    # Protect Markdown links before HTML escaping.
    protected_links: list[tuple[str, str]] = []

    def protect_link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        url = html.escape(match.group(2), quote=True)
        token = f"@@NEXODOCS_LINK_{len(protected_links)}@@"
        markup = f'<link href="{url}" color="#1D4ED8">{label}</link>'
        protected_links.append((token, markup))
        return token

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", protect_link, text)

    # Escape user/source content before adding allowed ReportLab markup.
    text = html.escape(text)

    # Inline code.
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)

    # Bold before italic.
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)

    # Restore protected links as ReportLab markup.
    for token, markup in protected_links:
        text = text.replace(token, markup)

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
            spaceAfter=3 * mm,
            textColor=colors.HexColor("#15233C"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=5 * mm,
            textColor=colors.HexColor("#334155"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceBefore=5 * mm,
            spaceAfter=2.5 * mm,
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
            spaceBefore=3.5 * mm,
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
            firstLineIndent=-3.5 * mm,
            spaceAfter=1.4 * mm,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoFrontMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13,
            leftIndent=4 * mm,
            rightIndent=4 * mm,
            spaceAfter=1.1 * mm,
            textColor=colors.HexColor("#334155"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="NexoLabelLine",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.8,
            leading=14,
            spaceAfter=1.2 * mm,
            textColor=colors.HexColor("#111827"),
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
    footer = f"Página {doc.page}"

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
    front_matter = True
    h1_seen = False
    front_subtitle_seen = False

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
            # The first separator ends the document front matter. Later
            # separators are semantic Markdown separators and only add spacing.
            if front_matter:
                front_matter = False
                story.append(Spacer(1, 3 * mm))
            else:
                story.append(Spacer(1, 1.5 * mm))
            continue

        if line.startswith("# "):
            flush_paragraph()
            if h1_seen:
                story.append(Spacer(1, 4 * mm))
            else:
                story.append(Spacer(1, 8 * mm))
            story.append(Paragraph(inline_markdown(line[2:].strip()), styles["NexoTitle"]))
            h1_seen = True
            continue

        if line.startswith("## "):
            flush_paragraph()
            heading = line[3:].strip()
            if front_matter and not front_subtitle_seen:
                story.append(Paragraph(inline_markdown(heading), styles["NexoSubtitle"]))
                front_subtitle_seen = True
            else:
                story.append(Paragraph(inline_markdown(heading), styles["NexoH2"]))
            continue

        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line[4:].strip()), styles["NexoH3"]))
            continue

        if line.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line[2:].strip()), styles["NexoNote"]))
            continue

        # Support the unordered-list markers used by common Markdown formatters.
        bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", line)
        if bullet_match:
            flush_paragraph()
            item = inline_markdown(bullet_match.group(1).strip())
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{item}", styles["NexoBullet"]))
            continue

        # Keep label/value lines separate. This fixes front-matter metadata and
        # contact blocks such as **Responsável:** / **E-mail:** / **Ramal:**.
        if re.match(r"^\*\*[^*]+:\*\*\s*", line):
            flush_paragraph()
            style = styles["NexoFrontMeta"] if front_matter else styles["NexoLabelLine"]
            story.append(Paragraph(inline_markdown(line), style))
            continue

        paragraph_buffer.append(line)

    flush_paragraph()
    return story


def extract_pdf_text(pdf_path: Path) -> tuple[int, str]:
    reader = PdfReader(str(pdf_path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return len(reader.pages), text


def validate_pdf(pdf_path: Path) -> None:
    pages, text = extract_pdf_text(pdf_path)

    if pages < 1:
        raise RuntimeError("Validação falhou: o PDF não contém páginas.")

    if len(text.strip()) < 1000:
        raise RuntimeError(
            "Validação falhou: pouco texto foi extraído do PDF; ele pode não estar pesquisável."
        )

    missing = [marker for marker in REQUIRED_TEXT_MARKERS if marker not in text]
    if missing:
        raise RuntimeError(
            "Validação falhou: marcadores obrigatórios ausentes: " + ", ".join(missing)
        )

    forbidden = [marker for marker in FORBIDDEN_TEXT_MARKERS if marker in text]
    if forbidden:
        raise RuntimeError(
            "Validação falhou: artefatos de Markdown foram parar no PDF: "
            + ", ".join(forbidden)
        )

    print("Validação automática: PASS")
    print(f"Páginas: {pages}")
    print(f"Caracteres extraídos: {len(text)}")
    for marker in REQUIRED_TEXT_MARKERS:
        print(f"Marcador OK: {marker}")


def build_pdf(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")

    markdown_text = input_path.read_text(encoding="utf-8")
    if not markdown_text.strip():
        raise ValueError("O arquivo Markdown está vazio.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="NexoDocs - Manual Corporativo da Clínica Horizonte",
        author="NexoDocs - Challenge Alura Agentes",
        subject="Base de conhecimento corporativa fictícia para sistema RAG",
        creator="NexoDocs PDF Builder",
    )

    doc.build(
        markdown_to_story(markdown_text),
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer,
        canvasmaker=DeterministicCanvas,
    )

    validate_pdf(output_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gera e valida o PDF pesquisável da base de conhecimento NexoDocs."
    )
    parser.add_argument(
        "--input",
        default="knowledge-base/manual_corporativo_clinica_horizonte_v1.0.md",
        help="Caminho do Markdown de entrada.",
    )
    parser.add_argument(
        "--output",
        default="knowledge-base/manual_corporativo_clinica_horizonte_v1.0.pdf",
        help="Caminho do PDF de saída.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    build_pdf(input_path, output_path)

    print("PDF gerado e validado com sucesso:")
    print(output_path.resolve())


if __name__ == "__main__":
    main()
