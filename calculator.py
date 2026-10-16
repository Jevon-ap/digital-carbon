"""
Modul Logika Perhitungan Emisi Gas Rumah Kaca (GRK)
Berdasarkan Pedoman Teknis "Kalkulator Hijau V.2 (2026)"
Standar GHG Protocol, ISO 14064, PCAF (Financed Emissions), dan OJK Taksonomi Hijau Indonesia.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np

# Path default dataset
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_FE_BBM_PATH = DATA_DIR / "fe_bbm.csv"
DEFAULT_FE_LISTRIK_PATH = DATA_DIR / "fe_listrik.csv"
DEFAULT_FE_SEKTORAL_PATH = DATA_DIR / "fe_sektoral.csv"

# Nilai default konstanta
DEFAULT_FE_GRID_NASIONAL = 0.7900  # kgCO2e / kWh
KG_TO_TON = 0.001


# ==============================================================================
# PRESET EFISIENSI KENDARAAN OPERASIONAL (km/Liter)
# ==============================================================================
VEHICLE_PRESETS: Dict[str, Dict[str, Union[float, str]]] = {
    "Sepeda Motor Bensin (Bebek / Skutik)": {
        "efisiensi": 40.0,
        "default_bbm": "Pertalite (RON 90)",
        "kategori": "Roda Dua"
    },
    "Mobil Penumpang Kecil / LCGC / City Car": {
        "efisiensi": 15.0,
        "default_bbm": "Pertalite (RON 90)",
        "kategori": "Roda Empat Ringan"
    },
    "Mobil Penumpang MPV / SUV Bensin": {
        "efisiensi": 10.5,
        "default_bbm": "Pertamax (RON 92)",
        "kategori": "Roda Empat Sedang"
    },
    "Mobil Penumpang SUV / Crossover Diesel": {
        "efisiensi": 11.5,
        "default_bbm": "Pertamina DEX (CN 53)",
        "kategori": "Roda Empat Diesel"
    },
    "Pikap / Kendaraan Niaga Ringan (Solar)": {
        "efisiensi": 9.5,
        "default_bbm": "Solar Subsidi / Biosolar B35",
        "kategori": "Niaga Ringan"
    },
    "Truk Sedang / Engkel / Box (Solar)": {
        "efisiensi": 6.5,
        "default_bbm": "Solar Subsidi / Biosolar B35",
        "kategori": "Truk Sedang"
    },
    "Truk Berat / Tronton / Trailer (Solar)": {
        "efisiensi": 3.5,
        "default_bbm": "Solar Subsidi / Biosolar B35",
        "kategori": "Truk Berat"
    },
    "Bus Operasional / Pariwisata (Solar)": {
        "efisiensi": 4.0,
        "default_bbm": "Solar Subsidi / Biosolar B35",
        "kategori": "Bus Angkutan"
    },
    "Kustom (Input Manual)": {
        "efisiensi": 10.0,
        "default_bbm": "Pertalite (RON 90)",
        "kategori": "Kustom"
    }
}


# ==============================================================================
# FUNGSI PEMUATAN DATA REFERENSI
# ==============================================================================
def load_fe_bbm(filepath: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Memuat tabel faktor emisi bahan bakar minyak dan gas."""
    path = Path(filepath) if filepath else DEFAULT_FE_BBM_PATH
    if not path.exists():
        raise FileNotFoundError(f"Berkas faktor emisi BBM tidak ditemukan: {path}")
    df = pd.read_csv(path)
    df["faktor_emisi"] = pd.to_numeric(df["faktor_emisi"], errors="coerce").fillna(0.0)
    return df


