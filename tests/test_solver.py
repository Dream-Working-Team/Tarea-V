"""
Pruebas unitarias para validar el motor de Programación Dinámica y el Exportador TXT.
Verifica que la solución para el ejercicio oficial de la UJAP coincida al 100%
con la teoría y las láminas del profesor ($3,300 de costo total).
"""

import unittest
from pathlib import Path
import sys

# Permitir importación del paquete src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.problem import ProblemData, CostModel
from src.solver.dp_solver import WorkforceDPSolver
from src.exporters.txt_exporter import TxtReportExporter


class TestWorkforceDPSolver(unittest.TestCase):

    def setUp(self):
        self.problem = ProblemData.create_default()
        self.solver = WorkforceDPSolver(self.problem)

    def test_official_optimal_cost(self):
        """Verifica que el costo total óptimo sea exactamente $3,300 (33 unidades)."""
        solution = self.solver.solve()
        self.assertEqual(solution.total_cost, 3300.0)
        self.assertEqual(solution.total_cost_hundreds, 33.0)

    def test_official_optimal_schedule(self):
        """Verifica la trayectoria de decisiones semana por semana."""
        solution = self.solver.solve()
        expected_workforce = [5, 8, 8, 6, 6]
        expected_actions = ["CONTRATAR", "CONTRATAR", "MANTENER", "DESPEDIR", "MANTENER"]
        expected_costs = [1400.0, 1300.0, 0.0, 600.0, 0.0]

        self.assertEqual(len(solution.schedule), 5)
        for i, item in enumerate(solution.schedule):
            self.assertEqual(item.assigned_workforce, expected_workforce[i], f"Fallo en semana {i+1}")
            self.assertEqual(item.action_type, expected_actions[i], f"Fallo en acción semana {i+1}")
            self.assertEqual(item.week_total_cost, expected_costs[i], f"Fallo en costo semana {i+1}")

    def test_stage_5_optimal_values(self):
        """Verifica la Etapa 5 (x_4 -> x_5=6)."""
        solution = self.solver.solve()
        stage_5 = next(s for s in solution.stages if s.stage_num == 5)

        self.assertEqual(stage_5.optimal_costs[4], 800.0)
        self.assertEqual(stage_5.optimal_costs[5], 600.0)
        self.assertEqual(stage_5.optimal_costs[6], 0.0)

    def test_stage_1_optimal_values(self):
        """Verifica la Etapa 1 (x_0=0 -> min = 3300 en x_1=5)."""
        solution = self.solver.solve()
        stage_1 = next(s for s in solution.stages if s.stage_num == 1)

        self.assertEqual(stage_1.optimal_costs[0], 3300.0)
        self.assertEqual(stage_1.optimal_decisions[0], [5])

    def test_txt_export(self):
        """Verifica la generación correcta del archivo .txt en la carpeta salidas/."""
        solution = self.solver.solve()
        exporter = TxtReportExporter()
        output_file = exporter.export(self.problem, solution, "test_salida.txt")

        self.assertTrue(output_file.exists())
        content = output_file.read_text(encoding="utf-8")
        self.assertIn("COSTO TOTAL MÍNIMO DEL PROYECTO:", content)
        self.assertIn("$3,300.00", content)
        self.assertIn("ETAPA / SEMANA 5", content)
        self.assertIn("ETAPA / SEMANA 1", content)


if __name__ == "__main__":
    unittest.main()
