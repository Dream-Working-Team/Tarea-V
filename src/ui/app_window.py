"""
Ventana Principal de la Aplicación (Orquestador de la GUI).
Integra componentes modulares: Sidebar, Barra KPI y Vistas de Pestañas.
"""

import os
from pathlib import Path
import subprocess
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from ..models.problem import ProblemData
from ..models.solution import WorkforceSolution
from ..solver.dp_solver import WorkforceDPSolver
from ..exporters.txt_exporter import TxtReportExporter

from .components.sidebar import SidebarFrame
from .components.kpi_bar import KPIBarFrame
from .views.schedule_view import ScheduleView
from .views.stages_view import StagesView
from .views.txt_preview_view import TxtPreviewView
from .views.theory_view import TheoryView


# Configuración estética global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class WorkforceAppGUI(ctk.CTk):
    """
    Ventana principal de la aplicación.
    Diseño profesional que orquesta la interacción entre componentes y la lógica de negocio.
    """

    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("Planificación de Fuerza de Trabajo | Programación Dinámica — UJAP")
        self.geometry("1240x820")
        self.minsize(1050, 720)

        # Servicios de dominio
        self.exporter = TxtReportExporter()
        self.current_problem: Optional[ProblemData] = None
        self.current_solution: Optional[WorkforceSolution] = None

        # Construcción visual
        self._build_layout()
        self.solve_problem(auto_export=False)

    def _build_layout(self) -> None:
        """Configura el grid principal y ensambla los componentes."""
        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Panel Lateral Izquierdo (Sidebar)
        self.sidebar = SidebarFrame(
            self,
            on_solve=self.solve_problem,
            on_export=self.export_txt,
            on_open_folder=self.open_output_folder
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Área Principal Derecha (Dashboard)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Barra Superior de Indicadores (KPIs)
        self.kpi_bar = KPIBarFrame(self.main_container)
        self.kpi_bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Pestañas del Dashboard
        self._build_tabs()

    def _build_tabs(self) -> None:
        """Crea el contenedor de pestañas y asocia las vistas modulares."""
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.grid(row=1, column=0, sticky="nsew")

        # Pestaña 1: Plan Óptimo Semanal
        tab_schedule_frame = self.tabview.add("📋 Plan Óptimo Semanal")
        tab_schedule_frame.grid_columnconfigure(0, weight=1)
        tab_schedule_frame.grid_rowconfigure(0, weight=1)
        self.view_schedule = ScheduleView(tab_schedule_frame)
        self.view_schedule.grid(row=0, column=0, sticky="nsew")

        # Pestaña 2: Tablas de Programación Dinámica
        tab_stages_frame = self.tabview.add("🧮 Tablas Paso a Paso (PD)")
        tab_stages_frame.grid_columnconfigure(0, weight=1)
        tab_stages_frame.grid_rowconfigure(0, weight=1)
        self.view_stages = StagesView(tab_stages_frame)
        self.view_stages.grid(row=0, column=0, sticky="nsew")

        # Pestaña 3: Visor de Salida TXT
        tab_txt_frame = self.tabview.add("📄 Visor de Salida TXT")
        tab_txt_frame.grid_columnconfigure(0, weight=1)
        tab_txt_frame.grid_rowconfigure(0, weight=1)
        self.view_txt = TxtPreviewView(tab_txt_frame)
        self.view_txt.grid(row=0, column=0, sticky="nsew")

        # Pestaña 4: Marco Teórico
        tab_theory_frame = self.tabview.add("📚 Fundamento Teórico")
        tab_theory_frame.grid_columnconfigure(0, weight=1)
        tab_theory_frame.grid_rowconfigure(0, weight=1)
        self.view_theory = TheoryView(tab_theory_frame)
        self.view_theory.grid(row=0, column=0, sticky="nsew")

    def solve_problem(self, auto_export: bool = False) -> None:
        """Ejecuta el algoritmo de programación dinámica y refresca las vistas."""
        try:
            problem = self.sidebar.parse_problem_data()
            solver = WorkforceDPSolver(problem)
            solution = solver.solve()

            self.current_problem = problem
            self.current_solution = solution

            # 1. Actualizar KPIs
            self.kpi_bar.update_metrics(problem, solution)

            # 2. Actualizar Vistas
            self.view_schedule.render(solution)
            self.view_stages.update_selector_options(len(problem.demands))
            self.view_stages.render(solution)

            # 3. Actualizar vista previa TXT
            report_text = self.exporter.generate_report_text(problem, solution)
            self.view_txt.update_content(
                report_text,
                "Reporte calculado en memoria. Presione 'Generar Salida TXT' para guardarlo."
            )

            if auto_export:
                self.export_txt(silent=True)

        except Exception as e:
            messagebox.showerror("Error en Parámetros", str(e))

    def export_txt(self, silent: bool = False) -> None:
        """Exporta el reporte paso a paso a un archivo .txt en la carpeta salidas/."""
        if not self.current_problem or not self.current_solution:
            self.solve_problem()

        target_path = self.exporter.export(self.current_problem, self.current_solution)
        status_msg = f"✓ Archivo generado exitosamente: {target_path.name}"
        self.view_txt.set_status(status_msg, is_success=True)

        if not silent:
            messagebox.showinfo(
                "Exportación Exitosa",
                f"El reporte paso a paso se ha guardado correctamente en:\n\n{target_path}\n\n"
                f"También se actualizó: salidas/salida_fuerza_trabajo_actual.txt"
            )

    def open_output_folder(self) -> None:
        """Abre la carpeta de salidas en el explorador de archivos del sistema operativo."""
        out_dir = self.exporter.output_dir
        if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(out_dir))
            else:
                subprocess.run(["xdg-open", str(out_dir)])
        except Exception as e:
            messagebox.showerror("Error al abrir carpeta", f"No se pudo abrir la carpeta: {e}")
