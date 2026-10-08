"""
Módulo de Interfaz Gráfica de Usuario (GUI) moderna con CustomTkinter.
Arquitectura Orientada a Objetos: Separa vistas, controladores y componentes.
"""

import os
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, List

import customtkinter as ctk

from ..models.problem import ProblemData, CostModel
from ..models.solution import WorkforceSolution, StageResult
from ..solver.dp_solver import WorkforceDPSolver
from ..exporters.txt_exporter import TxtReportExporter


# Configuración estética global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MetricCard(ctk.CTkFrame):
    """Componente reutilizable para tarjetas de métricas / KPI."""

    def __init__(self, master, title: str, value: str, subtitle: str = "", **kwargs):
        super().__init__(master, corner_radius=10, fg_color=("gray85", "#1f2937"), **kwargs)
        self.title_label = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "#9ca3af")
        )
        self.title_label.pack(padx=14, pady=(10, 2), anchor="w")

        self.value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("gray10", "#38bdf8")
        )
        self.value_label.pack(padx=14, pady=(0, 2), anchor="w")

        self.sub_label = ctk.CTkLabel(
            self, text=subtitle, font=ctk.CTkFont(size=11),
            text_color=("gray50", "#6b7280")
        )
        self.sub_label.pack(padx=14, pady=(0, 10), anchor="w")

    def update_values(self, value: str, subtitle: str = ""):
        self.value_label.configure(text=value)
        if subtitle:
            self.sub_label.configure(text=subtitle)


