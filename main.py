"""
Punto de Entrada Principal (Entrypoint)
Universidad José Antonio Páez - Métodos Cuantitativos
Modelo de Tamaño de la Fuerza de Trabajo mediante Programación Dinámica

Uso:
    python main.py             # Inicia la interfaz gráfica moderna (GUI)
    python main.py --cli       # Ejecuta en terminal y exporta el reporte TXT
"""

import sys
import argparse
from pathlib import Path

# Configurar encoding UTF-8 en consola Windows
if sys.platform == "win32" and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar importación de src
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.models.problem import ProblemData
from src.solver.dp_solver import WorkforceDPSolver
from src.exporters.txt_exporter import TxtReportExporter


def run_cli_mode():
    """Ejecuta el programa en modo línea de comandos y genera la salida TXT."""
    print("=" * 80)
    print(" UNIVERSIDAD JOSÉ ANTONIO PÁEZ - MÉTODOS CUANTITATIVOS")
    print(" PROGRAMACIÓN DINÁMICA: MODELO DE FUERZA DE TRABAJO")
    print("=" * 80)
    print("Cargando datos del problema oficial...")

    problem = ProblemData.create_default()
    solver = WorkforceDPSolver(problem)
    solution = solver.solve()

    print(f"\n✓ Solución óptima calculada:")
    print(f"  • Costo total mínimo: ${solution.total_cost:,.2f} ({solution.total_cost_hundreds:.0f} unidades)")
    print("\nCronograma Óptimo:")
    for item in solution.schedule:
        print(f"  Semana {item.week}: {item.action_description} -> Asignados: {item.assigned_workforce} | Costo: ${item.week_total_cost:,.2f}")

    exporter = TxtReportExporter()
    txt_path = exporter.export(problem, solution)
    print(f"\n✓ Salida TXT generada exitosamente en:\n  {txt_path}")
    print(f"  {exporter.output_dir / 'salida_fuerza_trabajo_actual.txt'}")
    print("=" * 80)


def run_gui_mode():
    """Inicia la interfaz gráfica de usuario en CustomTkinter."""
    from src.ui.app_window import WorkforceAppGUI
    app = WorkforceAppGUI()
    app.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Optimizador de Fuerza de Trabajo por Programación Dinámica")
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo consola sin interfaz gráfica")
    args = parser.parse_args()

    if args.cli:
        run_cli_mode()
    else:
        try:
            run_gui_mode()
        except Exception as e:
            print(f"[!] Error al iniciar la interfaz gráfica: {e}")
            print("[*] Iniciando en modo consola alternativo (CLI)...")
            run_cli_mode()


if __name__ == "__main__":
    main()
