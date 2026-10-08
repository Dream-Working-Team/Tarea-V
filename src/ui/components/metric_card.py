"""
Componente reutilizable para tarjetas de métricas / KPI.
"""

import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    """Tarjeta individual estilizada para mostrar indicadores clave (KPI)."""

    def __init__(self, master, title: str, value: str, subtitle: str = "", **kwargs):
        super().__init__(master, corner_radius=10, fg_color=("gray85", "#1f2937"), **kwargs)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "#9ca3af")
        )
        self.title_label.pack(padx=14, pady=(10, 2), anchor="w")

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("gray10", "#38bdf8")
        )
        self.value_label.pack(padx=14, pady=(0, 2), anchor="w")

        self.sub_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#6b7280")
        )
        self.sub_label.pack(padx=14, pady=(0, 10), anchor="w")

    def update_values(self, value: str, subtitle: str = "") -> None:
        """Actualiza el valor numérico y texto secundario de la tarjeta."""
        self.value_label.configure(text=value)
        if subtitle:
            self.sub_label.configure(text=subtitle)
