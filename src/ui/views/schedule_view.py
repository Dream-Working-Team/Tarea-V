"""
Vista del Cronograma y Plan Óptimo Semanal (Pestaña 1).
"""

import customtkinter as ctk
from ...models.solution import WorkforceSolution


class ScheduleView(ctk.CTkFrame):
    """Panel que presenta la política óptima semana a semana."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_lbl = ctk.CTkLabel(
            self,
            text="Cronograma de Asignación de Fuerza de Trabajo y Costos Semanales",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 8))

        self.schedule_scroll = ctk.CTkScrollableFrame(self)
        self.schedule_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def render(self, solution: WorkforceSolution) -> None:
        """Renderiza la tabla estilizada del plan óptimo semanal."""
        for widget in self.schedule_scroll.winfo_children():
            widget.destroy()

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

        for idx, item in enumerate(solution.schedule):
            bg_color = ("gray90", "#111827") if idx % 2 == 0 else ("gray85", "#1f2937")
            row_frame = ctk.CTkFrame(self.schedule_scroll, fg_color=bg_color, corner_radius=6)
            row_frame.pack(fill="x", pady=2, padx=4)

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
