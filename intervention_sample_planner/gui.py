"""Tkinter interface for Intervention Sample Planner."""

# File version: 1.0; date: 2026-05-11

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from .calculator import (
    PlanningError,
    StudyConfig,
    calculate_plan,
    config_to_dict,
    load_config,
    render_report,
    save_config,
)
from .i18n import t
from .version import APP_WINDOW_TITLE


FIELD_GROUPS = [
    (
        "design",
        [
            "study_name",
            "language",
            "analysis_unit",
            "observation_unit",
            "outcome_type",
            "alternative",
            "alpha",
            "power",
            "primary_comparisons",
            "allocation_ratio",
        ],
    ),
    (
        "continuous_outcome",
        ["effect_size_d", "mean_control", "mean_intervention", "sd_pooled"],
    ),
    (
        "binary_outcome",
        ["proportion_control", "proportion_intervention"],
    ),
    (
        "corrections",
        [
            "apply_fpc",
            "finite_population",
            "cluster_average_size",
            "intraclass_correlation",
            "response_rate",
            "completion_rate",
            "usable_data_rate",
            "extra_buffer_rate",
        ],
    ),
    ("labels_notes", ["intervention_label", "control_label", "notes"]),
]

FIELD_TYPES = {
    "study_name": "text",
    "language": "language",
    "analysis_unit": "text",
    "observation_unit": "text",
    "outcome_type": "outcome",
    "alternative": "alternative",
    "alpha": "rate",
    "power": "rate",
    "primary_comparisons": "int",
    "allocation_ratio": "float",
    "effect_size_d": "optional_float",
    "mean_control": "optional_float",
    "mean_intervention": "optional_float",
    "sd_pooled": "optional_float",
    "proportion_control": "rate",
    "proportion_intervention": "rate",
    "apply_fpc": "bool",
    "finite_population": "optional_int",
    "cluster_average_size": "float",
    "intraclass_correlation": "rate",
    "response_rate": "rate",
    "completion_rate": "rate",
    "usable_data_rate": "rate",
    "extra_buffer_rate": "rate",
    "intervention_label": "text",
    "control_label": "text",
    "notes": "multiline",
}

WIZARD_FIELDS = [
    "study_name",
    "outcome_type",
    "effect_size_d",
    "proportion_control",
    "proportion_intervention",
    "alpha",
    "power",
    "allocation_ratio",
    "response_rate",
    "completion_rate",
    "usable_data_rate",
    "primary_comparisons",
    "cluster_average_size",
    "intraclass_correlation",
]

WIZARD_KEY_OVERRIDES = {
    "cluster_average_size": "clusters",
    "intraclass_correlation": "clusters",
}


