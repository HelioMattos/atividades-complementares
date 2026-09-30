#!/usr/bin/env python3
"""Gera o Anexo II só com identificação e data.

Preenche nome, período, matrícula e a data de Vassouras. A rubrica, as
horas e a assinatura ficam em branco: a faculdade lança as horas e a
assinatura é feita pelo gov.br.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent

INK = (0.05, 0.12, 0.38)

NAME_BASELINE = 315.2
MATRICULA_BASELINE = 331.4
NAME_X = 176.0
NAME_MAX_WIDTH = 236.0
PERIODO_BOX = (462.0, 508.0)
MATRICULA_X = 142.0
DATE_BLANKS = {
    "dia": (327.33, 349.33),
    "mes": (366.33, 460.67),
    "ano": (477.67, 510.67),
}
DATE_BASELINE = 294.2

MESES = (
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
)

FONTES = (
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
    r"C:\Windows\Fonts\timesbd.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "/Library/Fonts/Times New Roman Bold.ttf",
)


def encontrar_modelo() -> Path:
    nomes = (
        "Formulario_de_Atividades_Complementares.pdf",
        "Formulário de Atividades Complementares.pdf",
        "Formulário de Atividades Complementares (1).pdf",
    )
    for nome in nomes:
        for caminho in (ROOT / "modelo" / nome, ROOT / nome):
            if caminho.is_file():
                return caminho
    raise FileNotFoundError(
        "Coloque o PDF em branco em modelo/Formulario_de_Atividades_Complementares.pdf"
    )


def abrir_fonte(doc: pymupdf.Document) -> tuple[pymupdf.Font, str]:
    for caminho in FONTES:
        if Path(caminho).is_file():
            for pagina in doc:
                pagina.insert_font(fontname="form", fontfile=caminho)
            return pymupdf.Font(fontfile=caminho), "form"
    return pymupdf.Font("tibo"), "tibo"


def desenhar(page, fonte_nome: str, texto: str, x: float, baseline: float, tamanho: float) -> None:
    page.insert_text((x, baseline), texto, fontname=fonte_nome, fontsize=tamanho, color=INK)


def desenhar_centralizado(page, fonte, fonte_nome, texto, x0, x1, baseline, tamanho) -> None:
    largura = fonte.text_length(texto, fontsize=tamanho)
    desenhar(page, fonte_nome, texto, x0 + (x1 - x0 - largura) / 2, baseline, tamanho)


def tamanho_que_cabe(fonte: pymupdf.Font, texto: str, largura_maxima: float, tamanho: float = 11) -> float:
    while tamanho > 7 and fonte.text_length(texto, fontsize=tamanho) > largura_maxima:
        tamanho -= 0.5
    return tamanho


def nome_arquivo(nome: str) -> str:
    base = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_")
    return base or "aluno"


def gerar_pdf(dados: dict) -> bytes:
    """dados: nome, periodo (ex. 8º), matricula, data {dia, mes, ano}."""
    doc = pymupdf.open(encontrar_modelo())
    fonte, fonte_nome = abrir_fonte(doc)
    pagina1, pagina2 = doc[0], doc[1]

    nome = dados["nome"].strip().upper()
    tamanho_nome = tamanho_que_cabe(fonte, nome, NAME_MAX_WIDTH)
    desenhar(pagina1, fonte_nome, nome, NAME_X, NAME_BASELINE, tamanho_nome)
    desenhar_centralizado(pagina1, fonte, fonte_nome, dados["periodo"], *PERIODO_BOX, NAME_BASELINE, 11)
    desenhar(pagina1, fonte_nome, dados["matricula"], MATRICULA_X, MATRICULA_BASELINE, 11)

    for chave in ("dia", "mes", "ano"):
        desenhar_centralizado(
            pagina2,
            fonte,
            fonte_nome,
            dados["data"][chave],
            *DATE_BLANKS[chave],
            DATE_BASELINE,
            11,
        )

    pdf = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return pdf