class WorkforceAppGUI(ctk.CTk):
    """
    Ventana principal de la aplicación.
    Diseño profesional con panel lateral de control y dashboard con pestañas.
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

        # Inicialización de la vista
        self._build_layout()
        self._set_default_inputs()
        self.solve_problem(auto_export=False)

    def _build_layout(self):
        """Construye la distribución principal (Sidebar + Main Content)."""
        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Panel Lateral Izquierdo (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(20, weight=1)

        self._build_sidebar_content()

        # 2. Área Principal Derecha (Dashboard)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._build_kpi_bar()
        self._build_tabview()

    def _build_sidebar_content(self):
        """Construye los controles y campos en el panel lateral."""
        # Encabezado
        logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="UNIVERSIDAD JOSÉ ANTONIO PÁEZ",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1e3a8a", "#60a5fa")
        )
        logo_label.pack(padx=20, pady=(20, 2), anchor="w")

        sub_header = ctk.CTkLabel(
            self.sidebar_frame,
            text="Métodos Cuantitativos • Programación Dinámica",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#9ca3af")
        )
        sub_header.pack(padx=20, pady=(0, 14), anchor="w")

        sep = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color=("gray75", "#374151"))
        sep.pack(fill="x", padx=16, pady=(0, 14))

        # Título Sección Entradas
        section_lbl = ctk.CTkLabel(
            self.sidebar_frame,
            text="PARÁMETROS DEL MODELO",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        section_lbl.pack(padx=20, pady=(0, 8), anchor="w")

        # Scrollframe para inputs por si la resolución es menor
        self.inputs_frame = ctk.CTkScrollableFrame(self.sidebar_frame, height=310, fg_color="transparent")
        self.inputs_frame.pack(fill="x", padx=12, pady=0)

        # Inputs
        self.entry_demands = self._create_input_field(
            "Demandas por semana (b_i):",
            "Separadas por coma: ej. 5, 7, 8, 4, 6"
        )
        self.entry_surplus_cost = self._create_input_field(
            "Costo mano obra excedente ($/sem):",
            "300"
        )
        self.entry_hiring_fixed = self._create_input_field(
            "Costo fijo de contratación ($):",
            "400"
        )
        self.entry_hiring_var = self._create_input_field(
            "Costo variable contratación ($/trab):",
            "200"
        )
        self.entry_initial_workforce = self._create_input_field(
            "Fuerza laboral inicial (x_0):",
            "0"
        )

        # Botones de Acción
        btn_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(14, 0))

        self.btn_solve = ctk.CTkButton(
            btn_frame,
            text="▶ Resolver Problema",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=36,
            command=self.solve_problem
        )
        self.btn_solve.pack(fill="x", pady=4)

        self.btn_export = ctk.CTkButton(
            btn_frame,
            text="📄 Generar Salida TXT",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=34,
            command=self.export_txt
        )
        self.btn_export.pack(fill="x", pady=4)

        self.btn_reset = ctk.CTkButton(
            btn_frame,
            text="🔄 Restablecer Valores",
            fg_color=("gray75", "#374151"),
            hover_color=("gray65", "#4b5563"),
            height=32,
            command=self._set_default_inputs
        )
        self.btn_reset.pack(fill="x", pady=4)

        self.btn_open_folder = ctk.CTkButton(
            btn_frame,
            text="📂 Abrir Carpeta Salidas",
            fg_color=("gray75", "#374151"),
            hover_color=("gray65", "#4b5563"),
            height=32,
            command=self.open_output_folder
        )
        self.btn_open_folder.pack(fill="x", pady=4)

        # Footer con apariencia
        footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=16, pady=16)

        mode_lbl = ctk.CTkLabel(footer_frame, text="Modo Visual:", font=ctk.CTkFont(size=11))
        mode_lbl.pack(side="left", padx=4)

        self.mode_menu = ctk.CTkOptionMenu(
            footer_frame,
            values=["Oscuro (Dark)", "Claro (Light)"],
            width=130,
            height=26,
            command=self._change_appearance_mode
        )
        self.mode_menu.pack(side="right", padx=4)
        self.mode_menu.set("Oscuro (Dark)")

    def _create_input_field(self, label_text: str, placeholder: str = "") -> ctk.CTkEntry:
        """Crea un campo de entrada con su etiqueta asociada."""
        lbl = ctk.CTkLabel(
            self.inputs_frame,
            text=label_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        lbl.pack(fill="x", padx=4, pady=(6, 1))

        entry = ctk.CTkEntry(
            self.inputs_frame,
            placeholder_text=placeholder,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        entry.pack(fill="x", padx=4, pady=(0, 4))
        return entry

    def _build_kpi_bar(self):
        """Construye la barra superior con tarjetas de resumen / KPI."""
        self.kpi_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for i in range(4):
            self.kpi_frame.grid_columnconfigure(i, weight=1)

        self.card_cost = MetricCard(self.kpi_frame, "COSTO TOTAL MÍNIMO", "$3,300.00", "33 unidades ($100)")
        self.card_cost.grid(row=0, column=0, sticky="ew", padx=4)

        self.card_weeks = MetricCard(self.kpi_frame, "DURACIÓN PROYECTO", "5 Semanas", "Etapas evaluadas")
        self.card_weeks.grid(row=0, column=1, sticky="ew", padx=4)

        self.card_peak = MetricCard(self.kpi_frame, "PICO DE PERSONAL", "8 Trabajadores", "Semana 2 y 3")
        self.card_peak.grid(row=0, column=2, sticky="ew", padx=4)

        self.card_status = MetricCard(self.kpi_frame, "ESTADO BELLMAN", "Óptimo Global", "Inducción hacia atrás")
        self.card_status.grid(row=0, column=3, sticky="ew", padx=4)

    def _build_tabview(self):
        """Construye el contenedor de pestañas principal."""
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=1, column=0, sticky="nsew")

        self.tab_schedule = self.tabview.add("📋 Plan Óptimo Semanal")
        self.tab_stages = self.tabview.add("🧮 Tablas Paso a Paso (PD)")
        self.tab_txt = self.tabview.add("📄 Visor de Salida TXT")
        self.tab_theory = self.tabview.add("📚 Fundamento Teórico")

        self._build_schedule_tab()
        self._build_stages_tab()
        self._build_txt_tab()
        self._build_theory_tab()

    def _build_schedule_tab(self):
        """Pestaña 1: Plan Óptimo Semanal."""
        self.tab_schedule.grid_columnconfigure(0, weight=1)
        self.tab_schedule.grid_rowconfigure(1, weight=1)

        header_lbl = ctk.CTkLabel(
            self.tab_schedule,
            text="Cronograma de Asignación de Fuerza de Trabajo y Costos Semanales",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 8))

        self.schedule_scroll = ctk.CTkScrollableFrame(self.tab_schedule)
        self.schedule_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def _build_stages_tab(self):
        """Pestaña 2: Tablas de Programación Dinámica paso a paso."""
        self.tab_stages.grid_columnconfigure(0, weight=1)
        self.tab_stages.grid_rowconfigure(1, weight=1)

        # Barra de control para seleccionar etapa
        control_bar = ctk.CTkFrame(self.tab_stages, fg_color="transparent")
        control_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 8))

        sel_lbl = ctk.CTkLabel(control_bar, text="Seleccionar Etapa:", font=ctk.CTkFont(size=12, weight="bold"))
        sel_lbl.pack(side="left", padx=(0, 8))

        self.stage_selector = ctk.CTkSegmentedButton(
            control_bar,
            values=["Semana 5", "Semana 4", "Semana 3", "Semana 2", "Semana 1", "Todas las Etapas"],
            command=self._on_stage_selection_changed
        )
        self.stage_selector.pack(side="left", fill="x", expand=True, padx=4)
        self.stage_selector.set("Todas las Etapas")

        self.stages_scroll = ctk.CTkScrollableFrame(self.tab_stages)
        self.stages_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def _build_txt_tab(self):
        """Pestaña 3: Visor del archivo de salida TXT."""
        self.tab_txt.grid_columnconfigure(0, weight=1)
        self.tab_txt.grid_rowconfigure(1, weight=1)

        action_bar = ctk.CTkFrame(self.tab_txt, fg_color="transparent")
        action_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 8))

        self.txt_status_lbl = ctk.CTkLabel(
            action_bar,
            text="Listo para exportar reporte.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "#9ca3af")
        )
        self.txt_status_lbl.pack(side="left")

        btn_copy = ctk.CTkButton(
            action_bar,
            text="📋 Copiar Todo",
            width=110,
            height=28,
            command=self._copy_txt_to_clipboard
        )
        btn_copy.pack(side="right", padx=4)

        btn_save_as = ctk.CTkButton(
            action_bar,
            text="💾 Guardar Como...",
            width=130,
            height=28,
            command=self._save_txt_as
        )
        btn_save_as.pack(side="right", padx=4)

        self.txt_textbox = ctk.CTkTextbox(
            self.tab_txt,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.txt_textbox.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def _build_theory_tab(self):
        """Pestaña 4: Documentación teórica del modelo de la UJAP."""
        self.tab_theory.grid_columnconfigure(0, weight=1)
        self.tab_theory.grid_rowconfigure(0, weight=1)

        theory_box = ctk.CTkTextbox(
            self.tab_theory,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        theory_box.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        theory_text = """
