import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
import pandas as pd
import shutil
import uuid
import random

# --- CustomTkinter Tema Ayarları ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Renk Paleti ---
SIDEBAR_BG     = "#1e2a3a"
SIDEBAR_BTN    = "#2d3f55"
SIDEBAR_HOVER  = "#3b82f6"
HEADER_BG      = "#1e293b"
MAIN_BG        = "#0f172a"
CARD_BG        = "#1e293b"
ACCENT_GREEN   = "#22c55e"
ACCENT_ORANGE  = "#f97316"
ACCENT_RED     = "#ef4444"
ACCENT_BLUE    = "#3b82f6"
ACCENT_TEAL    = "#14b8a6"
ACCENT_PURPLE  = "#a855f7"
ACCENT_CRIMSON = "#dc2626"
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
ENTRY_BG       = "#334155"
ENTRY_BORDER   = "#475569"

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    FONT_NAME = 'DejaVuSans'
except:
    print("Uyarı: 'DejaVuSans.ttf' fontu bulunamadı.")
    FONT_NAME = 'Helvetica'



class ExamSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sınav Hazırlama ve Planlama Sistemi")
        self.root.geometry("1350x780")

        # --- GÜVENLİ İKON YÜKLEME ---
        # Dosyanın tam yolunu oluşturuyoruz
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "sinav.ico")

        if os.path.exists(icon_path):
            try:
                # Bazı Windows sürümlerinde wm_iconbitmap daha kararlı çalışır
                self.root.after(200, lambda: self.root.wm_iconbitmap(icon_path))
            except Exception as e:
                print(f"İkon yükleme hatası: {e}")
        else:
            print("Uyarı: sinav.ico dosyası bulunamadı.")
        # ----------------------------

        self.root.configure(bg=MAIN_BG)
        self.image_folder = 'images'
        os.makedirs(self.image_folder, exist_ok=True)

        self.selected_question_ids = []
        self.selected_student_ids = []

        self.init_database()
        self.create_sidebar()
        self.create_main_area()
        self.show_students_module()
       

    # ─────────────────────────────── VERİTABANI ───────────────────────────────
    def init_database(self):
        self.conn = sqlite3.connect('sinav_sistemi.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ogrenciler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                sinif TEXT NOT NULL,
                ogrenci_no TEXT UNIQUE NOT NULL
            )
        ''')
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sorular (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ders_adi TEXT NOT NULL,
                    soru_baslik TEXT NOT NULL,
                    soru_tipi TEXT NOT NULL,
                    secenek_a TEXT, secenek_b TEXT, secenek_c TEXT,
                    secenek_d TEXT, secenek_e TEXT,
                    soru_gorsel_yolu TEXT
                )
            ''')
        except sqlite3.OperationalError:
            try:
                self.cursor.execute("ALTER TABLE sorular ADD COLUMN soru_gorsel_yolu TEXT")
            except sqlite3.OperationalError:
                pass
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ogretmenler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT NOT NULL UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS derslikler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                derslik_adi TEXT NOT NULL UNIQUE,
                kapasite INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    # ─────────────────────────────── SIDEBAR ──────────────────────────────────
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0,
                                    fg_color=SIDEBAR_BG)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo alanı
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="#16213e", corner_radius=0)
        logo_frame.pack(fill="x")
        ctk.CTkLabel(logo_frame, text="📄 SINAV SİSTEMİ",
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=22)

        # Menü butonları
        self._menu_buttons = []
        menus = [
            ("👨‍🎓  Öğrenciler",   self.show_students_module),
            ("📝  Sorular",        self.show_questions_module),
            ("📄  Sınav Oluştur",  self.show_exam_module),
            ("📅  Sınav Planlama", self.show_planning_module),
        ]
        for text, cmd in menus:
            self.create_menu_button(self.sidebar, text, cmd)
            
        
        ctk.CTkLabel(self.sidebar, text="V 1.1",
                     font=ctk.CTkFont(size=10),
                     text_color=TEXT_SECONDARY).pack(side="bottom", pady=2)
        ctk.CTkLabel(self.sidebar, text="Geliştirici: Emrullah ALKAÇ", 
                     font=ctk.CTkFont(size=12), 
                     text_color=TEXT_PRIMARY).pack(side="bottom", pady=2)

    def create_menu_button(self, parent, text, command):
        btn = ctk.CTkButton(
            parent, text=text, command=command,
            anchor="w",
            fg_color=SIDEBAR_BTN,
            hover_color=SIDEBAR_HOVER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Arial", size=13),
            corner_radius=8,
            height=44,
        )
        btn.pack(fill="x", padx=12, pady=4)
        self._menu_buttons.append(btn)
        return btn

    # ─────────────────────────────── ANA ALAN ─────────────────────────────────
    def create_main_area(self):
        self.main_area = ctk.CTkFrame(self.root, corner_radius=0, fg_color=MAIN_BG)
        self.main_area.pack(side="left", fill="both", expand=True)

    def clear_main_area(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def create_header(self, text, color):
        header = ctk.CTkFrame(self.main_area, fg_color=color, corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=text,
                     font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                     text_color="white").pack(pady=16)
        return header

    # ─────────────────────────── ÖĞRENCI MODÜLÜ ───────────────────────────────
    def show_students_module(self):
        self.clear_main_area()
        self.create_header("Öğrenci Yönetimi", ACCENT_ORANGE)

        content = ctk.CTkFrame(self.main_area, fg_color=MAIN_BG)
        content.pack(fill="both", expand=True, padx=20, pady=15)

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        self._ctk_btn(btn_frame, "➕ Yeni Öğrenci Ekle",   self.open_student_form,           ACCENT_GREEN)
        self._ctk_btn(btn_frame, "📥 Excel'den İçe Aktar", self.import_students_from_excel,  ACCENT_TEAL)
        self._ctk_btn(btn_frame, "✏️ Güncelle",             self.open_student_form_for_edit,  ACCENT_ORANGE)
        self._ctk_btn(btn_frame, "🗑️ Sil",                  self.delete_student,              ACCENT_RED)

        list_frame = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=10)
        list_frame.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(list_frame, text="📄 Kayıtlı Öğrenciler",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(10, 4))

        columns = ('ID', 'Ad', 'Soyad', 'Sınıf', 'Öğrenci No')
        self.students_tree = self._make_treeview(list_frame, columns)
        self.students_tree.column('ID', width=55)
        self.students_tree.bind('<Double-1>', lambda e: self.open_student_form_for_edit())
        self.load_students()

    def load_students(self):
        self.clear_treeview(self.students_tree)
        self.cursor.execute('SELECT * FROM ogrenciler ORDER BY sinif, ad')
        for row in self.cursor.fetchall():
            self.students_tree.insert('', 'end', values=row)

    def open_student_form(self, student_data=None):
        win = self._make_toplevel("Öğrenci Formu" if not student_data else "Öğrenciyi Düzenle", "420x340")
        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=20)

        fields = [("Ad:", "ad"), ("Soyad:", "soyad"), ("Sınıf:", "sinif"), ("Öğrenci No:", "ogrenci_no")]
        entries = {}
        for i, (lbl, key) in enumerate(fields):
            ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=12),
                         text_color=TEXT_PRIMARY).grid(row=i, column=0, sticky="w", pady=8, padx=5)
            e = ctk.CTkEntry(frame, width=240, fg_color=ENTRY_BG,
                             border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
            e.grid(row=i, column=1, pady=8, padx=5)
            if student_data:
                e.insert(0, student_data.get(key, ''))
            entries[key] = e

        save_btn = ctk.CTkButton(frame, text="Kaydet", fg_color=ACCENT_GREEN,
                                 hover_color="#16a34a", font=ctk.CTkFont(weight="bold"))
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=18)
        if student_data:
            save_btn.configure(command=lambda: self.update_student(student_data['id'], entries, win))
        else:
            save_btn.configure(command=lambda: self.add_student(entries, win))

    def open_student_form_for_edit(self):
        selected = self.get_selected_item(self.students_tree)
        if not selected: return
        student_id, ad, soyad, sinif, ogrenci_no = selected['values']
        self.open_student_form({'id': student_id, 'ad': ad, 'soyad': soyad, 'sinif': sinif, 'ogrenci_no': ogrenci_no})

    def add_student(self, entries, window):
        data = {key: e.get().strip() for key, e in entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!", parent=window)
            return
        try:
            self.cursor.execute('INSERT INTO ogrenciler (ad, soyad, sinif, ogrenci_no) VALUES (?, ?, ?, ?)', tuple(data.values()))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Öğrenci başarıyla eklendi!")
            window.destroy()
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu öğrenci numarası zaten kayıtlı!", parent=window)

    def update_student(self, student_id, entries, window):
        data = {key: e.get().strip() for key, e in entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!", parent=window)
            return
        try:
            self.cursor.execute('UPDATE ogrenciler SET ad=?, soyad=?, sinif=?, ogrenci_no=? WHERE id=?',
                                (data['ad'], data['soyad'], data['sinif'], data['ogrenci_no'], student_id))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Öğrenci başarıyla güncellendi!")
            window.destroy()
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu öğrenci numarası başka birine ait!", parent=window)

    def delete_student(self):
        selected = self.get_selected_item(self.students_tree)
        if not selected: return
        if messagebox.askyesno("Onay", "Seçili öğrenci silinecek. Emin misiniz?"):
            self.cursor.execute('DELETE FROM ogrenciler WHERE id = ?', (selected['values'][0],))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Öğrenci silindi!")
            self.load_students()

    def import_students_from_excel(self):
        filepath = filedialog.askopenfilename(title="Öğrenci Excel Dosyasını Seçin",
                                              filetypes=[("Excel Dosyaları", "*.xlsx")])
        if not filepath: return
        try:
            df = pd.read_excel(filepath)
            required_cols = {'Ad', 'Soyad', 'Sınıf', 'OgrenciNo'}
            if not required_cols.issubset(df.columns):
                messagebox.showerror("Hata", f"Gerekli sütunlar bulunamadı!\n{', '.join(required_cols)}")
                return
            success_count = fail_count = 0
            for _, row in df.iterrows():
                try:
                    self.cursor.execute('INSERT INTO ogrenciler (ad, soyad, sinif, ogrenci_no) VALUES (?, ?, ?, ?)',
                                        (row['Ad'], row['Soyad'], row['Sınıf'], str(row['OgrenciNo'])))
                    success_count += 1
                except sqlite3.IntegrityError:
                    fail_count += 1
            self.conn.commit()
            messagebox.showinfo("İşlem Tamamlandı",
                                f"{success_count} öğrenci aktarıldı.\n{fail_count} kayıt atlandı.")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Hata", f"Excel okunurken hata: {e}")

    # ──────────────────────────── SORU MODÜLÜ ─────────────────────────────────
    def show_questions_module(self):
        self.clear_main_area()
        self.create_header("Soru Bankası", ACCENT_TEAL)

        content = ctk.CTkFrame(self.main_area, fg_color=MAIN_BG)
        content.pack(fill="both", expand=True, padx=20, pady=15)

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        self._ctk_btn(btn_frame, "➕ Yeni Soru Ekle",        self.open_question_form,           ACCENT_GREEN)
        self._ctk_btn(btn_frame, "📥 Excel'den İçe Aktar",   self.import_questions_from_excel,  ACCENT_TEAL)
        self._ctk_btn(btn_frame, "✏️ Seçili Soruyu Güncelle", self.open_question_form_for_edit,  ACCENT_ORANGE)
        self._ctk_btn(btn_frame, "🗑️ Seçili Soruyu Sil",     self.delete_question,              ACCENT_RED)

        list_frame = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=10)
        list_frame.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(list_frame, text="Kayıtlı Sorular",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(10, 4))

        columns = ('ID', 'Ders', 'Soru', 'Tip', 'Görsel')
        self.questions_tree = self._make_treeview(list_frame, columns)
        self.questions_tree.column('ID', width=50, anchor='center')
        self.questions_tree.column('Ders', width=150)
        self.questions_tree.column('Soru', width=400)
        self.questions_tree.column('Tip', width=120)
        self.questions_tree.column('Görsel', width=60, anchor='center')
        self.questions_tree.bind('<Double-1>', lambda e: self.open_question_form_for_edit())
        self.load_questions()

    def load_questions(self):
        self.clear_treeview(self.questions_tree)
        self.cursor.execute('SELECT id, ders_adi, soru_baslik, soru_tipi, soru_gorsel_yolu FROM sorular ORDER BY ders_adi')
        for row in self.cursor.fetchall():
            id_, ders, baslik, tip, gorsel = row
            kisalt = baslik[:70].replace('\n', ' ') + '...' if len(baslik) > 70 else baslik.replace('\n', ' ')
            self.questions_tree.insert('', 'end', values=(id_, ders, kisalt, tip, "✓" if gorsel else ""))

    def open_question_form(self, question_data=None):
        win = self._make_toplevel("Soru Formu" if not question_data else "Soruyu Düzenle", "600x620")
        content = ctk.CTkFrame(win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(content, text="Ders Adı:", text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=6)
        q_ders = ctk.CTkEntry(content, width=400, fg_color=ENTRY_BG,
                              border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
        q_ders.grid(row=0, column=1, pady=6)

        ctk.CTkLabel(content, text="📝 Soru:", text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="nw", pady=6)
        q_baslik = ctk.CTkTextbox(content, width=400, height=200,
                                   fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                   text_color=TEXT_PRIMARY)
        q_baslik.grid(row=1, column=1, pady=6)

        ctk.CTkLabel(content, text="Soru Tipi:", text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=6)
        q_tip = ctk.CTkComboBox(content, values=['Çoktan Seçmeli', 'Klasik'],
                                 state='readonly', width=200,
                                 fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                 button_color=ACCENT_BLUE, text_color=TEXT_PRIMARY)
        q_tip.grid(row=2, column=1, pady=6, sticky="w")
        q_tip.set('Çoktan Seçmeli')

        # Şıklar
        option_frame = ctk.CTkFrame(content, fg_color="transparent")
        option_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=8)
        q_secenekler = {}
        for i, label in enumerate(['A', 'B', 'C', 'D', 'E']):
            ctk.CTkLabel(option_frame, text=f"{label})", text_color=TEXT_PRIMARY,
                         font=ctk.CTkFont(size=12)).grid(row=i, column=0, sticky="w", pady=3)
            e = ctk.CTkEntry(option_frame, width=360, fg_color=ENTRY_BG,
                              border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
            e.grid(row=i, column=1, pady=3, padx=10)
            q_secenekler[label] = e

        # Görsel seçimi
        image_path_var = ctk.StringVar(value=question_data.get('soru_gorsel_yolu', '') if question_data else "")
        ctk.CTkLabel(content, text="Görsel:", text_color=TEXT_PRIMARY,
                     font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w", pady=8)
        img_ctrl = ctk.CTkFrame(content, fg_color="transparent")
        img_ctrl.grid(row=4, column=1, sticky="w", pady=8)
        gorsel_label = ctk.CTkLabel(img_ctrl, text="Görsel seçilmedi",
                                    text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=11, slant="italic"))
        gorsel_label.pack(side="left", padx=(0, 10))
        if image_path_var.get():
            gorsel_label.configure(text=os.path.basename(image_path_var.get()), text_color=ACCENT_BLUE)

        def select_image():
            fp = filedialog.askopenfilename(title="Görsel Seç", filetypes=[("Resim", "*.jpg *.png *.jpeg")])
            if not fp: return
            fn = f"{uuid.uuid4()}{os.path.splitext(fp)[1]}"
            np_ = os.path.join(self.image_folder, fn)
            shutil.copy(fp, np_)
            image_path_var.set(np_)
            gorsel_label.configure(text=os.path.basename(np_), text_color=ACCENT_BLUE)

        def remove_image():
            image_path_var.set("")
            gorsel_label.configure(text="Görsel seçilmedi", text_color=TEXT_SECONDARY)

        ctk.CTkButton(img_ctrl, text="Görsel Ekle/Değiştir", command=select_image,
                      fg_color=ACCENT_BLUE, hover_color="#2563eb", width=160).pack(side="left", padx=(0, 5))
        ctk.CTkButton(img_ctrl, text="Görseli Kaldır", command=remove_image,
                      fg_color=ACCENT_RED, hover_color="#b91c1c", width=120).pack(side="left")

        def toggle_options(choice=None):
            if q_tip.get() == 'Çoktan Seçmeli':
                option_frame.grid()
            else:
                option_frame.grid_remove()

        q_tip.configure(command=toggle_options)

        if question_data:
            q_ders.insert(0, question_data['ders_adi'])
            q_baslik.insert('1.0', question_data['soru_baslik'])
            q_tip.set(question_data['soru_tipi'])
            if question_data['soru_tipi'] == 'Çoktan Seçmeli':
                for key, val in q_secenekler.items():
                    val.insert(0, question_data.get(f'secenek_{key.lower()}', '') or '')
        toggle_options()

        entries = {'ders': q_ders, 'baslik': q_baslik, 'tip': q_tip,
                   'secenekler': q_secenekler, 'gorsel_yol': image_path_var}
        save_btn = ctk.CTkButton(content, text="Kaydet", fg_color=ACCENT_GREEN,
                                  hover_color="#16a34a", font=ctk.CTkFont(weight="bold"), width=160)
        save_btn.grid(row=5, column=1, sticky="e", pady=16)
        if question_data:
            save_btn.configure(command=lambda: self.update_question(question_data['id'], entries, win))
        else:
            save_btn.configure(command=lambda: self.add_question(entries, win))

    def open_question_form_for_edit(self):
        selected = self.get_selected_item(self.questions_tree)
        if not selected: return
        question_id = selected['values'][0]
        self.cursor.execute('SELECT * FROM sorular WHERE id = ?', (question_id,))
        q_raw = self.cursor.fetchone()
        if not q_raw: return
        col_names = [desc[0] for desc in self.cursor.description]
        self.open_question_form(dict(zip(col_names, q_raw)))

    def add_question(self, entries, window):
        ders = entries['ders'].get().strip()
        baslik = entries['baslik'].get('1.0', 'end').strip()
        tip = entries['tip'].get()
        gorsel_yol = entries['gorsel_yol'].get().strip() or None
        if not all([ders, baslik]):
            messagebox.showwarning("Uyarı", "Lütfen ders adı ve soruyu girin!", parent=window)
            return
        secenekler = {k: v.get().strip() for k, v in entries['secenekler'].items()}
        if tip == 'Çoktan Seçmeli' and not any(secenekler.values()):
            messagebox.showwarning("Uyarı", "En az bir seçenek doldurulmalıdır!", parent=window)
            return
        self.cursor.execute('''INSERT INTO sorular (ders_adi, soru_baslik, soru_tipi,
            secenek_a, secenek_b, secenek_c, secenek_d, secenek_e, soru_gorsel_yolu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (ders, baslik, tip, secenekler['A'], secenekler['B'], secenekler['C'],
             secenekler['D'], secenekler['E'], gorsel_yol))
        self.conn.commit()
        messagebox.showinfo("Başarılı", "Soru başarıyla eklendi!")
        window.destroy()
        self.load_questions()

    def update_question(self, question_id, entries, window):
        ders = entries['ders'].get().strip()
        baslik = entries['baslik'].get('1.0', 'end').strip()
        tip = entries['tip'].get()
        gorsel_yol = entries['gorsel_yol'].get().strip() or None
        if not all([ders, baslik]):
            messagebox.showwarning("Uyarı", "Lütfen ders adı ve soruyu girin!", parent=window)
            return
        secenekler = {k: v.get().strip() for k, v in entries['secenekler'].items()}
        if tip != 'Çoktan Seçmeli':
            secenekler = {k: None for k in ['A', 'B', 'C', 'D', 'E']}
        self.cursor.execute('''UPDATE sorular SET ders_adi=?, soru_baslik=?, soru_tipi=?,
            secenek_a=?, secenek_b=?, secenek_c=?, secenek_d=?, secenek_e=?, soru_gorsel_yolu=?
            WHERE id=?''',
            (ders, baslik, tip, secenekler['A'], secenekler['B'], secenekler['C'],
             secenekler['D'], secenekler['E'], gorsel_yol, question_id))
        self.conn.commit()
        messagebox.showinfo("Başarılı", "Soru başarıyla güncellendi!")
        window.destroy()
        self.load_questions()

    def delete_question(self):
        selected = self.get_selected_item(self.questions_tree)
        if not selected: return
        if messagebox.askyesno("Onay", "Seçili soru silinecek. Emin misiniz?"):
            self.cursor.execute('DELETE FROM sorular WHERE id = ?', (selected['values'][0],))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Soru silindi!")
            self.load_questions()

    def import_questions_from_excel(self):
        filepath = filedialog.askopenfilename(title="Soru Excel Dosyasını Seçin",
                                              filetypes=[("Excel Dosyaları", "*.xlsx")])
        if not filepath: return
        try:
            df = pd.read_excel(filepath).fillna('')
            required_cols = {'DersAdi', 'SoruBaslik', 'SoruTipi'}
            if not required_cols.issubset(df.columns):
                messagebox.showerror("Hata", f"Gerekli sütunlar bulunamadı!\n{', '.join(required_cols)}")
                return
            count = 0
            for _, row in df.iterrows():
                sec_a = row.get('SecenekA', ''); sec_b = row.get('SecenekB', '')
                sec_c = row.get('SecenekC', ''); sec_d = row.get('SecenekD', '')
                sec_e = row.get('SecenekE', '')
                self.cursor.execute('''INSERT INTO sorular (ders_adi, soru_baslik, soru_tipi,
                    secenek_a, secenek_b, secenek_c, secenek_d, secenek_e, soru_gorsel_yolu)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (row['DersAdi'], row['SoruBaslik'], row['SoruTipi'],
                     sec_a, sec_b, sec_c, sec_d, sec_e, None))
                count += 1
            self.conn.commit()
            messagebox.showinfo("İşlem Tamamlandı", f"{count} soru içe aktarıldı.")
            self.load_questions()
        except Exception as e:
            messagebox.showerror("Hata", f"Excel okunurken hata: {e}")

    # ────────────────────────── SINAV OLUŞTUR MODÜLÜ ──────────────────────────
    def show_exam_module(self):
        self.clear_main_area()
        self.create_header("Sınav Kağıdı Oluştur", ACCENT_PURPLE)

        content = ctk.CTkFrame(self.main_area, fg_color=MAIN_BG)
        content.pack(fill="both", expand=True, padx=20, pady=15)

        form_card = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=10)
        form_card.pack(fill="x", pady=8, padx=2)

        ctk.CTkLabel(form_card, text="Sınav Bilgileri",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, columnspan=4,
                                                   sticky="w", padx=18, pady=(14, 6))

        def lbl(txt, row, col):
            ctk.CTkLabel(form_card, text=txt, text_color=TEXT_SECONDARY,
                         font=ctk.CTkFont(size=12)).grid(row=row, column=col,
                                                          sticky="w", pady=7, padx=(18, 6))

        def ent(row, col, width=400, colspan=3):
            e = ctk.CTkEntry(form_card, width=width, fg_color=ENTRY_BG,
                              border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
            e.grid(row=row, column=col, pady=7, padx=(0, 18), columnspan=colspan)
            return e

        lbl("Okul Adı:", 1, 0);    self.exam_okul     = ent(1, 1)
        lbl("Öğretmen:", 2, 0);    self.exam_ogretmen = ent(2, 1)
        lbl("Ders:", 3, 0)
        self.cursor.execute('SELECT DISTINCT ders_adi FROM sorular')
        dersler = [r[0] for r in self.cursor.fetchall()]
        self.exam_ders = ctk.CTkComboBox(form_card, values=dersler, state='readonly', width=260,
                                          fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                          button_color=ACCENT_BLUE, text_color=TEXT_PRIMARY)
        self.exam_ders.grid(row=3, column=1, pady=7, padx=(0, 18), sticky="w")
        if dersler: self.exam_ders.set(dersler[0])

        lbl("Soru Sayısı:", 4, 0)
        self.soru_sayisi_var = ctk.IntVar(value=1)
        spin_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        spin_frame.grid(row=4, column=1, sticky="w", pady=7)
        from tkinter import Spinbox as TkSpinbox
        self.exam_soru_sayisi = TkSpinbox(spin_frame, from_=1, to=50, width=8,
                                           font=('Arial', 12),
                                           bg=ENTRY_BG, fg=TEXT_PRIMARY,
                                           textvariable=self.soru_sayisi_var,
                                           buttonbackground="#475569")
        self.exam_soru_sayisi.pack(side="left")
        self.selected_q_label = ctk.CTkLabel(spin_frame,
                                              text=f"Seçili Sorular: {len(self.selected_question_ids)}",
                                              text_color=ACCENT_BLUE,
                                              font=ctk.CTkFont(size=12, weight="bold"))
        self.selected_q_label.pack(side="left", padx=14)

        def on_ders_change(choice):
            self.selected_question_ids = []
            self.update_selected_q_label()
        self.exam_ders.configure(command=on_ders_change)

        ctk.CTkButton(form_card, text="📝 Soru Seçimi Yap",
                      command=self.open_select_questions_window,
                      fg_color=ACCENT_BLUE, hover_color="#2563eb",
                      font=ctk.CTkFont(weight="bold"), width=200,
                      ).grid(row=5, column=0, columnspan=2, pady=(10, 4), padx=18, sticky="w")

        lbl("Öğrenci Seçimi:", 6, 0)
        self.selected_s_label = ctk.CTkLabel(form_card,
                                              text=f"Seçili Öğrenciler: {len(self.selected_student_ids)}",
                                              text_color=ACCENT_BLUE,
                                              font=ctk.CTkFont(size=12, weight="bold"))
        self.selected_s_label.grid(row=6, column=1, sticky="w")

        ctk.CTkButton(form_card, text="🧑‍🎓 Öğrenci Seçimi Yap",
                      command=self.open_select_students_window,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a",
                      font=ctk.CTkFont(weight="bold"), width=220,
                      ).grid(row=7, column=0, columnspan=2, pady=(4, 10), padx=18, sticky="w")

        ctk.CTkButton(form_card, text="📄 Yazılı Oluştur",
                      command=self.create_exam_pdf,
                      fg_color=ACCENT_ORANGE, hover_color="#ea580c",
                      font=ctk.CTkFont(size=14, weight="bold"), height=44, width=240,
                      ).grid(row=8, column=0, columnspan=4, pady=18)

        self.update_selected_q_label()
        self.update_selected_s_label()

    def update_selected_q_label(self):
        count = len(self.selected_question_ids)
        self.selected_q_label.configure(text=f"Seçili Soru: {count}")
        if count > 0:
            self.exam_soru_sayisi.configure(state='disabled')
            self.soru_sayisi_var.set(count)
        else:
            self.exam_soru_sayisi.configure(state='normal')

    def update_selected_s_label(self):
        count = len(self.selected_student_ids)
        if count == 0:
            self.selected_s_label.configure(text="Seçili Öğrenci: Tüm Öğrenciler")
        else:
            self.selected_s_label.configure(text=f"Seçili Öğrenci: {count}")

    def open_select_students_window(self):
        win = self._make_toplevel("Sınava Dahil Edilecek Öğrencileri Seç", "620x620")
        hdr = ctk.CTkFrame(win, fg_color="#34495e", corner_radius=0, height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="Öğrenci Seçimi",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(pady=12)

        list_frame = ctk.CTkFrame(win, fg_color=CARD_BG, corner_radius=8)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ('Seç', 'ID', 'Ad Soyad', 'Sınıf', 'Öğrenci No')
        tree = self._make_treeview(list_frame, columns)
        tree.column('Seç', width=40, anchor='center')
        tree.column('ID', width=50, anchor='center')
        tree.column('Ad Soyad', width=200)
        tree.column('Sınıf', width=80, anchor='center')
        tree.column('Öğrenci No', width=100, anchor='center')

        self.cursor.execute('SELECT id, ad, soyad, sinif, ogrenci_no FROM ogrenciler ORDER BY sinif, ad')
        students_data = self.cursor.fetchall()
        s_selection = {}
        for s_id, ad, soyad, sinif, ogr_no in students_data:
            is_sel = s_id in self.selected_student_ids
            s_selection[s_id] = is_sel
            tag = "selected" if is_sel else "unselected"
            tree.insert('', 'end', iid=s_id,
                        values=("✓" if is_sel else "○", s_id, f"{ad} {soyad}", sinif, ogr_no),
                        tags=(tag,))
        tree.tag_configure('selected', background='#1d4ed8')

        def toggle(event):
            item = tree.focus()
            if not item: return
            s_id = int(item)
            new_sel = not s_selection.get(s_id, False)
            s_selection[s_id] = new_sel
            vals = list(tree.item(item, 'values'))
            vals[0] = "✓" if new_sel else "○"
            tree.item(item, values=tuple(vals), tags=("selected" if new_sel else "unselected",))
        tree.bind('<ButtonRelease-1>', toggle)

        def save_selection():
            self.selected_student_ids = [s_id for s_id, sel in s_selection.items() if sel]
            self.update_selected_s_label()
            messagebox.showinfo("Başarılı", f"{len(self.selected_student_ids)} öğrenci eklendi.", parent=win)
            win.destroy()

        ctk.CTkButton(win, text="Seçimi Kaydet ve Kapat", command=save_selection,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a",
                      font=ctk.CTkFont(weight="bold"), height=40
                      ).pack(side="right", padx=14, pady=10)

    def open_select_questions_window(self):
        ders_adi = self.exam_ders.get()
        if not ders_adi:
            messagebox.showwarning("Uyarı", "Lütfen önce bir ders seçin!")
            return
        win = self._make_toplevel(f"{ders_adi} Sorularını Seç", "820x620")
        hdr = ctk.CTkFrame(win, fg_color="#34495e", corner_radius=0, height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"Ders: {ders_adi} — Soru Seçimi",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(pady=12)

        list_frame = ctk.CTkFrame(win, fg_color=CARD_BG, corner_radius=8)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ('Seç', 'ID', 'Soru Başlığı', 'Tip', 'Görsel')
        tree = self._make_treeview(list_frame, columns)
        tree.column('Seç', width=40, anchor='center')
        tree.column('ID', width=50, anchor='center')
        tree.column('Soru Başlığı', width=500)
        tree.column('Tip', width=80, anchor='center')
        tree.column('Görsel', width=50, anchor='center')

        self.cursor.execute('SELECT id, soru_baslik, soru_tipi, soru_gorsel_yolu FROM sorular WHERE ders_adi = ?', (ders_adi,))
        questions_data = self.cursor.fetchall()
        q_selection = {}
        for q_id, baslik, tip, gorsel in questions_data:
            is_sel = q_id in self.selected_question_ids
            q_selection[q_id] = is_sel
            kisalt = baslik[:70].replace('\n', ' ') + '...' if len(baslik) > 70 else baslik.replace('\n', ' ')
            tag = "selected" if is_sel else "unselected"
            tree.insert('', 'end', iid=q_id,
                        values=("✓" if is_sel else "○", q_id, kisalt, tip, "✓" if gorsel else ""),
                        tags=(tag,))
        tree.tag_configure('selected', background='#1d4ed8')

        def toggle(event):
            item = tree.focus()
            if not item: return
            q_id = int(item)
            new_sel = not q_selection.get(q_id, False)
            q_selection[q_id] = new_sel
            vals = list(tree.item(item, 'values'))
            vals[0] = "✓" if new_sel else "○"
            tree.item(item, values=tuple(vals), tags=("selected" if new_sel else "unselected",))
        tree.bind('<ButtonRelease-1>', toggle)

        def save_selection():
            self.selected_question_ids = [q_id for q_id, sel in q_selection.items() if sel]
            self.update_selected_q_label()
            messagebox.showinfo("Başarılı", f"{len(self.selected_question_ids)} soru seçildi.", parent=win)
            win.destroy()

        ctk.CTkButton(win, text="Seçimi Kaydet ve Kapat", command=save_selection,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a",
                      font=ctk.CTkFont(weight="bold"), height=40
                      ).pack(side="right", padx=14, pady=10)

    def create_exam_pdf(self):
        okul = self.exam_okul.get().strip()
        ogretmen = self.exam_ogretmen.get().strip()
        ders = self.exam_ders.get()
        soru_sayisi_str = self.exam_soru_sayisi.get()
        if not all([okul, ogretmen, ders]):
            messagebox.showwarning("Uyarı", "Lütfen Okul Adı, Öğretmen ve Ders alanlarını doldurun!")
            return
        if self.selected_student_ids:
            ph = ', '.join('?' * len(self.selected_student_ids))
            self.cursor.execute(f'SELECT * FROM ogrenciler WHERE id IN ({ph}) ORDER BY sinif, ad',
                                self.selected_student_ids)
        else:
            self.cursor.execute('SELECT * FROM ogrenciler')
        ogrenciler = self.cursor.fetchall()
        if not ogrenciler:
            messagebox.showwarning("Uyarı", "Sistemde kayıtlı veya seçili öğrenci yok!")
            return
        sorular_raw = []
        if self.selected_question_ids:
            ph = ', '.join('?' * len(self.selected_question_ids))
            self.cursor.execute(f'SELECT * FROM sorular WHERE id IN ({ph}) ORDER BY id',
                                self.selected_question_ids)
            sorular_raw = self.cursor.fetchall()
            soru_sayisi = len(sorular_raw)
        else:
            try:
                soru_sayisi = int(soru_sayisi_str)
            except ValueError:
                messagebox.showwarning("Uyarı", "Soru Sayısı geçerli bir sayı olmalıdır.")
                return
            self.cursor.execute('SELECT * FROM sorular WHERE ders_adi = ? ORDER BY RANDOM() LIMIT ?',
                                (ders, soru_sayisi))
            sorular_raw = self.cursor.fetchall()
            if len(sorular_raw) < soru_sayisi:
                messagebox.showwarning("Uyarı", f"Yeterli soru yok! (Mevcut: {len(sorular_raw)})")
                return
        folder = filedialog.askdirectory(title="PDF'lerin Kaydedileceği Klasörü Seçin")
        if not folder: return
        try:
            for ogr in ogrenciler:
                fn = os.path.join(folder, f"Sinav_{ogr[1]}_{ogr[2]}_{ogr[4]}.pdf")
                self.generate_single_pdf(fn, ogr, okul, ogretmen, ders, sorular_raw)
            messagebox.showinfo("Başarılı", f"{len(ogrenciler)} öğrenci için PDF oluşturuldu!\n{soru_sayisi} soru kullanıldı.")
            self.selected_question_ids = []
            self.selected_student_ids = []
            self.update_selected_q_label()
            self.update_selected_s_label()
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulurken hata: {e}")

    # ──────────────────────── SINAV PLANLAMA MODÜLÜ ───────────────────────────
    def show_planning_module(self):
        self.clear_main_area()
        self.create_header("Ortak Sınav Derslik ve Gözetmen Atama", ACCENT_CRIMSON)

        container = ctk.CTkFrame(self.main_area, fg_color=MAIN_BG)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        # 3 sütunlu grid
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, weight=2)
        container.rowconfigure(0, weight=1)

        # ── Öğretmenler ──
        t_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10)
        t_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(t_card, text="Gözetmen Öğretmenler",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=12, pady=(12, 4))
        self.teacher_tree = self._make_treeview(t_card, ('ID', 'Ad Soyad'), height=16)
        self.teacher_tree.column('ID', width=40, anchor='center')
        self.load_teachers()
        btn_row = ctk.CTkFrame(t_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(btn_row, text="➕ Ekle", command=self.add_teacher,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a", width=100).pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkButton(btn_row, text="🗑️ Sil", command=self.delete_teacher,
                      fg_color=ACCENT_RED, hover_color="#b91c1c", width=100).pack(side="left", expand=True, fill="x", padx=2)

        # ── Derslikler ──
        c_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10)
        c_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(c_card, text="Derslikler",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=12, pady=(12, 4))
        self.classroom_tree = self._make_treeview(c_card, ('ID', 'Derslik Adı', 'Kapasite'), height=16)
        self.classroom_tree.column('ID', width=40, anchor='center')
        self.classroom_tree.column('Kapasite', width=70, anchor='center')
        self.load_classrooms()
        btn_row2 = ctk.CTkFrame(c_card, fg_color="transparent")
        btn_row2.pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(btn_row2, text="➕ Ekle", command=self.add_classroom,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a", width=100).pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkButton(btn_row2, text="🗑️ Sil", command=self.delete_classroom,
                      fg_color=ACCENT_RED, hover_color="#b91c1c", width=100).pack(side="left", expand=True, fill="x", padx=2)

        # ── Planlama Formu ──
        p_card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10)
        p_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(p_card, text="Planlama Yap",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, columnspan=2,
                                                   sticky="w", padx=18, pady=(14, 6))

        def flbl(txt, row):
            ctk.CTkLabel(p_card, text=txt, text_color=TEXT_SECONDARY,
                         font=ctk.CTkFont(size=12)).grid(row=row, column=0, sticky="w",
                                                          pady=10, padx=18)
        def fent(row):
            e = ctk.CTkEntry(p_card, width=260, fg_color=ENTRY_BG,
                              border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
            e.grid(row=row, column=1, pady=10, padx=(0, 18))
            return e

        flbl("Sınav Adı:", 1);        self.plan_sinav_adi = fent(1)
        flbl("Sınıf Seviyesi:", 2)
        self.plan_sinif_seviyesi = ctk.CTkComboBox(
            p_card, values=["Tüm Öğrenciler", "9. Sınıflar", "10. Sınıflar", "11. Sınıflar", "12. Sınıflar"],
            state='readonly', width=260,
            fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
            button_color=ACCENT_BLUE, text_color=TEXT_PRIMARY)
        self.plan_sinif_seviyesi.grid(row=2, column=1, pady=10, padx=(0, 18))
        self.plan_sinif_seviyesi.set("9. Sınıflar")

        flbl("Tarih (GG.AA.YYYY):", 3); self.plan_tarih = fent(3)
        self.plan_tarih.insert(0, datetime.now().strftime('%d.%m.%Y'))
        flbl("Saat (SS:DD):", 4);       self.plan_saat = fent(4)
        self.plan_saat.insert(0, "10:00")

        ctk.CTkButton(p_card, text="📊 Planla ve PDF'e Aktar",
                      command=self.create_exam_plan,
                      fg_color=ACCENT_PURPLE, hover_color="#9333ea",
                      font=ctk.CTkFont(size=13, weight="bold"), height=44, width=280,
                      ).grid(row=5, column=0, columnspan=2, pady=28)

    def create_exam_plan(self):
        sinav_adi = self.plan_sinav_adi.get().strip()
        seviye = self.plan_sinif_seviyesi.get()
        tarih = self.plan_tarih.get().strip()
        saat = self.plan_saat.get().strip()
        if not all([sinav_adi, seviye, tarih, saat]):
            messagebox.showwarning("Uyarı", "Lütfen planlama formundaki tüm alanları doldurun!")
            return
        if seviye == "Tüm Öğrenciler":
            self.cursor.execute('SELECT * FROM ogrenciler')
        else:
            sinif_no = seviye.split('.')[0]
            self.cursor.execute('SELECT * FROM ogrenciler WHERE sinif LIKE ?', (f'{sinif_no}%',))
        ogrenciler = self.cursor.fetchall()
        self.cursor.execute('SELECT * FROM derslikler ORDER BY derslik_adi')
        derslikler = self.cursor.fetchall()
        self.cursor.execute('SELECT * FROM ogretmenler')
        ogretmenler = self.cursor.fetchall()
        if not ogrenciler:
            messagebox.showerror("Hata", f"'{seviye}' için öğrenci bulunamadı.")
            return
        if not derslikler:
            messagebox.showerror("Hata", "Sistemde derslik yok!")
            return
        if not ogretmenler:
            messagebox.showerror("Hata", "Sistemde gözetmen yok!")
            return
        toplam_kapasite = sum(d[2] for d in derslikler)
        if toplam_kapasite < len(ogrenciler):
            messagebox.showerror("Hata", f"Kapasite yetersiz!\nÖğrenci: {len(ogrenciler)} / Kapasite: {toplam_kapasite}")
            return
        if len(derslikler) > len(ogretmenler):
            messagebox.showwarning("Uyarı", f"Yeterli gözetmen yok! Bazı derslikler boş kalacak.")
        random.shuffle(list(ogrenciler)); ogrenciler = list(ogrenciler)
        random.shuffle(ogrenciler)
        ogretmenler = list(ogretmenler); random.shuffle(ogretmenler)
        atama_plani = {}
        ogrenci_index = 0
        for derslik in derslikler:
            did, dad, kap = derslik
            atama_plani[did] = {'bilgi': derslik, 'ogrenciler': [], 'ogretmen': None}
            for _ in range(kap):
                if ogrenci_index < len(ogrenciler):
                    atama_plani[did]['ogrenciler'].append(ogrenciler[ogrenci_index])
                    ogrenci_index += 1
                else:
                    break
        for i, did in enumerate(atama_plani):
            if i < len(ogretmenler):
                atama_plani[did]['ogretmen'] = ogretmenler[i]
        self.generate_assignment_pdf(atama_plani, sinav_adi, tarih, saat)

    def generate_assignment_pdf(self, atama_plani, sinav_adi, tarih, saat):
        filename = filedialog.asksaveasfilename(
            title="Atama Planı PDF'ini Kaydet",
            defaultextension=".pdf",
            filetypes=[("PDF Dosyaları", "*.pdf")],
            initialfile=f"{sinav_adi.replace(' ', '_')}_Atama_Listesi.pdf")
        if not filename: return
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
        story = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CT', parent=styles['h1'], fontName=FONT_NAME, fontSize=14, alignment=TA_CENTER, spaceAfter=8)
        cell_style  = ParagraphStyle('CS', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10)
        for i, (derslik_id, data) in enumerate(atama_plani.items()):
            derslik_bilgi = data['bilgi']
            ogrenciler    = data['ogrenciler']
            ogretmen      = data['ogretmen']
            if not ogrenciler: continue
            story.append(Paragraph(sinav_adi, title_style))
            story.append(Paragraph("Sınav Yoklama ve Gözetmen Tutanağı", styles['h2']))
            story.append(Spacer(1, 0.5*cm))
            goz_adi = ogretmen[1] if ogretmen else "ATANMADI"
            header_data = [
                [Paragraph('<b>Sınav Tarihi/Saati:</b>', cell_style), Paragraph(f'{tarih} - {saat}', cell_style),
                 Paragraph('<b>Derslik:</b>', cell_style),            Paragraph(f'<b>{derslik_bilgi[1]}</b>', cell_style)],
                [Paragraph('<b>Gözetmen Öğretmen:</b>', cell_style),  Paragraph(goz_adi, cell_style),
                 Paragraph('<b>Öğrenci Sayısı:</b>', cell_style),     Paragraph(str(len(ogrenciler)), cell_style)]
            ]
            ht = Table(header_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
            ht.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), FONT_NAME), ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, colors.grey), ('PADDING', (0,0), (-1,-1), 5),
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey), ('BACKGROUND', (2,0), (2,-1), colors.lightgrey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(ht); story.append(Spacer(1, 0.7*cm))
            ogrenci_list_data = [['Sıra No', 'Öğrenci No', 'Adı Soyadı', 'Sınıfı', 'İmza']]
            for idx, ogr in enumerate(ogrenciler, 1):
                ogrenci_list_data.append([idx, ogr[4], f'{ogr[1]} {ogr[2]}', ogr[3], ''])
            ot = Table(ogrenci_list_data, colWidths=[1.5*cm, 3*cm, 6*cm, 3*cm, 3.5*cm])
            ot.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), FONT_NAME), ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4a69bd')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (2,1), (2,-1), 'LEFT'),
            ]))
            story.append(ot)
            keys = list(atama_plani.keys())
            if derslik_id != keys[-1]:
                story.append(PageBreak())
        try:
            doc.build(story)
            messagebox.showinfo("Başarılı", f"PDF oluşturuldu!\nKonum: {filename}")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF hatası: {e}")

    def add_teacher(self):
        win = self._make_toplevel("Yeni Öğretmen Ekle", "360x160")
        ctk.CTkLabel(win, text="Öğretmenin Adı Soyadı:",
                     text_color=TEXT_PRIMARY).pack(pady=(18, 6))
        e = ctk.CTkEntry(win, width=280, fg_color=ENTRY_BG,
                          border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
        e.pack()
        def save():
            name = e.get().strip()
            if not name: return
            try:
                self.cursor.execute('INSERT INTO ogretmenler (ad_soyad) VALUES (?)', (name,))
                self.conn.commit(); self.load_teachers(); win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Hata", "Bu isimde öğretmen zaten kayıtlı!", parent=win)
        ctk.CTkButton(win, text="Kaydet", command=save,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a").pack(pady=14)

    def delete_teacher(self):
        selected = self.get_selected_item(self.teacher_tree)
        if not selected: return
        if messagebox.askyesno("Onay", "Seçili öğretmen silinecek. Emin misiniz?"):
            self.cursor.execute('DELETE FROM ogretmenler WHERE id = ?', (selected['values'][0],))
            self.conn.commit(); self.load_teachers()

    def load_teachers(self):
        self.clear_treeview(self.teacher_tree)
        self.cursor.execute('SELECT id, ad_soyad FROM ogretmenler ORDER BY ad_soyad')
        for row in self.cursor.fetchall():
            self.teacher_tree.insert('', 'end', values=row)

    def add_classroom(self):
        win = self._make_toplevel("Yeni Derslik Ekle", "360x200")
        ctk.CTkLabel(win, text="Derslik Adı:", text_color=TEXT_PRIMARY).pack(pady=(18, 4))
        ad_e = ctk.CTkEntry(win, width=280, fg_color=ENTRY_BG,
                             border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
        ad_e.pack()
        ctk.CTkLabel(win, text="Kapasite:", text_color=TEXT_PRIMARY).pack(pady=(12, 4))
        kap_e = ctk.CTkEntry(win, width=280, fg_color=ENTRY_BG,
                              border_color=ENTRY_BORDER, text_color=TEXT_PRIMARY)
        kap_e.pack()
        def save():
            ad = ad_e.get().strip(); kap_str = kap_e.get().strip()
            if not ad or not kap_str:
                messagebox.showerror("Hata", "Alanlar boş olamaz!", parent=win); return
            try:
                kap = int(kap_str)
                self.cursor.execute('INSERT INTO derslikler (derslik_adi, kapasite) VALUES (?, ?)', (ad, kap))
                self.conn.commit(); self.load_classrooms(); win.destroy()
            except ValueError:
                messagebox.showerror("Hata", "Kapasite sayı olmalıdır!", parent=win)
            except sqlite3.IntegrityError:
                messagebox.showerror("Hata", "Bu isimde derslik zaten var!", parent=win)
        ctk.CTkButton(win, text="Kaydet", command=save,
                      fg_color=ACCENT_GREEN, hover_color="#16a34a").pack(pady=14)

    def delete_classroom(self):
        selected = self.get_selected_item(self.classroom_tree)
        if not selected: return
        if messagebox.askyesno("Onay", "Seçili derslik silinecek. Emin misiniz?"):
            self.cursor.execute('DELETE FROM derslikler WHERE id = ?', (selected['values'][0],))
            self.conn.commit(); self.load_classrooms()

    def load_classrooms(self):
        self.clear_treeview(self.classroom_tree)
        self.cursor.execute('SELECT id, derslik_adi, kapasite FROM derslikler ORDER BY derslik_adi')
        for row in self.cursor.fetchall():
            self.classroom_tree.insert('', 'end', values=row)

    # ─────────────────────────── PDF OLUŞTURMA ────────────────────────────────
    def generate_single_pdf(self, filename, ogrenci, okul, ogretmen, ders, sorular):
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
        story = []
        styles = getSampleStyleSheet()
        title_style  = ParagraphStyle('CT', parent=styles['h1'],   fontName=FONT_NAME, fontSize=16, alignment=TA_CENTER, spaceAfter=10)
        ders_style   = ParagraphStyle('CT', parent=styles['h2'],   fontName=FONT_NAME, fontSize=14, alignment=TA_CENTER)
        normal_style = ParagraphStyle('CN', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10, spaceAfter=6, leading=14)
        footer_style = ParagraphStyle('FS', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, alignment=TA_CENTER)
        story.extend([Paragraph(okul, title_style), Spacer(1, 0.3*cm),
                      Paragraph(f"<b>{ders} Sınavı</b>", ders_style), Spacer(1, 0.5*cm)])
        ogrenci_data = [['Ad Soyad:', f"{ogrenci[1]} {ogrenci[2]}", 'Sınıf:', ogrenci[3]],
                        ['Öğrenci No:', ogrenci[4], 'Tarih:', datetime.now().strftime('%d.%m.%Y')]]
        ot = Table(ogrenci_data, colWidths=[3*cm, 6*cm, 2*cm, 4*cm])
        ot.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ecf0f1')),
                                ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
                                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7')),
                                ('PADDING', (0,0), (-1,-1), 8)]))
        story.extend([ot, Spacer(1, 0.7*cm)])
        col_names = [desc[0] for desc in self.cursor.description]
        for idx, soru_raw in enumerate(sorular, 1):
            soru = dict(zip(col_names, soru_raw))
            soru_text = f"<b>Soru {idx}.</b> {soru['soru_baslik'].replace(chr(10), '<br/>')}"
            sp = Paragraph(soru_text, normal_style)
            st = Table([[sp]], colWidths=['100%'])
            st.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f0f0')),
                                    ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
            story.append(st)
            if soru.get('soru_gorsel_yolu') and os.path.exists(soru['soru_gorsel_yolu']):
                try:
                    story.append(Spacer(1, 0.2*cm))
                    img = Image(soru['soru_gorsel_yolu']); img.drawWidth = 12*cm
                    img.drawHeight = (img.drawWidth / img.imageWidth) * img.imageHeight
                    story.append(img); story.append(Spacer(1, 0.2*cm))
                except Exception as e:
                    print(f"Resim eklenemedi: {e}")
            if soru['soru_tipi'] == 'Çoktan Seçmeli':
                sec_data = []
                for harf, key in zip(['A','B','C','D','E'],
                                     ['secenek_a','secenek_b','secenek_c','secenek_d','secenek_e']):
                    if soru.get(key):
                        ss = ParagraphStyle('SS', parent=normal_style, leftIndent=10)
                        sec_data.append([Paragraph(f"<b>{harf})</b>", ss), Paragraph(soru[key], ss)])
                if sec_data:
                    sec_t = Table(sec_data, colWidths=[1*cm, 16*cm])
                    sec_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                                               ('LEFTPADDING', (0,0), (-1,-1), 0)]))
                    story.append(sec_t)
            else:
                story.append(Spacer(1, 2.5*cm))
            story.append(Spacer(1, 0.4*cm))
        story.extend([Spacer(1, 1*cm), Paragraph(f"<i>Sınavı Hazırlayan: {ogretmen}</i>", footer_style)])
        doc.build(story)

    # ──────────────────────────── YARDIMCI METOTLAR ───────────────────────────
    def _ctk_btn(self, parent, text, command, color):
        btn = ctk.CTkButton(parent, text=text, command=command,
                            fg_color=color, hover_color=self._darken(color),
                            font=ctk.CTkFont(size=12, weight="bold"),
                            height=36, corner_radius=8)
        btn.pack(side="left", padx=(0, 8))
        return btn

    @staticmethod
    def _darken(hex_color):
        """Verilen hex rengi %20 koyulaştırır."""
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r, g, b = max(0, int(r * 0.8)), max(0, int(g * 0.8)), max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _make_treeview(self, parent, columns, height=14):
        """Koyu temalı bir ttk.Treeview oluşturur."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Dark.Treeview",
                        background="#1e293b", foreground="#f1f5f9",
                        fieldbackground="#1e293b", rowheight=26,
                        font=('Arial', 11))
        style.configure("Dark.Treeview.Heading",
                        background="#334155", foreground="#94a3b8",
                        font=('Arial', 11, 'bold'), relief="flat")
        style.map("Dark.Treeview",
                  background=[('selected', '#3b82f6')],
                  foreground=[('selected', 'white')])

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        tree = ttk.Treeview(frame, columns=columns, show='headings',
                            height=height, style="Dark.Treeview")
        for col in columns:
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree

    def _make_toplevel(self, title, geometry):
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry(geometry)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        win.configure(fg_color=MAIN_BG)
        return win

    def get_selected_item(self, treeview):
        selected = treeview.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen listeden bir öğe seçin!")
            return None
        return treeview.item(selected[0])

    def clear_treeview(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = ctk.CTk()
    app = ExamSystem(root)
    root.mainloop()

