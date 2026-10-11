import time
from scrape import DIR_RAW, PAUSA, URL_ONDAS, URL_VENTO, baixar_html

DIR_RAW.mkdir(parents=True, exist_ok=True)

html_ondas = baixar_html(URL_ONDAS)
(DIR_RAW / "pagina_ondas.html").write_text(html_ondas, encoding="utf-8")
print("ondas:", len(html_ondas))

time.sleep(PAUSA)

html_vento = baixar_html(URL_VENTO)
(DIR_RAW / "pagina_vento.html").write_text(html_vento, encoding="utf-8")
print("vento:", len(html_vento))
