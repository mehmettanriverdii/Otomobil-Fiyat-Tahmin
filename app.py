import sys
import joblib
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import *

model = joblib.load("modeller/xgb_random.pkl")
kodlanmis = joblib.load("modeller/kodlanmis.pkl")
scaler = joblib.load("modeller/scaler.pkl")

df = pd.read_csv("temizlenmis_otomobil_verisi.csv")

def encode(kodlanmis, deger):
    return kodlanmis.transform([deger])[0] if deger in kodlanmis.classes_ else -1

class AracFiyatTahmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Araç Fiyat Tahmini")
        self.init_ui()

    def init_ui(self):
        self.resize(650, 300)  
    
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
    
        
        self.combo_marka = QComboBox()
        self.combo_seri = QComboBox()
        self.combo_model = QComboBox()
        self.combo_vites = QComboBox()
        self.combo_yakit = QComboBox()
        self.combo_kasa = QComboBox()
        self.combo_renk = QComboBox()
        self.combo_kimden = QComboBox()
    
        for cb in [self.combo_marka, self.combo_seri, self.combo_model,
                   self.combo_vites, self.combo_yakit, self.combo_kasa,
                   self.combo_renk, self.combo_kimden]:
            cb.setMinimumWidth(230)
    
        self.combo_marka.addItems(sorted(df["marka"].unique()))
        self.combo_marka.currentTextChanged.connect(self.guncelle_seri)
        self.combo_seri.currentTextChanged.connect(self.guncelle_model)
    
        self.combo_vites.addItems(kodlanmis["vites_tipi"].classes_)
        self.combo_yakit.addItems(kodlanmis["yakit_tipi"].classes_)
        self.combo_kasa.addItems(kodlanmis["kasa_tipi"].classes_)
        self.combo_renk.addItems(kodlanmis["renk"].classes_)
        self.combo_kimden.addItems(kodlanmis["kimden"].classes_)
    
        sol_widgetler = [
            ("Marka:", self.combo_marka),
            ("Seri:", self.combo_seri),
            ("Model:", self.combo_model),
            ("Vites Tipi:", self.combo_vites),
            ("Yakıt Tipi:", self.combo_yakit),
            ("Kasa Tipi:", self.combo_kasa),
            ("Renk:", self.combo_renk),
            ("Kimden:", self.combo_kimden)
        ]
    
        for i, (etiket, widget) in enumerate(sol_widgetler):
            grid.addWidget(QLabel(etiket), i, 0)
            grid.addWidget(widget, i, 1)
    
        
        self.yil_input = QLineEdit()
        self.km_input = QLineEdit()
        self.motor_hacmi_input = QLineEdit()
        self.motor_gucu_input = QLineEdit()
        self.degisen_sayisi_input = QLineEdit()
        self.boyali_sayisi_input = QLineEdit()
    
        sag_widgetler = [
            ("Yıl:", self.yil_input),
            ("Kilometre:", self.km_input),
            ("Motor Hacmi:", self.motor_hacmi_input),
            ("Motor Gücü:", self.motor_gucu_input),
            ("Değişen Sayısı:", self.degisen_sayisi_input),
            ("Boyalı Sayısı:", self.boyali_sayisi_input)
        ]
    
        for i, (etiket, widget) in enumerate(sag_widgetler):
            grid.addWidget(QLabel(etiket), i, 2)
            grid.addWidget(widget, i, 3)
    
        
        self.tahmin_button = QPushButton("Fiyat Tahmin Et")
        self.temizle_button = QPushButton("Temizle")
    
        self.tahmin_button.clicked.connect(self.tahmin_et)
        self.temizle_button.clicked.connect(self.temizle)
    
        buton_layout = QHBoxLayout()
        buton_layout.addWidget(self.tahmin_button)
        buton_layout.addWidget(self.temizle_button)
    
        ana_layout = QVBoxLayout()
        ana_layout.addLayout(grid)
        ana_layout.addLayout(buton_layout)
    
        self.setLayout(ana_layout)
        self.guncelle_seri(self.combo_marka.currentText())


    def guncelle_seri(self, secilen_marka):
        seriler = df[df["marka"] == secilen_marka]["seri"].unique()
        self.combo_seri.clear()
        self.combo_seri.addItems(sorted(seriler))
        self.guncelle_model()

    def guncelle_model(self):
        marka = self.combo_marka.currentText()
        seri = self.combo_seri.currentText()
        modeller = df[(df["marka"] == marka) & (df["seri"] == seri)]["model"].unique()
        self.combo_model.clear()
        self.combo_model.addItems(sorted(modeller))

    def tahmin_et(self):
        try:
            veri = [
                encode(kodlanmis["marka"], self.combo_marka.currentText()),
                encode(kodlanmis["seri"], self.combo_seri.currentText()),
                encode(kodlanmis["model"], self.combo_model.currentText()),
                int(self.yil_input.text()),
                int(self.km_input.text()),
                encode(kodlanmis["vites_tipi"], self.combo_vites.currentText()),
                encode(kodlanmis["yakit_tipi"], self.combo_yakit.currentText()),
                encode(kodlanmis["kasa_tipi"], self.combo_kasa.currentText()),
                encode(kodlanmis["renk"], self.combo_renk.currentText()),
                int(self.motor_hacmi_input.text()),
                int(self.motor_gucu_input.text()),
                int(self.degisen_sayisi_input.text()),
                int(self.boyali_sayisi_input.text()),
                encode(kodlanmis["kimden"], self.combo_kimden.currentText())
            ]
            veri_std = scaler.transform(np.array(veri).reshape(1, -1))
            tahmin = model.predict(veri_std)[0]
            QMessageBox.information(self, "Tahmini Fiyat", f"{int(tahmin):,} TL".replace(",", "."))
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Giriş hatası:\n{e}")
            
    def temizle(self):
        self.yil_input.clear()
        self.km_input.clear()
        self.motor_hacmi_input.clear()
        self.motor_gucu_input.clear()
        self.degisen_sayisi_input.clear()
        self.boyali_sayisi_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AracFiyatTahmin()
    pencere.show()
    sys.exit(app.exec_())
