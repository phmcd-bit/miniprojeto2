import pandas as pd
from scrape import parsear_mares, DIR_RAW

html = (DIR_RAW / "pagina_mares.html").read_text(encoding="utf-8")
linhas = parsear_mares(html, 2026, 10)

df = pd.DataFrame(linhas)
print(len(df), "linhas")
print(df.head(6))
print(df["tipo"].value_counts())
print(df["dia"].nunique(), "dias")