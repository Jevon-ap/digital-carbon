# 🌱 Kalkulator Hijau V.2 (2026)
### Sistem Inventarisasi Emisi Gas Rumah Kaca (GRK) & Financed Emissions Terstandar

Aplikasi web interaktif berbasis **Streamlit** dan **Python** untuk menghitung emisi GRK secara presisi berdasarkan standar resmi **"Buku Panduan Kalkulator Hijau V.2 (2026)"**, standar global **GHG Protocol Corporate Standard**, standar **PCAF (Partnership for Carbon Accounting Financials)** untuk emisi terbiayai sektor keuangan, dan regulasi **OJK Taksonomi Hijau Indonesia 2.0 / POJK 51**.

---

## 📁 Struktur Proyek Modular

```text
d:\project\
│
├── app.py                     # Antarmuka Streamlit (UI/UX, Sidebar, Form, Chart, Ekspor)
├── calculator.py              # Pustaka fungsi logika akuntansi emisi (Scope 1, 2, 3, 4)
├── report_generator.py        # Generator laporan resmi (PDF, Excel, CSV)
├── test_calculator.py         # Rangkaian pengujian unit test (unittest)
├── README.md                  # Dokumentasi teknis & panduan penggunaan
│
├── data/                      # Folder tabel referensi faktor emisi (CSV)
│   ├── fe_bbm.csv             # Faktor emisi bahan bakar stasioner & bergerak
│   ├── fe_listrik.csv         # Faktor emisi kelistrikan grid nasional & regional
│   ├── fe_sektoral.csv        # Faktor emisi kredit sektoral (PCAF & OJK)
│   └── templates/             # Berkas template untuk unggah massal (bulk upload)
│       ├── template_scope1.csv
│       ├── template_scope2.csv
│       ├── template_scope3.csv
│       └── template_scope4.csv
```

---

## 🧮 Logika Perhitungan & Metodologi (Kalkulator Hijau V.2)

### 1. Scope 1 (Emisi Langsung)
- **a. Penggunaan BBM Statis (Genset / Boiler / Dapur):**
  $$\text{Emisi } (\text{kgCO}_2\text{e}) = \text{Volume BBM} \times \text{Faktor Emisi BBM } (\text{kgCO}_2\text{e}/\text{satuan})$$
- **b. Kendaraan Operasional (Jarak Tempuh):**
  $$\text{Konsumsi Liter} = \frac{\text{Jarak Tempuh } (\text{km})}{\text{Efisiensi BBM } (\text{km/Liter})}$$
  $$\text{Emisi } (\text{kgCO}_2\text{e}) = \text{Jarak Tempuh} \times \left(\frac{\text{Faktor Emisi BBM}}{\text{Efisiensi BBM}}\right)$$

### 2. Scope 2 (Emisi Tidak Langsung dari Listrik)
- **Pembelian Listrik PLN / Industri:**
  $$\text{Emisi } (\text{kgCO}_2\text{e}) = \text{Konsumsi Listrik } (\text{kWh}) \times \text{Faktor Emisi Listrik Grid } (\text{kgCO}_2\text{e/kWh})$$
  - *Default Grid Nasional:* $0.7900 \text{ kgCO}_2\text{e/kWh}$
  - *Jamali (Jawa - Madura - Bali):* $0.8100 \text{ kgCO}_2\text{e/kWh}$
  - *Sumatra:* $0.7600 \text{ kgCO}_2\text{e/kWh}$
  - *Kalimantan:* $0.8300 \text{ kgCO}_2\text{e/kWh}$
  - *Sulawesi:* $0.7200 \text{ kgCO}_2\text{e/kWh}$
  - *Listrik Hijau Bersertifikat (REC):* $0.0000 \text{ kgCO}_2\text{e/kWh}$

### 3. Scope 3 (Financed Emissions - PCAF Sektor Keuangan)
- **Opsi A: Pendekatan Emisi Dilaporkan Debitur (Reported Emissions):**
  $$\text{Attribution Factor} = \min\left(1.0, \frac{\text{Nilai Baki Debet Kredit}}{\text{EVIC atau Total Aset Debitur}}\right)$$
  $$\text{Financed Emission } (\text{tCO}_2\text{e}) = \text{Attribution Factor} \times \text{Total Emisi Debitur } (\text{tCO}_2\text{e})$$
- **Opsi B: Pendekatan Aktivitas Ekonomi / Proksi Sektoral (Physical/Economic Activity):**
  $$\text{Financed Emission } (\text{tCO}_2\text{e}) = \text{Nilai Baki Debet } (\text{Juta Rp}) \times \text{Faktor Emisi Kredit Sektoral } (\text{tCO}_2\text{e / Juta Rp})$$

### 4. Scope 4 (Avoided Emissions & Offsetting)
- **Penghindaran Emisi Pembangkit Surya (PLTS Atap):**
  $$\text{Avoided } (\text{tCO}_2\text{e}) = \frac{\text{kWh Generasi} \times \text{Faktor Emisi Grid}}{1000}$$
- **Substitusi Armada Kendaraan Listrik (EV vs ICE):**
  $$\text{Avoided } (\text{kgCO}_2\text{e}) = \max\left(0, \text{Emisi ICE} - \text{Emisi EV}\right)$$
- **Kredit Karbon Terverifikasi (SPE-GRK):**
  Offsetting 1:1 dari Bursa Karbon resmi (IDXCarbon).
- **Akuntansi Bersih (Net Emissions):**
  $$\text{Total Gross Emissions} = \text{Scope 1} + \text{Scope 2} + \text{Scope 3}$$
  $$\text{Total Net Emissions} = \max\left(0, \text{Gross} - \text{Scope 4}\right)$$

---

## 🚀 Cara Menjalankan Aplikasi

Jalankan perintah berikut di terminal:
```bash
streamlit run app.py
```
Akses di browser: `http://localhost:8501`

Untuk menjalankan unit test:
```bash
python -m unittest test_calculator.py
```

---

## 🌟 Fitur Utama Aplikasi

1. **Dashboard & Metric Cards Eksekutif**:
   - Total Gross Emissions (tCO2e), Total Avoided (Scope 4), Net Emissions, dan Offset Ratio (%).
   - Donut Chart interaktif komposisi per Scope (Plotly).
   - Waterfall Chart perbandingan Gross vs Scope 4 vs Net.
   - Bar Chart horizontal emisi terbiayai per sektor kredit (Scope 3).
2. **Form Interaktif Fleksibel**:
   - Input manual interaktif dengan dropdown BBM, kendaraan, grid wilayah, dan sektor.
   - Validasi nilai negatif dan penanganan *null value* otomatis.
3. **Fitur Unggah Massal (Bulk Upload)**:
   - Dukungan file format CSV dan Excel (`.xlsx`).
   - Tombol unduh berkas template CSV untuk setiap scope.
4. **Ekspor Laporan Multiformat**:
   - **PDF Resmi**: Dokumen eksekutif berstandar ISO/GHG Protocol lengkap dengan ringkasan KPI, tabel data, catatan metodologi, dan blok tanda tangan.
   - **Excel (.xlsx)**: Workbook multi-sheet dengan styling hijau profesional, header berbayang, dan kolom terformat.
   - **CSV**: Rekapitulasi data gabungan terpadu.
5. **Mode Demo 1-Klik**:
   - Tombol **"📥 Muat Demo"** di sidebar langsung memuat contoh data portofolio riil.
