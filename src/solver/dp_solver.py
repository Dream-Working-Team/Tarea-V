"""
Motor de Programación Dinámica Determinística: Modelo de Tamaño de la Fuerza de Trabajo.
Implementa el algoritmo de Inducción Hacia Atrás (Backward Induction)
y la Reconstrucción Hacia Adelante (Forward Policy Trajectory).
"""

from typing import Dict, List, Tuple
from ..models.problem import ProblemData, CostModel
from ..models.solution import (
    StageEvaluation,
    StageResult,
    OptimalScheduleItem,
    WorkforceSolution
)


class WorkforceDPSolver:
    """
    Solucionador por Programación Dinámica del modelo de tamaño de la fuerza laboral.
    """

    def __init__(self, problem: ProblemData):
        self.problem = problem
        self.problem.validate()
        self.cost_model = problem.cost_model
        self.n_weeks = len(problem.demands)

    def _compute_decision_ranges(self) -> List[List[int]]:
        """
        Calcula el rango admisible de decisiones x_i para cada semana i (1..n):
        b_i <= x_i <= max_{k >= i} b_k
        """
        ranges: List[List[int]] = []
        for i in range(self.n_weeks):
            min_val = self.problem.demands[i]
            max_val = max(self.problem.demands[i:])
            ranges.append(list(range(min_val, max_val + 1)))
        return ranges

    def _compute_state_ranges(self, decision_ranges: List[List[int]]) -> List[List[int]]:
        """
        Calcula los estados factibles x_{i-1} que entran a cada etapa i:
        - Para la etapa 1: [initial_workforce] (típicamente 0)
        - Para la etapa i (i > 1): el rango de decisiones admisibles en la etapa i-1
        """
        state_ranges: List[List[int]] = []
        for i in range(self.n_weeks):
            if i == 0:
                state_ranges.append([self.problem.initial_workforce])
            else:
                state_ranges.append(list(decision_ranges[i - 1]))
        return state_ranges

    def _format_formula_hundreds(
        self, excess: int, hired: int, future_hundreds: float, total_hundreds: float, is_last_stage: bool
    ) -> str:
        """Formatea la expresión en cientos de dólares tal como en la teoría UJAP."""
        # Término excedente: 3(x_i - b_i)
        excess_str = f"3({excess})" if excess > 0 else "0"

        # Término contratación: [4 + 2(x_i - x_{i-1})]
        if hired > 0:
            hired_str = f"[4 + 2({hired})]"
        else:
            hired_str = "0"

        tot_str = f"{int(total_hundreds) if total_hundreds.is_integer() else total_hundreds}"

        if is_last_stage:
            return f"{excess_str} + {hired_str} = {tot_str}"

        future_str = f"{int(future_hundreds) if future_hundreds.is_integer() else future_hundreds}"
        return f"{excess_str} + {hired_str} + {future_str} = {tot_str}"

    def _format_formula_dollars(
        self,
        excess: int,
        surplus_cost: float,
        hired: int,
        hiring_cost: float,
        future_cost: float,
        total_cost: float
    ) -> str:
        """Formatea la expresión aritmética en dólares reales."""
        surplus_part = f"${surplus_cost:,.0f}" if surplus_cost > 0 else "$0"
        hiring_part = f"${hiring_cost:,.0f}" if hiring_cost > 0 else "$0"
        future_part = f"${future_cost:,.0f}" if future_cost > 0 else "$0"
        total_part = f"${total_cost:,.0f}"

        if future_cost == 0:
            return f"{surplus_part} + {hiring_part} = {total_part}"
        return f"{surplus_part} + {hiring_part} + {future_part} = {total_part}"

    def solve(self) -> WorkforceSolution:
        """
        Ejecuta la optimización completa:
        1. Inducción hacia atrás desde etapa n hasta etapa 1.
        2. Reconstrucción hacia adelante de la trayectoria óptima.
        """
        decision_ranges = self._compute_decision_ranges()
        state_ranges = self._compute_state_ranges(decision_ranges)

        stage_results: List[StageResult] = []
        # future_optimal_costs mapea x_i a f_{i+1}(x_i)
        future_optimal_costs: Dict[int, float] = {}

        # 1. Inducción Hacia Atrás (Backward Induction: n -> 1)
        for stage_idx in range(self.n_weeks - 1, -1, -1):
            stage_num = stage_idx + 1
            min_demand = self.problem.demands[stage_idx]
            decisions = decision_ranges[stage_idx]
            states = state_ranges[stage_idx]

            result = StageResult(
                stage_num=stage_num,
                min_demand=min_demand,
                state_values=states,
                decision_values=decisions
            )

            for x_prev in states:
                best_cost = float("inf")
                best_decisions: List[int] = []

                for x_curr in decisions:
                    excess = max(0, x_curr - min_demand)
                    diff = x_curr - x_prev
                    hired = max(0, diff)
                    fired = max(0, -diff)

                    surplus_cost = self.cost_model.calc_surplus_cost(excess)
                    hiring_cost = self.cost_model.calc_hiring_cost(hired)
                    firing_cost = self.cost_model.calc_firing_cost(fired)

                    # Condición de frontera para última etapa: f_{n+1} = 0
                    future_cost = future_optimal_costs.get(x_curr, 0.0)
                    total_cost = surplus_cost + hiring_cost + firing_cost + future_cost

                    total_hundreds = total_cost / 100.0
                    future_hundreds = future_cost / 100.0

                    formula_hundreds = self._format_formula_hundreds(
                        excess, hired, future_hundreds, total_hundreds, is_last_stage=(stage_idx == self.n_weeks - 1)
                    )
                    formula_dollars = self._format_formula_dollars(
                        excess, surplus_cost, hired, hiring_cost, future_cost, total_cost
                    )

                    eval_item = StageEvaluation(
                        x_prev=x_prev,
                        x_curr=x_curr,
                        excess_workers=excess,
                        surplus_cost=surplus_cost,
                        hired_workers=hired,
                        hiring_cost=hiring_cost,
                        firing_cost=firing_cost,
                        future_cost=future_cost,
                        total_cost=total_cost,
                        arithmetic_breakdown=formula_dollars,
                        arithmetic_breakdown_hundreds=formula_hundreds,
                        is_optimal=False
                    )
                    result.evaluations[(x_prev, x_curr)] = eval_item

                    # Verificamos si es mínimo para este estado x_prev
                    if total_cost < best_cost - 1e-6:
                        best_cost = total_cost
                        best_decisions = [x_curr]
                    elif abs(total_cost - best_cost) < 1e-6:
                        best_decisions.append(x_curr)

                result.optimal_costs[x_prev] = best_cost
                result.optimal_decisions[x_prev] = best_decisions

                # Marcar evaluaciones óptimas
                for opt_x in best_decisions:
                    result.evaluations[(x_prev, opt_x)].is_optimal = True

            # Actualizamos future_optimal_costs para la etapa previa (stage_idx - 1)
            future_optimal_costs = {
                state: result.optimal_costs[state] for state in states
            }
            stage_results.append(result)

        # Ordenar etapas de 5 a 1 (o guardar referencia indexada por etapa)
        # stage_results actualmente está [Etapa 5, Etapa 4, ..., Etapa 1]
        stage_by_num: Dict[int, StageResult] = {
            s.stage_num: s for s in stage_results
        }

        # 2. Reconstrucción Hacia Adelante (Forward Policy Trajectory: 1 -> n)
        schedule: List[OptimalScheduleItem] = []
        current_state = self.problem.initial_workforce
        cumulative_cost = 0.0

        for stage_num in range(1, self.n_weeks + 1):
            stage_res = stage_by_num[stage_num]
            opt_decisions = stage_res.optimal_decisions.get(current_state, [])
            if not opt_decisions:
                # Fallback por seguridad numérica
                opt_x = stage_res.decision_values[0]
            else:
                opt_x = opt_decisions[0]

            min_demand = stage_res.min_demand
            excess = max(0, opt_x - min_demand)
            diff = opt_x - current_state

            if diff > 0:
                action_type = "CONTRATAR"
                action_count = diff
                action_desc = f"Contratar {diff} trabajador(es)"
            elif diff < 0:
                action_type = "DESPEDIR"
                action_count = abs(diff)
                action_desc = f"Despedir {abs(diff)} trabajador(es)"
            else:
                action_type = "MANTENER"
                action_count = 0
                action_desc = "Ningún cambio (mantener personal)"

            surplus_cost = self.cost_model.calc_surplus_cost(excess)
            hiring_cost = self.cost_model.calc_hiring_cost(max(0, diff))
            firing_cost = self.cost_model.calc_firing_cost(max(0, -diff))
            week_cost = surplus_cost + hiring_cost + firing_cost
            cumulative_cost += week_cost

            schedule_item = OptimalScheduleItem(
                week=stage_num,
                min_demand=min_demand,
                initial_workers=current_state,
                assigned_workforce=opt_x,
                action_type=action_type,
                action_count=action_count,
                action_description=action_desc,
                excess_workers=excess,
                surplus_cost=surplus_cost,
                hiring_cost=hiring_cost,
                firing_cost=firing_cost,
                week_total_cost=week_cost,
                cumulative_cost=cumulative_cost
            )
            schedule.append(schedule_item)
            current_state = opt_x

        total_cost = cumulative_cost

        # Retornamos las etapas en orden de resolución (5 descendiendo a 1)
        return WorkforceSolution(
            stages=stage_results,
            schedule=schedule,
            total_cost=total_cost
        )
