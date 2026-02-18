import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd 
import time 
import re
import mysql.connector

class ArabaOzellikleriTopla():
    def __init__(self, araba_linkleri_dosyasi):
        self.araba_linkleri_dosyasi = araba_linkleri_dosyasi
        self.araba_linkleri = pd.read_csv(self.araba_linkleri_dosyasi)
        self.oturum = None
        self.semafor = asyncio.Semaphore(40)
        self.oznitelik_haritasi = {
            "Marka":"marka",
            "Seri":"seri",
            "Model":"model",
            "Yıl":"yil",
            "Kilometre":"kilometre",
            "Vites Tipi":"vites_tipi",
            "Yakıt Tipi":"yakit_tipi",
            "Kasa Tipi":"kasa_tipi",
            "Renk":"renk",
            "Motor Hacmi":"motor_hacmi",
            "Motor Gücü":"motor_gucu",
            "Değişen Sayısı":"degisen_sayisi",
            "Boyalı Sayısı":"boyali_sayisi",
            "Kimden":"kimden",
            "Fiyat":"fiyat"
        }
        self.araba_oznitelik = list(self.oznitelik_haritasi.keys())
        self.basari_sayisi = 0  
        self.veritabani_baglanti = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mehmet123.",
            database="araba_db"
        )
        self.cursor = self.veritabani_baglanti.cursor() 
    
    
    async def baslat(self):
        baslangic_zamani = time.time()
        async with aiohttp.ClientSession() as oturum:
            self.oturum = oturum
            gorevler = []
            for _, seri in self.araba_linkleri.iterrows():
                link = seri["link"]
                gorevler.append(asyncio.create_task(self.__araba_detaylari_cek(link)))
                        
            await asyncio.gather(*gorevler)
         
        self.cursor.close()
        self.veritabani_baglanti.close()
         
        bitis_zamani = time.time()
        gecen_sure = bitis_zamani - baslangic_zamani
        print(f"İşlem tamamlandı. Geçen süre: {gecen_sure // 60} dakika.")
        print(f"Toplam başarılı çekilen ilan sayısı: {self.basari_sayisi}")
    
    
    @staticmethod
    def __motor_aralik_ortalama(metin: str) -> int:
        temiz_metin = metin.lower().replace("cm3", "")
        sayilar = list(map(int, re.findall(r"\d+", temiz_metin)))
        if len(sayilar) == 2:
            return (sayilar[0] + sayilar[1]) // 2
        elif len(sayilar) == 1:
            return sayilar[0]
        else:
            return None
    
    
    @staticmethod
    def __int_cevir(metin: str) -> int:
        if metin is None:
            return None
        sayilar = re.findall(r"\d+", metin.replace(".", ""))
        return int("".join(sayilar)) if sayilar else None
    
    
    @staticmethod
    def __boya_degisen_ayikla(metin: str) -> int:
        if "tamamı orjinal" in metin.lower():
            return 0, 0
        if "belirtilmemiş" in metin.lower():
            return None, None
        
        degisen = re.search(r"(\d+)\s*değişen", metin.lower())
        boyali = re.search(r"(\d+)\s*boyalı", metin.lower())
        
        degisen_sayisi = int(degisen.group(1)) if degisen else 0
        boyali_sayisi = int(boyali.group(1)) if boyali else 0
        
        return degisen_sayisi, boyali_sayisi 
        
    
    def __ozellikleri_ayikla(self, html) -> dict:
        fiyat_etiket = html.find("div", class_="desktop-information-price")
        fiyat = fiyat_etiket.text.strip() if fiyat_etiket else None
        
        ozellikler = {oznitelik: None for oznitelik in self.araba_oznitelik}
        ozellikler["Fiyat"] = ArabaOzellikleriTopla.__int_cevir(fiyat)
        
        ozellikler_div = html.find("div", class_="product-properties-details")
        if ozellikler_div:
            satirlar_div = ozellikler_div.find_all("div", class_="property-item")
            for satir in satirlar_div:
                key = satir.find("div", class_="property-key").text.strip()
                value = satir.find("div", class_="property-value").text.strip()
                    
                if key == "Boya-değişen":
                    degisen, boyali = ArabaOzellikleriTopla.__boya_degisen_ayikla(value)
                    ozellikler["Değişen Sayısı"] = degisen 
                    ozellikler["Boyalı Sayısı"] = boyali
                    
                elif key in ozellikler:
                    if key in ["Kilometre", "Yıl"]:
                        ozellikler[key] = ArabaOzellikleriTopla.__int_cevir(value)
                    
                    elif key in ["Motor Hacmi", "Motor Gücü"]:
                        ozellikler[key] = ArabaOzellikleriTopla.__motor_aralik_ortalama(value)
                        
                    else:
                        ozellikler[key] = value
                                
        return ozellikler
    
    def __veritabanina_ekle(self, ozellikler: dict):
        alanlar = list(self.oznitelik_haritasi.values())
        sql = f"""
        INSERT INTO araba_bilgileri ({",".join(alanlar)}) VALUES ({",".join(['%s'] * len(alanlar))})
        """
        degerler = [ozellikler.get(key, None) for key in self.araba_oznitelik]
        try:
            self.cursor.execute(sql, degerler)
            self.veritabani_baglanti.commit()
        except mysql.connector.Error as err:
            print(f"Veritabanı kaydında hata: {err}")
    
    async def __araba_detaylari_cek(self, url): 
        async with self.semafor:
            try:
                async with self.oturum.get(url, timeout=15) as response:
                    if response.status == 200: 
                        html_text = await response.text()
                        html = BeautifulSoup(html_text, "html.parser")
                        ozellikler = self.__ozellikleri_ayikla(html)
                        self.__veritabanina_ekle(ozellikler)
                        self.basari_sayisi += 1
                        del html_text, html
                    else:
                        print(f"{url} - Status: {response.status}")
                await asyncio.sleep(0.2)                   
            except Exception as e:
                print(f"{url} Hata: {e}")
                     