def load_fe_listrik(filepath: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Memuat tabel faktor emisi kelistrikan per wilayah grid."""
    path = Path(filepath) if filepath else DEFAULT_FE_LISTRIK_PATH
    if not path.exists():
        raise FileNotFoundError(f"Berkas faktor emisi listrik tidak ditemukan: {path}")
    df = pd.read_csv(path)
    df["faktor_emisi"] = pd.to_numeric(df["faktor_emisi"], errors="coerce").fillna(DEFAULT_FE_GRID_NASIONAL)
    return df


def load_fe_sektoral(filepath: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Memuat tabel faktor emisi pembiayaan sektoral (PCAF & OJK)."""
    path = Path(filepath) if filepath else DEFAULT_FE_SEKTORAL_PATH
    if not path.exists():
        raise FileNotFoundError(f"Berkas faktor emisi sektoral tidak ditemukan: {path}")
    df = pd.read_csv(path)
    df["faktor_emisi"] = pd.to_numeric(df["faktor_emisi"], errors="coerce").fillna(0.0)
    return df


# ==============================================================================
# FUNGSI VALIDASI INPUT
# ==============================================================================
def validate_non_negative(val: Union[int, float], name: str = "Nilai") -> float:
    """
    Memvalidasi agar nilai tidak boleh negatif dan bukan NaN.
    Jika None atau NaN, kembalikan 0.0.
    Jika bernilai negatif, lemparkan ValueError.
    """
    if val is None or pd.isna(val):
        return 0.0
    val_float = float(val)
    if val_float < 0:
        raise ValueError(f"{name} tidak boleh bernilai negatif: {val_float}")
    return val_float


# ==============================================================================
# 1. SCOPE 1 - EMISI LANGSUNG (DIRECT EMISSIONS)
# ==============================================================================
def calc_scope1_stationary(
    volume: float,
    faktor_emisi: float,
    deskripsi: str = "BBM Statis / Boiler / Genset",
    jenis_bbm: str = "Solar Subsidi / Biosolar B35",
    satuan: str = "Liter"
) -> Dict[str, Union[str, float]]:
    """
    Perhitungan Emisi Penggunaan BBM Statis (Genset/Boiler) & Peralatan Bergerak:
    Rumus: Emisi (kgCO2e) = Volume_BBM * Faktor_Emisi_BBM (kgCO2e per Liter/Kg)
    
    Returns:
        Dict hasil kalkulasi (kgCO2e, tCO2e, parameter).
    """
    vol = validate_non_negative(volume, "Volume BBM")
    fe = validate_non_negative(faktor_emisi, "Faktor Emisi BBM")
    
    emisi_kg = vol * fe
    emisi_ton = emisi_kg * KG_TO_TON
    
    return {
        "scope": "Scope 1",
        "sub_kategori": "BBM Statis / Industri",
        "deskripsi": deskripsi,
        "jenis_bbm": jenis_bbm,
        "volume": vol,
        "satuan": satuan,
        "faktor_emisi": fe,
        "emisi_kgco2e": round(emisi_kg, 4),
        "emisi_tco2e": round(emisi_ton, 6)
    }


def calc_scope1_mobile_distance(
    jarak_km: float,
    efisiensi_km_per_liter: float,
    faktor_emisi: float,
    jenis_kendaraan: str = "Mobil Penumpang MPV / SUV Bensin",
    jenis_bbm: str = "Pertamax (RON 92)",
    deskripsi: str = "Kendaraan Operasional Kantor"
) -> Dict[str, Union[str, float]]:
    """
    Perhitungan Kendaraan Operasional Berbasis Jarak Tempuh Terstandar:
    Rumus:
        Liter_Terkonsumsi = Jarak_Tempuh (km) / Efisiensi_BBM_Kendaraan (km/Liter)
        Emisi (kgCO2e) = Jarak_Tempuh * (Faktor_Emisi_BBM / Efisiensi_BBM_Kendaraan)
    
    Returns:
        Dict hasil kalkulasi (kgCO2e, tCO2e, konsumsi liter, parameter).
    """
    dist = validate_non_negative(jarak_km, "Jarak Tempuh (km)")
    eff = validate_non_negative(efisiensi_km_per_liter, "Efisiensi BBM (km/Liter)")
    fe = validate_non_negative(faktor_emisi, "Faktor Emisi BBM")
    
    if eff <= 0:
        raise ValueError("Efisiensi BBM kendaraan harus lebih besar dari 0 km/Liter.")
    
    liter_terkonsumsi = dist / eff
    emisi_kg = dist * (fe / eff)
    emisi_ton = emisi_kg * KG_TO_TON
    
    return {
        "scope": "Scope 1",
        "sub_kategori": "Kendaraan Operasional Bergerak",
        "deskripsi": deskripsi,
        "jenis_kendaraan": jenis_kendaraan,
        "jenis_bbm": jenis_bbm,
        "jarak_km": dist,
        "efisiensi_km_l": eff,
        "konsumsi_liter": round(liter_terkonsumsi, 4),
        "faktor_emisi": fe,
        "emisi_kgco2e": round(emisi_kg, 4),
        "emisi_tco2e": round(emisi_ton, 6)
    }


# ==============================================================================
# 2. SCOPE 2 - EMISI TIDAK LANGSUNG DARI LISTRIK (ELECTRICITY INDIRECT EMISSIONS)
# ==============================================================================
def calc_scope2_electricity(
    konsumsi_kwh: float,
    faktor_emisi_grid: float = DEFAULT_FE_GRID_NASIONAL,
    wilayah_grid: str = "Nasional (Rata-rata Grid Indonesia)",
    deskripsi: str = "Gedung Kantor / Fasilitas Operasional"
) -> Dict[str, Union[str, float]]:
    """
    Perhitungan Pembelian Listrik PLN / Industri:
    Rumus: Emisi (kgCO2e) = Konsumsi_Listrik (kWh) * Faktor_Emisi_Listrik (kgCO2e/kWh)
    
    Returns:
        Dict hasil kalkulasi (kgCO2e, tCO2e, parameter).
    """
    kwh = validate_non_negative(konsumsi_kwh, "Konsumsi Listrik (kWh)")
    fe = validate_non_negative(faktor_emisi_grid, "Faktor Emisi Listrik Grid")
    
    emisi_kg = kwh * fe
    emisi_ton = emisi_kg * KG_TO_TON
    
    return {
        "scope": "Scope 2",
        "sub_kategori": "Pembelian Listrik Jaringan",
        "deskripsi": deskripsi,
        "wilayah_grid": wilayah_grid,
        "konsumsi_kwh": kwh,
        "faktor_emisi_kwh": fe,
        "emisi_kgco2e": round(emisi_kg, 4),
        "emisi_tco2e": round(emisi_ton, 6)
    }


# ==============================================================================
# 3. SCOPE 3 - FINANCED EMISSIONS (EMISI TERBIAYAI SEKTOR KEUANGAN - PCAF)
# ==============================================================================
def calc_scope3_reported(
    baki_debet_rp: float,
    evic_atau_aset_rp: float,
    total_emisi_debitur_tco2e: float,
    nama_debitur: str = "Debitur Portofolio A",
    sektor: str = "Korporasi Manufaktur"
) -> Dict[str, Union[str, float]]:
    """
    Opsi A: Pendekatan Emisi Dilaporkan Debitur (Reported Emissions - PCAF)
    Rumus:
        Attribution_Factor = Nilai_Baki_Debet_Kredit / EVIC_atau_Total_Aset_Debitur
        Financed Emission (tCO2e) = Attribution_Factor * Total_Emisi_Debitur (tCO2e)
    """
    baki = validate_non_negative(baki_debet_rp, "Nilai Baki Debet Kredit (Rp)")
    aset = validate_non_negative(evic_atau_aset_rp, "EVIC atau Total Aset Debitur (Rp)")
    emisi_debitur = validate_non_negative(total_emisi_debitur_tco2e, "Total Emisi Debitur (tCO2e)")
    
    if aset <= 0:
        raise ValueError("EVIC / Total Aset Debitur harus lebih besar dari 0.")
    
    attribution_factor = baki / aset
    # Attribution factor tidak boleh bernilai negatif, biasanya maksimal 1.0 (100%)
    attribution_factor_clamped = min(max(attribution_factor, 0.0), 1.0)
    
    financed_ton = attribution_factor_clamped * emisi_debitur
    financed_kg = financed_ton * 1000.0
    
    return {
        "scope": "Scope 3",
        "metode": "Reported Emissions (PCAF Opsi A)",
        "nama_debitur": nama_debitur,
        "sektor": sektor,
        "baki_debet_rp": baki,
        "evic_atau_aset_rp": aset,
        "attribution_factor": round(attribution_factor_clamped, 6),
        "total_emisi_debitur_tco2e": emisi_debitur,
        "emisi_tco2e": round(financed_ton, 6),
        "emisi_kgco2e": round(financed_kg, 4)
    }


def calc_scope3_sectoral(
    baki_debet_juta_rp: float,
    faktor_emisi_sektoral: float,
    nama_debitur: str = "Debitur Sektoral B",
    kode_sektor: str = "C",
    nama_sektor: str = "Industri Manufaktur Kimia Logam Semen dan Kertas"
) -> Dict[str, Union[str, float]]:
    """
    Opsi B: Pendekatan Aktivitas Ekonomi / Proksi Sektoral (Physical/Economic Activity - PCAF)
    Rumus:
        Financed Emission (tCO2e) = Nilai_Baki_Debet_Kredit_dalam_Juta_Rp * Faktor_Emisi_Kredit_Sektoral (tCO2e per Juta Rp)
    """
    baki_juta = validate_non_negative(baki_debet_juta_rp, "Nilai Baki Debet (Juta Rp)")
    fe_sektor = validate_non_negative(faktor_emisi_sektoral, "Faktor Emisi Sektoral (tCO2e/Juta Rp)")
    
    financed_ton = baki_juta * fe_sektor
    financed_kg = financed_ton * 1000.0
    
    return {
        "scope": "Scope 3",
        "metode": "Proksi Sektoral (PCAF Opsi B)",
        "nama_debitur": nama_debitur,
        "kode_sektor": kode_sektor,
        "sektor": nama_sektor,
        "baki_debet_juta_rp": baki_juta,
        "faktor_emisi_sektoral": fe_sektor,
        "emisi_tco2e": round(financed_ton, 6),
        "emisi_kgco2e": round(financed_kg, 4)
    }


# ==============================================================================
# 4. SCOPE 4 - AVOIDED EMISSIONS & OFFSETTING (PENGURANGAN & PENURUNAN EMISI)
# ==============================================================================
def calc_scope4_solar_pv(
    kwh_dihasilkan: float,
    faktor_emisi_grid: float = DEFAULT_FE_GRID_NASIONAL,
    deskripsi: str = "Pembangkit Listrik Tenaga Surya (PLTS Atap)"
) -> Dict[str, Union[str, float]]:
    """
    Potensi Penghindaran Emisi dari Penggunaan Panel Surya / EBT:
    Rumus: Avoided Emissions (tCO2e) = (kWh_dihemat * Faktor_Emisi_Listrik_Grid) / 1000
    """
    kwh = validate_non_negative(kwh_dihasilkan, "Produksi/Penghematan Listrik EBT (kWh)")
    fe = validate_non_negative(faktor_emisi_grid, "Faktor Emisi Listrik Grid")
    
    avoided_kg = kwh * fe
    avoided_ton = avoided_kg * KG_TO_TON
    
    return {
        "scope": "Scope 4",
        "kategori": "EBT / PLTS Atap",
        "deskripsi": deskripsi,
        "kwh_generasi": kwh,
        "faktor_emisi_grid": fe,
        "avoided_kgco2e": round(avoided_kg, 4),
        "avoided_tco2e": round(avoided_ton, 6)
    }


def calc_scope4_ev_avoided(
    jarak_km: float,
    efisiensi_ice_km_per_liter: float = 12.0,
    fe_bbm_ice: float = 2.3100,  # Pertalite default
    konsumsi_ev_kwh_per_km: float = 0.16,  # rata-rata EV mobil penumpang
    fe_listrik_grid: float = DEFAULT_FE_GRID_NASIONAL,
    deskripsi: str = "Substitusi Armada Kendaraan Listrik (EV)"
) -> Dict[str, Union[str, float]]:
    """
    Potensi Pengurangan Emisi dari Substitusi Kendaraan Listrik (EV) vs Konvensional (ICE):
    Rumus:
        Emisi_ICE_Dihindari (kgCO2e) = Jarak_km * (FE_BBM / Efisiensi_ICE)
        Emisi_EV_Pengisian (kgCO2e) = Jarak_km * Konsumsi_EV (kWh/km) * FE_Grid
        Avoided_Net (kgCO2e) = max(0, Emisi_ICE_Dihindari - Emisi_EV_Pengisian)
    """
    dist = validate_non_negative(jarak_km, "Jarak Tempuh EV (km)")
    eff_ice = validate_non_negative(efisiensi_ice_km_per_liter, "Efisiensi ICE (km/L)")
    fe_bbm = validate_non_negative(fe_bbm_ice, "Faktor Emisi BBM ICE")
    cons_ev = validate_non_negative(konsumsi_ev_kwh_per_km, "Konsumsi Daya EV (kWh/km)")
    fe_grid = validate_non_negative(fe_listrik_grid, "Faktor Emisi Grid Listrik")
    
    if eff_ice <= 0:
        raise ValueError("Efisiensi ICE harus lebih besar dari 0.")
    
    emisi_ice_kg = dist * (fe_bbm / eff_ice)
    emisi_ev_kg = dist * cons_ev * fe_grid
    avoided_kg = max(0.0, emisi_ice_kg - emisi_ev_kg)
    avoided_ton = avoided_kg * KG_TO_TON
    
    return {
        "scope": "Scope 4",
        "kategori": "Kendaraan Listrik (EV)",
        "deskripsi": deskripsi,
        "jarak_km": dist,
        "emisi_ice_kgco2e": round(emisi_ice_kg, 4),
        "emisi_ev_kgco2e": round(emisi_ev_kg, 4),
        "avoided_kgco2e": round(avoided_kg, 4),
        "avoided_tco2e": round(avoided_ton, 6)
    }


def calc_scope4_carbon_offset(
    kredit_tco2e: float,
    penyedia_proyek: str = "Bursa Karbon Indonesia (IDXCarbon) / SPE-GRK",
    deskripsi: str = "Pembelian Sertifikat Penurunan Emisi GRK Terverifikasi",
    nomor_sertifikat: str = "SPE-GRK-2026-001"
) -> Dict[str, Union[str, float]]:
    """
    Pencatatan Pembelian Kredit Karbon / Sertifikat Penurunan Emisi (SPE-GRK):
    Rumus: Offsetting (tCO2e) = Jumlah Kredit Karbon Terverifikasi
    """
    kredit = validate_non_negative(kredit_tco2e, "Jumlah Kredit Karbon (tCO2e)")
    
    return {
        "scope": "Scope 4",
        "kategori": "Kredit Karbon / SPE-GRK",
        "deskripsi": deskripsi,
        "penyedia_proyek": penyedia_proyek,
        "nomor_sertifikat": nomor_sertifikat,
        "avoided_tco2e": round(kredit, 6),
        "avoided_kgco2e": round(kredit * 1000.0, 4)
    }


# ==============================================================================
# FUNGSI REKAPITULASI TOTAL & NET EMISSIONS
# ==============================================================================
@dataclass
class EmissionSummary:
    scope1_tco2e: float = 0.0
    scope2_tco2e: float = 0.0
    scope3_tco2e: float = 0.0
    scope4_tco2e: float = 0.0  # Avoided & Offset
    gross_tco2e: float = 0.0
    net_tco2e: float = 0.0
    offset_percentage: float = 0.0
    
    # Detail counts
    count_scope1: int = 0
    count_scope2: int = 0
    count_scope3: int = 0
    count_scope4: int = 0


def calculate_overall_summary(
    scope1_items: List[Dict],
    scope2_items: List[Dict],
    scope3_items: List[Dict],
    scope4_items: List[Dict]
) -> EmissionSummary:
    """
    Menghitung agregasi total dari seluruh scope:
    - Gross Emissions = Scope 1 + Scope 2 + Scope 3
    - Total Scope 4 (Avoided & Offsets)
    - Net Emissions = max(0, Gross - Scope 4)
    - Persentase Pengurangan = (Scope 4 / Gross) * 100%
    """
    s1 = sum(float(item.get("emisi_tco2e", 0.0)) for item in scope1_items)
    s2 = sum(float(item.get("emisi_tco2e", 0.0)) for item in scope2_items)
    s3 = sum(float(item.get("emisi_tco2e", 0.0)) for item in scope3_items)
    s4 = sum(float(item.get("avoided_tco2e", 0.0)) for item in scope4_items)
    
    gross = s1 + s2 + s3
    net = max(0.0, gross - s4)
    pct = (s4 / gross * 100.0) if gross > 0 else 0.0
    
    return EmissionSummary(
        scope1_tco2e=round(s1, 6),
        scope2_tco2e=round(s2, 6),
        scope3_tco2e=round(s3, 6),
        scope4_tco2e=round(s4, 6),
        gross_tco2e=round(gross, 6),
        net_tco2e=round(net, 6),
        offset_percentage=round(min(pct, 100.0), 2),
        count_scope1=len(scope1_items),
        count_scope2=len(scope2_items),
        count_scope3=len(scope3_items),
        count_scope4=len(scope4_items)
    )


# ==============================================================================
# FUNGSI PEMROSESAN MASSAL (BULK UPLOAD)
# ==============================================================================
def process_bulk_scope1(df: pd.DataFrame, df_fe_bbm: pd.DataFrame) -> Tuple[List[Dict], List[str]]:
    """
    Memproses DataFrame unggahan massal Scope 1.
    Format kolom yang didukung:
    - Tipe: 'Statis' atau 'Bergerak'
    - Deskripsi
    - Jenis BBM
    - Volume (jika statis)
    - Jarak_KM (jika bergerak)
    - Efisiensi_KM_L (jika bergerak)
    """
    items = []
    errors = []
    
    # Buat lookup faktor emisi
    fe_dict = dict(zip(df_fe_bbm["jenis_bbm"], df_fe_bbm["faktor_emisi"]))
    default_bbm = list(fe_dict.keys())[0]
    
    for idx, row in df.iterrows():
        row_num = idx + 1
        tipe = str(row.get("tipe", "Statis")).strip().capitalize()
        deskripsi = str(row.get("deskripsi", f"Kegiatan Scope 1 #{row_num}")).strip()
        jenis_bbm = str(row.get("jenis_bbm", default_bbm)).strip()
        fe = fe_dict.get(jenis_bbm, 2.3100)
        
        try:
            if "Statis" in tipe:
                vol = float(row.get("volume", 0.0))
                if vol < 0:
                    errors.append(f"Baris {row_num}: Volume tidak boleh negatif.")
                    continue
                satuan = str(row.get("satuan", "Liter")).strip()
                item = calc_scope1_stationary(vol, fe, deskripsi=deskripsi, jenis_bbm=jenis_bbm, satuan=satuan)
                items.append(item)
            else:
                jarak = float(row.get("jarak_km", 0.0))
                efisiensi = float(row.get("efisiensi_km_l", 10.0))
                if jarak < 0 or efisiensi <= 0:
                    errors.append(f"Baris {row_num}: Jarak >= 0 dan Efisiensi > 0 diperlukan.")
                    continue
                kendaraan = str(row.get("jenis_kendaraan", "Kendaraan Operasional")).strip()
                item = calc_scope1_mobile_distance(
                    jarak_km=jarak,
                    efisiensi_km_per_liter=efisiensi,
                    faktor_emisi=fe,
                    jenis_kendaraan=kendaraan,
                    jenis_bbm=jenis_bbm,
                    deskripsi=deskripsi
                )
                items.append(item)
        except Exception as e:
            errors.append(f"Baris {row_num}: Gagal diproses ({str(e)})")
            
    return items, errors


def process_bulk_scope2(df: pd.DataFrame, df_fe_listrik: pd.DataFrame) -> Tuple[List[Dict], List[str]]:
    """Memproses DataFrame unggahan massal Scope 2."""
    items = []
    errors = []
    
    fe_dict = dict(zip(df_fe_listrik["wilayah_grid"], df_fe_listrik["faktor_emisi"]))
    default_grid = list(fe_dict.keys())[0]
    
    for idx, row in df.iterrows():
        row_num = idx + 1
        deskripsi = str(row.get("deskripsi", f"Fasilitas Listrik #{row_num}")).strip()
        wilayah_grid = str(row.get("wilayah_grid", default_grid)).strip()
        fe = fe_dict.get(wilayah_grid, DEFAULT_FE_GRID_NASIONAL)
        
        try:
            kwh = float(row.get("konsumsi_kwh", 0.0))
            if kwh < 0:
                errors.append(f"Baris {row_num}: Konsumsi kWh tidak boleh negatif.")
                continue
            item = calc_scope2_electricity(kwh, fe, wilayah_grid=wilayah_grid, deskripsi=deskripsi)
            items.append(item)
        except Exception as e:
            errors.append(f"Baris {row_num}: Gagal diproses ({str(e)})")
            
    return items, errors


def process_bulk_scope3(df: pd.DataFrame, df_fe_sektoral: pd.DataFrame) -> Tuple[List[Dict], List[str]]:
    """Memproses DataFrame unggahan massal Scope 3 (Financed Emissions)."""
    items = []
    errors = []
    
    fe_sektor_dict = dict(zip(df_fe_sektoral["kode_sektor"], df_fe_sektoral["faktor_emisi"]))
    nama_sektor_dict = dict(zip(df_fe_sektoral["kode_sektor"], df_fe_sektoral["nama_sektor"]))
    
    for idx, row in df.iterrows():
        row_num = idx + 1
        metode = str(row.get("metode", "Sektoral")).strip().capitalize()
        nama_debitur = str(row.get("nama_debitur", f"Debitur #{row_num}")).strip()
        
        try:
            if "Reported" in metode:
                baki = float(row.get("baki_debet_rp", 0.0))
                aset = float(row.get("evic_atau_aset_rp", 1.0))
                emisi = float(row.get("total_emisi_debitur_tco2e", 0.0))
                sektor = str(row.get("sektor", "Korporasi")).strip()
                item = calc_scope3_reported(baki, aset, emisi, nama_debitur=nama_debitur, sektor=sektor)
                items.append(item)
            else:
                baki_juta = float(row.get("baki_debet_juta_rp", 0.0))
                kode = str(row.get("kode_sektor", "C")).strip().upper()
                fe = fe_sektor_dict.get(kode, 0.050)
                nama_sektor = nama_sektor_dict.get(kode, f"Sektor {kode}")
                item = calc_scope3_sectoral(baki_juta, fe, nama_debitur=nama_debitur, kode_sektor=kode, nama_sektor=nama_sektor)
                items.append(item)
        except Exception as e:
            errors.append(f"Baris {row_num}: Gagal diproses ({str(e)})")
            
    return items, errors


def process_bulk_scope4(df: pd.DataFrame) -> Tuple[List[Dict], List[str]]:
    """Memproses DataFrame unggahan massal Scope 4 (Avoided & Offsets)."""
    items = []
    errors = []
    
    for idx, row in df.iterrows():
        row_num = idx + 1
        kategori = str(row.get("kategori", "EBT")).strip()
        deskripsi = str(row.get("deskripsi", f"Inisiatif Scope 4 #{row_num}")).strip()
        
        try:
            if "EBT" in kategori or "Solar" in kategori or "PLTS" in kategori:
                kwh = float(row.get("kwh_generasi", 0.0))
                fe_grid = float(row.get("faktor_emisi_grid", DEFAULT_FE_GRID_NASIONAL))
                item = calc_scope4_solar_pv(kwh, fe_grid, deskripsi=deskripsi)
                items.append(item)
            elif "EV" in kategori or "Listrik" in kategori or "Armada" in kategori:
                jarak = float(row.get("jarak_km", 0.0))
                eff_ice = float(row.get("efisiensi_ice_km_per_liter", 12.0))
                fe_bbm = float(row.get("fe_bbm_ice", 2.31))
                cons_ev = float(row.get("konsumsi_ev_kwh_per_km", 0.16))
                fe_grid = float(row.get("fe_listrik_grid", DEFAULT_FE_GRID_NASIONAL))
                item = calc_scope4_ev_avoided(
                    jarak_km=jarak,
                    efisiensi_ice_km_per_liter=eff_ice,
                    fe_bbm_ice=fe_bbm,
                    konsumsi_ev_kwh_per_km=cons_ev,
                    fe_listrik_grid=fe_grid,
                    deskripsi=deskripsi
                )
                items.append(item)
            elif "Kredit" in kategori or "SPE" in kategori or "Offset" in kategori:
                kredit = float(row.get("kredit_tco2e", 0.0))
                penyedia = str(row.get("penyedia_proyek", "Bursa Karbon IDXCarbon")).strip()
                sertifikat = str(row.get("nomor_sertifikat", f"SPE-GRK-2026-{row_num:03d}")).strip()
                item = calc_scope4_carbon_offset(kredit, penyedia_proyek=penyedia, deskripsi=deskripsi, nomor_sertifikat=sertifikat)
                items.append(item)
            else:
                errors.append(f"Baris {row_num}: Kategori '{kategori}' tidak dikenali (Pilih: EBT, EV, atau Kredit Karbon).")
        except Exception as e:
            errors.append(f"Baris {row_num}: Gagal diproses ({str(e)})")
            
    return items, errors

