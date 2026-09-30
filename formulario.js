const MESES = [
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
];

const INK = PDFLib.rgb(0.05, 0.12, 0.38);
const NAME_BASELINE = 315.2;
const MATRICULA_BASELINE = 331.4;
const NAME_X = 176.0;
const NAME_MAX_WIDTH = 236.0;
const PERIODO_BOX = [462.0, 508.0];
const MATRICULA_X = 142.0;
const DATE_BLANKS = {
  dia: [327.33, 349.33],
  mes: [366.33, 460.67],
  ano: [477.67, 510.67],
};
const DATE_BASELINE = 294.2;

const formulario = document.querySelector("#formulario");
const caixaErros = document.querySelector("#erros");
const botao = document.querySelector("#gerar");
const campoData = formulario.elements.data;

campoData.value = hojeLocal();

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const dados = lerDados();
  const erros = validar(dados);
  if (erros.length) {
    mostrarErros(erros);
    return;
  }

  botao.disabled = true;
  botao.textContent = "Gerando PDF...";
  mostrarErros([]);
  try {
    await baixarPdf(dados);
  } catch (erro) {
    console.error(erro);
    mostrarErros(["Não foi possível gerar o PDF. Tente de novo."]);
  } finally {
    botao.disabled = false;
    botao.textContent = "Gerar PDF";
  }
});

function hojeLocal() {
  const agora = new Date();
  const mes = String(agora.getMonth() + 1).padStart(2, "0");
  const dia = String(agora.getDate()).padStart(2, "0");
  return `${agora.getFullYear()}-${mes}-${dia}`;
}

function lerDados() {
  return {
    nome: formulario.elements.nome.value.trim(),
    periodo: formulario.elements.periodo.value.trim(),
    matricula: formulario.elements.matricula.value.replace(/\D/g, ""),
    data: formulario.elements.data.value.trim(),
  };
}

function validar(dados) {
  const erros = [];
  if (dados.nome.length < 5) erros.push("Informe o nome completo.");
  if (!/^(?:[1-9]|10)$/.test(dados.periodo)) erros.push("Escolha o período.");
  if (!/^\d{6,12}$/.test(dados.matricula)) erros.push("A matrícula precisa ter de 6 a 12 números.");
  if (!dataValida(dados.data)) erros.push("Informe uma data válida.");
  return erros;
}

function dataValida(iso) {
  const partes = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!partes) return false;
  const ano = Number(partes[1]);
  const mes = Number(partes[2]);
  const dia = Number(partes[3]);
  const data = new Date(ano, mes - 1, dia);
  return data.getFullYear() === ano && data.getMonth() === mes - 1 && data.getDate() === dia;
}

function mostrarErros(erros) {
  caixaErros.replaceChildren();
  if (!erros.length) {
    caixaErros.hidden = true;
    return;
  }
  for (const erro of erros) {
    const linha = document.createElement("p");
    linha.textContent = erro;
    caixaErros.append(linha);
  }
  caixaErros.hidden = false;
}

async function baixarPdf(dados) {
  const [ano, mes, dia] = dados.data.split("-").map(Number);
  const resposta = await fetch("modelo/Formulario_de_Atividades_Complementares.pdf");
  if (!resposta.ok) throw new Error("Modelo do PDF indisponível.");

  const pdf = await PDFLib.PDFDocument.load(await resposta.arrayBuffer());
  const fonte = await pdf.embedFont(PDFLib.StandardFonts.TimesRomanBold);
  const [pagina1, pagina2] = pdf.getPages();
  const nome = dados.nome.toUpperCase();
  const tamanhoNome = tamanhoQueCabe(fonte, nome, NAME_MAX_WIDTH);

  desenhar(pagina1, fonte, nome, NAME_X, NAME_BASELINE, tamanhoNome);
  desenharCentralizado(pagina1, fonte, `${dados.periodo}º`, PERIODO_BOX[0], PERIODO_BOX[1], NAME_BASELINE, 11);
  desenhar(pagina1, fonte, dados.matricula, MATRICULA_X, MATRICULA_BASELINE, 11);
  desenharCentralizado(pagina2, fonte, String(dia), ...DATE_BLANKS.dia, DATE_BASELINE, 11);
  desenharCentralizado(pagina2, fonte, MESES[mes - 1], ...DATE_BLANKS.mes, DATE_BASELINE, 11);
  desenharCentralizado(pagina2, fonte, String(ano), ...DATE_BLANKS.ano, DATE_BASELINE, 11);

  const bytes = await pdf.save();
  const arquivo = `Formulario_${nomeArquivo(dados.nome)}.pdf`;
  const url = URL.createObjectURL(new Blob([bytes], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = arquivo;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function desenhar(page, fonte, texto, x, baseline, tamanho) {
  page.drawText(texto, {
    x,
    // A fonte padrão do PDF fica 1,7 pt acima da linha do formulário.
    y: page.getHeight() - baseline - 1.7,
    size: tamanho,
    font: fonte,
    color: INK,
  });
}

function desenharCentralizado(page, fonte, texto, x0, x1, baseline, tamanho) {
  const largura = fonte.widthOfTextAtSize(texto, tamanho);
  desenhar(page, fonte, texto, x0 + (x1 - x0 - largura) / 2, baseline, tamanho);
}

function tamanhoQueCabe(fonte, texto, larguraMaxima, tamanho = 11) {
  while (tamanho > 7 && fonte.widthOfTextAtSize(texto, tamanho) > larguraMaxima) {
    tamanho -= 0.5;
  }
  return tamanho;
}

function nomeArquivo(nome) {
  const base = nome
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^A-Za-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return base || "aluno";
}
