"""
Componente que agrupa la barra superior de indicadores clave (KPI).
"""

import customtkinter as ctk
from .metric_card import MetricCard
from ...models.solution import WorkforceSolution
from ...models.problem import ProblemData


class KPIBarFrame(ctk.CTkFrame):
    """Contenedor de métricas ejecutivas en la parte superior del Dashboard."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

        self.card_cost = MetricCard(self, "COSTO TOTAL MÍNIMO", "$3,300.00", "33 unidades ($100)")
        self.card_cost.grid(row=0, column=0, sticky="ew", padx=4)

        self.card_weeks = MetricCard(self, "DURACIÓN PROYECTO", "5 Semanas", "Etapas evaluadas")
        self.card_weeks.grid(row=0, column=1, sticky="ew", padx=4)

        self.card_peak = MetricCard(self, "PICO DE PERSONAL", "8 Trabajadores", "Semana 2 y 3")
        self.card_peak.grid(row=0, column=2, sticky="ew", padx=4)

        self.card_status = MetricCard(self, "ESTADO BELLMAN", "Óptimo Global", "Inducción hacia atrás")
        self.card_status.grid(row=0, column=3, sticky="ew", padx=4)

    def update_metrics(self, problem: ProblemData, solution: WorkforceSolution) -> None:
        """Actualiza todas las tarjetas con los datos de la solución actual."""
        self.card_cost.update_values(
            f"${solution.total_cost:,.2f}",
            f"{solution.total_cost_hundreds:,.2f} unidades ($100)"
        )
        self.card_weeks.update_values(
            f"{len(problem.demands)} Semanas",
            "Horizonte evaluado"
        )
        max_assigned = max(item.assigned_workforce for item in solution.schedule)
        self.card_peak.update_values(
            f"{max_assigned} Trabajadores",
            "Máximo simultáneo"
        )
        self.card_status.update_values(
            "Óptimo Global",
            "Inducción hacia atrás"
        )
