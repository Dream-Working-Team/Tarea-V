"""
Vista del Marco Teórico y Formulación Matemática (Pestaña 4).
"""

import customtkinter as ctk


class TheoryView(ctk.CTkFrame):
    """Panel que presenta la formulación teórica de la cátedra de Métodos Cuantitativos."""

    THEORY_DOCUMENTATION = """UNIVERSIDAD JOSÉ ANTONIO PÁEZ
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

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.theory_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.theory_box.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.theory_box.insert("1.0", self.THEORY_DOCUMENTATION.strip())
        self.theory_box.configure(state="disabled")