UNIVERSIDAD JOSÉ ANTONIO PÁEZ
FACULTAD DE INGENIERÍA - ESCUELA DE COMPUTACIÓN
CÁTEDRA: MÉTODOS CUANTITATIVOS
TEMA: PROGRAMACIÓN DINÁMICA - MODELO DE TAMAÑO DE LA FUERZA DE TRABAJO

1. DEFINICIÓN DEL MODELO
El modelo de tamaño de la fuerza laboral se aplica para determinar la cantidad de trabajadores a contratar o despedir semana a semana durante la ejecución de un proyecto con duración de n semanas.
El objetivo principal es MINIMIZAR el costo total de mano de obra requerido a lo largo de todo el horizonte temporal.

2. ELEMENTOS DE PROGRAMACIÓN DINÁMICA
• Etapas (i): Cada una de las semanas del proyecto (i = 1, 2, ..., n). La resolución se realiza mediante Inducción Hacia Atrás (Backward Induction), desde la última semana hasta la primera (i = n down to 1).
• Variable de Decisión (x_i): Cantidad total de trabajadores contratados/activos durante la semana i.
  Restricción: x_i >= b_i (se debe satisfacer siempre la demanda mínima de mano de obra b_i).
  Cota superior admisible: x_i <= max_{k >= i} b_k (no es óptimo mantener más que la demanda futura máxima).
• Variable de Estado (x_{i-1}): Cantidad de trabajadores disponibles que provienen de la semana anterior (x_0 = 0 por condición inicial).

3. FUNCIONES DE COSTO (EN CIENTOS DE DÓLARES)
• Costo por Excedente C1(x_i - b_i):
    C1 = 3 * (x_i - b_i)   si x_i > b_i
    C1 = 0                 si x_i = b_i
    (Representa $300 por cada trabajador excedente por semana).

• Costo por Contratación C2(x_i - x_{i-1}):
    C2 = 4 + 2 * (x_i - x_{i-1})   si x_i > x_{i-1}
    C2 = 0                         si x_i <= x_{i-1}
    (Representa un costo fijo de $400 más $200 por cada trabajador contratado).

