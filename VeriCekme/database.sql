# USE araba_db;
CREATE TABLE araba_bilgileri (
id INT AUTO_INCREMENT PRIMARY KEY,
marka VARCHAR(50),
seri VARCHAR(50),
model VARCHAR(50),
yil INT,
kilometre INT,
vites_tipi VARCHAR(50),
yakit_tipi VARCHAR(50),
kasa_tipi VARCHAR(50),
renk VARCHAR(50),
motor_hacmi INT,
motor_gucu INT,
degisen_sayisi INT,
boyali_sayisi INT,
kimden VARCHAR(50),
fiyat INT
);