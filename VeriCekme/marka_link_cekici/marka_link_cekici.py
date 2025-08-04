import requests 
from bs4 import BeautifulSoup
import time 
import re 

class MarkaLinkCekici():
    sade_url = "" 
    marka_linkleri = list() 
    marka_isimleri = list() 
    marka_sayilari = list() 
     
    @staticmethod   
    def __sayi_ayikla(metin: str) -> int: 
        araba_sayisi = int("".join(re.findall(r"\d+", metin))) 
        return araba_sayisi
    
    @staticmethod
    def __metin_ayikla(metin: str) -> str: 
        model = r"[A-Za-zÜüÖöİıŞşÇçĞğ\s-]+" 
        marka_ismi = "".join(re.findall(model, metin)).strip()
        return marka_ismi
    
    @staticmethod
    def __marka_linklerini_dosyaya_kaydet():
        with open("marka_linkleri.csv", "w", encoding="utf-8") as file:
            file.write("marka,adet,link\n")
            for isim, adet, link in zip(MarkaLinkCekici.marka_isimleri[1:], MarkaLinkCekici.marka_sayilari[1:], MarkaLinkCekici.marka_linkleri[1:]): 
                file.write(f"{isim},{adet},{link}\n")
                
        print("Kayıt Tamamlandı.")   
          
    @classmethod   
    def marka_linklerini_cek(cls, site_url: str):
        cls.sade_url = site_url[:re.search(".com", site_url).end()] 
        yanit = requests.get(site_url) 
        time.sleep(2) 
        html = BeautifulSoup(yanit.text, "html.parser") 
        div= html.find(class_="category-facet") 
        a_etiketleri = div.find_all("a") 
        
        for a in a_etiketleri:
            link = a.get("href") 
            metin = str(a.text.strip()) 
            isim = cls.__metin_ayikla(metin)
            adet = cls.__sayi_ayikla(metin)
            
            if link: 
                link = cls.sade_url + link
                cls.marka_isimleri.append(isim)
                cls.marka_sayilari.append(adet)
                cls.marka_linkleri.append(link)
                
        cls.__marka_linklerini_dosyaya_kaydet()
            