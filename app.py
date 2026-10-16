"""
Aplikasi Kalkulator Hijau V.2 (2026)
Antarmuka Streamlit untuk Inventarisasi Emisi GRK & Financed Emissions
Sesuai Standar GHG Protocol, PCAF, OJK Taksonomi Hijau Indonesia, dan ESDM/KLHK.
"""

import io
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import calculator as calc
import report_generator as rep

# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Kalkulator Hijau V.2 (2026) | GHG & Financed Emissions",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk gaya visual modern & profesional
st.markdown("""
<style>
    /* Font & container styling */
    .main {
        background-color: #FAFAFA;
    }
    
    /* Hero Banner */
    .hero-card {
        background: linear-gradient(135deg, #0F382C 0%, #1B5E43 60%, #2D8A64 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(15, 56, 44, 0.15);
    }
    .hero-card h1 {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    .hero-card p {
        color: #D1E7DD !important;
        font-size: 14px !important;
        margin-bottom: 0 !important;
    }
    
    /* Metric Cards */
    .metric-container {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    }
    .custom-metric-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .custom-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0F382C;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Status Badge */
    .badge-tag {
        display: inline-block;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 20px;
    }
    .badge-green {
        background-color: #DEF7EC;
        color: #03543F;
    }
    .badge-blue {
        background-color: #E1EFFE;
        color: #1E429F;
    }
    .badge-amber {
        background-color: #FEF08A;
        color: #713F12;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# INISIALISASI SESSION STATE
# ==============================================================================
if "scope1_data" not in st.session_state:
    st.session_state["scope1_data"] = []

if "scope2_data" not in st.session_state:
    st.session_state["scope2_data"] = []

if "scope3_data" not in st.session_state:
    st.session_state["scope3_data"] = []

if "scope4_data" not in st.session_state:
    st.session_state["scope4_data"] = []

if "company_info" not in st.session_state:
    st.session_state["company_info"] = {
        "entitas": "PT Bank Hijau Nusantara Tbk",
        "tahun": "2026",
        "penilai": "Tim ESG & Penilai Emisi Karbon"
    }


# ==============================================================================
# PEMUATAN DATA REFERENSI
# ==============================================================================
@st.cache_data
def get_fe_datasets():
    df_bbm = calc.load_fe_bbm()
    df_listrik = calc.load_fe_listrik()
    df_sektoral = calc.load_fe_sektoral()
    return df_bbm, df_listrik, df_sektoral

df_fe_bbm, df_fe_listrik, df_fe_sektoral = get_fe_datasets()


# ==============================================================================
# FUNGSI PEMUATAN DEMO & RESET
# ==============================================================================
def load_sample_demo_data():
    """Memuat data contoh komprehensif ke session state."""
    st.session_state["scope1_data"] = [
        calc.calc_scope1_stationary(2500, 2.18, deskripsi="Genset Cadangan Kantor Pusat", jenis_bbm="Solar Subsidi / Biosolar B35"),
        calc.calc_scope1_stationary(4200, 3.02, deskripsi="Boiler Pemanas Fasilitas Pabrik", jenis_bbm="Minyak Bakar (Fuel Oil/MFO)"),
        calc.calc_scope1_stationary(550, 2.98, deskripsi="LPG Dapur Kantin & Fasilitas Karyawan", jenis_bbm="LPG", satuan="Kg"),
        calc.calc_scope1_mobile_distance(14500, 6.5, 2.18, jenis_kendaraan="Truk Sedang / Engkel / Box (Solar)", jenis_bbm="Solar Subsidi / Biosolar B35", deskripsi="Armada Truk Logistik Distribusi"),
        calc.calc_scope1_mobile_distance(24000, 10.5, 2.33, jenis_kendaraan="Mobil Penumpang MPV / SUV Bensin", jenis_bbm="Pertamax (RON 92)", deskripsi="Kendaraan Dinas Operasional Kantor"),
        calc.calc_scope1_mobile_distance(15000, 40.0, 2.31, jenis_kendaraan="Sepeda Motor Bensin (Bebek / Skutik)", jenis_bbm="Pertalite (RON 90)", deskripsi="Motor Operasional Lapangan & Kurir")
    ]
    
    st.session_state["scope2_data"] = [
        calc.calc_scope2_electricity(95000, 0.81, wilayah_grid="Jamali (Jawa - Madura - Bali)", deskripsi="Gedung Kantor Pusat Sudirman Jakarta"),
        calc.calc_scope2_electricity(380000, 0.81, wilayah_grid="Jamali (Jawa - Madura - Bali)", deskripsi="Pabrik & Gudang Karawang"),
        calc.calc_scope2_electricity(32000, 0.76, wilayah_grid="Sumatra (Interkoneksi Sistem Sumatra)", deskripsi="Kantor Cabang Medan"),
        calc.calc_scope2_electricity(22000, 0.83, wilayah_grid="Kalimantan (Sistem Barito - Mahakam & Khatulistiwa)", deskripsi="Kantor Operasional Balikpapan"),
        calc.calc_scope2_electricity(65000, 0.00, wilayah_grid="Listrik Hijau Bersertifikat (PLN REC / EBT 100%)", deskripsi="Pusat Data / Server Hijau REC")
    ]
    
    st.session_state["scope3_data"] = [
        calc.calc_scope3_sectoral(35000, 0.045, nama_debitur="PT Agro Nusantara Hijau", kode_sektor="A", nama_sektor="Pertanian Perkebunan Kehutanan dan Perikanan"),
        calc.calc_scope3_sectoral(80000, 0.128, nama_debitur="PT Borneo Tambang Bara", kode_sektor="B", nama_sektor="Pertambangan Batubara Minyak Gas dan Mineral"),
        calc.calc_scope3_sectoral(55000, 0.092, nama_debitur="PT Indokimia Presisi Semen", kode_sektor="C", nama_sektor="Industri Manufaktur Kimia Logam Semen dan Kertas"),
        calc.calc_scope3_sectoral(40000, 0.098, nama_debitur="PT Samudera Logistik Ekspres", kode_sektor="I", nama_sektor="Transportasi Darat Laut dan Udara"),
        calc.calc_scope3_reported(baki_debet_rp=120_000_000_000, evic_atau_aset_rp=600_000_000_000, total_emisi_debitur_tco2e=85000, nama_debitur="PT Semen Mega Persada Tbk", sektor="Industri Semen & Bangunan"),
        calc.calc_scope3_reported(baki_debet_rp=45_000_000_000, evic_atau_aset_rp=150_000_000_000, total_emisi_debitur_tco2e=12000, nama_debitur="PT Kimia Farma Nusa", sektor="Manufaktur Kimia Farmasi")
    ]
    
    st.session_state["scope4_data"] = [
        calc.calc_scope4_solar_pv(65000, 0.81, deskripsi="PLTS Atap Gedung Pusat Sudirman 150 kWp"),
        calc.calc_scope4_solar_pv(28000, 0.81, deskripsi="PLTS Atap Gudang Distribusi Karawang"),
        calc.calc_scope4_ev_avoided(160000, efisiensi_ice_km_per_liter=12.0, fe_bbm_ice=2.31, konsumsi_ev_kwh_per_km=0.16, fe_listrik_grid=0.81, deskripsi="Armada Operasional 15 Unit EV Car"),
        calc.calc_scope4_ev_avoided(75000, efisiensi_ice_km_per_liter=40.0, fe_bbm_ice=2.31, konsumsi_ev_kwh_per_km=0.04, fe_listrik_grid=0.81, deskripsi="Armada 25 Sepeda Motor Listrik Kurir"),
        calc.calc_scope4_carbon_offset(750.0, penyedia_proyek="Bursa Karbon Indonesia (IDXCarbon)", deskripsi="SPE-GRK Restorasi Lahan Gambut Katingan", nomor_sertifikat="SPE-GRK-ID-2026-0042"),
        calc.calc_scope4_carbon_offset(350.0, penyedia_proyek="Bursa Karbon Indonesia (IDXCarbon)", deskripsi="SPE-GRK Pembangkit Minihidro Sumbar", nomor_sertifikat="SPE-GRK-ID-2026-0098")
    ]


def clear_all_data():
    """Mengosongkan semua data tercatat."""
    st.session_state["scope1_data"] = []
    st.session_state["scope2_data"] = []
    st.session_state["scope3_data"] = []
    st.session_state["scope4_data"] = []


# ==============================================================================
# PERHITUNGAN AGREGASI RINGKASAN
# ==============================================================================
summary = calc.calculate_overall_summary(
    st.session_state["scope1_data"],
    st.session_state["scope2_data"],
    st.session_state["scope3_data"],
    st.session_state["scope4_data"]
)


# ==============================================================================
# SIDEBAR NAVIGATION & KONTROL
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/natural-food.png", width=64)
    st.markdown("### **Kalkulator Hijau V.2**")
    st.caption("Standard Buku Panduan Emisi GRK & Financed Emissions (2026)")
    
    st.markdown("---")
    menu = st.radio(
        "Pilih Menu Navigasi:",
        [
            "📊 Dashboard & Ringkasan Emisi",
            "🔥 Kalkulator Scope 1 (Emisi Langsung)",
            "⚡ Kalkulator Scope 2 (Emisi Listrik)",
            "🏦 Kalkulator Scope 3 (Financed Emissions)",
            "🍃 Kalkulator Scope 4 (Offsetting & EBT)",
            "📑 Ekspor Laporan & Panduan Metodologi"
        ]
    )
    
    st.markdown("---")
    st.markdown("#### **Status Data Emisi**")
    st.markdown(f"""
    - **Scope 1:** `{summary.count_scope1}` data ({summary.scope1_tco2e:,.2f} tCO2e)
    - **Scope 2:** `{summary.count_scope2}` data ({summary.scope2_tco2e:,.2f} tCO2e)
    - **Scope 3:** `{summary.count_scope3}` data ({summary.scope3_tco2e:,.2f} tCO2e)
    - **Scope 4:** `{summary.count_scope4}` data ({summary.scope4_tco2e:,.2f} tCO2e)
    """)
    
    st.markdown("---")
    st.markdown("#### **Aksi Cepat Data**")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("📥 Muat Demo", use_container_width=True, help="Muat data contoh portofolio lengkap"):
            load_sample_demo_data()
            st.toast("Data sampel berhasil dimuat!", icon="✅")
            st.rerun()
    with col_sb2:
        if st.button("🗑️ Reset Data", use_container_width=True, help="Hapus seluruh data kalkulator"):
            clear_all_data()
            st.toast("Seluruh data telah dikosongkan.", icon="🧹")
            st.rerun()

    st.markdown("---")
    with st.expander("ℹ️ Profil Entitas Pelapor"):
        st.session_state["company_info"]["entitas"] = st.text_input(
            "Nama Entitas / Perusahaan",
            value=st.session_state["company_info"].get("entitas", "PT Bank Hijau Nusantara Tbk")
        )
        st.session_state["company_info"]["tahun"] = st.text_input(
            "Tahun Pelaporan",
            value=st.session_state["company_info"].get("tahun", "2026")
        )
        st.session_state["company_info"]["penilai"] = st.text_input(
            "Penilai / Verifikator",
            value=st.session_state["company_info"].get("penilai", "Tim ESG & Penilai Emisi Karbon")
        )


# ==============================================================================
# HALAMAN 1: DASHBOARD & RINGKASAN EMISI
# ==============================================================================
if menu == "📊 Dashboard & Ringkasan Emisi":
    st.markdown("""
    <div class="hero-card">
        <h1>🌱 Kalkulator Hijau V.2 (2026)</h1>
        <p>Sistem Akuntansi Gas Rumah Kaca (GRK) Presisi Berstandar GHG Protocol, PCAF Standard, dan Taksonomi Hijau Indonesia 2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    # METRIC CARDS SECTION
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="custom-metric-card">
            <div class="metric-title">TOTAL EMISI KOTOR (GROSS)</div>
            <div class="metric-value" style="color:#C53030;">{summary.gross_tco2e:,.2f} <span style="font-size:14px;">tCO2e</span></div>
            <div class="metric-sub">Scope 1 + Scope 2 + Scope 3</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="custom-metric-card">
            <div class="metric-title">TOTAL PENGURANGAN (SCOPE 4)</div>
            <div class="metric-value" style="color:#2B6CB0;">{summary.scope4_tco2e:,.2f} <span style="font-size:14px;">tCO2e</span></div>
            <div class="metric-sub">EBT + Armada EV + SPE-GRK Offsets</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="custom-metric-card">
            <div class="metric-title">TOTAL EMISI BERSIH (NET)</div>
            <div class="metric-value" style="color:#2E7D32;">{summary.net_tco2e:,.2f} <span style="font-size:14px;">tCO2e</span></div>
            <div class="metric-sub">Emisi Kotor dikurangi Scope 4 Terverifikasi</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="custom-metric-card">
            <div class="metric-title">OFFSET RATIO / PENURUNAN</div>
            <div class="metric-value" style="color:#0F5132;">{summary.offset_percentage:.1f}%</div>
            <div class="metric-sub">Pencapaian Dekarbonisasi Menuju NZE</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # VISUALISASI GRAFIK UTAMA
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.markdown("#### 🎯 Komposisi Emisi per Scope (Gross)")
        if summary.gross_tco2e > 0:
            labels = ["Scope 1 (Emisi Langsung)", "Scope 2 (Listrik Jaringan)", "Scope 3 (Financed Emissions)"]
            values = [summary.scope1_tco2e, summary.scope2_tco2e, summary.scope3_tco2e]
            colors_scope = ["#E65100", "#F57C00", "#1976D2"]
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors_scope),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
                hovertemplate="<b>%{label}</b><br>Emisi: %{value:,.2f} tCO2e<br>Porsi: %{percent}<extra></extra>"
            )])
            fig_donut.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=20, b=50, l=10, r=10),
                height=350
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("💡 Belum ada data emisi kotor. Klik **'📥 Muat Demo'** di sidebar atau tambahkan data di menu kalkulator untuk melihat visualisasi.")

    with col_chart2:
        st.markdown("#### ⚖️ Dekarbonisasi: Gross vs Scope 4 vs Net")
        if summary.gross_tco2e > 0 or summary.scope4_tco2e > 0:
            fig_wf = go.Figure(go.Waterfall(
                name="Emisi",
                orientation="v",
                measure=["relative", "relative", "total"],
                x=["Emisi Kotor (Gross)", "Scope 4 (Pengurangan/Offsets)", "Emisi Bersih (Net)"],
                textposition="outside",
                text=[f"{summary.gross_tco2e:,.1f}", f"-{summary.scope4_tco2e:,.1f}", f"{summary.net_tco2e:,.1f}"],
                y=[summary.gross_tco2e, -summary.scope4_tco2e, 0],
                connector={"line": {"color": "#CBD5E0"}},
                decreasing={"marker": {"color": "#2B6CB0"}},
                increasing={"marker": {"color": "#C53030"}},
                totals={"marker": {"color": "#2E7D32"}}
            ))
            fig_wf.update_layout(
                yaxis_title="Emisi (tCO2e)",
                margin=dict(t=20, b=50, l=10, r=10),
                height=350
            )
            st.plotly_chart(fig_wf, use_container_width=True)
        else:
            st.info("💡 Data grafik perbandingan akan muncul setelah data diinput.")

    # GRAFIK KHUSUS SCOPE 3 (EMISI PER SEKTOR KREDIT)
    st.markdown("---")
    st.markdown("#### 🏦 Distribusi Financed Emissions per Sektor Kredit (Scope 3 - PCAF)")
    if len(st.session_state["scope3_data"]) > 0:
        df_s3 = pd.DataFrame(st.session_state["scope3_data"])
        sector_agg = df_s3.groupby("sektor")["emisi_tco2e"].sum().reset_index().sort_values(by="emisi_tco2e", ascending=True)
        
        fig_bar = px.bar(
            sector_agg,
            x="emisi_tco2e",
            y="sektor",
            orientation="h",
            color="emisi_tco2e",
            color_continuous_scale="Tealgrn",
            labels={"emisi_tco2e": "Financed Emissions (tCO2e)", "sektor": "Sektor Ekonomi"},
            title="Intensitas Emisi Pembiayaan per Sektor Portofolio"
        )
        fig_bar.update_layout(
            margin=dict(t=40, b=40, l=10, r=10),
            height=320,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("💡 Belum ada data Scope 3. Input debitur atau pinjaman di tab **Kalkulator Scope 3** untuk melihat grafik sektoral.")

    # TABEL RINGKASAN SEMUA SCOPE
    st.markdown("---")
    st.markdown("#### 📋 Matriks Rangkuman Inventarisasi Emisi")
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        tbl_summary = pd.DataFrame([
            {"Lingkup": "Scope 1 (Emisi Langsung)", "Item Terdata": summary.count_scope1, "Total Emisi (tCO2e)": f"{summary.scope1_tco2e:,.4f}", "Proporsi Gross": f"{(summary.scope1_tco2e/summary.gross_tco2e*100 if summary.gross_tco2e>0 else 0):.2f}%"},
            {"Lingkup": "Scope 2 (Listrik Jaringan)", "Item Terdata": summary.count_scope2, "Total Emisi (tCO2e)": f"{summary.scope2_tco2e:,.4f}", "Proporsi Gross": f"{(summary.scope2_tco2e/summary.gross_tco2e*100 if summary.gross_tco2e>0 else 0):.2f}%"},
            {"Lingkup": "Scope 3 (Financed Emissions)", "Item Terdata": summary.count_scope3, "Total Emisi (tCO2e)": f"{summary.scope3_tco2e:,.4f}", "Proporsi Gross": f"{(summary.scope3_tco2e/summary.gross_tco2e*100 if summary.gross_tco2e>0 else 0):.2f}%"},
            {"Lingkup": "TOTAL GROSS EMISSIONS", "Item Terdata": summary.count_scope1 + summary.count_scope2 + summary.count_scope3, "Total Emisi (tCO2e)": f"{summary.gross_tco2e:,.4f}", "Proporsi Gross": "100.00%"},
            {"Lingkup": "Scope 4 (Pengurangan/Offsets)", "Item Terdata": summary.count_scope4, "Total Emisi (tCO2e)": f"-{summary.scope4_tco2e:,.4f}", "Proporsi Gross": f"-{summary.offset_percentage:.2f}%"},
            {"Lingkup": "TOTAL NET EMISSIONS", "Item Terdata": "-", "Total Emisi (tCO2e)": f"{summary.net_tco2e:,.4f}", "Proporsi Gross": "-"}
        ])
        st.dataframe(tbl_summary, use_container_width=True, hide_index=True)

    with col_t2:
        st.markdown("""
        **Pedoman Akuntansi Emisi:**
        - **Scope 1**: Penggunaan bahan bakar statis (genset/boiler) & jarak tempuh kendaraan dinas.
        - **Scope 2**: Emisi listrik grid PLN berdasarkan faktor emisi regional/spasial.
        - **Scope 3**: Emisi terbiayai (*financed emissions*) dari debitur portofolio kredit perbankan.
        - **Scope 4**: Penurunan emisi dari EBT (solar PV), armada EV, dan pembelian sertifikat kredit karbon (SPE-GRK).
        """)


# ==============================================================================
# HALAMAN 2: KALKULATOR SCOPE 1 (EMISI LANGSUNG)
# ==============================================================================
elif menu == "🔥 Kalkulator Scope 1 (Emisi Langsung)":
    st.markdown("## 🔥 Kalkulator Scope 1: Emisi Langsung")
    st.caption("Menghitung emisi dari pembakaran BBM stasioner (Genset/Boiler) dan kendaraan operasional bergerak.")
    
    tab_manual, tab_bulk, tab_data = st.tabs(["📝 Input Manual", "📂 Unggah Massal (Bulk Upload)", "📊 Data Tersimpan"])
    
    with tab_manual:
        st.markdown("##### Pilih Tipe Emisi Scope 1:")
        tipe_s1 = st.radio("Metode Perhitungan:", ["BBM Statis / Industri (Genset, Boiler, Dapur)", "Kendaraan Operasional Bergerak (Jarak Tempuh)"], horizontal=True)
        
        if "BBM Statis" in tipe_s1:
            with st.form("form_scope1_statis"):
                st.markdown("###### Parameter Penggunaan BBM Statis:")
                col_a, col_b = st.columns(2)
                with col_a:
                    deskripsi = st.text_input("Deskripsi Aktivitas / Lokasi", value="Genset Cadangan Kantor Pusat")
                    jenis_bbm = st.selectbox("Jenis Bahan Bakar Minyak / Gas:", df_fe_bbm["jenis_bbm"].tolist())
                
                # Ambil faktor emisi dan satuan default
                fe_row = df_fe_bbm[df_fe_bbm["jenis_bbm"] == jenis_bbm].iloc[0]
                fe_default = float(fe_row["faktor_emisi"])
                satuan_default = str(fe_row["satuan"])
                
                with col_b:
                    volume = st.number_input(f"Volume Konsumsi ({satuan_default})", min_value=0.0, value=1000.0, step=50.0)
                    fe_input = st.number_input(f"Faktor Emisi ({fe_row['kategori']} - kgCO2e/{satuan_default})", min_value=0.0, value=fe_default, format="%.4f")
                
                submitted = st.form_submit_button("➕ Tambahkan ke Scope 1", use_container_width=True)
                if submitted:
                    if volume <= 0:
                        st.error("⚠️ Volume konsumsi harus lebih besar dari 0.")
                    else:
                        item = calc.calc_scope1_stationary(volume, fe_input, deskripsi=deskripsi, jenis_bbm=jenis_bbm, satuan=satuan_default)
                        st.session_state["scope1_data"].append(item)
                        st.success(f"✅ Data berhasil ditambahkan! Emisi: {item['emisi_tco2e']} tCO2e ({item['emisi_kgco2e']:,.2f} kgCO2e)")
                        time.sleep(0.5)
                        st.rerun()

        else:
            with st.form("form_scope1_mobile"):
                st.markdown("###### Parameter Kendaraan Operasional (Jarak Tempuh):")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    deskripsi = st.text_input("Deskripsi Kendaraan / Rute", value="Armada Operasional Distribusi")
                    preset_kendaraan = st.selectbox("Kategori / Model Kendaraan Terstandar:", list(calc.VEHICLE_PRESETS.keys()))
                    preset_info = calc.VEHICLE_PRESETS[preset_kendaraan]
                    default_eff = float(preset_info["efisiensi"])
                    default_bbm = str(preset_info["default_bbm"])
                    
                with col_m2:
                    bbm_index = df_fe_bbm["jenis_bbm"].tolist().index(default_bbm) if default_bbm in df_fe_bbm["jenis_bbm"].tolist() else 0
                    jenis_bbm = st.selectbox("Jenis BBM Kendaraan:", df_fe_bbm["jenis_bbm"].tolist(), index=bbm_index)
                    fe_row = df_fe_bbm[df_fe_bbm["jenis_bbm"] == jenis_bbm].iloc[0]
                    fe_default = float(fe_row["faktor_emisi"])

                col_m3, col_m4, col_m5 = st.columns(3)
                with col_m3:
                    jarak_km = st.number_input("Jarak Tempuh Operasional (km)", min_value=0.0, value=5000.0, step=100.0)
                with col_m4:
                    efisiensi = st.number_input("Efisiensi BBM (km / Liter)", min_value=0.1, value=default_eff, step=0.5)
                with col_m5:
                    fe_val = st.number_input("Faktor Emisi BBM (kgCO2e/Liter)", min_value=0.0, value=fe_default, format="%.4f")

                submit_mobile = st.form_submit_button("➕ Tambahkan Kendaraan ke Scope 1", use_container_width=True)
                if submit_mobile:
                    if jarak_km <= 0:
                        st.error("⚠️ Jarak tempuh harus lebih besar dari 0 km.")
                    elif efisiensi <= 0:
                        st.error("⚠️ Efisiensi BBM harus lebih besar dari 0 km/Liter.")
                    else:
                        item = calc.calc_scope1_mobile_distance(
                            jarak_km=jarak_km,
                            efisiensi_km_per_liter=efisiensi,
                            faktor_emisi=fe_val,
                            jenis_kendaraan=preset_kendaraan,
                            jenis_bbm=jenis_bbm,
                            deskripsi=deskripsi
                        )
                        st.session_state["scope1_data"].append(item)
                        st.success(f"✅ Data berhasil ditambahkan! Konsumsi: {item['konsumsi_liter']:,.1f} L | Emisi: {item['emisi_tco2e']} tCO2e")
                        time.sleep(0.5)
                        st.rerun()

    with tab_bulk:
        st.markdown("##### 📂 Unggah Massal Data Scope 1 (CSV / Excel)")
        st.caption("Unggah berkas untuk memasukkan puluhan hingga ratusan baris data sekaligus.")
        
        # Download Template
        template_path = Path("data/templates/template_scope1.csv")
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    "📥 Unduh Format Template Scope 1 (CSV)",
                    data=f.read(),
                    file_name="template_scope1.csv",
                    mime="text/csv"
                )
        
        uploaded_file = st.file_uploader("Pilih Berkas CSV / Excel Scope 1:", type=["csv", "xlsx", "xls"], key="bulk_s1")
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                st.write("Pratinjau Data Unggahan (5 baris pertama):")
                st.dataframe(df_upload.head(5), use_container_width=True)
                
                if st.button("🚀 Proses & Simpan ke Scope 1", key="btn_proc_s1"):
                    items, errors = calc.process_bulk_scope1(df_upload, df_fe_bbm)
                    if items:
                        st.session_state["scope1_data"].extend(items)
                        st.success(f"Berhasil memproses {len(items)} baris data ke Scope 1!")
                    if errors:
                        st.warning(f"Terdapat {len(errors)} kendala pada baris data:")
                        for err in errors[:5]:
                            st.write(f"- {err}")
                    time.sleep(1.0)
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca berkas: {e}")

    with tab_data:
        st.markdown("##### 📋 Daftar Aktivitas Scope 1 Tersimpan")
        if st.session_state["scope1_data"]:
            df_s1_current = pd.DataFrame(st.session_state["scope1_data"])
            st.dataframe(df_s1_current, use_container_width=True)
            
            total_s1 = df_s1_current["emisi_tco2e"].sum()
            st.info(f"**Total Emisi Scope 1:** {total_s1:,.4f} tCO2e ({df_s1_current['emisi_kgco2e'].sum():,.2f} kgCO2e) dari {len(df_s1_current)} aktivitas.")
            
            if st.button("🗑️ Hapus Seluruh Data Scope 1"):
                st.session_state["scope1_data"] = []
                st.toast("Data Scope 1 berhasil dikosongkan.")
                st.rerun()
        else:
            st.info("Belum ada data Scope 1 tercatat. Gunakan tab **Input Manual** atau **Unggah Massal** di atas.")


