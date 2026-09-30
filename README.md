# Atividades complementares

Sistema para preencher o Anexo II da Universidade de Vassouras, Curso de Engenharia de Software.

## Para a turma

O formulário fica neste endereço, com o computador de origem desligado:

https://heliomattos.github.io/atividades-complementares/

Cada pessoa preenche nome, período, matrícula e data, e baixa o próprio PDF. Os dados não ficam gravados.

O PDF recebe apenas:

- nome
- período
- matrícula
- data

A rubrica, as horas e a assinatura ficam em branco. A faculdade lança as horas. A assinatura é feita pelo gov.br.

## Como abrir

Na pasta do projeto, com o Python instalado:

```bash
pip install -r requirements.txt
python app.py
```

Abra [http://127.0.0.1:43123](http://127.0.0.1:43123), preencha os quatro campos e baixe o PDF.

O formulário em branco fica em `modelo/Formulario_de_Atividades_Complementares.pdf`.
