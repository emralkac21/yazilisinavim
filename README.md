# 📄 Sınav Hazırlama ve Planlama Sistemi

Eğitimciler ve okul yönetimleri için tasarlanmış, sınav süreçlerini dijitalleştiren ve otomatikleştiren kapsamlı bir masaüstü uygulamasıdır. Öğrenci yönetimi, soru havuzu oluşturma, kişiselleştirilmiş sınav kitapçıkları (PDF) üretme ve ortak sınavlar için otomatik gözetmen/salon ataması yapma gibi işlemleri tek bir çatı altında toplar.

## ✨ Temel Özellikler

- **Öğrenci Yönetimi:** Öğrencileri manuel olarak ekleyin veya `.xlsx` (Excel) dosyalarından toplu olarak içe aktarın.
- **Soru Bankası:** Ders bazlı sorular (çoktan seçmeli veya klasik) oluşturun. Sorulara görsel ekleyin veya Excel'den toplu soru aktarımı yapın.
- **Otomatik PDF Sınav Kağıtları:** - Belirli bir dersten rastgele sorular çekin veya manuel soru seçimi yapın.
  - Sınava girecek öğrencileri seçin ve her öğrenci için adı, soyadı, sınıfı ve okul numarası yazılı özel filigranlı PDF sınav kağıtları oluşturun.
- **Ortak Sınav Planlama:** - Derslik kapasitelerini ve gözetmen öğretmenleri sisteme tanımlayın.
  - Sınava girecek sınıfları seçerek öğrencileri salonlara otomatik ve rastgele dağıtın.
  - Gözetmen imza sirkülerini barındıran PDF formatında yoklama tutanakları üretin.
- **Modern ve Karanlık Tema:** `CustomTkinter` ile geliştirilmiş, göz yormayan modern arayüz.

## 🛠️ Kullanılan Teknolojiler

- **Arayüz (GUI):** CustomTkinter & Tkinter
- **Veritabanı:** SQLite3 (`sinav_sistemi.db` olarak lokal çalışır)
- **Veri Analizi ve İçe Aktarım:** Pandas, OpenPyXL
- **PDF Üretimi:** ReportLab
<img width="1920" height="1080" alt="Screenshot_3" src="https://github.com/user-attachments/assets/a06a80d5-eff3-4664-8a21-53f4587911eb" />
<img width="1920" height="1080" alt="Screenshot_2" src="https://github.com/user-attachments/assets/ee4884a1-84fd-4a5e-9a3d-02811c4e60bc" />
<img width="1920" height="1080" alt="Screenshot_1" src="https://github.com/user-attachments/assets/bdb90d76-15f8-4178-ba20-5817f52a31ca" />
<img width="1920" height="1080" alt="Screenshot_5" src="https://github.com/user-attachments/assets/910fff96-1bb4-449c-b957-5c642cb5563d" />
<img width="1920" height="1080" alt="Screenshot_6" src="https://github.com/user-attachments/assets/45733bf4-515a-44a4-8a11-f4da9fb7028a" />
<img width="1920" height="1080" alt="Screenshot_4" src="https://github.com/user-attachments/assets/bf9ee246-3b10-45c9-a320-32f8f24a1c11" />
## ⚙️ Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için sisteminizde [Python 3.8+](https://www.python.org/) kurulu olmalıdır.

**1. Depoyu klonlayın:**
```bash
git clone [https://github.com/kullanici-adiniz/sinav-sistemi.git](https://github.com/kullanici-adiniz/yazilisinavi.git)
cd yazilisinavi