# ==============================================================================
# HALAMAN 3: KALKULATOR SCOPE 2 (EMISI LISTRIK)
# ==============================================================================
elif menu == "⚡ Kalkulator Scope 2 (Emisi Listrik)":
    st.markdown("## ⚡ Kalkulator Scope 2: Emisi Listrik Tidak Langsung")
    st.caption("Menghitung emisi tidak langsung dari pembelian listrik jaringan PLN / Industri berdasarkan faktor emisi regional.")
    
    tab_manual, tab_bulk, tab_data = st.tabs(["📝 Input Manual", "📂 Unggah Massal (Bulk Upload)", "📊 Data Tersimpan"])
    
    with tab_manual:
        with st.form("form_scope2"):
            st.markdown("###### Parameter Pembelian Listrik Jaringan:")
            col1, col2 = st.columns(2)
            with col1:
                deskripsi = st.text_input("Nama Gedung / Fasilitas", value="Gedung Kantor Pusat")
                wilayah_grid = st.selectbox(
                    "Wilayah Grid / Jaringan Kelistrikan:",
                    df_fe_listrik["wilayah_grid"].tolist(),
                    index=0
                )
            
            fe_row = df_fe_listrik[df_fe_listrik["wilayah_grid"] == wilayah_grid].iloc[0]
            fe_default = float(fe_row["faktor_emisi"])
            
            with col2:
                konsumsi_kwh = st.number_input("Konsumsi Listrik (kWh)", min_value=0.0, value=25000.0, step=500.0)
                fe_kwh = st.number_input("Faktor Emisi Grid (kgCO2e/kWh)", min_value=0.0, value=fe_default, format="%.4f")
            
            st.caption(f"ℹ️ **Referensi Grid:** {fe_row['keterangan']}")
            
            submit_s2 = st.form_submit_button("➕ Tambahkan ke Scope 2", use_container_width=True)
            if submit_s2:
                if konsumsi_kwh <= 0:
                    st.error("⚠️ Konsumsi kWh harus lebih besar dari 0.")
                else:
                    item = calc.calc_scope2_electricity(konsumsi_kwh, fe_kwh, wilayah_grid=wilayah_grid, deskripsi=deskripsi)
                    st.session_state["scope2_data"].append(item)
                    st.success(f"✅ Fasilitas berhasil ditambahkan! Emisi: {item['emisi_tco2e']} tCO2e ({item['emisi_kgco2e']:,.2f} kgCO2e)")
                    time.sleep(0.5)
                    st.rerun()

    with tab_bulk:
        st.markdown("##### 📂 Unggah Massal Data Scope 2 (CSV / Excel)")
        template_path = Path("data/templates/template_scope2.csv")
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    "📥 Unduh Format Template Scope 2 (CSV)",
                    data=f.read(),
                    file_name="template_scope2.csv",
                    mime="text/csv"
                )
        
        uploaded_file_s2 = st.file_uploader("Pilih Berkas CSV / Excel Scope 2:", type=["csv", "xlsx", "xls"], key="bulk_s2")
        if uploaded_file_s2 is not None:
            try:
                if uploaded_file_s2.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file_s2)
                else:
                    df_upload = pd.read_excel(uploaded_file_s2)
                
                st.write("Pratinjau Data Unggahan:")
                st.dataframe(df_upload.head(5), use_container_width=True)
                
                if st.button("🚀 Proses & Simpan ke Scope 2", key="btn_proc_s2"):
                    items, errors = calc.process_bulk_scope2(df_upload, df_fe_listrik)
                    if items:
                        st.session_state["scope2_data"].extend(items)
                        st.success(f"Berhasil menambahkan {len(items)} fasilitas ke Scope 2!")
                    if errors:
                        st.warning(f"Catatan ({len(errors)} baris bermasalah):")
                        for err in errors[:5]:
                            st.write(f"- {err}")
                    time.sleep(1.0)
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca berkas: {e}")

    with tab_data:
        st.markdown("##### 📋 Daftar Fasilitas Scope 2 Tersimpan")
        if st.session_state["scope2_data"]:
            df_s2_current = pd.DataFrame(st.session_state["scope2_data"])
            st.dataframe(df_s2_current, use_container_width=True)
            
            total_s2 = df_s2_current["emisi_tco2e"].sum()
            total_kwh = df_s2_current["konsumsi_kwh"].sum()
            st.info(f"**Total Emisi Scope 2:** {total_s2:,.4f} tCO2e | **Total Konsumsi:** {total_kwh:,.0f} kWh dari {len(df_s2_current)} fasilitas.")
            
            if st.button("🗑️ Hapus Seluruh Data Scope 2"):
                st.session_state["scope2_data"] = []
                st.toast("Data Scope 2 berhasil dikosongkan.")
                st.rerun()
        else:
            st.info("Belum ada data Scope 2 tercatat.")


