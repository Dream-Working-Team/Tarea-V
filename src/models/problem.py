"""
Módulo de dominio para la definición del Problema y Modelo de Costos.
Aplica principios de Programación Orientada a Objetos (POO) y Responsabilidad Única.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CostModel:
    """
    Modelo de costos para la gestión de mano de obra en Programación Dinámica.
    Por defecto maneja valores en dólares reales ($):
      - Excedente: $300 por trabajador por semana
      - Contratación: $400 costo fijo + $200 por trabajador por semana
      - Despido: $0
    """
    surplus_cost_per_worker: float = 300.0
    hiring_fixed_cost: float = 400.0
    hiring_variable_cost: float = 200.0
    firing_cost_per_worker: float = 0.0

    def calc_surplus_cost(self, excess_workers: int) -> float:
        """Calcula el costo por excedente de trabajadores: C1(x_i - b_i)."""
        if excess_workers > 0:
            return self.surplus_cost_per_worker * excess_workers
        return 0.0

    def calc_hiring_cost(self, hired_workers: int) -> float:
        """Calcula el costo por contratación: C2(x_i - x_{i-1})."""
        if hired_workers > 0:
            return self.hiring_fixed_cost + (self.hiring_variable_cost * hired_workers)
        return 0.0

    def calc_firing_cost(self, fired_workers: int) -> float:
        """Calcula el costo por despido de trabajadores (0 por defecto)."""
        if fired_workers > 0:
            return self.firing_cost_per_worker * fired_workers
        return 0.0

    def evaluate_transition(
        self, x_curr: int, x_prev: int, min_demand: int
    ) -> Tuple[float, float, float]:
        """
        Calcula la terna de costos (excedente, contratación, despido)
        al pasar del estado x_prev a la decisión x_curr con demanda mínima min_demand.
        """
        excess = max(0, x_curr - min_demand)
        surplus_cost = self.calc_surplus_cost(excess)

        diff = x_curr - x_prev
        hired = max(0, diff)
        fired = max(0, -diff)

        hiring_cost = self.calc_hiring_cost(hired)
        firing_cost = self.calc_firing_cost(fired)

        return surplus_cost, hiring_cost, firing_cost


@dataclass
class ProblemData:
    """
    Representa los datos completos de entrada para el problema de
    tamaño de la fuerza de trabajo.
    """
    demands: List[int]
    cost_model: CostModel
    initial_workforce: int = 0

    @classmethod
    def create_default(cls) -> "ProblemData":
        """
        Instancia con los datos oficiales del problema de la UJAP:
        b = [5, 7, 8, 4, 6]
        C1 = $300/trabajador
        C2 = $400 fijo + $200/trabajador
        x_0 = 0
        """
        return cls(
            demands=[5, 7, 8, 4, 6],
            cost_model=CostModel(
                surplus_cost_per_worker=300.0,
                hiring_fixed_cost=400.0,
                hiring_variable_cost=200.0,
                firing_cost_per_worker=0.0
            ),
            initial_workforce=0
        )

    def validate(self) -> None:
        """Valida que los datos del problema sean consistentes."""
        if not self.demands:
            raise ValueError("La lista de demandas semanales no puede estar vacía.")
        for i, d in enumerate(self.demands, start=1):
            if d < 0:
                raise ValueError(f"La demanda de la semana {i} ({d}) no puede ser negativa.")
        if self.initial_workforce < 0:
            raise ValueError("La fuerza laboral inicial no puede ser negativa.")
        if self.cost_model.surplus_cost_per_worker < 0:
            raise ValueError("El costo por excedente no puede ser negativo.")
        if self.cost_model.hiring_fixed_cost < 0:
            raise ValueError("El costo fijo de contratación no puede ser negativo.")
        if self.cost_model.hiring_variable_cost < 0:
            raise ValueError("El costo variable de contratación no puede ser negativo.")
