"""
Vistas de pestañas especializadas para el Dashboard.
"""

from .schedule_view import ScheduleView
from .stages_view import StagesView
from .txt_preview_view import TxtPreviewView
from .theory_view import TheoryView

__all__ = ["ScheduleView", "StagesView", "TxtPreviewView", "TheoryView"]