# ==============================================================================
# HALAMAN 4: KALKULATOR SCOPE 3 (FINANCED EMISSIONS - PCAF)
# ==============================================================================
elif menu == "🏦 Kalkulator Scope 3 (Financed Emissions)":
    st.markdown("## 🏦 Kalkulator Scope 3: Financed Emissions (Sektor Keuangan)")
    st.caption("Perhitungan emisi yang dibiayai lembaga perbankan/keuangan berbasis standar PCAF (Partnership for Carbon Accounting Financials) & OJK Taksonomi Hijau Indonesia.")
    
    tab_manual, tab_bulk, tab_data = st.tabs(["📝 Input Manual", "📂 Unggah Massal (Bulk Upload)", "📊 Data Portofolio"])
    
    with tab_manual:
        opsi_pcaf = st.radio(
            "Pilih Pendekatan PCAF:",
            [
                "Opsi B: Proksi Sektoral / Aktivitas Ekonomi (Economic Activity / Sectoral Proxy)",
                "Opsi A: Emisi Dilaporkan Debitur (Reported Emissions / Attribution Factor)"
            ]
        )
        
        if "Opsi B" in opsi_pcaf:
            st.markdown("###### Pendekatan Proksi Sektoral (PCAF Opsi B)")
            st.caption("Digunakan jika debitur belum memiliki audit inventarisasi emisi GRK mandiri.")
            with st.form("form_s3_sektoral"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    nama_debitur = st.text_input("Nama Debitur / Nasabah", value="PT Manufaktur Presisi Cemerlang")
                    pilihan_sektor = st.selectbox(
                        "Sektor Usaha (Taksonomi OJK / PCAF):",
                        options=df_fe_sektoral.apply(lambda r: f"[{r['kode_sektor']}] {r['nama_sektor']}", axis=1).tolist()
                    )
                
                kode_pilihan = pilihan_sektor.split("]")[0].replace("[", "").strip()
                row_sektor = df_fe_sektoral[df_fe_sektoral["kode_sektor"] == kode_pilihan].iloc[0]
                fe_sektor_default = float(row_sektor["faktor_emisi"])
                nama_sektor_clean = str(row_sektor["nama_sektor"])
                
                with col_s2:
                    baki_debet_juta = st.number_input("Nilai Baki Debet / Outstanding Kredit (Juta Rupiah)", min_value=0.0, value=25000.0, step=1000.0)
                    fe_sektor_val = st.number_input("Faktor Emisi Kredit (tCO2e / Juta Rp)", min_value=0.0, value=fe_sektor_default, format="%.4f")
                
                st.caption(f"ℹ️ **Kategori Risiko Emisi:** {row_sektor['kategori_risiko']} | Nilai Kredit: Rp {baki_debet_juta*1_000_000:,.0f}")
                
                submit_s3_b = st.form_submit_button("➕ Tambahkan Pinjaman ke Scope 3", use_container_width=True)
                if submit_s3_b:
                    if baki_debet_juta <= 0:
                        st.error("⚠️ Nilai baki debet harus lebih besar dari 0.")
                    else:
                        item = calc.calc_scope3_sectoral(
                            baki_debet_juta_rp=baki_debet_juta,
                            faktor_emisi_sektoral=fe_sektor_val,
                            nama_debitur=nama_debitur,
                            kode_sektor=kode_pilihan,
                            nama_sektor=nama_sektor_clean
                        )
                        st.session_state["scope3_data"].append(item)
                        st.success(f"✅ Fasilitas kredit ditambahkan! Financed Emission: {item['emisi_tco2e']:,.2f} tCO2e")
                        time.sleep(0.5)
                        st.rerun()

        else:
            st.markdown("###### Pendekatan Emisi Dilaporkan Debitur (PCAF Opsi A)")
            st.caption("Digunakan jika debitur korporasi memiliki laporan emisi GRK yang telah diaudit / dipublikasikan.")
            with st.form("form_s3_reported"):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    nama_debitur = st.text_input("Nama Korporasi Debitur", value="PT Semen Nusantara Tbk")
                    sektor = st.text_input("Kategori Industri / Sektor", value="Industri Semen & Manufaktur")
                    total_emisi_debitur = st.number_input("Total Emisi GRK Debitur (tCO2e/tahun)", min_value=0.0, value=85000.0, step=500.0)
                
                with col_r2:
                    baki_debet_rp = st.number_input("Nilai Baki Debet Pinjaman Bank (Rupiah)", min_value=0.0, value=120_000_000_000.0, step=1_000_000_000.0)
                    evic_rp = st.number_input("EVIC / Total Nilai Aset Perusahaan Debitur (Rupiah)", min_value=1.0, value=600_000_000_000.0, step=10_000_000_000.0)
                    
                    if evic_rp > 0:
                        att_factor = min(baki_debet_rp / evic_rp, 1.0)
                        st.info(f"Faktor Atribusi Bank: **{att_factor*100:.2f}%**")

                submit_s3_a = st.form_submit_button("➕ Tambahkan Pinjaman Korporasi ke Scope 3", use_container_width=True)
                if submit_s3_a:
                    if baki_debet_rp <= 0:
                        st.error("⚠️ Nilai baki debet harus lebih besar dari 0.")
                    elif evic_rp <= 0:
                        st.error("⚠️ EVIC / Total aset harus lebih besar dari 0.")
                    else:
                        item = calc.calc_scope3_reported(
                            baki_debet_rp=baki_debet_rp,
                            evic_atau_aset_rp=evic_rp,
                            total_emisi_debitur_tco2e=total_emisi_debitur,
                            nama_debitur=nama_debitur,
                            sektor=sektor
                        )
                        st.session_state["scope3_data"].append(item)
                        st.success(f"✅ Data berhasil ditambahkan! Financed Emission: {item['emisi_tco2e']:,.2f} tCO2e (Atribusi: {item['attribution_factor']*100:.2f}%)")
                        time.sleep(0.5)
                        st.rerun()

    with tab_bulk:
        st.markdown("##### 📂 Unggah Massal Portofolio Kredit Scope 3 (CSV / Excel)")
        template_path = Path("data/templates/template_scope3.csv")
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    "📥 Unduh Format Template Scope 3 (CSV)",
                    data=f.read(),
                    file_name="template_scope3.csv",
                    mime="text/csv"
                )
        
        uploaded_file_s3 = st.file_uploader("Pilih Berkas Portofolio Kredit:", type=["csv", "xlsx", "xls"], key="bulk_s3")
        if uploaded_file_s3 is not None:
            try:
                if uploaded_file_s3.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file_s3)
                else:
                    df_upload = pd.read_excel(uploaded_file_s3)
                
                st.write("Pratinjau Data Unggahan:")
                st.dataframe(df_upload.head(5), use_container_width=True)
                
                if st.button("🚀 Proses & Simpan ke Scope 3", key="btn_proc_s3"):
                    items, errors = calc.process_bulk_scope3(df_upload, df_fe_sektoral)
                    if items:
                        st.session_state["scope3_data"].extend(items)
                        st.success(f"Berhasil menambahkan {len(items)} fasilitas kredit ke Scope 3!")
                    if errors:
                        st.warning(f"Catatan kendala ({len(errors)} baris):")
                        for err in errors[:5]:
                            st.write(f"- {err}")
                    time.sleep(1.0)
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca berkas: {e}")

    with tab_data:
        st.markdown("##### 📋 Daftar Portofolio Kredit Scope 3 Tersimpan")
        if st.session_state["scope3_data"]:
            df_s3_current = pd.DataFrame(st.session_state["scope3_data"])
            st.dataframe(df_s3_current, use_container_width=True)
            
            total_s3 = df_s3_current["emisi_tco2e"].sum()
            st.info(f"**Total Financed Emissions:** {total_s3:,.4f} tCO2e dari {len(df_s3_current)} debitur/fasilitas kredit.")
            
            if st.button("🗑️ Hapus Seluruh Data Scope 3"):
                st.session_state["scope3_data"] = []
                st.toast("Data Scope 3 berhasil dikosongkan.")
                st.rerun()
        else:
            st.info("Belum ada portofolio kredit tercatat.")


