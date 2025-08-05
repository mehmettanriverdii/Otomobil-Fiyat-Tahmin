from marka_link_cekici import MarkaLinkCekici
from araba_link_cekici import ArabaLinkToplayici
from araba_ozellik_cekici import ArabaOzellikleriTopla
import asyncio
import mysql.connector
import pandas as pd


# Marka Link Cekimi
url = "https://www.arabam.com/ikinci-el/otomobil"
# MarkaLinkCekici.marka_linklerini_cek(url)


# Her bir markaya ait ilan link cekimi
# araba_link = ArabaLinkToplayici(marka_dosyasi="marka_linkleri.csv", site_url=url)
# asyncio.run(araba_link.baslat())


# Her bir markaya ait arabaların ozelliklerinin cekimi
# araba_ozellik = ArabaOzellikleriTopla(araba_linkleri_dosyasi="tum_araba_linkleri.csv")
# asyncio.run(araba_ozellik.baslat())

# baglanti = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="**********",
#     database="araba_db"
# )
# sorgu = "SELECT * FROM araba_bilgileri"
# veri = pd.read_sql(sorgu, con=baglanti)
# baglanti.close()
# veri.to_csv("araba_bilgileri.csv", index=False, encoding="utf-8")
