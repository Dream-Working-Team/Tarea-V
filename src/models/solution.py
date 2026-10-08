"""
Módulo con las clases que representan la evaluación de etapas,
las tablas de programación dinámica y el plan óptimo resultante.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class StageEvaluation:
    """
    Evaluación individual de una combinación (Estado x_{i-1}, Decisión x_i)
    dentro de una etapa de programación dinámica.
    """
    x_prev: int
    x_curr: int
    excess_workers: int
    surplus_cost: float
    hired_workers: int
    hiring_cost: float
    firing_cost: float
    future_cost: float
    total_cost: float
    arithmetic_breakdown: str
    arithmetic_breakdown_hundreds: str
    is_optimal: bool = False


@dataclass
class StageResult:
    """
    Representa la tabla completa calculada para una etapa (semana i)
    en la inducción hacia atrás.
    """
    stage_num: int
    min_demand: int
    state_values: List[int]
    decision_values: List[int]
    evaluations: Dict[Tuple[int, int], StageEvaluation] = field(default_factory=dict)
    optimal_costs: Dict[int, float] = field(default_factory=dict)
    optimal_decisions: Dict[int, List[int]] = field(default_factory=dict)

    def get_eval(self, x_prev: int, x_curr: int) -> StageEvaluation:
        """Retorna la evaluación para una combinación estado-decisión."""
        return self.evaluations.get((x_prev, x_curr))


@dataclass
class OptimalScheduleItem:
    """
    Línea de ejecución semanal para la política óptima.
    """
    week: int
    min_demand: int
    initial_workers: int
    assigned_workforce: int
    action_type: str  # 'CONTRATAR', 'DESPEDIR', 'MANTENER'
    action_count: int
    action_description: str
    excess_workers: int
    surplus_cost: float
    hiring_cost: float
    firing_cost: float
    week_total_cost: float
    cumulative_cost: float


@dataclass
class WorkforceSolution:
    """
    Resultado global de la optimización por Programación Dinámica.
    """
    stages: List[StageResult]
    schedule: List[OptimalScheduleItem]
    total_cost: float

    @property
    def total_cost_hundreds(self) -> float:
        """Costo total en cientos de dólares."""
        return self.total_cost / 100.0
