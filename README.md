# Universidad José Antonio Páez — Métodos Cuantitativos
## Modelo de Tamaño de la Fuerza de Trabajo (Programación Dinámica)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-emerald.svg)](https://customtkinter.tomschimansky.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Soluci%C3%B3n%20%C3%93ptima%20Verificada-brightgreen.svg)]()

> **Facultad de Ingeniería — Escuela de Ingeniería en Computación**  
> **Asignatura:** Métodos Cuantitativos  
> **Corte V — Tarea:** Modelo de tamaño de la fuerza de trabajo (3 puntos)  
> **Organización:** Dream Working Team  

---

## 📌 1. Descripción del Proyecto

Este software implementa la resolución analítica y computacional del **Modelo de Tamaño de la Fuerza de Trabajo** (*Workforce Size Model*) mediante el método determinístico de **Programación Dinámica** con **Inducción Hacia Atrás (Backward Induction)**.

El sistema fue concebido bajo estándares de ingeniería de software senior:
- **100% Orientado a Objetos (POO):** Modelado con separación estricta de responsabilidades (SOLID).
- **Interfaz Gráfica Moderna (GUI):** Construida con `CustomTkinter`, soportando temas Oscuro (*Dark*) y Claro (*Light*), visualización interactiva de tablas de programación dinámica y tarjetas de métricas (KPIs).
- **Muestreo Paso a Paso:** Muestra con total transparencia las operaciones aritméticas de cada etapa ($5 \to 1$).
- **Salidas en TXT:** Genera automáticamente reportes académicos estructurados dentro de la carpeta designada `salidas/`.
- **Flexibilidad:** Carga los parámetros oficiales por defecto pero permite al usuario modificar cualquier valor (semanas, demandas, costos fijos y variables).

---

## 📋 2. Enunciado Oficial del Problema

> *"Un contratista estima que el tamaño de la fuerza de trabajo necesaria durante las siguientes 5 semanas es de 5, 7, 8, 4 y 6 trabajadores, respectivamente. La mano de obra excedente conservada en la fuerza de trabajo costará $300 por trabajador por semana, y una nueva contratación en cualquier semana incurrirá en un costo fijo de $400 más $200 por trabajador por semana."*

### Parámetros Base:
- **Horizonte de planificación:** $n = 5$ semanas.
- **Demandas mínimas requeridas:**
  $$b_1 = 5, \quad b_2 = 7, \quad b_3 = 8, \quad b_4 = 4, \quad b_5 = 6$$
- **Costo de excedente ($C_1$):** $\$300$ por trabajador / semana ($3$ cientos de dólares).
- **Costo de contratación ($C_2$):** Costo fijo de $\$400$ ($4$ cientos) $+$ costo variable de $\$200$ ($2$ cientos) por trabajador.
- **Costo de despido:** $\$0$ (no penalizado).
- **Fuerza laboral inicial:** $x_0 = 0$ trabajadores.

---

## 🧠 3. Fundamentación Teórica y Formulación de Bellman

### 3.1 Variables y Elementos del Modelo
1. **Etapas ($i$):** Cada semana $i \in \{1, 2, 3, 4, 5\}$, resueltas en sentido inverso ($i = 5, 4, 3, 2, 1$).
2. **Variable de Estado ($x_{i-1}$):** Número de trabajadores disponibles provenientes de la semana anterior ($x_0 = 0$).
3. **Variable de Decisión ($x_i$):** Número de trabajadores asignados para la semana $i$.
   - **Cota inferior:** $x_i \ge b_i$ (se debe satisfacer obligatoriamente la demanda semanal).
   - **Cota superior:** $x_i \le \max_{k \ge i} b_k$ (no es óptimo mantener más personal que la demanda futura máxima).
4. **Ecuación Recursiva:**
   $$f_i(x_{i-1}) = \min_{x_i \ge b_i} \left\{ C_1(x_i - b_i) + C_2(x_i - x_{i-1}) + f_{i+1}(x_i) \right\}$$
   con la condición de frontera final:
   $$f_{n+1}(x_n) = 0$$

---

## 🧮 4. Solución Paso a Paso Verificada

### Resumen de Etapas (Inducción Hacia Atrás)

