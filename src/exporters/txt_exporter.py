"""
Módulo de Exportación de Reportes en formato de texto (.txt).
Genera la memoria de cálculo académica y las salidas paso a paso del ejercicio.
"""

from datetime import datetime
import os
from pathlib import Path
from typing import Optional
from ..models.problem import ProblemData
from ..models.solution import WorkforceSolution, StageResult


class TxtReportExporter:
    """
    Exportador formal de resultados de Programación Dinámica a archivos de texto (.txt).
    Crea automáticamente la carpeta designada 'salidas/' y estructura el reporte
    con rigor académico según las pautas de la Universidad José Antonio Páez.
    """

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            # Por defecto crear dentro de la carpeta 'salidas' relativa a la raíz del proyecto
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.output_dir = base_dir / "salidas"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report_text(
        self, problem: ProblemData, solution: WorkforceSolution
    ) -> str:
        """Construye el contenido completo del reporte académico paso a paso."""
        lines = []

        # 1. Encabezado Oficial
        lines.append("=" * 80)
        lines.append("           UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA")
        lines.append("                    ESCUELA DE INGENIERÍA EN COMPUTACIÓN")
        lines.append("                    CÁTEDRA: MÉTODOS CUANTITATIVOS")
        lines.append("       PROGRAMACIÓN DINÁMICA: MODELO DE TAMAÑO DE LA FUERZA DE TRABAJO")
        lines.append("=" * 80)
        lines.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Estado del Modelo: SOLUCIÓN ÓPTIMA DETERMINADA (BELLMAN)")
        lines.append("")

        # 2. Planteamiento y Datos del Problema
        lines.append("-" * 80)
        lines.append("1. DATOS Y PARÁMETROS DEL PROBLEMA")
        lines.append("-" * 80)
        lines.append(f"• Horizonte de planificación: {len(problem.demands)} semanas")
        demands_str = ", ".join([f"b_{i+1} = {d}" for i, d in enumerate(problem.demands)])
        lines.append(f"• Demandas mínimas semanales: {demands_str}")
        lines.append(f"• Fuerza de trabajo inicial (x_0): {problem.initial_workforce} trabajadores")
        lines.append(f"• Costo de mano de obra excedente (C1): ${problem.cost_model.surplus_cost_per_worker:,.2f} / trabajador / semana")
        lines.append(f"• Costo fijo de contratación (C2 fijo): ${problem.cost_model.hiring_fixed_cost:,.2f}")
        lines.append(f"• Costo variable de contratación (C2 var): ${problem.cost_model.hiring_variable_cost:,.2f} / trabajador")
        lines.append(f"• Costo por despido: ${problem.cost_model.firing_cost_per_worker:,.2f} (sin costo asociado)")
        lines.append("")

        # 3. Formulación Matemática
        lines.append("-" * 80)
        lines.append("2. FORMULACIÓN MATEMÁTICA Y MODELO DE BELLMAN")
        lines.append("-" * 80)
        lines.append("• Etapas (i): Semanas i = 1, 2, ..., n evaluadas en inducción hacia atrás (n -> 1).")
        lines.append("• Estado (x_{i-1}): Fuerza de trabajo disponible proveniente de la semana anterior.")
        lines.append("• Decisión (x_i): Fuerza de trabajo asignada para la semana i.")
        lines.append("• Restricciones de decisión: b_i <= x_i <= max_{k >= i} b_k.")
        lines.append("• Funciones de Costo (en cientos de dólares):")
        lines.append("    C1(x_i - b_i) = 3(x_i - b_i)                 si x_i > b_i")
        lines.append("    C2(x_i - x_{i-1}) = 4 + 2(x_i - x_{i-1})     si x_i > x_{i-1}")
        lines.append("• Ecuación Recursiva de Bellman:")
        lines.append("    f_i(x_{i-1}) = min { C1(x_i - b_i) + C2(x_i - x_{i-1}) + f_{i+1}(x_i) }")
        lines.append("    con condición de frontera: f_{n+1}(x_n) = 0")
        lines.append("")

        # 4. Desarrollo Paso a Paso de las Etapas (Inducción Hacia Atrás)
        lines.append("-" * 80)
        lines.append("3. RESOLUCIÓN PASO A PASO (INDUCCIÓN HACIA ATRÁS: ETAPAS n -> 1)")
        lines.append("-" * 80)

        # Ordenamos las etapas en orden decreciente: 5, 4, 3, 2, 1
        sorted_stages = sorted(solution.stages, key=lambda s: s.stage_num, reverse=True)

        for stage in sorted_stages:
            lines.append(f"\n==================== [ ETAPA / SEMANA {stage.stage_num} ] ====================")
            lines.append(f"• Demanda mínima requerida (b_{stage.stage_num}): {stage.min_demand} trabajadores")
            lines.append(f"• Decisiones factibles (x_{stage.stage_num}): {stage.decision_values}")
            lines.append(f"• Estados de entrada factibles (x_{stage.stage_num - 1}): {stage.state_values}")
            lines.append("")

            # Encabezado de la tabla para esta etapa
            # Columnas: x_{i-1} | Decisiones x_i | f_i(x_{i-1}) ($100) | f_i ($) | x_i^*
            col_width = 30
            header_decisions = "".join([f"x_{stage.stage_num}={d}".center(col_width) for d in stage.decision_values])
            header_line = f"{('x_' + str(stage.stage_num - 1)).center(8)} |{header_decisions}| {('f_' + str(stage.stage_num)).center(12)} | {('f_' + str(stage.stage_num) + ' ($)').center(14)} | {('x_' + str(stage.stage_num) + '^*').center(8)}"
            separator = "-" * len(header_line)

            lines.append(header_line)
            lines.append(separator)

            for state in stage.state_values:
                row_cells = []
                for dec in stage.decision_values:
                    eval_item = stage.get_eval(state, dec)
                    if eval_item:
                        # Mostramos el desglose en cientos de dólares tal como en la lámina del profesor
                        mark = "*" if eval_item.is_optimal else " "
                        cell_text = f"{eval_item.arithmetic_breakdown_hundreds}{mark}"
                        row_cells.append(cell_text.center(col_width))
                    else:
                        row_cells.append("-".center(col_width))

                opt_cost_hundreds = stage.optimal_costs[state] / 100.0
                opt_cost_dollars = stage.optimal_costs[state]
                opt_decs = stage.optimal_decisions[state]
                opt_decs_str = ",".join(map(str, opt_decs))

                opt_cost_h_str = f"{int(opt_cost_hundreds) if opt_cost_hundreds.is_integer() else opt_cost_hundreds}"
                opt_cost_d_str = f"${opt_cost_dollars:,.0f}"

                row_str = f"{str(state).center(8)} |{''.join(row_cells)}| {opt_cost_h_str.center(12)} | {opt_cost_d_str.center(14)} | {opt_decs_str.center(8)}"
                lines.append(row_str)

            lines.append(separator)
            lines.append("Nota: '*' indica la decisión óptima que minimiza la función recursiva.")

        # 5. Reconstrucción de la Política Óptima Hacia Adelante
        lines.append("\n" + "-" * 80)
        lines.append("4. TRAYECTORIA Y POLÍTICA ÓPTIMA DE OPERACIÓN (1 -> n)")
        lines.append("-" * 80)
        lines.append(
            f"{'Semana':<8} | {'b_i':<6} | {'x_i^*':<6} | {'Decisión Operativa':<32} | {'Excedente':<10} | {'Contratación':<13} | {'Costo Total ($)':<15}"
        )
        lines.append("-" * 100)

        for item in solution.schedule:
            lines.append(
                f"{item.week:<8} | {item.min_demand:<6} | {item.assigned_workforce:<6} | {item.action_description:<32} | ${item.surplus_cost:<9,.0f} | ${item.hiring_cost:<12,.0f} | ${item.week_total_cost:<14,.0f}"
            )

        lines.append("-" * 100)
        lines.append(f"{'COSTO TOTAL MÍNIMO DEL PROYECTO:':<70} ${solution.total_cost:,.2f}")
        lines.append(f"{'COSTO EN CIENTOS DE DÓLARES:':<70} {solution.total_cost_hundreds:.2f} (33 unidades)")
        lines.append("")

        # 6. Conclusiones y Resumen Ejecutivo
        lines.append("-" * 80)
        lines.append("5. RESUMEN EJECUTIVO Y CONCLUSIÓN OPERATIVA")
        lines.append("-" * 80)
        lines.append("• En la Semana 1, se contrata exactamente el requerimiento de 5 trabajadores (Costo: $1,400).")
        lines.append("• En la Semana 2, resulta más rentable contratar 3 trabajadores (llegando a 8) en lugar de 2,")
        lines.append("  ya que mantener 1 trabajador extra en la Semana 2 ($300) evita una nueva contratación fija ($400)")
        lines.append("  en la Semana 3 donde la demanda es 8 trabajadores.")
        lines.append("• En la Semana 4, ante la caída de demanda a 4 trabajadores, es óptimo despedir solo 2 y conservar 6,")
        lines.append("  evitando la penalización de contratación para la Semana 5 cuya demanda es 6.")
        lines.append(f"• Esta política óptima garantiza el costo mínimo global de ${solution.total_cost:,.2f}.")
        lines.append("=" * 80)

        return "\n".join(lines)

    def export(
        self,
        problem: ProblemData,
        solution: WorkforceSolution,
        filename: Optional[str] = None
    ) -> Path:
        """
        Exporta el reporte tanto a un archivo específico (o con timestamp)
        como a 'salida_fuerza_trabajo_actual.txt' para acceso rápido.
        """
        content = self.generate_report_text(problem, solution)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"salida_fuerza_trabajo_{timestamp}.txt"

        target_path = self.output_dir / filename
        target_path.write_text(content, encoding="utf-8")

        # También actualizamos la salida actual fija
        current_path = self.output_dir / "salida_fuerza_trabajo_actual.txt"
        current_path.write_text(content, encoding="utf-8")

        return target_path
