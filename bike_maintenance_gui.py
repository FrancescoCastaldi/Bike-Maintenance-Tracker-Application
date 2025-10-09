"""Graphical user interface for the Bike Maintenance Tracker.

This application extends the original console program with a Tk themed UI
implemented using ``ttkbootstrap``.  It keeps compatibility with the existing
``records.txt`` and ``components.txt`` files so that data can be shared between
both interfaces.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from ttkbootstrap import Window, ttk
from ttkbootstrap.constants import BOTH, END, LEFT, RIGHT, TOP, W
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry, Spinbox

# ---------------------------------------------------------------------------
# Data model and persistence helpers
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR_NAME = "BikeMaintenanceData"
MAX_RECORDS = 100

DEFAULT_COMPONENTS = [
    "Front Tire",
    "Rear Tire",
    "Front Inner Tube",
    "Rear Inner Tube",
    "Front Derailleur Cable",
    "Rear Derailleur Cable",
    "Front Brake Cable",
    "Rear Brake Cable",
    "Handlebar Tape",
]


def determine_default_data_dir() -> Path:
    """Choose a sensible default directory for persistent data."""

    legacy_records = BASE_DIR / "records.txt"
    legacy_components = BASE_DIR / "components.txt"
    if legacy_records.exists() or legacy_components.exists():
        return BASE_DIR

    documents_dir = Path.home() / "Documents"
    if documents_dir.exists():
        return documents_dir / DEFAULT_DATA_DIR_NAME

    return Path.home() / DEFAULT_DATA_DIR_NAME


@dataclass
class MaintenanceRecord:
    date: str
    description: str


@dataclass
class ComponentStatus:
    name: str
    wear_level: int


class DataManager:
    """Load and persist maintenance data using the existing file format."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir: Path = (data_dir or determine_default_data_dir()).expanduser()
        self.records_file: Path = Path()
        self.components_file: Path = Path()
        self.records: List[MaintenanceRecord] = []
        self.components: List[ComponentStatus] = []
        self.bike_weight: float = 0.0
        self._update_file_paths()
        self.reload()

    # -- public API -----------------------------------------------------
    def reload(self) -> None:
        self._update_file_paths()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records = self._read_records()
        self.bike_weight, self.components = self._read_components()
        if not self.records_file.exists():
            self.save_records()
        if not self.components_file.exists():
            self.save_components()

    def add_record(self, record: MaintenanceRecord) -> None:
        if len(self.records) >= MAX_RECORDS:
            raise ValueError("Maximum number of records reached")
        self.records.append(record)
        self.save_records()

    def remove_record(self, index: int) -> None:
        if 0 <= index < len(self.records):
            del self.records[index]
            self.save_records()

    def set_bike_weight(self, weight: float) -> None:
        self.bike_weight = weight
        self.save_components()

    def set_component_wear(self, index: int, wear_level: int) -> None:
        if 0 <= index < len(self.components):
            clamped_level = max(0, min(100, wear_level))
            self.components[index].wear_level = clamped_level
            self.save_components()

    def save_records(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self.records_file.open("w", encoding="utf-8") as file:
            file.write(f"{len(self.records)}\n")
            for record in self.records:
                description = record.description.replace("\n", " ").strip()
                file.write(f"{record.date}\n")
                file.write(f"{description}\n")

    def save_components(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        components_to_write = self.components or [
            ComponentStatus(name=name, wear_level=0) for name in DEFAULT_COMPONENTS
        ]
        with self.components_file.open("w", encoding="utf-8") as file:
            file.write(f"{self.bike_weight:.2f}\n")
            for component in components_to_write:
                file.write(f"{component.wear_level}\n")

    def set_data_directory(self, new_directory: Path) -> None:
        new_directory = new_directory.expanduser().resolve()
        new_directory.mkdir(parents=True, exist_ok=True)
        self.data_dir = new_directory
        self._update_file_paths()
        self.save_records()
        self.save_components()
        self.reload()

    def get_data_directory(self) -> Path:
        return self.data_dir

    # -- internal helpers -----------------------------------------------
    def _update_file_paths(self) -> None:
        self.records_file = self.data_dir / "records.txt"
        self.components_file = self.data_dir / "components.txt"

    def _read_records(self) -> List[MaintenanceRecord]:
        if not self.records_file.exists():
            return []

        try:
            with self.records_file.open("r", encoding="utf-8") as file:
                first_line = file.readline()
                count = int(first_line.strip())
                records: List[MaintenanceRecord] = []
                for _ in range(max(0, count)):
                    date_line = file.readline()
                    description_line = file.readline()
                    if not date_line or not description_line:
                        break
                    records.append(
                        MaintenanceRecord(
                            date=date_line.strip(),
                            description=description_line.strip(),
                        )
                    )
                return records
        except (OSError, ValueError):
            return []

    def _read_components(self) -> tuple[float, List[ComponentStatus]]:
        components = [ComponentStatus(name=name, wear_level=0) for name in DEFAULT_COMPONENTS]
        if not self.components_file.exists():
            return 0.0, components

        try:
            with self.components_file.open("r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines()]
        except OSError:
            return 0.0, components

        weight = 0.0
        if lines:
            try:
                weight = float(lines[0])
            except ValueError:
                weight = 0.0

        for index, component in enumerate(components, start=1):
            if index < len(lines):
                try:
                    wear_level = int(lines[index])
                    component.wear_level = max(0, min(100, wear_level))
                except ValueError:
                    component.wear_level = 0

        return weight, components


# ---------------------------------------------------------------------------
# Graphical interface
# ---------------------------------------------------------------------------


class FuturisticHeader(ttk.Frame):
    """Animated header with a neon gradient and scanning effect."""

    def __init__(self, master: tk.Widget, *, title: str, subtitle: str) -> None:
        super().__init__(master, padding=0)
        self.configure(style="Glass.TFrame")
        self.canvas = tk.Canvas(
            self,
            height=120,
            highlightthickness=0,
            bd=0,
            bg="#050b14",
        )
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.bind("<Configure>", self._draw_background)
        self._title_id = self.canvas.create_text(
            35,
            48,
            anchor="w",
            text=title,
            fill="#e2e8f0",
            font=("Orbitron", 26, "bold"),
        )
        self._subtitle_id = self.canvas.create_text(
            35,
            82,
            anchor="w",
            text=subtitle,
            fill="#38bdf8",
            font=("Segoe UI", 12),
        )
        self._scan_position = 0
        self.after(1200, self._animate_pulse)
        self._animate_scan()

    def update_subtitle(self, text: str) -> None:
        self.canvas.itemconfigure(self._subtitle_id, text=text)

    # -- drawing helpers -------------------------------------------------
    def _draw_background(self, _event: tk.Event | None = None) -> None:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self.canvas.delete("gradient")
        steps = max(1, width // 6)
        for step in range(steps):
            ratio = step / steps
            color = self._interpolate_color("#06111c", "#00f0ff", ratio ** 0.7)
            x0 = int(step * width / steps)
            x1 = int((step + 1) * width / steps)
            self.canvas.create_rectangle(
                x0,
                0,
                x1,
                height,
                fill=color,
                outline="",
                tags="gradient",
            )
        self.canvas.create_line(
            0,
            height - 3,
            width,
            height - 3,
            fill="#00ffd5",
            width=3,
            tags="gradient",
        )

    def _animate_scan(self) -> None:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self.canvas.delete("scan")
        x_start = (self._scan_position % (width + 240)) - 120
        self.canvas.create_rectangle(
            x_start,
            0,
            x_start + 120,
            height,
            fill="#00ffd544",
            outline="",
            tags="scan",
        )
        self._scan_position += 12
        self.after(70, self._animate_scan)

    def _animate_pulse(self) -> None:
        current_color = self.canvas.itemcget(self._title_id, "fill")
        next_color = "#f8fafc" if current_color == "#e2e8f0" else "#e2e8f0"
        self.canvas.itemconfigure(self._title_id, fill=next_color)
        self.after(1600, self._animate_pulse)

    @staticmethod
    def _interpolate_color(start_hex: str, end_hex: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))
        start_rgb = tuple(int(start_hex[i : i + 2], 16) for i in (1, 3, 5))
        end_rgb = tuple(int(end_hex[i : i + 2], 16) for i in (1, 3, 5))
        blended = tuple(int(s + (e - s) * ratio) for s, e in zip(start_rgb, end_rgb))
        return "#" + "".join(f"{value:02x}" for value in blended)


class BikeMaintenanceApp(ttk.Frame):
    def __init__(self, master: Window, manager: DataManager) -> None:
        super().__init__(master, padding=24, style="Glass.TFrame")
        self.manager = manager
        self.master = master
        self.metric_labels: Dict[str, Tuple[ttk.Label, str]] = {}
        self.diagnostics_summary: ttk.Label | None = None
        self.alerts_list: tk.Listbox | None = None
        self.chart_figure: Figure | None = None
        self.chart_axes = None
        self.chart_canvas: FigureCanvasTkAgg | None = None
        self.quick_date_entry: DateEntry | None = None
        self.quick_description_var = tk.StringVar(value="")
        self.quick_status_var = tk.StringVar(value="")
        self.save_location_var = tk.StringVar(value=str(self.manager.get_data_directory()))
        self._init_style()
        self.pack(fill=BOTH, expand=True)
        self._create_widgets()

    # -- setup ----------------------------------------------------------
    def _create_widgets(self) -> None:
        self.header = FuturisticHeader(
            self,
            title="Bike Maintenance Nexus",
            subtitle="Initializing telemetry...",
        )
        self.header.pack(fill="x", pady=(0, 20))

        self._create_quick_entry_panel()
        self._update_storage_display()
        self._create_metric_cards()

        notebook = ttk.Notebook(self, bootstyle="secondary")
        notebook.pack(fill=BOTH, expand=True)

        self._create_records_tab(notebook)
        self._create_weight_tab(notebook)
        self._create_components_tab(notebook)
        self._create_diagnostics_tab(notebook)

    def _create_quick_entry_panel(self) -> None:
        panel = ttk.Frame(self, padding=(18, 14), style="GlassInner.TFrame")
        panel.pack(fill="x", pady=(0, 18))
        panel.columnconfigure(1, weight=1)

        ttk.Label(panel, text="Quick Record Entry", style="NeonSmall.TLabel").grid(
            row=0, column=0, columnspan=3, sticky=W
        )

        ttk.Label(panel, text="Date", style="Neon.TLabel").grid(row=1, column=0, sticky=W, pady=(8, 0))
        self.quick_date_entry = DateEntry(panel, bootstyle="primary", dateformat="%Y-%m-%d")
        self.quick_date_entry.grid(row=2, column=0, sticky="we", pady=(4, 0))

        ttk.Label(panel, text="Description", style="Neon.TLabel").grid(
            row=1, column=1, sticky=W, padx=(16, 0), pady=(8, 0)
        )
        description_entry = ttk.Entry(
            panel,
            textvariable=self.quick_description_var,
            width=60,
        )
        description_entry.grid(row=2, column=1, sticky="we", padx=(16, 0), pady=(4, 0))

        ttk.Button(
            panel,
            text="Save Record",
            bootstyle="success",
            command=self._submit_quick_record,
        ).grid(row=2, column=2, sticky="e", padx=(16, 0), pady=(4, 0))

        storage_frame = ttk.Frame(panel, style="GlassInner.TFrame")
        storage_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        storage_frame.columnconfigure(1, weight=1)

        ttk.Label(storage_frame, text="Saving to", style="PathLabel.TLabel").grid(row=0, column=0, sticky=W)
        ttk.Label(
            storage_frame,
            textvariable=self.save_location_var,
            style="PathInfo.TLabel",
            wraplength=420,
        ).grid(row=0, column=1, sticky="w", padx=(6, 0))

        ttk.Button(
            storage_frame,
            text="Change Folder",
            bootstyle="secondary",
            command=self._choose_save_folder,
        ).grid(row=0, column=2, sticky="e", padx=(12, 0))

        ttk.Label(
            panel,
            textvariable=self.quick_status_var,
            style="PathInfo.TLabel",
        ).grid(row=4, column=0, columnspan=3, sticky=W, pady=(10, 0))

    # -- records tab ----------------------------------------------------
    def _create_records_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Maintenance Records")

        columns = ("date", "description")
        self.records_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            height=12,
            bootstyle="info",
        )
        self.records_tree.heading("date", text="Date")
        self.records_tree.heading("description", text="Description")
        self.records_tree.column("date", width=120, anchor=W)
        self.records_tree.column("description", width=520, anchor=W)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.records_tree.yview)
        self.records_tree.configure(yscrollcommand=scrollbar.set)

        self.records_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill="y")

        button_bar = ttk.Frame(tab)
        button_bar.pack(side=TOP, fill="x", pady=(15, 0))

        add_button = ttk.Button(
            button_bar,
            text="Add Record",
            bootstyle="success",
            command=self._open_add_record_dialog,
        )
        add_button.pack(side=LEFT)

        delete_button = ttk.Button(
            button_bar,
            text="Delete Selected",
            bootstyle="danger",
            command=self._delete_selected_record,
        )
        delete_button.pack(side=LEFT, padx=10)

        refresh_button = ttk.Button(
            button_bar,
            text="Refresh",
            bootstyle="secondary",
            command=self._refresh_records,
        )
        refresh_button.pack(side=LEFT)

        self.records_status = ttk.Label(tab, text="")
        self.records_status.pack(side=TOP, anchor=W, pady=(10, 0))

        self._refresh_records()

    def _submit_quick_record(self) -> None:
        if not self.quick_date_entry:
            return

        self.quick_status_var.set("")

        if len(self.manager.records) >= MAX_RECORDS:
            Messagebox.show_warning(
                "The records list is full. Remove an entry before adding a new one.",
                title="Maximum Records Reached",
            )
            return

        date_value = self.quick_date_entry.entry.get().strip()
        description_value = self.quick_description_var.get().strip()

        if not date_value or not description_value:
            self.quick_status_var.set("Please provide both date and description.")
            return

        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            self.quick_status_var.set("Date must follow YYYY-MM-DD format.")
            return

        new_record = MaintenanceRecord(date=date_value, description=description_value)
        try:
            self.manager.add_record(new_record)
        except ValueError as exc:
            Messagebox.show_error(str(exc), title="Unable to Add Record")
            return

        self.quick_description_var.set("")
        self.quick_status_var.set("Record saved successfully.")
        self._refresh_records()

    def _choose_save_folder(self) -> None:
        initial_dir = str(self.manager.get_data_directory())
        selected = filedialog.askdirectory(
            parent=self,
            initialdir=initial_dir,
            title="Select storage folder",
        )
        if not selected:
            return

        try:
            self.manager.set_data_directory(Path(selected))
        except OSError as exc:
            Messagebox.show_error(str(exc), title="Unable to Update Folder")
            return

        self.quick_status_var.set("Storage folder updated.")
        self._update_storage_display()
        self._refresh_records()
        self._refresh_components()

    def _update_storage_display(self) -> None:
        path = str(self.manager.get_data_directory())
        self.save_location_var.set(path)
        if hasattr(self, "header"):
            self.header.update_subtitle(f"Data directory: {path}")

    def _refresh_records(self) -> None:
        self.manager.reload()
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        for index, record in enumerate(self.manager.records):
            self.records_tree.insert("", END, iid=str(index), values=(record.date, record.description))
        if self.manager.records:
            message = f"Loaded {len(self.manager.records)} record(s)."
        else:
            message = "No maintenance records available."
        self.records_status.configure(text=message)
        self._update_storage_display()
        self._refresh_diagnostics()

    def _open_add_record_dialog(self) -> None:
        if len(self.manager.records) >= MAX_RECORDS:
            Messagebox.show_warning(
                "The records list is full. Remove an entry before adding a new one.",
                title="Maximum Records Reached",
            )
            return

        dialog = ttk.Toplevel(self)
        dialog.title("Add Maintenance Record")
        dialog.resizable(False, False)
        dialog.grab_set()

        ttk.Label(dialog, text="Date", padding=(10, 10, 10, 0)).grid(row=0, column=0, sticky=W)
        date_entry = DateEntry(dialog, bootstyle="primary", dateformat="%Y-%m-%d")
        date_entry.grid(row=1, column=0, sticky=W, padx=10)

        ttk.Label(dialog, text="Description", padding=(10, 10, 10, 0)).grid(row=2, column=0, sticky=W)
        description_text = tk.Text(dialog, height=6, width=50, wrap="word")
        description_text.grid(row=3, column=0, padx=10, pady=(0, 10))

        button_row = ttk.Frame(dialog)
        button_row.grid(row=4, column=0, pady=(0, 10))

        def submit() -> None:
            date_value = date_entry.entry.get().strip()
            description_value = description_text.get("1.0", "end").strip()
            if not date_value or not description_value:
                Messagebox.show_warning("Please provide both the date and description.", title="Missing Information")
                return
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                Messagebox.show_warning("Date must be in YYYY-MM-DD format.", title="Invalid Date")
                return

            new_record = MaintenanceRecord(date=date_value, description=description_value)
            try:
                self.manager.add_record(new_record)
            except ValueError as exc:
                Messagebox.show_error(str(exc), title="Unable to Add Record")
                return

            Messagebox.show_info("Record added successfully!", title="Success")
            dialog.destroy()
            self._refresh_records()

        submit_button = ttk.Button(button_row, text="Save", bootstyle="success", command=submit)
        submit_button.pack(side=LEFT, padx=5)

        cancel_button = ttk.Button(button_row, text="Cancel", bootstyle="secondary", command=dialog.destroy)
        cancel_button.pack(side=LEFT, padx=5)

        dialog.wait_window()

    def _delete_selected_record(self) -> None:
        selection = self.records_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a record to delete.", title="No Selection")
            return

        index = int(selection[0])
        result = Messagebox.yesno("Delete the selected record?", title="Confirm Deletion")
        if result == "Yes":
            self.manager.remove_record(index)
            self._refresh_records()

    # -- bike weight tab ------------------------------------------------
    def _create_weight_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Bike Weight")

        ttk.Label(tab, text="Current Bike Weight", font=("Segoe UI", 14, "bold")).pack(anchor=W)
        self.weight_display = ttk.Label(tab, font=("Segoe UI", 12))
        self.weight_display.pack(anchor=W, pady=(5, 15))

        ttk.Label(tab, text="Update Weight (kg)", font=("Segoe UI", 11)).pack(anchor=W)
        self.weight_var = tk.StringVar(value=f"{self.manager.bike_weight:.2f}")
        weight_entry = ttk.Entry(tab, textvariable=self.weight_var, width=10)
        weight_entry.pack(anchor=W, pady=(5, 10))

        update_button = ttk.Button(
            tab,
            text="Save Weight",
            bootstyle="success",
            command=self._update_weight,
        )
        update_button.pack(anchor=W)

        self.weight_status = ttk.Label(tab, text="")
        self.weight_status.pack(anchor=W, pady=(10, 0))

        self._refresh_weight_display()

    def _refresh_weight_display(self) -> None:
        self.weight_display.configure(text=f"{self.manager.bike_weight:.2f} kg")
        self.weight_var.set(f"{self.manager.bike_weight:.2f}")
        self._refresh_diagnostics()

    def _update_weight(self) -> None:
        try:
            weight = float(self.weight_var.get().replace(",", "."))
        except ValueError:
            Messagebox.show_warning("Enter a valid numeric weight.", title="Invalid Weight")
            return

        self.manager.set_bike_weight(weight)
        self.weight_status.configure(text="Bike weight updated successfully.")
        self._refresh_weight_display()

    # -- components tab -------------------------------------------------
    def _create_components_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Components")

        columns = ("component", "wear")
        self.components_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            height=10,
            bootstyle="info",
            selectmode="browse",
        )
        self.components_tree.heading("component", text="Component")
        self.components_tree.heading("wear", text="Wear (%)")
        self.components_tree.column("component", width=300, anchor=W)
        self.components_tree.column("wear", width=120, anchor=W)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.components_tree.yview)
        self.components_tree.configure(yscrollcommand=scrollbar.set)

        self.components_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill="y")

        controls = ttk.Frame(tab, padding=(0, 15, 0, 0))
        controls.pack(side=TOP, fill="x")

        self.wear_var = tk.IntVar(value=0)
        ttk.Label(controls, text="Selected Wear Level", font=("Segoe UI", 11)).pack(anchor=W)
        self.wear_progress = ttk.Progressbar(
            controls,
            maximum=100,
            variable=self.wear_var,
            bootstyle="success-striped",
        )
        self.wear_progress.pack(fill="x", pady=(5, 10))

        self.wear_spin = Spinbox(
            controls,
            from_=0,
            to=100,
            increment=1,
            width=5,
            bootstyle="info",
            textvariable=self.wear_var,
        )
        self.wear_spin.pack(anchor=W)

        update_button = ttk.Button(
            controls,
            text="Save Wear Level",
            bootstyle="success",
            command=self._update_component_wear,
        )
        update_button.pack(anchor=W, pady=(10, 0))

        refresh_button = ttk.Button(
            controls,
            text="Refresh",
            bootstyle="secondary",
            command=self._refresh_components,
        )
        refresh_button.pack(anchor=W, pady=(5, 0))

        self.components_status = ttk.Label(controls, text="")
        self.components_status.pack(anchor=W, pady=(10, 0))

        self.components_tree.bind("<<TreeviewSelect>>", self._on_component_select)

        self._refresh_components()

    def _refresh_components(self) -> None:
        self.manager.reload()
        for item in self.components_tree.get_children():
            self.components_tree.delete(item)
        for index, component in enumerate(self.manager.components):
            self.components_tree.insert(
                "",
                END,
                iid=str(index),
                values=(component.name, f"{component.wear_level}%"),
            )
        if self.manager.components:
            self.components_status.configure(text="Select a component to adjust its wear level.")
        else:
            self.components_status.configure(text="No component data available.")
        self.wear_var.set(0)
        self._refresh_diagnostics()

    def _on_component_select(self, event: tk.Event) -> None:  # pragma: no cover - UI callback
        selection = self.components_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        wear_level = self.manager.components[index].wear_level
        self.wear_var.set(wear_level)

    def _update_component_wear(self) -> None:
        selection = self.components_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a component to update.", title="No Selection")
            return

        index = int(selection[0])
        wear_level = int(self.wear_var.get())
        self.manager.set_component_wear(index, wear_level)
        self.components_status.configure(text="Component wear level updated successfully.")
        self._refresh_components()

    # -- diagnostics tab ------------------------------------------------
    def _create_diagnostics_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=20, style="Glass.TFrame")
        notebook.add(tab, text="Diagnostics")

        self.diagnostics_summary = ttk.Label(
            tab,
            text="System telemetry will appear here once data is available.",
            style="Neon.TLabel",
            wraplength=680,
        )
        self.diagnostics_summary.pack(anchor=W, pady=(0, 20))

        content = ttk.Frame(tab, style="Glass.TFrame")
        content.pack(fill=BOTH, expand=True)

        chart_frame = ttk.Frame(content, padding=15, style="GlassInner.TFrame")
        chart_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.chart_figure = Figure(figsize=(5.8, 3.6), dpi=100)
        self.chart_figure.patch.set_facecolor("#050b14")
        self.chart_axes = self.chart_figure.add_subplot(111)
        self.chart_axes.set_facecolor("#050b14")
        self.chart_axes.tick_params(colors="#94a3b8")
        for spine in self.chart_axes.spines.values():
            spine.set_color("#1f2937")
        self.chart_axes.set_title("Component Wear Distribution", color="#e2e8f0", pad=16)
        self.chart_axes.set_xlabel("Wear %", color="#94a3b8")
        self.chart_axes.set_ylabel("Component", color="#94a3b8")

        self.chart_canvas = FigureCanvasTkAgg(self.chart_figure, master=chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        alerts_frame = ttk.Frame(content, padding=15, style="GlassInner.TFrame")
        alerts_frame.pack(side=RIGHT, fill="y", padx=(18, 0))

        ttk.Label(alerts_frame, text="Critical Components", style="NeonSmall.TLabel").pack(anchor=W)

        self.alerts_list = tk.Listbox(
            alerts_frame,
            height=12,
            bg="#06121f",
            fg="#f97316",
            relief="flat",
            highlightthickness=0,
            selectbackground="#0ea5e9",
            selectforeground="#0f172a",
            font=("Segoe UI", 10),
        )
        self.alerts_list.pack(fill=BOTH, expand=True, pady=(12, 12))

        ttk.Button(
            alerts_frame,
            text="Service Recommendations",
            bootstyle="warning-outline",
            command=self._suggest_wear_adjustment,
        ).pack(fill="x")

        self._refresh_diagnostics()

    def _suggest_wear_adjustment(self) -> None:
        recommendations: List[str] = []
        for component in self.manager.components:
            if component.wear_level >= 90:
                recommendations.append(f"{component.name}: Replace immediately (>{component.wear_level}% wear)")
            elif component.wear_level >= 70:
                recommendations.append(f"{component.name}: Schedule inspection soon ({component.wear_level}% wear)")

        if not recommendations:
            Messagebox.show_info("All components are operating within safe parameters.", title="System Nominal")
            return

        Messagebox.show_info("\n".join(recommendations), title="Maintenance Recommendations")

    # -- shared styling -------------------------------------------------
    def _init_style(self) -> None:
        self.master.configure(bg="#050b14")
        style = self.master.style
        style.configure("Glass.TFrame", background="#050b14")
        style.configure("GlassInner.TFrame", background="#071120", borderwidth=0)
        style.configure("Neon.TLabel", background="#050b14", foreground="#e2e8f0", font=("Segoe UI", 12))
        style.configure("NeonSmall.TLabel", background="#071120", foreground="#38bdf8", font=("Segoe UI", 11, "bold"))
        style.configure("MetricHeading.TLabel", background="#071120", foreground="#64748b", font=("Segoe UI", 9, "bold"))
        style.configure("MetricValue.TLabel", background="#071120", foreground="#f8fafc", font=("Orbitron", 20, "bold"))
        style.configure("MetricCard.TFrame", background="#071120", borderwidth=0)
        style.configure("PathLabel.TLabel", background="#071120", foreground="#38bdf8", font=("Segoe UI", 10, "bold"))
        style.configure("PathInfo.TLabel", background="#071120", foreground="#94a3b8", font=("Segoe UI", 9))
        style.configure("Treeview", background="#0d1624", foreground="#e2e8f0", fieldbackground="#0d1624", bordercolor="#1f2937")
        style.configure("Treeview.Heading", background="#111c2d", foreground="#38bdf8", font=("Segoe UI", 10, "bold"))
        style.map(
            "Treeview",
            background=[("selected", "#0ea5e9")],
            foreground=[("selected", "#04121f")],
        )
        style.map(
            "TButton",
            background=[("active", "#00f0ff"), ("pressed", "#00f0ff")],
            foreground=[("active", "#04121f"), ("pressed", "#04121f")],
        )

    def _create_metric_cards(self) -> None:
        panel = ttk.Frame(self, style="Glass.TFrame")
        panel.pack(fill="x", pady=(0, 18))

        card_specs = [
            ("records", "Maintenance Logs", "#00f0ff"),
            ("weight", "Bike Mass", "#a855f7"),
            ("alerts", "Critical Alerts", "#f97316"),
        ]

        for key, title, color in card_specs:
            card = ttk.Frame(panel, padding=(20, 16), style="MetricCard.TFrame")
            card.pack(side=LEFT, expand=True, fill="x", padx=6)

            ttk.Label(card, text=title.upper(), style="MetricHeading.TLabel").pack(anchor=W)
            value_label = ttk.Label(card, text="--", style="MetricValue.TLabel")
            value_label.configure(foreground=color)
            value_label.pack(anchor=W, pady=(6, 0))

            accent = tk.Canvas(card, height=3, highlightthickness=0, bd=0, bg="#071120")
            accent.pack(fill="x", pady=(14, 0))
            accent.create_rectangle(0, 0, 120, 3, fill=color, outline="")

            self.metric_labels[key] = (value_label, color)

    def _refresh_diagnostics(self) -> None:
        if not self.metric_labels:
            return

        total_records = len(self.manager.records)
        components = self.manager.components
        average_wear = mean([component.wear_level for component in components]) if components else 0.0
        critical_components = [component for component in components if component.wear_level >= 70]

        if "records" in self.metric_labels:
            self.metric_labels["records"][0].configure(text=f"{total_records:02d}")
        if "weight" in self.metric_labels:
            weight_text = f"{self.manager.bike_weight:.1f} kg" if self.manager.bike_weight else "-- kg"
            self.metric_labels["weight"][0].configure(text=weight_text)
        if "alerts" in self.metric_labels:
            self.metric_labels["alerts"][0].configure(text=str(len(critical_components)))

        if self.diagnostics_summary is not None:
            summary = (
                f"{total_records} maintenance log(s) • Avg wear {average_wear:.1f}% • "
                f"{len(critical_components)} critical alert(s)"
            )
            self.diagnostics_summary.configure(text=summary)

        if self.header is not None:
            subtitle = (
                f"Logs: {total_records}   Avg Wear: {average_wear:.1f}%   Alerts: {len(critical_components)}"
            )
            self.header.update_subtitle(subtitle)

        if self.alerts_list is not None:
            self.alerts_list.delete(0, END)
            if critical_components:
                for component in critical_components:
                    self.alerts_list.insert(
                        END,
                        f"{component.name} — {component.wear_level}% wear",
                    )
            else:
                self.alerts_list.insert(END, "All components within nominal range.")

        if self.chart_axes is not None and self.chart_canvas is not None:
            self.chart_axes.clear()
            self.chart_axes.set_facecolor("#050b14")
            self.chart_axes.set_title("Component Wear Distribution", color="#e2e8f0", pad=16)
            self.chart_axes.set_xlabel("Wear %", color="#94a3b8")
            self.chart_axes.set_ylabel("Component", color="#94a3b8")
            self.chart_axes.tick_params(colors="#94a3b8")
            for spine in self.chart_axes.spines.values():
                spine.set_color("#1f2937")
            self.chart_axes.grid(axis="x", color="#1f2937", linestyle="--", linewidth=0.6)
            self.chart_axes.set_xlim(0, 100)

            if components:
                component_names = [component.name for component in components]
                wear_values = [component.wear_level for component in components]
                colors = [self._neon_gradient_color(index, len(components)) for index in range(len(components))]
                self.chart_axes.barh(component_names, wear_values, color=colors, edgecolor="#0f172a")
            else:
                self.chart_axes.text(
                    0.5,
                    0.5,
                    "No component data",
                    color="#64748b",
                    ha="center",
                    va="center",
                    transform=self.chart_axes.transAxes,
                )

            self.chart_canvas.draw_idle()

    @staticmethod
    def _neon_gradient_color(index: int, total: int) -> str:
        base_palette = ["#00f0ff", "#38bdf8", "#a855f7", "#f97316", "#facc15"]
        if total <= len(base_palette):
            return base_palette[index % len(base_palette)]
        ratio = index / max(1, total - 1)
        return FuturisticHeader._interpolate_color("#00f0ff", "#f472b6", ratio)


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------


def main() -> None:
    manager = DataManager()
    window = Window(title="Bike Maintenance Tracker", themename="cyborg")
    window.geometry("980x720")
    window.minsize(820, 600)
    BikeMaintenanceApp(window, manager)
    window.mainloop()


if __name__ == "__main__":
    main()