• Costo por Despido:
    No se incurre en costo al despedir trabajadores (costo = $0).

4. ECUACIÓN RECURSIVA DE BELLMAN
    f_i(x_{i-1}) = min { C1(x_i - b_i) + C2(x_i - x_{i-1}) + f_{i+1}(x_i) }
    para x_i >= b_i, con f_{n+1}(x_n) = 0.

5. RAZÓN DE LA POLÍTICA ÓPTIMA DE LA TAREA
• Semana 1 (b_1=5): Se contratan 5 trabajadores (Costo: $1,400).
• Semana 2 (b_2=7): Es más rentable contratar 3 (llegar a 8) que solo 2, porque conservar 1 excedente ($300) evita pagar el costo fijo de contratación ($400) en la Semana 3 donde b_3=8.
• Semana 4 (b_4=4): Ante la reducción a 4 trabajadores, es óptimo despedir solo 2 y conservar 6, evitando volver a contratar en la Semana 5 donde b_5=6.
• Costo Total Mínimo: $3,300 (33 cientos de dólares).
"""
        theory_box.insert("1.0", theory_text.strip())
        theory_box.configure(state="disabled")

    def _set_default_inputs(self):
        """Carga los valores por defecto del ejercicio en los campos de entrada."""
        self.entry_demands.delete(0, tk.END)
        self.entry_demands.insert(0, "5, 7, 8, 4, 6")

        self.entry_surplus_cost.delete(0, tk.END)
        self.entry_surplus_cost.insert(0, "300")

        self.entry_hiring_fixed.delete(0, tk.END)
        self.entry_hiring_fixed.insert(0, "400")

        self.entry_hiring_var.delete(0, tk.END)
        self.entry_hiring_var.insert(0, "200")

        self.entry_initial_workforce.delete(0, tk.END)
        self.entry_initial_workforce.insert(0, "0")

    def _parse_inputs(self) -> ProblemData:
        """Lee y valida los valores ingresados por el usuario."""
        raw_demands = self.entry_demands.get().strip()
        if not raw_demands:
            raise ValueError("Por favor ingrese las demandas mínimas semanales.")

        try:
            demands = [int(x.strip()) for x in raw_demands.split(",") if x.strip()]
        except ValueError:
            raise ValueError("Las demandas deben ser números enteros separados por comas (ej: 5, 7, 8, 4, 6).")

        try:
            surplus_cost = float(self.entry_surplus_cost.get().strip())
            hiring_fixed = float(self.entry_hiring_fixed.get().strip())
            hiring_var = float(self.entry_hiring_var.get().strip())
            initial_wf = int(self.entry_initial_workforce.get().strip())
        except ValueError:
            raise ValueError("Los costos y fuerza inicial deben ser valores numéricos válidos.")

        cost_model = CostModel(
            surplus_cost_per_worker=surplus_cost,
            hiring_fixed_cost=hiring_fixed,
            hiring_variable_cost=hiring_var,
            firing_cost_per_worker=0.0
        )
        problem = ProblemData(
            demands=demands,
            cost_model=cost_model,
            initial_workforce=initial_wf
        )
        problem.validate()
        return problem

    def solve_problem(self, auto_export: bool = False):
        """Resuelve el problema y actualiza todas las vistas."""
        try:
            problem = self._parse_inputs()
            solver = WorkforceDPSolver(problem)
            solution = solver.solve()

            self.current_problem = problem
            self.current_solution = solution

            # Actualizar KPIs
            self.card_cost.update_values(
                f"${solution.total_cost:,.2f}",
                f"{solution.total_cost_hundreds:,.2f} unidades ($100)"
            )
            self.card_weeks.update_values(
                f"{len(problem.demands)} Semanas",
                f"Horizonte evaluado"
            )
            max_assigned = max(item.assigned_workforce for item in solution.schedule)
            self.card_peak.update_values(
                f"{max_assigned} Trabajadores",
                "Máximo simultáneo"
            )

            # Renderizar Vistas
            self._render_schedule_table(solution)
            self._render_stages_view(solution)
            self._update_txt_preview(problem, solution)

            if auto_export:
                self.export_txt(silent=True)

        except Exception as e:
            messagebox.showerror("Error en Parámetros", str(e))

    def _render_schedule_table(self, solution: WorkforceSolution):
        """Renderiza la tabla estilizada del plan óptimo semanal."""
        for widget in self.schedule_scroll.winfo_children():
            widget.destroy()

        # Encabezados de columnas
        headers = [
            "Semana", "Demanda (b_i)", "Personal (x_i*)", "Decisión Operativa",
            "Excedente ($)", "Contratación ($)", "Costo Semanal ($)", "Costo Acumulado ($)"
        ]
        header_frame = ctk.CTkFrame(self.schedule_scroll, fg_color=("gray80", "#1e293b"), corner_radius=6)
        header_frame.pack(fill="x", pady=(0, 6), padx=4)

        for col_idx, h_text in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=h_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=120 if col_idx != 3 else 220,
                anchor="center"
            )
            lbl.pack(side="left", padx=4, pady=6)

        # Filas de datos
        for idx, item in enumerate(solution.schedule):
            bg_color = ("gray90", "#111827") if idx % 2 == 0 else ("gray85", "#1f2937")
            row_frame = ctk.CTkFrame(self.schedule_scroll, fg_color=bg_color, corner_radius=6)
            row_frame.pack(fill="x", pady=2, padx=4)

            # Color del badge según la acción
            badge_color = "#38bdf8" if item.action_type == "CONTRATAR" else (
                "#f97316" if item.action_type == "DESPEDIR" else "#94a3b8"
            )

            cols_data = [
                (f"Semana {item.week}", 120, None),
                (str(item.min_demand), 120, None),
                (str(item.assigned_workforce), 120, "#38bdf8"),
                (item.action_description, 220, badge_color),
                (f"${item.surplus_cost:,.0f}", 120, None),
                (f"${item.hiring_cost:,.0f}", 120, None),
                (f"${item.week_total_cost:,.0f}", 120, "#34d399"),
                (f"${item.cumulative_cost:,.0f}", 120, None),
            ]

            for text_val, width_val, text_col in cols_data:
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=text_val,
                    font=ctk.CTkFont(size=12, weight="bold" if text_col else "normal"),
                    text_color=text_col if text_col else ("gray10", "gray90"),
                    width=width_val,
                    anchor="center"
                )
                lbl.pack(side="left", padx=4, pady=8)

        # Fila Total
        total_frame = ctk.CTkFrame(self.schedule_scroll, fg_color=("#0284c7", "#0369a1"), corner_radius=6)
        total_frame.pack(fill="x", pady=(8, 4), padx=4)

        total_lbl = ctk.CTkLabel(
            total_frame,
            text=f"COSTO TOTAL MÍNIMO DEL PROYECTO: ${solution.total_cost:,.2f}  ({solution.total_cost_hundreds:.0f} unidades)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        )
        total_lbl.pack(pady=10)

    def _render_stages_view(self, solution: WorkforceSolution):
        """Renderiza las tablas de programación dinámica para cada etapa."""
        for widget in self.stages_scroll.winfo_children():
            widget.destroy()

        current_filter = self.stage_selector.get()
        sorted_stages = sorted(solution.stages, key=lambda s: s.stage_num, reverse=True)

        for stage in sorted_stages:
            stage_name = f"Semana {stage.stage_num}"
            if current_filter != "Todas las Etapas" and current_filter != stage_name:
                continue

            stage_card = ctk.CTkFrame(self.stages_scroll, corner_radius=8, fg_color=("gray85", "#1e293b"))
            stage_card.pack(fill="x", pady=8, padx=4)

            # Título de etapa
            title_frame = ctk.CTkFrame(stage_card, fg_color="transparent")
            title_frame.pack(fill="x", padx=12, pady=(10, 6))

            t_lbl = ctk.CTkLabel(
                title_frame,
                text=f"ETAPA {stage.stage_num} (Semana {stage.stage_num}) — Demanda mínima b_{stage.stage_num} = {stage.min_demand}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#0284c7", "#38bdf8")
            )
            t_lbl.pack(side="left")

            # Tabla de decisiones
            # Header
            tbl_frame = ctk.CTkFrame(stage_card, fg_color=("gray90", "#0f172a"), corner_radius=6)
            tbl_frame.pack(fill="x", padx=12, pady=(0, 12))

            h_row = ctk.CTkFrame(tbl_frame, fg_color=("gray80", "#1e293b"))
            h_row.pack(fill="x", padx=4, pady=4)

            ctk.CTkLabel(h_row, text=f"x_{stage.stage_num - 1}", width=70, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
            for d in stage.decision_values:
                ctk.CTkLabel(
                    h_row, text=f"x_{stage.stage_num}={d}", width=190, font=ctk.CTkFont(weight="bold")
                ).pack(side="left", padx=2)
            ctk.CTkLabel(h_row, text=f"f_{stage.stage_num} ($100)", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
            ctk.CTkLabel(h_row, text=f"f_{stage.stage_num} ($)", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
            ctk.CTkLabel(h_row, text=f"x_{stage.stage_num}*", width=70, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)

            for s in stage.state_values:
                d_row = ctk.CTkFrame(tbl_frame, fg_color=("gray95", "#1e2937"))
                d_row.pack(fill="x", padx=4, pady=2)

                ctk.CTkLabel(d_row, text=str(s), width=70, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
                for d in stage.decision_values:
                    eval_item = stage.get_eval(s, d)
                    if eval_item:
                        text_val = eval_item.arithmetic_breakdown_hundreds
                        is_opt = eval_item.is_optimal
                        col = "#34d399" if is_opt else None
                        txt = f"{text_val} ★" if is_opt else text_val
                    else:
                        txt = "-"
                        col = None

                    ctk.CTkLabel(
                        d_row, text=txt, width=190, text_color=col,
                        font=ctk.CTkFont(weight="bold" if col else "normal")
                    ).pack(side="left", padx=2)

                opt_c_h = stage.optimal_costs[s] / 100.0
                opt_c_d = stage.optimal_costs[s]
                opt_decs = ",".join(map(str, stage.optimal_decisions[s]))

                ctk.CTkLabel(
                    d_row, text=f"{opt_c_h:.0f}", width=100, text_color="#38bdf8", font=ctk.CTkFont(weight="bold")
                ).pack(side="left", padx=2)
                ctk.CTkLabel(
                    d_row, text=f"${opt_c_d:,.0f}", width=100, text_color="#34d399", font=ctk.CTkFont(weight="bold")
                ).pack(side="left", padx=2)
                ctk.CTkLabel(
                    d_row, text=opt_decs, width=70, text_color="#f59e0b", font=ctk.CTkFont(weight="bold")
                ).pack(side="left", padx=2)

    def _on_stage_selection_changed(self, value: str):
        if self.current_solution:
            self._render_stages_view(self.current_solution)

    def _update_txt_preview(self, problem: ProblemData, solution: WorkforceSolution):
        """Actualiza el texto en la pestaña de vista previa TXT."""
        report_text = self.exporter.generate_report_text(problem, solution)
        self.txt_textbox.delete("1.0", tk.END)
        self.txt_textbox.insert("1.0", report_text)
        self.txt_status_lbl.configure(text=f"Reporte calculado en memoria. Presione 'Generar Salida TXT' para guardarlo.")

    def export_txt(self, silent: bool = False):
        """Exporta el reporte a un archivo .txt en la carpeta salidas/."""
        if not self.current_problem or not self.current_solution:
            self.solve_problem()

        target_path = self.exporter.export(self.current_problem, self.current_solution)
        status_msg = f"✓ Archivo generado exitosamente: {target_path.name}"
        self.txt_status_lbl.configure(text=status_msg, text_color="#34d399")

        if not silent:
            messagebox.showinfo(
                "Exportación Exitosa",
                f"El reporte paso a paso se ha guardado correctamente en:\n\n{target_path}\n\n"
                f"También se actualizó: salidas/salida_fuerza_trabajo_actual.txt"
            )

    def open_output_folder(self):
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

    def _copy_txt_to_clipboard(self):
        """Copia todo el texto del reporte al portapapeles."""
        text = self.txt_textbox.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", "Contenido del reporte copiado al portapapeles.")

    def _save_txt_as(self):
        """Permite al usuario guardar el reporte en una ruta personalizada."""
        text = self.txt_textbox.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile="reporte_fuerza_trabajo.txt"
        )
        if file_path:
            Path(file_path).write_text(text, encoding="utf-8")
            messagebox.showinfo("Guardado", f"Archivo guardado exitosamente en:\n{file_path}")

    def _change_appearance_mode(self, new_mode: str):
        """Cambia el modo de apariencia visual entre claro y oscuro."""
        if "Oscuro" in new_mode:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
