"""Graphical user interface for the Bike Maintenance Tracker.

This application extends the original console program with a Tk themed UI
implemented using ``ttkbootstrap``.  It keeps compatibility with the existing
``records.txt`` and ``components.txt`` files so that data can be shared between
both interfaces.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import ttkbootstrap as ttk
from ttkbootstrap import Window
from ttkbootstrap.constants import BOTH, END, LEFT, RIGHT, TOP, W
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry

BASE_DIR = Path(__file__).resolve().parent
RECORDS_FILE = BASE_DIR / "records.txt"
COMPONENTS_FILE = BASE_DIR / "components.txt"
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

    def __init__(self) -> None:
        self.records: List[MaintenanceRecord] = []
        self.components: List[ComponentStatus] = []
        self.bike_weight: float = 0.0
        self.reload()

    def reload(self) -> None:
        self.records = self._read_records()
        self.bike_weight, self.components = self._read_components()
        if not RECORDS_FILE.exists():
            self.save_records()
        if not COMPONENTS_FILE.exists():
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
        RECORDS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with RECORDS_FILE.open("w", encoding="utf-8") as file:
            file.write(f"{len(self.records)}\n")
            for record in self.records:
                description = record.description.replace("\n", " ").strip()
                file.write(f"{record.date}\n")
                file.write(f"{description}\n")

    def save_components(self) -> None:
        COMPONENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with COMPONENTS_FILE.open("w", encoding="utf-8") as file:
            file.write(f"{self.bike_weight:.2f}\n")
            for component in self.components:
                file.write(f"{component.wear_level}\n")

    def _read_records(self) -> List[MaintenanceRecord]:
        if not RECORDS_FILE.exists():
            return []

        try:
            with RECORDS_FILE.open("r", encoding="utf-8") as file:
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
        if not COMPONENTS_FILE.exists():
            return 0.0, components

        try:
            with COMPONENTS_FILE.open("r", encoding="utf-8") as file:
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


class BikeMaintenanceApp(ttk.Frame):
    def __init__(self, master: Window, manager: DataManager) -> None:
        super().__init__(master, padding=20)
        self.manager = manager
        self.pack(fill=BOTH, expand=True)
        self._create_widgets()

    def _create_widgets(self) -> None:
        title = ttk.Label(
            self,
            text="Bike Maintenance Tracker",
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(pady=(0, 20))

        notebook = ttk.Notebook(self, bootstyle="secondary")
        notebook.pack(fill=BOTH, expand=True)

        self._create_records_tab(notebook)
        self._create_weight_tab(notebook)
        self._create_components_tab(notebook)

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

    def _update_weight(self) -> None:
        try:
            weight = float(self.weight_var.get().replace(",", "."))
        except ValueError:
            Messagebox.show_warning("Enter a valid numeric weight.", title="Invalid Weight")
            return

        self.manager.set_bike_weight(weight)
        self.weight_status.configure(text="Bike weight updated successfully.")
        self._refresh_weight_display()

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

        self.wear_spin = ttk.Spinbox(
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

    def _on_component_select(self, event: tk.Event) -> None:
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


def main() -> None:
    manager = DataManager()
    window = Window(title="Bike Maintenance Tracker", themename="flatly")
    window.geometry("900x650")
    window.minsize(780, 560)
    BikeMaintenanceApp(window, manager)
    window.mainloop()


if __name__ == "__main__":
    main()
