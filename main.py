"""
Punto de Entrada Principal (Entrypoint Orientado a Objetos).
Universidad José Antonio Páez - Métodos Cuantitativos
Modelo de Tamaño de la Fuerza de Trabajo mediante Programación Dinámica.

Uso:
    python main.py             # Inicia la interfaz gráfica moderna (GUI)
    python main.py --cli       # Ejecuta en terminal y exporta el reporte TXT
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Configurar encoding UTF-8 en consola Windows
if sys.platform == "win32" and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar importación del paquete src
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.models.problem import ProblemData
from src.solver.dp_solver import WorkforceDPSolver
from src.exporters.txt_exporter import TxtReportExporter


class WorkforceApplication:
    """
    Clase controladora de arranque y ciclo de vida de la aplicación.
    Administra la ejecución tanto en modo Gráfico (GUI) como en modo Consola (CLI).
    """

    def __init__(self, cli_mode: bool = False):
        self.cli_mode = cli_mode
        self.exporter = TxtReportExporter()

    @classmethod
    def from_args(cls, args: Optional[list] = None) -> "WorkforceApplication":
        """
        Método de fábrica (Factory Method) que procesa los argumentos de línea de comandos.
        """
        parser = argparse.ArgumentParser(
            description="Optimizador del Modelo de Tamaño de la Fuerza de Trabajo (Programación Dinámica - UJAP)"
        )
        parser.add_argument(
            "--cli",
            action="store_true",
            help="Ejecutar en modo consola sin levantar la interfaz gráfica"
        )
        parsed = parser.parse_args(args)
        return cls(cli_mode=parsed.cli)

    def run_cli(self) -> int:
        """
        Ejecuta el flujo completo en consola: resuelve el problema base
        y genera el reporte en formato TXT.
        """
        print("=" * 80)
        print(" UNIVERSIDAD JOSÉ ANTONIO PÁEZ - MÉTODOS CUANTITATIVOS")
        print(" PROGRAMACIÓN DINÁMICA: MODELO DE FUERZA DE TRABAJO")
        print("=" * 80)
        print("Cargando datos del problema oficial...")

        problem = ProblemData.create_default()
        solver = WorkforceDPSolver(problem)
        solution = solver.solve()

        print("\n✓ Solución óptima calculada:")
        print(f"  • Costo total mínimo: ${solution.total_cost:,.2f} ({solution.total_cost_hundreds:.0f} unidades)")
        print("\nCronograma Óptimo Semana a Semana:")
        for item in solution.schedule:
            print(
                f"  Semana {item.week}: {item.action_description:<32} "
                f"-> Asignados: {item.assigned_workforce} | Costo: ${item.week_total_cost:,.2f}"
            )

        txt_path = self.exporter.export(problem, solution)
        print(f"\n✓ Salida TXT generada exitosamente en:\n  {txt_path}")
        print(f"  {self.exporter.output_dir / 'salida_fuerza_trabajo_actual.txt'}")
        print("=" * 80)
        return 0

    def run_gui(self) -> int:
        """
        Inicia la aplicación en interfaz gráfica moderna con CustomTkinter.
        """
        from src.ui.app_window import WorkforceAppGUI

        app = WorkforceAppGUI()
        app.mainloop()
        return 0

    def run(self) -> int:
        """
        Punto de despacho principal según el modo configurado.
        """
        if self.cli_mode:
            return self.run_cli()

        try:
            return self.run_gui()
        except Exception as e:
            print(f"[!] Error al iniciar la interfaz gráfica: {e}")
            print("[*] Iniciando en modo consola alternativo (CLI)...")
            return self.run_cli()


if __name__ == "__main__":
    app = WorkforceApplication.from_args()
    sys.exit(app.run())