# ==============================================================================
# HALAMAN 5: KALKULATOR SCOPE 4 (OFFSETTING & EBT)
# ==============================================================================
elif menu == "🍃 Kalkulator Scope 4 (Offsetting & EBT)":
    st.markdown("## 🍃 Kalkulator Scope 4: Avoided Emissions & Offsetting")
    st.caption("Pencatatan penurunan emisi terverifikasi dari Pembangkit EBT/Solar PV, Armada EV, dan Pembelian Kredit Karbon (SPE-GRK). Dicatat terpisah dari emisi kotor.")
    
    tab_manual, tab_bulk, tab_data = st.tabs(["📝 Input Manual", "📂 Unggah Massal (Bulk Upload)", "📊 Data Tersimpan"])
    
    with tab_manual:
        tipe_s4 = st.radio(
            "Pilih Kategori Penurunan Emisi:",
            [
                "☀️ Penggunaan Panel Surya / EBT (Solar PV)",
                "🚗 Substitusi Armada Kendaraan Listrik (EV vs ICE)",
                "📜 Pembelian Kredit Karbon / SPE-GRK (Bursa Karbon IDXCarbon)"
            ]
        )
        
        if "Panel Surya" in tipe_s4:
            with st.form("form_s4_solar"):
                st.markdown("###### Parameter PLTS Atap / Pembangkit Surya:")
                col1, col2 = st.columns(2)
                with col1:
                    deskripsi = st.text_input("Deskripsi Lokasi / Fasilitas PLTS", value="PLTS Atap Kantor Pusat 100 kWp")
                    wilayah_grid = st.selectbox("Wilayah Grid Listrik Tersubstitusi:", df_fe_listrik["wilayah_grid"].tolist(), index=1)
                
                fe_row = df_fe_listrik[df_fe_listrik["wilayah_grid"] == wilayah_grid].iloc[0]
                fe_default = float(fe_row["faktor_emisi"])
                
                with col2:
                    kwh_generasi = st.number_input("Produksi Listrik PLTS (kWh/tahun)", min_value=0.0, value=35000.0, step=1000.0)
                    fe_grid = st.number_input("Faktor Emisi Grid Tersubstitusi (kgCO2e/kWh)", min_value=0.0, value=fe_default, format="%.4f")
                
                submit_s4_solar = st.form_submit_button("➕ Tambahkan Penghematan EBT", use_container_width=True)
                if submit_s4_solar:
                    if kwh_generasi <= 0:
                        st.error("⚠️ Produksi kWh harus lebih besar dari 0.")
                    else:
                        item = calc.calc_scope4_solar_pv(kwh_generasi, fe_grid, deskripsi=deskripsi)
                        st.session_state["scope4_data"].append(item)
                        st.success(f"✅ Inisiatif PLTS ditambahkan! Avoided Emissions: {item['avoided_tco2e']:,.2f} tCO2e")
                        time.sleep(0.5)
                        st.rerun()

        elif "Kendaraan Listrik" in tipe_s4:
            with st.form("form_s4_ev"):
                st.markdown("###### Parameter Substitusi Armada Listrik (EV):")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    deskripsi = st.text_input("Deskripsi Armada EV", value="Armada 10 Unit Mobil Listrik Kantor")
                    jarak_km = st.number_input("Total Jarak Tempuh Armada (km/tahun)", min_value=0.0, value=120000.0, step=5000.0)
                    eff_ice = st.number_input("Efisiensi Kendaraan Konvensional Pembanding (km/Liter)", min_value=0.1, value=12.0, step=0.5)
                
                with col_e2:
                    fe_bbm = st.number_input("Faktor Emisi BBM Konvensional (kgCO2e/L)", min_value=0.0, value=2.3100, format="%.4f")
                    cons_ev = st.number_input("Konsumsi Daya EV (kWh/km)", min_value=0.01, value=0.16, step=0.01, format="%.3f")
                    fe_grid = st.number_input("Faktor Emisi Listrik Pengisian Grid (kgCO2e/kWh)", min_value=0.0, value=0.81, format="%.4f")
                
                submit_s4_ev = st.form_submit_button("➕ Tambahkan Penurunan Emisi EV", use_container_width=True)
                if submit_s4_ev:
                    if jarak_km <= 0:
                        st.error("⚠️ Jarak tempuh harus lebih besar dari 0.")
                    else:
                        item = calc.calc_scope4_ev_avoided(
                            jarak_km=jarak_km,
                            efisiensi_ice_km_per_liter=eff_ice,
                            fe_bbm_ice=fe_bbm,
                            konsumsi_ev_kwh_per_km=cons_ev,
                            fe_listrik_grid=fe_grid,
                            deskripsi=deskripsi
                        )
                        st.session_state["scope4_data"].append(item)
                        st.success(f"✅ Armada EV ditambahkan! Avoided Emissions: {item['avoided_tco2e']:,.2f} tCO2e (ICE: {item['emisi_ice_kgco2e']:,.0f} kg vs EV: {item['emisi_ev_kgco2e']:,.0f} kg)")
                        time.sleep(0.5)
                        st.rerun()

        else:
            with st.form("form_s4_offset"):
                st.markdown("###### Parameter Kredit Karbon / SPE-GRK:")
                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    deskripsi = st.text_input("Deskripsi Pembelian Kredit Karbon", value="Pembelian Sertifikat Penurunan Emisi GRK")
                    penyedia = st.text_input("Penyedia Proyek / Bursa", value="Bursa Karbon Indonesia (IDXCarbon) / PT Rimba Makmur")
                with col_o2:
                    kredit_ton = st.number_input("Jumlah Kredit Karbon Terverifikasi (tCO2e)", min_value=0.0, value=500.0, step=50.0)
                    sertifikat = st.text_input("Nomor Seri / Registrasi Sertifikat SPE-GRK", value="SPE-GRK-IDX-2026-0042")
                
                submit_s4_offset = st.form_submit_button("➕ Catat Kredit Karbon Offsetting", use_container_width=True)
                if submit_s4_offset:
                    if kredit_ton <= 0:
                        st.error("⚠️ Jumlah kredit karbon harus lebih besar dari 0.")
                    else:
                        item = calc.calc_scope4_carbon_offset(
                            kredit_tco2e=kredit_ton,
                            penyedia_proyek=penyedia,
                            deskripsi=deskripsi,
                            nomor_sertifikat=sertifikat
                        )
                        st.session_state["scope4_data"].append(item)
                        st.success(f"✅ Kredit karbon berhasil dicatat! Total Offsetting: {item['avoided_tco2e']:,.2f} tCO2e")
                        time.sleep(0.5)
                        st.rerun()

    with tab_bulk:
        st.markdown("##### 📂 Unggah Massal Data Scope 4 (CSV / Excel)")
        template_path = Path("data/templates/template_scope4.csv")
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    "📥 Unduh Format Template Scope 4 (CSV)",
                    data=f.read(),
                    file_name="template_scope4.csv",
                    mime="text/csv"
                )
        
        uploaded_file_s4 = st.file_uploader("Pilih Berkas Inisiatif Scope 4:", type=["csv", "xlsx", "xls"], key="bulk_s4")
        if uploaded_file_s4 is not None:
            try:
                if uploaded_file_s4.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file_s4)
                else:
                    df_upload = pd.read_excel(uploaded_file_s4)
                
                st.write("Pratinjau Data Unggahan:")
                st.dataframe(df_upload.head(5), use_container_width=True)
                
                if st.button("🚀 Proses & Simpan ke Scope 4", key="btn_proc_s4"):
                    items, errors = calc.process_bulk_scope4(df_upload)
                    if items:
                        st.session_state["scope4_data"].extend(items)
                        st.success(f"Berhasil menambahkan {len(items)} inisiatif ke Scope 4!")
                    if errors:
                        st.warning(f"Catatan kendala ({len(errors)} baris):")
                        for err in errors[:5]:
                            st.write(f"- {err}")
                    time.sleep(1.0)
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca berkas: {e}")

    with tab_data:
        st.markdown("##### 📋 Daftar Inisiatif Scope 4 Tersimpan")
        if st.session_state["scope4_data"]:
            df_s4_current = pd.DataFrame(st.session_state["scope4_data"])
            st.dataframe(df_s4_current, use_container_width=True)
            
            total_s4 = df_s4_current["avoided_tco2e"].sum()
            st.info(f"**Total Avoided Emissions & Offsetting:** {total_s4:,.4f} tCO2e dari {len(df_s4_current)} inisiatif.")
            
            if st.button("🗑️ Hapus Seluruh Data Scope 4"):
                st.session_state["scope4_data"] = []
                st.toast("Data Scope 4 berhasil dikosongkan.")
                st.rerun()
        else:
            st.info("Belum ada data Scope 4 tercatat.")


