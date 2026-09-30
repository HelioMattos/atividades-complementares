#!/usr/bin/env python3
"""Sistema para preencher nome, período, matrícula e data no Anexo II."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from preencher_formulario import MESES, gerar_pdf, nome_arquivo

ROOT = Path(__file__).resolve().parent
ZIP_TURMA = ROOT / "atividades-complementares-para-turma.zip"
app = FastAPI(title="Atividades complementares")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")

PERIODOS = list(range(1, 11))


def pagina(request: Request, dados: dict, erros: list[str], status: int = 200):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "dados": dados,
            "erros": erros,
            "periodos": PERIODOS,
            "hoje": date.today().isoformat(),
        },
        status_code=status,
    )


@app.get("/baixar-sistema")
def baixar_sistema():
    if not ZIP_TURMA.is_file():
        return HTMLResponse("O arquivo ZIP não está nesta pasta.", status_code=404)
    return FileResponse(
        ZIP_TURMA,
        media_type="application/zip",
        filename="atividades-complementares-para-turma.zip",
    )


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return pagina(request, {"nome": "", "periodo": "", "matricula": "", "data": date.today().isoformat()}, [])


@app.post("/gerar")
def gerar(
    request: Request,
    nome: str = Form(""),
    periodo: str = Form(""),
    matricula: str = Form(""),
    data: str = Form(""),
):
    dados = {
        "nome": nome.strip(),
        "periodo": periodo.strip(),
        "matricula": re.sub(r"\D", "", matricula),
        "data": data.strip(),
    }
    erros = validar(dados)
    if erros:
        return pagina(request, dados, erros, status=400)

    ano, mes, dia = (int(parte) for parte in dados["data"].split("-"))
    pdf = gerar_pdf(
        {
            "nome": dados["nome"],
            "periodo": f"{dados['periodo']}º",
            "matricula": dados["matricula"],
            "data": {"dia": str(dia), "mes": MESES[mes - 1], "ano": str(ano)},
        }
    )
    arquivo = f"Formulario_{nome_arquivo(dados['nome'])}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{arquivo}"'},
    )


def validar(dados: dict) -> list[str]:
    erros = []
    if len(dados["nome"]) < 5:
        erros.append("Informe o nome completo.")
    if dados["periodo"] not in {str(numero) for numero in PERIODOS}:
        erros.append("Escolha o período.")
    if not dados["matricula"].isdigit() or not 6 <= len(dados["matricula"]) <= 12:
        erros.append("A matrícula precisa ter de 6 a 12 números.")
    try:
        ano, mes, dia = (int(parte) for parte in dados["data"].split("-"))
        date(ano, mes, dia)
    except ValueError:
        erros.append("Informe uma data válida.")
    return erros


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=43123, reload=False)
