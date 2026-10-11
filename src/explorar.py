from bs4 import BeautifulSoup
from scrape import DIR_RAW

html = (DIR_RAW / "pagina_mares.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

tabelas = soup.select("table:has(tr.tabla_mareas_fila)")

for i, t in enumerate(tabelas):
    titulo = t.find_previous(["h1", "h2", "h3"])
    linhas = [tr for tr in t.select("tr") if tr.get_text(strip=True)]
    print(f"\n=== tabela {i} | titulo antes dela:",
          titulo.get_text(" ", strip=True) if titulo else None)
    for tr in linhas[:3] + linhas[-1:]:
        print("  ", tr.get_text(" ", strip=True)[:80])

# como sao por dentro a celula da lua e a primeira celula de mare
linha = tabelas[0].select_one("tr:has(div.tabla_mareas_marea_hora)")
print("\nLUA:", linha.select_one("td.tabla_mareas_luna"))
print("\nMARE:", linha.select_one("td.tabla_mareas_marea"))