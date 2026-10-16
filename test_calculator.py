"""
Unit Tests untuk modul calculator.py (Kalkulator Hijau V.2)
"""
import unittest
import pandas as pd
from calculator import (
    calc_scope1_stationary,
    calc_scope1_mobile_distance,
    calc_scope2_electricity,
    calc_scope3_reported,
    calc_scope3_sectoral,
    calc_scope4_solar_pv,
    calc_scope4_ev_avoided,
    calc_scope4_carbon_offset,
    calculate_overall_summary,
    validate_non_negative,
    load_fe_bbm,
    load_fe_listrik,
    load_fe_sektoral,
    process_bulk_scope1,
    process_bulk_scope2,
    process_bulk_scope3
)

class TestCalculatorHijau(unittest.TestCase):

    def test_load_data(self):
        df_bbm = load_fe_bbm()
        df_listrik = load_fe_listrik()
        df_sektoral = load_fe_sektoral()
        self.assertGreater(len(df_bbm), 5)
        self.assertGreater(len(df_listrik), 5)
        self.assertGreater(len(df_sektoral), 5)

    def test_validate_non_negative(self):
        self.assertEqual(validate_non_negative(10), 10.0)
        self.assertEqual(validate_non_negative(None), 0.0)
        self.assertEqual(validate_non_negative(pd.NA), 0.0)
        with self.assertRaises(ValueError):
            validate_non_negative(-5, "Test Nilai")

    def test_scope1_stationary(self):
        # 1000 Liter Solar Subsidi (2.18 kgCO2e/Liter)
        res = calc_scope1_stationary(volume=1000.0, faktor_emisi=2.18)
        self.assertAlmostEqual(res["emisi_kgco2e"], 2180.0, places=3)
        self.assertAlmostEqual(res["emisi_tco2e"], 2.180, places=4)

    def test_scope1_mobile_distance(self):
        # 1000 km, efisiensi 10 km/liter, FE 2.33 (Pertamax)
        # Liter = 1000 / 10 = 100 Liter
        # Emisi = 100 * 2.33 = 233 kgCO2e = 0.233 tCO2e
        res = calc_scope1_mobile_distance(
            jarak_km=1000.0,
            efisiensi_km_per_liter=10.0,
            faktor_emisi=2.33
        )
        self.assertAlmostEqual(res["konsumsi_liter"], 100.0, places=2)
        self.assertAlmostEqual(res["emisi_kgco2e"], 233.0, places=3)
        self.assertAlmostEqual(res["emisi_tco2e"], 0.233, places=4)

    def test_scope1_invalid_efficiency(self):
        with self.assertRaises(ValueError):
            calc_scope1_mobile_distance(jarak_km=100, efisiensi_km_per_liter=0, faktor_emisi=2.3)

    def test_scope2_electricity(self):
        # 10,000 kWh * 0.79 kgCO2e/kWh = 7,900 kgCO2e = 7.9 tCO2e
        res = calc_scope2_electricity(konsumsi_kwh=10000.0, faktor_emisi_grid=0.79)
        self.assertAlmostEqual(res["emisi_kgco2e"], 7900.0, places=2)
        self.assertAlmostEqual(res["emisi_tco2e"], 7.900, places=3)

    def test_scope3_reported(self):
        # Baki debet 20 Milyar, Total Aset/EVIC 100 Milyar (Attribution factor = 0.20)
        # Total Emisi Debitur = 500 tCO2e
        # Financed emission = 0.20 * 500 = 100 tCO2e
        res = calc_scope3_reported(
            baki_debet_rp=20_000_000_000,
            evic_atau_aset_rp=100_000_000_000,
            total_emisi_debitur_tco2e=500.0
        )
        self.assertAlmostEqual(res["attribution_factor"], 0.20, places=4)
        self.assertAlmostEqual(res["emisi_tco2e"], 100.0, places=3)

    def test_scope3_sectoral(self):
        # Baki debet Rp 5.000 Juta (5 Milyar) * 0.092 tCO2e/Juta Rp = 460 tCO2e
        res = calc_scope3_sectoral(
            baki_debet_juta_rp=5000.0,
            faktor_emisi_sektoral=0.092
        )
        self.assertAlmostEqual(res["emisi_tco2e"], 460.0, places=3)

    def test_scope4_solar(self):
        # 5,000 kWh * 0.79 kgCO2e/kWh = 3,950 kgCO2e = 3.95 tCO2e
        res = calc_scope4_solar_pv(kwh_dihasilkan=5000.0, faktor_emisi_grid=0.79)
        self.assertAlmostEqual(res["avoided_tco2e"], 3.950, places=3)

    def test_scope4_ev(self):
        # 10,000 km, ICE 10 km/L @ 2.31 kgCO2e/L = 1000 L * 2.31 = 2310 kgCO2e
        # EV 0.16 kWh/km @ 0.79 kgCO2e/kWh = 1600 kWh * 0.79 = 1264 kgCO2e
        # Avoided = 2310 - 1264 = 1046 kgCO2e = 1.046 tCO2e
        res = calc_scope4_ev_avoided(
            jarak_km=10000.0,
            efisiensi_ice_km_per_liter=10.0,
            fe_bbm_ice=2.31,
            konsumsi_ev_kwh_per_km=0.16,
            fe_listrik_grid=0.79
        )
        self.assertAlmostEqual(res["avoided_kgco2e"], 1046.0, places=2)
        self.assertAlmostEqual(res["avoided_tco2e"], 1.046, places=3)

    def test_scope4_carbon_offset(self):
        res = calc_scope4_carbon_offset(kredit_tco2e=50.0)
        self.assertEqual(res["avoided_tco2e"], 50.0)
        self.assertEqual(res["avoided_kgco2e"], 50000.0)

    def test_overall_summary(self):
        s1 = [calc_scope1_stationary(1000, 2.18)]  # 2.18 tCO2e
        s2 = [calc_scope2_electricity(10000, 0.79)] # 7.9 tCO2e
        s3 = [calc_scope3_sectoral(1000, 0.05)]     # 50 tCO2e
        s4 = [calc_scope4_solar_pv(5000, 0.79)]     # 3.95 tCO2e
        
        summary = calculate_overall_summary(s1, s2, s3, s4)
        gross_expected = 2.18 + 7.9 + 50.0 # 60.08
        self.assertAlmostEqual(summary.gross_tco2e, gross_expected, places=2)
        self.assertAlmostEqual(summary.scope4_tco2e, 3.95, places=2)
        self.assertAlmostEqual(summary.net_tco2e, gross_expected - 3.95, places=2)
        self.assertAlmostEqual(summary.offset_percentage, (3.95 / gross_expected) * 100.0, places=1)

if __name__ == "__main__":
    unittest.main()
