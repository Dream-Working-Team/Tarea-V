"""
Componente del Panel Lateral (Sidebar).
Gestiona las entradas de parámetros, validación de formularios y botones de acción.
"""

import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

# pyrefly: ignore [missing-import]
from ...models.problem import ProblemData, CostModel


class SidebarFrame(ctk.CTkFrame):
    """Panel lateral de configuración y controles principales."""

    def __init__(
        self,
        master,
        on_solve: Callable[[], None],
        on_export: Callable[[], None],
        on_open_folder: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, width=320, corner_radius=0, **kwargs)
        self.on_solve = on_solve
        self.on_export = on_export
        self.on_open_folder = on_open_folder

        self._build_header()
        self._build_input_fields()
        self._build_action_buttons()
        self._build_theme_switcher()
        self.set_default_values()

    def _build_header(self) -> None:
        """Construye el encabezado institucional."""
        logo_label = ctk.CTkLabel(
            self,
            text="UNIVERSIDAD JOSÉ ANTONIO PÁEZ",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1e3a8a", "#60a5fa")
        )
        logo_label.pack(padx=20, pady=(20, 2), anchor="w")

        sub_header = ctk.CTkLabel(
            self,
            text="Métodos Cuantitativos • Programación Dinámica",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#9ca3af")
        )
        sub_header.pack(padx=20, pady=(0, 14), anchor="w")

        sep = ctk.CTkFrame(self, height=2, fg_color=("gray75", "#374151"))
        sep.pack(fill="x", padx=16, pady=(0, 14))

        section_lbl = ctk.CTkLabel(
            self,
            text="PARÁMETROS DEL MODELO",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        section_lbl.pack(padx=20, pady=(0, 8), anchor="w")

    def _build_input_fields(self) -> None:
        """Construye el scrollable frame con los campos del formulario."""
        self.inputs_scroll = ctk.CTkScrollableFrame(self, height=310, fg_color="transparent")
        self.inputs_scroll.pack(fill="x", padx=12, pady=0)

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

    def _create_input_field(self, label_text: str, placeholder: str = "") -> ctk.CTkEntry:
        """Crea un campo individual con su respectiva etiqueta."""
        lbl = ctk.CTkLabel(
            self.inputs_scroll,
            text=label_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        lbl.pack(fill="x", padx=4, pady=(6, 1))

        entry = ctk.CTkEntry(
            self.inputs_scroll,
            placeholder_text=placeholder,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        entry.pack(fill="x", padx=4, pady=(0, 4))
        return entry

    def _build_action_buttons(self) -> None:
        """Construye los botones de acción principales."""
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(14, 0))

        self.btn_solve = ctk.CTkButton(
            btn_frame,
            text="▶ Resolver Problema",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=36,
            command=self.on_solve
        )
        self.btn_solve.pack(fill="x", pady=4)

        self.btn_export = ctk.CTkButton(
            btn_frame,
            text="📄 Generar Salida TXT",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=34,
            command=self.on_export
        )
        self.btn_export.pack(fill="x", pady=4)

        self.btn_reset = ctk.CTkButton(
            btn_frame,
            text="🔄 Restablecer Valores",
            fg_color=("gray75", "#374151"),
            hover_color=("gray65", "#4b5563"),
            height=32,
            command=self.set_default_values
        )
        self.btn_reset.pack(fill="x", pady=4)

        self.btn_open_folder = ctk.CTkButton(
            btn_frame,
            text="📂 Abrir Carpeta Salidas",
            fg_color=("gray75", "#374151"),
            hover_color=("gray65", "#4b5563"),
            height=32,
            command=self.on_open_folder
        )
        self.btn_open_folder.pack(fill="x", pady=4)

    def _build_theme_switcher(self) -> None:
        """Construye el selector de tema inferior."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
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

    def set_default_values(self) -> None:
        """Carga los valores por defecto del ejercicio oficial de la UJAP."""
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

    def parse_problem_data(self) -> ProblemData:
        """Extrae, valida y retorna los datos del problema desde los campos del formulario."""
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
            raise ValueError("Los costos y la fuerza inicial deben ser números válidos.")

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

    def _change_appearance_mode(self, new_mode: str) -> None:
        """Cambia el modo de apariencia visual entre claro y oscuro."""
        if "Oscuro" in new_mode:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