#### • Etapa 5 ($i = 5, b_5 = 6, x_5 = 6$)
$$f_5(x_4) = \min_{x_5=6} \{ 3(x_5 - 6) + [4 + 2(x_5 - x_4)] \}$$
- $x_4 = 4 \implies 0 + [4 + 2(2)] = \mathbf{8}$ ($800) $\to x_5^* = 6$
- $x_4 = 5 \implies 0 + [4 + 2(1)] = \mathbf{6}$ ($600) $\to x_5^* = 6$
- $x_4 = 6 \implies 0 + 0 = \mathbf{0}$ ($0) $\to x_5^* = 6$

#### • Etapa 4 ($i = 4, b_4 = 4, x_4 \in \{4, 5, 6\}$)
Estado de entrada: $x_3 = 8$. Como $x_4 \le 6 < 8$, no hay costo de contratación.
- $x_4 = 4 \implies 3(0) + 0 + 8 = 8$
- $x_4 = 5 \implies 3(1) + 0 + 6 = 9$
- $x_4 = 6 \implies 3(2) + 0 + 0 = \mathbf{6}$ ($600) $\to x_4^* = 6, \quad f_4(8) = 6$

#### • Etapa 3 ($i = 3, b_3 = 8, x_3 = 8$)
- $x_2 = 7 \implies 3(0) + [4 + 2(1)] + 6 = \mathbf{12}$ ($1,200) $\to x_3^* = 8$
- $x_2 = 8 \implies 3(0) + 0 + 6 = \mathbf{6}$ ($600) $\to x_3^* = 8$

#### • Etapa 2 ($i = 2, b_2 = 7, x_2 \in \{7, 8\}$)
- $x_1 = 5 \implies \min\{0 + [4+2(2)] + 12 = 20, \; 3(1) + [4+2(3)] + 6 = \mathbf{19}\} \to x_2^* = 8$
- $x_1 = 6 \implies \min\{0 + [4+2(1)] + 12 = 18, \; 3(1) + [4+2(2)] + 6 = \mathbf{17}\} \to x_2^* = 8$
- $x_1 = 7 \implies \min\{0 + 0 + 12 = \mathbf{12}, \; 3(1) + [4+2(1)] + 6 = 15\} \to x_2^* = 7$
- $x_1 = 8 \implies \min\{0 + 0 + 12 = 12, \; 3(1) + 0 + 6 = \mathbf{9}\} \to x_2^* = 8$

#### • Etapa 1 ($i = 1, b_1 = 5, x_0 = 0$)
- $x_1 = 5 \implies 0 + [4 + 2(5)] + 19 = \mathbf{33}$
- $x_1 = 6 \implies 3 + [4 + 2(6)] + 17 = 36$
- $x_1 = 7 \implies 6 + [4 + 2(7)] + 12 = 36$
- $x_1 = 8 \implies 9 + [4 + 2(8)] + 9 = 38$
- **Mínimo Global:** $f_1(0) = \mathbf{33}$ ($\mathbf{\$3,300}$) con $x_1^* = 5$.

---

### 📊 Política Óptima Resultante (Trayectoria 1 $\to$ 5)

| Semana ($i$) | Demanda ($b_i$) | Personal Real ($x_i^*$) | Decisión Operativa | Excedente | Contratación | Costo Semanal ($) | Costo Acumulado ($) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 5 | **5** | Contratar 5 trabajadores | $0 | $1,400 | **$1,400** | $1,400 |
| **2** | 7 | **8** | Contratar 3 trabajadores | $300 (1 trab.) | $1,000 | **$1,300** | $2,700 |
| **3** | 8 | **8** | Mantener personal | $0 | $0 | **$0** | $2,700 |
| **4** | 4 | **6** | Despedir 2 trabajadores | $600 (2 trab.) | $0 | **$600** | $3,300 |
| **5** | 6 | **6** | Mantener personal | $0 | $0 | **$0** | **$3,300** |

> **Costo Total Mínimo del Proyecto:** **$3,300.00** *(Coincidencia exacta con la diapositiva 31 del M.Sc. Ricardo Caballero)*.

---

## 🏗️ 5. Arquitectura del Software (POO)

El proyecto está diseñado bajo una arquitectura modular desacoplada:

