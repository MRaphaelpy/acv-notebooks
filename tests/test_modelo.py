"""Testes do modelo com números redondos de conferência (NÃO são dados do estudo).

    python3 -m unittest discover -s tests
"""
import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
import modelo  # noqa: E402
import potencia  # noqa: E402


def p_base(**kw):
    p = {"C_novo": 200.0, "EP_novo": 1000.0, "P_ant": 30.0, "P_novo": 10.0, "h": 2000.0,
         "FE_BR": 0.05, "FE_alt": 0.7, "FEP_BR": 1.5, "FEP_alt": 2.5, "CFV_ant": 0.0,
         "L_novo": 4.0, "m_ant": 2.0}
    p.update(kw)
    return p


class TestContas(unittest.TestCase):
    def test_t_estrela_de_cabeca(self):
        # ΔP 20 W = 0,02 kW × 2000 h = 40 kWh/ano × 0,05 = 2 kg/ano -> 200/2 = 100 anos
        self.assertAlmostEqual(modelo.t_estrela(200, 30, 10, 2000, 0.05), 100.0)

    def test_sem_economia(self):
        self.assertEqual(modelo.t_estrela(200, 10, 10, 2000, 0.05), float("inf"))

    def test_horas_dobradas_reduzem_t_pela_metade(self):
        t1 = modelo.t_estrela(200, 30, 10, 2000, 0.05)
        t2 = modelo.t_estrela(200, 30, 10, 4000, 0.05)
        self.assertAlmostEqual(t1 / t2, 2.0)

    def test_series_valores(self):
        p = p_base()
        s = modelo.series(p, p["FE_BR"], p["FEP_BR"], alocar=True)
        self.assertEqual(len(s["mes"]), 49)
        # A: 200 + 0,01 kW×2000 h×4 a×0,05 = 200 + 4 = 204
        self.assertAlmostEqual(s["A_co2"][-1], 204.0)
        # B: 0,03×2000×2×0,05 + 0,01×2000×2×0,05 + 200×(2/4) = 6 + 2 + 100 = 108
        self.assertAlmostEqual(s["B_co2"][-1], 108.0)
        self.assertEqual(s["B_res"][23], 0.0)
        self.assertEqual(s["B_res"][24], 2.0)

    def test_inversao_coerente_com_t_estrela(self):
        p = p_base()
        fe = modelo.fe_inversao(p)
        self.assertAlmostEqual(modelo.t_estrela(p["C_novo"], p["P_ant"], p["P_novo"], p["h"], fe), p["L_novo"])
        s = modelo.series(p, fe * 1.01, p["FEP_BR"], alocar=True)
        self.assertEqual(modelo.vencedor(s), "A (substituir)")
        s = modelo.series(p, fe * 0.99, p["FEP_BR"], alocar=True)
        self.assertEqual(modelo.vencedor(s), "B (prolongar)")


class TestLogs(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_powerstat(self):
        f = self.d / "x.log"
        f.write_text("Time    User  Nice   Sys  Idle    IO  Run Ctxt/s  IRQ/s  Watts\n"
                     "10:00:01   1.0   0.0   0.5  98.5   0.0    1    200    100   7.10\n"
                     "10:00:02   2.0   0.0   0.5  97.5   0.0    1    210    110   7.30\n")
        self.assertEqual([v for _, v in potencia.ler_log(f)], [7.10, 7.30])

    def test_log_constante_gera_alerta(self):
        pts = [(f"t{i}", 5.0) for i in range(600)]
        self.assertTrue(any("não varia" in a for a in potencia.validar(pts, "x")))


if __name__ == "__main__":
    unittest.main()
