"""
Vista de Tablas de Programación Dinámica Paso a Paso (Pestaña 2).
"""

from typing import Optional
import customtkinter as ctk
from ...models.solution import WorkforceSolution, StageResult


class StagesView(ctk.CTkFrame):
    """Panel que presenta las tablas de inducción hacia atrás paso a paso."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.current_solution: Optional[WorkforceSolution] = None

        self._build_controls()
        self.stages_scroll = ctk.CTkScrollableFrame(self)
        self.stages_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def _build_controls(self) -> None:
        """Construye el selector de etapa."""
        control_bar = ctk.CTkFrame(self, fg_color="transparent")
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

    def _on_stage_selection_changed(self, value: str) -> None:
        """Manejador del cambio de filtro en el segmented button."""
        if self.current_solution:
            self.render(self.current_solution)

    def update_selector_options(self, n_stages: int) -> None:
        """Actualiza las opciones del segmented button según el número de etapas."""
        values = [f"Semana {i}" for i in range(n_stages, 0, -1)] + ["Todas las Etapas"]
        self.stage_selector.configure(values=values)
        if self.stage_selector.get() not in values:
            self.stage_selector.set("Todas las Etapas")

    def render(self, solution: WorkforceSolution) -> None:
        """Renderiza las tablas de programación dinámica para cada etapa."""
        self.current_solution = solution

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

            title_frame = ctk.CTkFrame(stage_card, fg_color="transparent")
            title_frame.pack(fill="x", padx=12, pady=(10, 6))

            t_lbl = ctk.CTkLabel(
                title_frame,
                text=f"ETAPA {stage.stage_num} (Semana {stage.stage_num}) — Demanda mínima b_{stage.stage_num} = {stage.min_demand}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#0284c7", "#38bdf8")
            )
            t_lbl.pack(side="left")

            tbl_frame = ctk.CTkFrame(stage_card, fg_color=("gray90", "#0f172a"), corner_radius=6)
            tbl_frame.pack(fill="x", padx=12, pady=(0, 12))

            # Header row
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

            # Data rows
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