```
Tarea-V/
├── .gitignore                      # Exclusión de binarios y cachés temporales
├── LICENSE                         # Licencia MIT académica
├── README.md                       # Documentación exhaustiva
├── requirements.txt                # Dependencias (customtkinter)
├── main.py                         # Entrypoint (soporta GUI y CLI)
├── src/
│   ├── models/
│   │   ├── problem.py              # Clases ProblemData y CostModel
│   │   └── solution.py             # Clases StageEvaluation, StageResult, WorkforceSolution
│   ├── solver/
│   │   └── dp_solver.py            # Motor de Programación Dinámica (Backward Recursion)
│   ├── exporters/
│   │   └── txt_exporter.py         # Generador de reportes paso a paso (.txt)
│   └── ui/
│       └── app_window.py           # GUI moderna construida con CustomTkinter
├── salidas/
│   ├── salida_fuerza_trabajo_actual.txt     # Reporte fijo de la última corrida
│   └── salida_fuerza_trabajo_*.txt          # Reportes históricos con marca de tiempo
└── tests/
    └── test_solver.py              # Suite de pruebas unitarias automatizadas
```

### Principios de Diseño:
- **Separación de Responsabilidades:** El algoritmo matemático (`WorkforceDPSolver`) es completamente independiente de la interfaz visual (`WorkforceAppGUI`) y del generador de texto (`TxtReportExporter`).
- **Encapsulamiento:** Las reglas de costo y validación residen dentro de sus respectivas clases de dominio.
- **Inmutabilidad de Resultados:** Los objetos de evaluación y solución (`StageResult`, `WorkforceSolution`) representan estructuras de datos consolidadas.

---

## 🚀 6. Instalación y Ejecución

### Prerrequisitos
- Python 3.10 o superior (validado en Python 3.14).

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Dream-Working-Team/Tarea-V.git
cd Tarea-V
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación Gráfica (Recomendado)
```bash
python main.py
```

### 4. Ejecutar en Modo Consola (CLI)
Para generar el reporte `.txt` directamente sin abrir la interfaz gráfica:
```bash
python main.py --cli
```

### 5. Ejecutar las Pruebas Unitarias
```bash
python -m unittest tests/test_solver.py
```

---

## 🖥️ 7. Características de la Interfaz Gráfica

1. **Panel Lateral:**
   - Campos interactivos prellenados con los valores oficiales de la tarea.
   - Botón **`[▶ Resolver Problema]`**: Ejecuta el algoritmo de programación dinámica al instante.
   - Botón **`[📄 Generar Salida TXT]`**: Guarda el reporte formateado en la carpeta `salidas/`.
   - Botón **`[🔄 Restablecer Valores]`**: Restaura los valores iniciales del problema UJAP.
   - Botón **`[📂 Abrir Carpeta Salidas]`**: Abre directamente el explorador de archivos en la carpeta de salidas.
   - Switch de tema **Oscuro / Claro**.

2. **Panel de Resultados:**
   - **Tarjetas KPI:** Muestran el costo mínimo ($3,300), semanas evaluadas (5), pico de personal (8) y estado del algoritmo.
   - **Pestaña 1 (Plan Óptimo Semanal):** Tabla estética con colores indicativos de decisión (contratación, despido o mantenimiento).
   - **Pestaña 2 (Tablas Paso a Paso):** Desglose detallado de cada una de las matrices de Bellman con fórmulas aritméticas y marcado de óptimos.
   - **Pestaña 3 (Visor TXT):** Vista previa en tiempo real del archivo de texto generado, con botón para copiar al portapapeles.
   - **Pestaña 4 (Fundamento Teórico):** Compendio teórico y formulación matemática para consulta rápida.

---

## 📄 8. Salidas en Formato TXT

El sistema crea automáticamente la carpeta `salidas/` y almacena:
- `salida_fuerza_trabajo_actual.txt` (acceso directo a la última ejecución).
- `salida_fuerza_trabajo_YYYYMMDD_HHMMSS.txt` (historial cronológico).

El archivo contiene:
1. Encabezado institucional UJAP.
2. Parámetros del problema.
3. Formulación matemática formal.
4. Tablas completas de las 5 etapas con cálculo paso a paso.
5. Política óptima y cronograma semana a semana.
6. Resumen y conclusión operativa del contratista.

---

## 👥 Créditos
- **Universidad José Antonio Páez (UJAP)**
- **Facultad de Ingeniería — Escuela de Computación**
- **Cátedra:** Métodos Cuantitativos
- **Equipo:** Dream Working Team
- **Licencia:** [MIT](LICENSE)
