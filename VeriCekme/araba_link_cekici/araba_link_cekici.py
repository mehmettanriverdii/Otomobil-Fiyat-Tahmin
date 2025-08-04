import aiohttp 
import asyncio 
import pandas as pd 
from bs4 import BeautifulSoup 
import math  
import re 
import time

class ArabaLinkToplayici():
    def __init__(self, marka_dosyasi: str, site_url: str):
        self.marka_dosyasi = marka_dosyasi 
        self.site_url = site_url
        self.sade_url = self.site_url[:re.search(".com", self.site_url).end()] 
        self.sayfa_basi_url = 50 
        self.oturum = None 
        self.marka_linkleri = pd.read_csv(self.marka_dosyasi) 
        self.semafor = asyncio.Semaphore(40) 
        self.tum_linkler = list() 
        
       
    async def baslat(self): 
        baslangic_zamani = time.time() 
        async with aiohttp.ClientSession() as oturum: 
            self.oturum = oturum 
            gorevler = [] 
            
            for _, seri in self.marka_linkleri.iterrows(): 
                isim = seri["marka"]
                adet = seri["adet"]
                link = seri["link"]
                gorevler.append(asyncio.create_task(self.__marka_araba_linkleri_cek(isim, adet, link)))  
            await asyncio.gather(*gorevler) 
            
            with open("tum_araba_linkleri.csv", "w", encoding="utf-8") as file:
                file.write("link\n")
                for link in self.tum_linkler:
                    file.write(link + "\n")
                print(f"Toplam {len(self.tum_linkler)} araba linki kaydedildi.")

        bitis_zamani = time.time() 
        gecen_sure = bitis_zamani - baslangic_zamani
        print(f"İşlem tamamlandı. Yaklaşık olarak geçen süre: {(gecen_sure // 60) } dakika.")
    
    
    def __html_ayristir(self, html):
        satirlar = html.find_all("tr", class_="listing-list-item") 
        for satir in satirlar: 
            a = satir.find("a", class_="link-overlay")
            if a: 
                link = a.get("href") 
                if link: 
                    link = self.sade_url + link
                    self.tum_linkler.append(link)
        del satirlar, a 
                
          
    async def __marka_araba_linkleri_cek(self, marka_ismi: str, araba_adeti: int, marka_linki: str): 
        async with self.semafor: 
            if araba_adeti > 2500: 
                toplam_sayfa = 50 
            else:
                toplam_sayfa = math.ceil(araba_adeti / self.sayfa_basi_url)
            
            for sayfa in range(1, toplam_sayfa + 1):
                url = f"{marka_linki}?take=50&page={sayfa}"
                try:
                    async with self.oturum.get(url, timeout=15) as yanit: 
                        if yanit.status == 200: 
                            html_text = await yanit.text() 
                            html = BeautifulSoup(html_text, "html.parser") 
                            self.__html_ayristir(html)
                            del html_text, html 
                        else:
                            print(f"{marka_ismi} - {sayfa}. sayfa hatali. Status: {yanit.status}")
                    await asyncio.sleep(0.3) 
                except Exception as e:
                    print(f"{marka_ismi} - {sayfa}. sayfada hata: {e}")
                                                  