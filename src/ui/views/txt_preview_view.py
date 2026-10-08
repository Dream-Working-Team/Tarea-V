"""
Vista de Previsualización y Gestión de Archivos TXT (Pestaña 3).
"""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk


class TxtPreviewView(ctk.CTkFrame):
    """Panel que presenta el visor del archivo de texto y controles de guardado."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_action_bar()
        self._build_textbox()

    def _build_action_bar(self) -> None:
        """Construye la barra de herramientas superior."""
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 8))

        self.txt_status_lbl = ctk.CTkLabel(
            action_bar,
            text="Listo para exportar reporte.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "#9ca3af")
        )
        self.txt_status_lbl.pack(side="left")

        btn_copy = ctk.CTkButton(
            action_bar,
            text="📋 Copiar Todo",
            width=110,
            height=28,
            command=self._copy_txt_to_clipboard
        )
        btn_copy.pack(side="right", padx=4)

        btn_save_as = ctk.CTkButton(
            action_bar,
            text="💾 Guardar Como...",
            width=130,
            height=28,
            command=self._save_txt_as
        )
        btn_save_as.pack(side="right", padx=4)

    def _build_textbox(self) -> None:
        """Construye el área de texto monoespaciada."""
        self.txt_textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.txt_textbox.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

    def update_content(self, text_content: str, status_message: str = "") -> None:
        """Actualiza el texto en el visor."""
        self.txt_textbox.delete("1.0", tk.END)
        self.txt_textbox.insert("1.0", text_content)
        if status_message:
            self.set_status(status_message)

    def set_status(self, message: str, is_success: bool = False) -> None:
        """Actualiza el mensaje de estado superior."""
        color = "#34d399" if is_success else ("gray40", "#9ca3af")
        self.txt_status_lbl.configure(text=message, text_color=color)

    def _copy_txt_to_clipboard(self) -> None:
        """Copia todo el texto del reporte al portapapeles."""
        text = self.txt_textbox.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", "Contenido del reporte copiado al portapapeles.")

    def _save_txt_as(self) -> None:
        """Permite al usuario guardar el reporte en una ruta personalizada."""
        text = self.txt_textbox.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile="reporte_fuerza_trabajo.txt"
        )
        if file_path:
            Path(file_path).write_text(text, encoding="utf-8")
            messagebox.showinfo("Guardado", f"Archivo guardado exitosamente en:\n{file_path}")
