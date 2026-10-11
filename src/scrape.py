"""
Etapa 1 — coleta de dados de tabuademares.com/br/paraiba/joao-pessoa.

Objetivo: gravar em data/raw/ os CSVs que as Etapas 2 e 3 vão consumir.

    mares_<ano>.csv      tábua de marés do ano (4 marés por dia)
    mares_previsao.csv   marés do mês corrente, para cruzar com a previsão
    ondas.csv            altura de onda hora a hora (~7 dias à frente)
    vento.csv            velocidade do vento hora a hora (~7 dias à frente)

As funções abaixo estão vazias de propósito. Abra o site no navegador, use o
DevTools para descobrir onde cada dado vive no HTML e implemente o parse.
As colunas de cada CSV são sua decisão — só precisam sustentar as etapas
seguintes (ver README).

Rodar com: uv run python src/scrape.py
"""

import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Os imports acima são o ponto de partida: você vai usar todos eles.
# Seu editor pode marcá-los como não usados até você preencher as funções.

URL_BASE = "https://tabuademares.com/br/paraiba/joao-pessoa"
URL_ONDAS = f"{URL_BASE}/previsao/ondas"
URL_VENTO = f"{URL_BASE}/previsao/vento"

# Servidores rejeitam clientes sem User-Agent. Identifique-se.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Segundos de pausa entre requests. Não tire isso.
PAUSA = 1.5

DIR_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def baixar_html(url: str, dados_post: dict | None = None) -> str:
    """Baixa uma página e devolve o HTML.

    Use POST (passando `dados_post`) quando a página só devolver o conteúdo
    que você quer em resposta a um formulário; GET no resto.

    TODO: fazer a requisição com `requests`, checar o status e devolver o texto.
    Dica: `resp.raise_for_status()` falha alto quando o servidor recusa.
    """
    if dados_post is None:
        resp = requests.get(url, headers=HEADERS)
    else:
        resp = requests.post(url, headers=HEADERS, data=dados_post)

    resp.raise_for_status()
    return resp.text

def parsear_mares(html: str, ano: int, mes: int) -> list[dict]:
    """Extrai da tábua mensal uma linha por evento de maré.

    Cada dia tem cerca de 4 eventos (duas altas, duas baixas). Além de
    horário e altura, a página traz informação de coeficiente de maré e de
    fase da lua — decida o que vale a pena capturar.

    TODO: localizar a tabela no HTML e percorrer as linhas.
    """

    soup = BeautifulSoup(html, "html.parser")
    tabela = soup.select_one("table:has(tr.tabla_mareas_fila)")

    linhas = []
    for tr in tabela.select("tr:has(td.tabla_mareas_dia)"):
        dia = int(tr.select_one("td.tabla_mareas_dia").get_text(" ", strip=True).split()[0])
        nascer, por = (
            tr.select_one("td.tabla_mareas_salida_puesta_sol")
            .get_text(" ", strip=True)
            .split()
        )
        coeficiente = int(
            tr.select_one("td.tabla_mareas_coeficiente").get_text(" ", strip=True).split()[0]
        )

        for td in tr.select("td.tabla_mareas_marea"):
            div_hora = td.select_one("div.tabla_mareas_marea_hora")
            if div_hora is None or not div_hora.get_text(strip=True):
                continue  

            altura = td.select_one("span.tabla_mareas_marea_altura_numero")
            tipo = "baixa" if "tabla_mareas_hora_bajamar" in div_hora["class"] else "alta"

            linhas.append({
                "ano": ano,
                "mes": mes,
                "dia": dia,
                "hora": div_hora.get_text(strip=True),
                "altura": float(altura.get_text(strip=True).replace(",", ".")),
                "tipo": tipo,
                "coeficiente": coeficiente,
                "nascer_sol": nascer,
                "por_sol": por,
            })

    return linhas

def parsear_previsao(html: str, ano: int) -> list[dict]:
    """Extrai leituras horárias das páginas de previsão de onda e de vento.

    As duas páginas têm o mesmo layout: um bloco por dia, com uma linha por
    hora dentro. Uma função só deve dar conta das duas.

    TODO: percorrer os blocos de dia e, dentro deles, as linhas de hora.
    Atenção à data: o bloco mostra dia e mês abreviado, sem o ano.
    """

    soup = BeautifulSoup(html, "html.parser")
    blocos_dia = soup.select("div.ficha")  # ADAPTAÇÃO: bloco do dia

    linhas = []
    ano_atual = ano
    mes_anterior = None
    for bloco in blocos_dia:
        
        dia = bloco.select_one("span.dia").get_text(strip=True)
        mes_abrev = bloco.select_one("span.mes").get_text(strip=True)
        mes = {
            "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
            "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
        }[mes_abrev.lower()]

        if mes_anterior is not None and mes < mes_anterior:
            ano_atual += 1
        mes_anterior = mes

        for tr in bloco.select("div.f_temp_horas"):  
            celulas = tr.select("div.f_temp_hora")
            hora = celulas[0].get_text(strip=True)
            direcao = celulas[1].get_text(strip=True)

            valor = tr.select_one("div.grafico_temp_barra_relleno").get_text(" ", strip=True).split()[0]

            linhas.append({
                "ano": ano_atual,
                "mes": mes,
                "dia": int(dia),
                "hora": hora,
                "direcao": direcao,  
                "valor": float(valor.replace(",", ".")),
            })

    return linhas


def coletar_mares_do_ano(ano: int) -> pd.DataFrame:
    """Junta os 12 meses da tábua de marés de `ano` num DataFrame.

    TODO: iterar de janeiro a dezembro, chamar `baixar_html` + `parsear_mares`
    e dormir `PAUSA` entre requisições.
    """
    raise NotImplementedError


def main(ano: int = 2025) -> None:
    DIR_RAW.mkdir(parents=True, exist_ok=True)
    hoje = datetime.now()

    # TODO: montar os quatro CSVs em DIR_RAW.
    #
    #   1. tábua de marés do ano inteiro   -> mares_{ano}.csv
    #   2. marés do mês corrente           -> mares_previsao.csv
    #   3. previsão de ondas               -> ondas.csv
    #   4. previsão de vento               -> vento.csv
    #
    # Imprima quantas linhas cada arquivo recebeu: um CSV vazio é o erro mais
    # comum e o mais silencioso.
    raise NotImplementedError


if __name__ == "__main__":
    main()
