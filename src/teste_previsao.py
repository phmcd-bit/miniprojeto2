import pandas as pd

from scrape import DIR_RAW, parsear_previsao

for nome in ("ondas", "vento"):
    html = (DIR_RAW / f"pagina_{nome}.html").read_text(encoding="utf-8")
    linhas = parsear_previsao(html, 2026)
    df = pd.DataFrame(linhas)

    print(f"\n=== {nome} ===")
    print(len(df), "linhas")
    print(df.head(6))
    print(df.groupby(["mes", "dia"]).ngroups, "dias distintos")
    print("valor min/max:", df["valor"].min(), df["valor"].max())
    print("horas por dia:", df.groupby(["mes", "dia"]).size().unique())