# ==============================================================================
# HALAMAN 6: EKSPOR LAPORAN & PANDUAN METODOLOGI
# ==============================================================================
elif menu == "📑 Ekspor Laporan & Panduan Metodologi":
    st.markdown("## 📑 Ekspor Laporan Emisi & Panduan Metodologi")
    st.caption("Unduh laporan inventarisasi emisi GRK resmi dalam berbagai format dan pelajari referensi standar teknis.")
    
    col_exp1, col_exp2 = st.columns([1, 1])
    
    with col_exp1:
        st.markdown("### 📥 Ekspor Laporan Resmi")
        st.write(f"""
        - **Entitas Pelapor:** {st.session_state['company_info'].get('entitas')}
        - **Tahun Pelaporan:** {st.session_state['company_info'].get('tahun')}
        - **Total Gross Emissions:** `{summary.gross_tco2e:,.2f} tCO2e`
        - **Total Avoided/Offsetting:** `{summary.scope4_tco2e:,.2f} tCO2e`
        - **Total Net Emissions:** `{summary.net_tco2e:,.2f} tCO2e`
        """)
        
        df_s1 = pd.DataFrame(st.session_state["scope1_data"])
        df_s2 = pd.DataFrame(st.session_state["scope2_data"])
        df_s3 = pd.DataFrame(st.session_state["scope3_data"])
        df_s4 = pd.DataFrame(st.session_state["scope4_data"])
        
        # 1. Tombol Unduh PDF
        try:
            pdf_bytes = rep.generate_pdf_report(
                summary, df_s1, df_s2, df_s3, df_s4,
                company_info=st.session_state["company_info"]
            )
            st.download_button(
                "📄 Unduh Laporan Eksekutif Resmi (PDF)",
                data=pdf_bytes,
                file_name=f"Laporan_Emisi_GRK_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Gagal menyiapkan laporan PDF: {e}")

        # 2. Tombol Unduh Excel
        try:
            excel_bytes = rep.generate_excel_report(
                summary, df_s1, df_s2, df_s3, df_s4,
                company_info=st.session_state["company_info"]
            )
            st.download_button(
                "📊 Unduh Lembar Kerja Lengkap (Excel .xlsx)",
                data=excel_bytes,
                file_name=f"Laporan_Emisi_GRK_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Gagal menyiapkan laporan Excel: {e}")

        # 3. Tombol Unduh CSV
        try:
            csv_str = rep.generate_consolidated_csv(summary, df_s1, df_s2, df_s3, df_s4)
            st.download_button(
                "📁 Unduh Data Terkonsolidasi (CSV)",
                data=csv_str,
                file_name=f"Konsolidasi_Emisi_GRK_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Gagal menyiapkan CSV: {e}")

    with col_exp2:
        st.markdown("### 📚 Panduan Metodologi Teknis (2026)")
        
        with st.expander("📖 1. Scope 1 (Emisi Langsung)", expanded=True):
            st.markdown("""
            **a. BBM Statis (Genset / Boiler / Dapur):**
            $$Emisi\\ (kgCO_2e) = Volume\\ \\times\\ Faktor\\ Emisi\\ BBM$$
            
            **b. Kendaraan Operasional (Jarak Tempuh):**
            $$Emisi\\ (kgCO_2e) = Jarak\\ Tempuh\\ (km)\\ \\times\\ \\left(\\frac{Faktor\\ Emisi\\ BBM}{Efisiensi\\ (km/L)}\\right)$$
            """)

        with st.expander("📖 2. Scope 2 (Emisi Pembelian Listrik)"):
            st.markdown("""
            **Pembelian Listrik PLN / Industri:**
            $$Emisi\\ (kgCO_2e) = Konsumsi\\ (kWh)\\ \\times\\ Faktor\\ Emisi\\ Grid\\ (kgCO_2e/kWh)$$
            - Default Grid Nasional: `0.79 kgCO2e/kWh`
            - Jamali (Jawa - Bali): `0.81 kgCO2e/kWh`
            - Sumatra: `0.76 kgCO2e/kWh`
            - Kalimantan: `0.83 kgCO2e/kWh`
            - Sulawesi: `0.72 kgCO2e/kWh`
            """)

        with st.expander("📖 3. Scope 3 (Financed Emissions - PCAF)"):
            st.markdown("""
            **Opsi A (Reported Emissions Debitur):**
            $$Financed\\ Emisi\\ (tCO_2e) = \\left(\\frac{Baki\\ Debet}{EVIC\\ atau\\ Total\\ Aset}\\right)\\ \\times\\ Total\\ Emisi\\ Debitur$$
            
            **Opsi B (Proksi Sektoral / Physical Activity):**
            $$Financed\\ Emisi\\ (tCO_2e) = Baki\\ Debet\\ (Juta\\ Rp)\\ \\times\\ FE\\ Sektoral\\ (tCO_2e / Juta\\ Rp)$$
            """)

        with st.expander("📖 4. Scope 4 (Avoided Emissions & Offsets)"):
            st.markdown("""
            **a. PLTS Atap / Solar PV:**
            $$Avoided\\ (tCO_2e) = \\frac{kWh\\ Generasi\\ \\times\\ FE\\ Grid}{1000}$$
            
            **b. Substitusi Armada Kendaraan Listrik (EV vs ICE):**
            $$Avoided\\ (kgCO_2e) = Emisi_{ICE\\ dihindari} - Emisi_{EV\\ pengisian}$$
            
            **c. Sertifikat Penurunan Emisi (SPE-GRK):**
            Offsetting terverifikasi 1-ke-1 dari bursa karbon resmi (IDXCarbon).
            """)

    st.markdown("---")
    st.markdown("#### 🔍 Tabel Referensi Faktor Emisi Tersedia")
    tab_r1, tab_r2, tab_r3 = st.tabs(["Faktor Emisi BBM", "Faktor Emisi Grid Listrik", "Faktor Emisi Sektoral Kredit"])
    with tab_r1:
        st.dataframe(df_fe_bbm, use_container_width=True, hide_index=True)
    with tab_r2:
        st.dataframe(df_fe_listrik, use_container_width=True, hide_index=True)
    with tab_r3:
        st.dataframe(df_fe_sektoral, use_container_width=True, hide_index=True)