class PlannerApp(tk.Tk):
    """Main Tkinter window."""

    def __init__(self) -> None:
        super().__init__()
        self.config_model = StudyConfig()
        self.vars: dict[str, tk.Variable] = {}
        self.text_widgets: dict[str, tk.Text] = {}
        self.current_plan = None
        self.wizard_index = 0
        self.title(APP_WINDOW_TITLE)
        self.geometry("1120x780")
        self.minsize(920, 620)
        self._build_ui()

    @property
    def language(self) -> str:
        return self.config_model.language

    def _build_ui(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        self.vars = {}
        self.text_widgets = {}
        self.title(APP_WINDOW_TITLE)

        shell = ttk.Frame(self, padding=10)
        shell.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(shell)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=APP_WINDOW_TITLE, font=("Segoe UI", 16, "bold")).pack(
            side=tk.LEFT
        )
        ttk.Label(header, text=t(self.language, "language")).pack(side=tk.RIGHT, padx=(8, 0))
        self.language_var = tk.StringVar(value=self.language)
        language_combo = ttk.Combobox(
            header,
            textvariable=self.language_var,
            values=["en", "pt"],
            width=6,
            state="readonly",
        )
        language_combo.pack(side=tk.RIGHT)
        language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        self.notebook = ttk.Notebook(shell)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.wizard_tab = ttk.Frame(self.notebook, padding=12)
        self.data_tab = ttk.Frame(self.notebook, padding=8)
        self.results_tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.wizard_tab, text=t(self.language, "wizard_tab"))
        self.notebook.add(self.data_tab, text=t(self.language, "data_tab"))
        self.notebook.add(self.results_tab, text=t(self.language, "results_tab"))

        self._build_data_tab()
        self._sync_config_to_vars()
        self._build_wizard_tab()
        self._build_results_tab()

    def _on_language_change(self, _event: Any = None) -> None:
        try:
            self._sync_config_from_vars()
        except PlanningError:
            pass
        self.config_model.language = self.language_var.get()
        self._build_ui()

    def _build_wizard_tab(self) -> None:
        intro = ttk.Label(
            self.wizard_tab,
            text=t(self.language, "wizard_intro"),
            wraplength=920,
            font=("Segoe UI", 10),
        )
        intro.pack(anchor=tk.W, pady=(0, 12))

        self.wizard_card = ttk.Frame(self.wizard_tab, padding=12, relief=tk.GROOVE)
        self.wizard_card.pack(fill=tk.BOTH, expand=True)

        self.wizard_progress = ttk.Label(self.wizard_card, text="")
        self.wizard_progress.pack(anchor=tk.W)
        self.wizard_question = ttk.Label(
            self.wizard_card,
            text="",
            wraplength=880,
            font=("Segoe UI", 14, "bold"),
        )
        self.wizard_question.pack(anchor=tk.W, pady=(12, 4))
        self.wizard_why = ttk.Label(self.wizard_card, text="", wraplength=880)
        self.wizard_why.pack(anchor=tk.W, pady=(0, 16))

        self.wizard_input = ttk.Frame(self.wizard_card)
        self.wizard_input.pack(fill=tk.X, pady=(0, 16))

        buttons = ttk.Frame(self.wizard_card)
        buttons.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(buttons, text=t(self.language, "reset"), command=self._reset_wizard).pack(
            side=tk.LEFT
        )
        self.prev_button = ttk.Button(
            buttons, text=t(self.language, "previous"), command=self._wizard_previous
        )
        self.prev_button.pack(side=tk.RIGHT, padx=(8, 0))
        self.next_button = ttk.Button(buttons, text=t(self.language, "next"), command=self._wizard_next)
        self.next_button.pack(side=tk.RIGHT)

        self._render_wizard_step()

    def _build_data_tab(self) -> None:
        top = ttk.Frame(self.data_tab)
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(top, text=t(self.language, "direct_mode_hint")).pack(side=tk.LEFT)
        ttk.Button(top, text=t(self.language, "calculate"), command=self.calculate).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(top, text=t(self.language, "load_config"), command=self.load_configuration).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(top, text=t(self.language, "save_config"), command=self.save_configuration).pack(
            side=tk.RIGHT, padx=(8, 0)
        )

        canvas = tk.Canvas(self.data_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.data_tab, orient=tk.VERTICAL, command=canvas.yview)
        self.data_inner = ttk.Frame(canvas)
        self.data_inner.bind(
            "<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        window_id = canvas.create_window((0, 0), window=self.data_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0
        for group_key, fields in FIELD_GROUPS:
            header = ttk.Label(
                self.data_inner,
                text=t(self.language, group_key),
                font=("Segoe UI", 11, "bold"),
            )
            header.grid(row=row, column=0, columnspan=4, sticky="w", pady=(12, 4))
            row += 1
            for field in fields:
                row = self._add_config_field(self.data_inner, field, row)

        self.data_inner.columnconfigure(2, weight=1)

    def _build_results_tab(self) -> None:
        top = ttk.Frame(self.results_tab)
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(top, text=t(self.language, "calculate"), command=self.calculate).pack(side=tk.RIGHT)
        ttk.Button(top, text=t(self.language, "save_report"), command=self.save_report).pack(
            side=tk.RIGHT, padx=(0, 8)
        )

        self.results_notebook = ttk.Notebook(self.results_tab)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)

        summary_frame = ttk.Frame(self.results_notebook, padding=6)
        sensitivity_frame = ttk.Frame(self.results_notebook, padding=6)
        json_frame = ttk.Frame(self.results_notebook, padding=6)
        self.results_notebook.add(summary_frame, text=t(self.language, "summary_tab"))
        self.results_notebook.add(sensitivity_frame, text=t(self.language, "sensitivity_tab"))
        self.results_notebook.add(json_frame, text=t(self.language, "json_tab"))

        self.summary_text = self._make_text(summary_frame)
        self.summary_text.insert("1.0", t(self.language, "no_results"))
        self.sensitivity_table = self._make_sensitivity_table(sensitivity_frame)
        self.json_text = self._make_text(json_frame)

    def _make_text(self, parent: ttk.Frame) -> tk.Text:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        text = tk.Text(frame, wrap=tk.WORD, height=20, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return text

    def _make_sensitivity_table(self, parent: ttk.Frame) -> ttk.Treeview:
        columns = (
            "scenario",
            "valid_control",
            "valid_intervention",
            "valid_total",
            "invited_total",
        )
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        headings = {
            "scenario": t(self.language, "sens_col_scenario"),
            "valid_control": t(self.language, "sens_col_valid_control"),
            "valid_intervention": t(self.language, "sens_col_valid_intervention"),
            "valid_total": t(self.language, "sens_col_valid_total"),
            "invited_total": t(self.language, "sens_col_invited_total"),
        }
        widths = {
            "scenario": 190,
            "valid_control": 130,
            "valid_intervention": 150,
            "valid_total": 110,
            "invited_total": 110,
        }
        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(
                column,
                width=widths[column],
                minwidth=90,
                anchor=tk.E if column != "scenario" else tk.W,
                stretch=column == "scenario",
            )
        yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        return tree

    def _add_config_field(self, parent: ttk.Frame, field: str, row: int) -> int:
        label = ttk.Label(parent, text=t(self.language, f"field_{field}"))
        label.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Button(
            parent,
            text="?",
            width=3,
            command=lambda field=field: self._show_help(field),
        ).grid(row=row, column=1, sticky="w", padx=(0, 8), pady=4)

        widget = self._create_input(parent, field)
        widget.grid(row=row, column=2, sticky="ew", pady=4)
        return row + 1

    def _create_input(self, parent: ttk.Frame, field: str) -> tk.Widget:
        kind = FIELD_TYPES[field]
        if kind == "bool":
            var = tk.BooleanVar()
            self.vars[field] = var
            return ttk.Checkbutton(parent, variable=var)
        if kind == "multiline":
            text = tk.Text(parent, height=4, wrap=tk.WORD)
            self.text_widgets[field] = text
            return text
        var = tk.StringVar()
        self.vars[field] = var
        if kind == "language":
            return ttk.Combobox(parent, textvariable=var, values=["en", "pt"], state="readonly")
        if kind == "outcome":
            values = [t(self.language, "outcome_continuous"), t(self.language, "outcome_binary")]
            return ttk.Combobox(parent, textvariable=var, values=values, state="readonly")
        if kind == "alternative":
            values = [
                t(self.language, "alternative_two_sided"),
                t(self.language, "alternative_greater"),
                t(self.language, "alternative_less"),
            ]
            return ttk.Combobox(parent, textvariable=var, values=values, state="readonly")
        return ttk.Entry(parent, textvariable=var)

    def _show_help(self, field: str) -> None:
        messagebox.showinfo(
            t(self.language, f"field_{field}"),
            t(self.language, f"help_{field}"),
            parent=self,
        )

    def _visible_wizard_fields(self) -> list[str]:
        outcome = self._current_outcome_type()
        visible: list[str] = []
        for field in WIZARD_FIELDS:
            if field == "effect_size_d" and outcome != "continuous":
                continue
            if field in {"proportion_control", "proportion_intervention"} and outcome != "binary":
                continue
            visible.append(field)
        return visible

    def _current_outcome_type(self) -> str:
        var = self.vars.get("outcome_type")
        if not var:
            return self.config_model.outcome_type
        value = str(var.get())
        if value == t(self.language, "outcome_binary"):
            return "binary"
        if value == t(self.language, "outcome_continuous"):
            return "continuous"
        return self.config_model.outcome_type

    def _render_wizard_step(self) -> None:
        for child in self.wizard_input.winfo_children():
            child.destroy()
        fields = self._visible_wizard_fields()
        self.wizard_index = min(self.wizard_index, len(fields) - 1)
        field = fields[self.wizard_index]
        key = WIZARD_KEY_OVERRIDES.get(field, field)
        self.wizard_progress.configure(text=f"{self.wizard_index + 1} / {len(fields)}")
        self.wizard_question.configure(text=t(self.language, f"wizard_question_{key}"))
        self.wizard_why.configure(text=t(self.language, f"wizard_why_{key}"))

        ttk.Label(self.wizard_input, text=t(self.language, f"field_{field}")).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        ttk.Button(
            self.wizard_input,
            text="?",
            width=3,
            command=lambda field=field: self._show_help(field),
        ).grid(row=0, column=1, padx=(0, 8))
        widget = self._create_wizard_input(self.wizard_input, field)
        widget.grid(row=0, column=2, sticky="ew")
        self.wizard_input.columnconfigure(2, weight=1)

        self.prev_button.configure(state=tk.NORMAL if self.wizard_index > 0 else tk.DISABLED)
        self.next_button.configure(
            text=t(self.language, "finish") if self.wizard_index == len(fields) - 1 else t(self.language, "next")
        )

    def _create_wizard_input(self, parent: ttk.Frame, field: str) -> tk.Widget:
        if field not in self.vars and FIELD_TYPES[field] != "multiline":
            self.vars[field] = tk.StringVar()
        kind = FIELD_TYPES[field]
        if kind == "outcome":
            values = [t(self.language, "outcome_continuous"), t(self.language, "outcome_binary")]
            return ttk.Combobox(parent, textvariable=self.vars[field], values=values, state="readonly")
        if kind == "alternative":
            values = [
                t(self.language, "alternative_two_sided"),
                t(self.language, "alternative_greater"),
                t(self.language, "alternative_less"),
            ]
            return ttk.Combobox(parent, textvariable=self.vars[field], values=values, state="readonly")
        if kind == "bool":
            if field not in self.vars:
                self.vars[field] = tk.BooleanVar()
            return ttk.Checkbutton(parent, variable=self.vars[field])
        return ttk.Entry(parent, textvariable=self.vars[field])

    def _wizard_next(self) -> None:
        try:
            self._sync_config_from_vars()
        except PlanningError as exc:
            messagebox.showerror(t(self.language, "error"), str(exc), parent=self)
            return
        fields = self._visible_wizard_fields()
        if self.wizard_index == len(fields) - 1:
            self.calculate()
            self.notebook.select(self.results_tab)
            return
        self.wizard_index += 1
        self._render_wizard_step()

    def _wizard_previous(self) -> None:
        self.wizard_index = max(0, self.wizard_index - 1)
        self._render_wizard_step()

    def _reset_wizard(self) -> None:
        self.wizard_index = 0
        self.config_model = StudyConfig(language=self.language)
        self._sync_config_to_vars()
        self._render_wizard_step()

    def _sync_config_to_vars(self) -> None:
        for field in FIELD_TYPES:
            value = getattr(self.config_model, field)
            if field == "notes" and field in self.text_widgets:
                self.text_widgets[field].delete("1.0", tk.END)
                self.text_widgets[field].insert("1.0", value or "")
            elif field == "outcome_type" and field in self.vars:
                self.vars[field].set(self._display_outcome(value))
            elif field == "alternative" and field in self.vars:
                self.vars[field].set(self._display_alternative(value))
            elif field in self.vars:
                self.vars[field].set("" if value is None else str(value))
        if hasattr(self, "language_var"):
            self.language_var.set(self.config_model.language)

    def _sync_config_from_vars(self) -> None:
        data = config_to_dict(self.config_model)
        for field, kind in FIELD_TYPES.items():
            if kind == "multiline":
                widget = self.text_widgets.get(field)
                data[field] = widget.get("1.0", tk.END).strip() if widget else data.get(field, "")
                continue
            if field not in self.vars:
                continue
            raw = self.vars[field].get()
            if kind == "bool":
                data[field] = bool(raw)
            elif kind == "int":
                data[field] = self._parse_int(raw, field)
            elif kind == "optional_int":
                data[field] = self._parse_optional_int(raw, field)
            elif kind in {"float", "optional_float", "rate"}:
                optional = kind == "optional_float"
                data[field] = self._parse_number(raw, field, optional=optional, rate=kind == "rate")
            elif kind == "outcome":
                data[field] = self._internal_outcome(str(raw))
            elif kind == "alternative":
                data[field] = self._internal_alternative(str(raw))
            else:
                data[field] = str(raw)
        self.config_model = StudyConfig(**data)

    def _parse_number(self, raw: Any, field: str, optional: bool = False, rate: bool = False) -> float | None:
        text = str(raw).strip().replace(",", ".")
        if not text:
            if optional:
                return None
            raise PlanningError(f"{t(self.language, f'field_{field}')} is required.")
        percent = text.endswith("%")
        if percent:
            text = text[:-1].strip()
        try:
            value = float(text)
        except ValueError as exc:
            raise PlanningError(f"{t(self.language, f'field_{field}')} must be numeric.") from exc
        if rate and (percent or value > 1):
            value = value / 100
        return value

    def _parse_int(self, raw: Any, field: str) -> int:
        value = self._parse_number(raw, field)
        assert value is not None
        return int(value)

    def _parse_optional_int(self, raw: Any, field: str) -> int | None:
        if not str(raw).strip():
            return None
        value = self._parse_number(raw, field)
        assert value is not None
        return int(value)

    def _display_outcome(self, value: str) -> str:
        return t(self.language, "outcome_binary") if value == "binary" else t(self.language, "outcome_continuous")

    def _internal_outcome(self, value: str) -> str:
        return "binary" if value == t(self.language, "outcome_binary") or value == "binary" else "continuous"

    def _display_alternative(self, value: str) -> str:
        if value == "greater":
            return t(self.language, "alternative_greater")
        if value == "less":
            return t(self.language, "alternative_less")
        return t(self.language, "alternative_two_sided")

    def _internal_alternative(self, value: str) -> str:
        if value == t(self.language, "alternative_greater") or value == "greater":
            return "greater"
        if value == t(self.language, "alternative_less") or value == "less":
            return "less"
        return "two_sided"

    def calculate(self) -> None:
        try:
            self._sync_config_from_vars()
            self.current_plan = calculate_plan(self.config_model)
        except PlanningError as exc:
            messagebox.showerror(t(self.language, "error"), str(exc), parent=self)
            return
        self._update_results()

    def _update_results(self) -> None:
        if not self.current_plan:
            return
        report = render_report(self.current_plan, self.language)
        self._replace_text(self.summary_text, report)
        for item in self.sensitivity_table.get_children():
            self.sensitivity_table.delete(item)
        for row in self.current_plan.sensitivity:
            self.sensitivity_table.insert(
                "",
                tk.END,
                values=(row.label, row.control, row.intervention, row.total, row.invited_total),
            )
        self._replace_text(self.json_text, json.dumps(asdict(self.current_plan), indent=2, ensure_ascii=False))

    def _replace_text(self, text: tk.Text, content: str) -> None:
        text.delete("1.0", tk.END)
        text.insert("1.0", content)

    def save_configuration(self) -> None:
        try:
            self._sync_config_from_vars()
        except PlanningError as exc:
            messagebox.showerror(t(self.language, "error"), str(exc), parent=self)
            return
        filename = filedialog.asksaveasfilename(
            parent=self,
            title=t(self.language, "choose_json"),
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not filename:
            return
        save_config(self.config_model, filename)
        messagebox.showinfo(t(self.language, "ready"), t(self.language, "config_saved"), parent=self)

    def load_configuration(self) -> None:
        filename = filedialog.askopenfilename(
            parent=self,
            title=t(self.language, "choose_json"),
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not filename:
            return
        try:
            self.config_model = load_config(filename)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            messagebox.showerror(t(self.language, "error"), str(exc), parent=self)
            return
        self._build_ui()
        messagebox.showinfo(t(self.language, "ready"), t(self.language, "config_loaded"), parent=self)

    def save_report(self) -> None:
        if not self.current_plan:
            self.calculate()
        if not self.current_plan:
            return
        filename = filedialog.asksaveasfilename(
            parent=self,
            title=t(self.language, "choose_report"),
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All files", "*.*")],
        )
        if not filename:
            return
        Path(filename).write_text(render_report(self.current_plan, self.language), encoding="utf-8")
        messagebox.showinfo(t(self.language, "ready"), t(self.language, "report_saved"), parent=self)


def main() -> None:
    app = PlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
