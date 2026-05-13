"""Tkinter interface for Intervention Sample Planner."""

# File version: 2.1; date: 2026-05-12

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
    config_from_dict,
    config_to_dict,
    load_config,
    render_report,
    save_config,
    save_report_html,
    save_report_pdf,
)
from .content import get_design_content, get_field_content, get_general_content
from .i18n import t
from .version import APP_WINDOW_TITLE


FIELD_GROUPS = [
    ("design", ["workflow_path", "study_name", "study_design", "language"]),
    (
        "study_core",
        [
            "analysis_unit",
            "observation_unit",
            "outcome_type",
            "alternative",
            "alpha",
            "power",
            "primary_comparisons",
            "allocation_ratio",
            "pre_post_correlation",
        ],
    ),
    (
        "effect_inputs",
        [
            "effect_size_d",
            "mean_control",
            "mean_intervention",
            "sd_pooled",
            "proportion_control",
            "proportion_intervention",
        ],
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
    (
        "inverse_inputs",
        [
            "planned_control_n",
            "planned_intervention_n",
            "planned_total_n",
            "planned_effect_size",
            "planned_alpha",
            "planned_power",
            "observed_control_n",
            "observed_intervention_n",
            "observed_total_n",
            "observed_control_events",
            "observed_intervention_events",
            "observed_pre_success_post_failure",
            "observed_pre_failure_post_success",
            "observed_effect_size",
        ],
    ),
    ("labels_notes", ["intervention_label", "control_label", "notes"]),
]

FIELD_TYPES = {
    "study_name": "text",
    "workflow_path": "workflow",
    "study_design": "design",
    "analysis_mode": "mode",
    "language": "language",
    "analysis_unit": "text",
    "observation_unit": "text",
    "outcome_type": "outcome",
    "alternative": "alternative",
    "alpha": "rate",
    "power": "rate",
    "primary_comparisons": "int",
    "allocation_ratio": "float",
    "pre_post_correlation": "rate",
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
    "observed_control_n": "optional_int",
    "observed_intervention_n": "optional_int",
    "observed_total_n": "optional_int",
    "observed_control_events": "optional_int",
    "observed_intervention_events": "optional_int",
    "observed_pre_success_post_failure": "optional_int",
    "observed_pre_failure_post_success": "optional_int",
    "observed_effect_size": "optional_float",
    "planned_control_n": "optional_int",
    "planned_intervention_n": "optional_int",
    "planned_total_n": "optional_int",
    "planned_effect_size": "optional_float",
    "planned_alpha": "optional_rate",
    "planned_power": "optional_rate",
    "intervention_label": "text",
    "control_label": "text",
    "notes": "multiline",
}

class PlannerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.config_model = StudyConfig()
        self.vars: dict[str, tk.Variable] = {}
        self.range_override_vars: dict[str, tk.BooleanVar] = {}
        self.text_widgets: dict[str, tk.Text] = {}
        self.current_plan = None
        self.range_issues: list[str] = []
        self.wizard_index = 0
        self.title(APP_WINDOW_TITLE)
        self.geometry("1220x820")
        self.minsize(980, 680)
        self._build_ui()

    @property
    def language(self) -> str:
        return self.config_model.language

    def _build_ui(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        self.vars = {}
        self.range_override_vars = {}
        self.text_widgets = {}

        shell = ttk.Frame(self, padding=10)
        shell.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(shell)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=APP_WINDOW_TITLE, font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value=self.language)
        ttk.Label(header, text=t(self.language, "language")).pack(side=tk.RIGHT, padx=(8, 0))
        combo = ttk.Combobox(
            header,
            textvariable=self.language_var,
            values=["en", "pt"],
            width=6,
            state="readonly",
        )
        combo.pack(side=tk.RIGHT)
        combo.bind("<<ComboboxSelected>>", self._on_language_change)

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
        ttk.Label(
            self.wizard_tab,
            text=t(self.language, "wizard_intro"),
            wraplength=980,
        ).pack(anchor=tk.W, pady=(0, 12))

        self.wizard_card = ttk.Frame(self.wizard_tab, padding=12, relief=tk.GROOVE)
        self.wizard_card.pack(fill=tk.BOTH, expand=True)

        self.wizard_progress = ttk.Label(self.wizard_card, text="")
        self.wizard_progress.pack(anchor=tk.W)
        self.wizard_question = ttk.Label(
            self.wizard_card,
            text="",
            wraplength=920,
            font=("Segoe UI", 14, "bold"),
        )
        self.wizard_question.pack(anchor=tk.W, pady=(12, 4))
        self.wizard_why = ttk.Label(self.wizard_card, text="", wraplength=920, justify=tk.LEFT)
        self.wizard_why.pack(anchor=tk.W, pady=(0, 14))
        self.wizard_input = ttk.Frame(self.wizard_card)
        self.wizard_input.pack(fill=tk.X, pady=(0, 16))

        buttons = ttk.Frame(self.wizard_card)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text=t(self.language, "reset"), command=self._reset_wizard).pack(side=tk.LEFT)
        ttk.Button(buttons, text=t(self.language, "load_previous_plan"), command=self.load_previous_plan).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        self.prev_button = ttk.Button(buttons, text=t(self.language, "previous"), command=self._wizard_previous)
        self.prev_button.pack(side=tk.RIGHT, padx=(8, 0))
        self.next_button = ttk.Button(buttons, text=t(self.language, "next"), command=self._wizard_next)
        self.next_button.pack(side=tk.RIGHT)

        self._render_wizard_step()

    def _build_data_tab(self) -> None:
        top = ttk.Frame(self.data_tab)
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(top, text=t(self.language, "direct_mode_hint")).pack(side=tk.LEFT)
        ttk.Button(top, text=t(self.language, "calculate"), command=self.calculate).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(top, text=t(self.language, "load_config"), command=self.load_configuration).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(top, text=t(self.language, "load_previous_plan"), command=self.load_previous_plan).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(top, text=t(self.language, "save_config"), command=self.save_configuration).pack(side=tk.RIGHT)

        canvas = tk.Canvas(self.data_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.data_tab, orient=tk.VERTICAL, command=canvas.yview)
        self.data_inner = ttk.Frame(canvas)
        self.data_inner.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=self.data_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0
        for group_key, fields in FIELD_GROUPS:
            ttk.Label(
                self.data_inner,
                text=t(self.language, group_key),
                font=("Segoe UI", 11, "bold"),
            ).grid(row=row, column=0, columnspan=5, sticky="w", pady=(12, 4))
            row += 1
            for field in fields:
                if not self._show_field(field):
                    continue
                row = self._add_config_field(self.data_inner, field, row)

        self.data_inner.columnconfigure(2, weight=1)
        self.data_inner.columnconfigure(3, weight=1)

    def _build_results_tab(self) -> None:
        top = ttk.Frame(self.results_tab)
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(top, text=t(self.language, "calculate"), command=self.calculate).pack(side=tk.RIGHT)
        ttk.Button(top, text=t(self.language, "save_report"), command=self.save_report).pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(top, text=t(self.language, "save_pdf"), command=self.save_report_as_pdf).pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(top, text=t(self.language, "save_html"), command=self.save_report_as_html).pack(side=tk.RIGHT, padx=(0, 8))

        self.results_notebook = ttk.Notebook(self.results_tab)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)

        summary_frame = ttk.Frame(self.results_notebook, padding=6)
        sensitivity_frame = ttk.Frame(self.results_notebook, padding=6)
        evaluation_frame = ttk.Frame(self.results_notebook, padding=6)
        suggestions_frame = ttk.Frame(self.results_notebook, padding=6)
        json_frame = ttk.Frame(self.results_notebook, padding=6)
        self.results_notebook.add(summary_frame, text=t(self.language, "summary_tab"))
        self.results_notebook.add(sensitivity_frame, text=t(self.language, "sensitivity_tab"))
        self.results_notebook.add(evaluation_frame, text=t(self.language, "evaluation_tab"))
        self.results_notebook.add(suggestions_frame, text=t(self.language, "suggestions_tab"))
        self.results_notebook.add(json_frame, text=t(self.language, "json_tab"))

        self.summary_text = self._make_text(summary_frame)
        self.summary_text.insert("1.0", t(self.language, "no_results"))
        self.sensitivity_table = self._make_sensitivity_table(sensitivity_frame)
        self.evaluation_table = self._make_evaluation_table(evaluation_frame)
        self.suggestions_text = self._make_text(suggestions_frame)
        self.json_text = self._make_text(json_frame)

    def _make_text(self, parent: ttk.Frame) -> tk.Text:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        text = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return text

    def _make_sensitivity_table(self, parent: ttk.Frame) -> ttk.Treeview:
        columns = ("scenario", "valid_control", "valid_intervention", "valid_total", "invited_total")
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
            "scenario": 210,
            "valid_control": 120,
            "valid_intervention": 140,
            "valid_total": 110,
            "invited_total": 110,
        }
        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=widths[column], minwidth=90, anchor=tk.W if column == "scenario" else tk.E)
        yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        return tree

    def _make_evaluation_table(self, parent: ttk.Frame) -> ttk.Treeview:
        columns = ("category", "target", "required_control", "required_intervention", "required_total", "additional", "status")
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        headings = {
            "category": t(self.language, "eval_col_category"),
            "target": t(self.language, "eval_col_target"),
            "required_control": t(self.language, "eval_col_required_control"),
            "required_intervention": t(self.language, "eval_col_required_intervention"),
            "required_total": t(self.language, "eval_col_required_total"),
            "additional": t(self.language, "eval_col_additional"),
            "status": t(self.language, "eval_col_status"),
        }
        widths = {
            "category": 160,
            "target": 170,
            "required_control": 130,
            "required_intervention": 150,
            "required_total": 120,
            "additional": 120,
            "status": 120,
        }
        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=widths[column], minwidth=90, anchor=tk.W if column in {"category", "target", "status"} else tk.E)
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
        ttk.Label(parent, text=t(self.language, f"field_{field}")).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Button(parent, text="?", width=3, command=lambda field=field: self._show_help(field)).grid(
            row=row, column=1, sticky="w", padx=(0, 8), pady=4
        )
        widget = self._create_input(parent, field)
        widget.grid(row=row, column=2, sticky="ew", pady=4)
        range_label = ttk.Label(parent, text=self._range_text(field), wraplength=320, foreground="#555555")
        range_label.grid(row=row, column=3, sticky="w", padx=(12, 8), pady=4)
        if self._has_recommended_range(field):
            override = tk.BooleanVar(value=field in self.config_model.range_override_fields)
            self.range_override_vars[field] = override
            ttk.Checkbutton(parent, text=t(self.language, "range_override"), variable=override).grid(
                row=row, column=4, sticky="w", pady=4
            )
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
            widget = ttk.Combobox(parent, textvariable=var, values=["en", "pt"], state="readonly")
            widget.bind("<<ComboboxSelected>>", lambda _event, field=field: self._on_config_driver_change(field))
            return widget
        if kind == "workflow":
            widget = ttk.Combobox(parent, textvariable=var, values=self._workflow_values(), state="readonly")
            widget.bind("<<ComboboxSelected>>", lambda _event, field=field: self._on_config_driver_change(field))
            return widget
        if kind == "design":
            widget = ttk.Combobox(
                parent,
                textvariable=var,
                values=self._design_values(),
                state="readonly",
            )
            widget.bind("<<ComboboxSelected>>", lambda _event, field=field: self._on_config_driver_change(field))
            return widget
        if kind == "mode":
            return ttk.Combobox(parent, textvariable=var, values=self._mode_values(), state="readonly")
        if kind == "outcome":
            widget = ttk.Combobox(parent, textvariable=var, values=self._outcome_values(), state="readonly")
            widget.bind("<<ComboboxSelected>>", lambda _event, field=field: self._on_config_driver_change(field))
            return widget
        if kind == "alternative":
            return ttk.Combobox(parent, textvariable=var, values=self._alternative_values(), state="readonly")
        return ttk.Entry(parent, textvariable=var)

    def _on_config_driver_change(self, field: str) -> None:
        try:
            selected_index = self.notebook.index(self.notebook.select())
        except tk.TclError:
            selected_index = 1
        try:
            self._sync_config_from_vars()
        except PlanningError:
            self._sync_driver_field_only(field)
        self._build_ui()
        self.notebook.select(min(selected_index, self.notebook.index("end") - 1))

    def _sync_driver_field_only(self, field: str) -> None:
        data = config_to_dict(self.config_model)
        if field == "workflow_path":
            data["workflow_path"] = self._current_workflow_path()
            data["analysis_mode"] = "plan" if data["workflow_path"] == "plan_study" else "evaluate"
            data["had_planned_sample"] = data["workflow_path"] == "evaluate_against_plan"
        elif field == "study_design":
            data["study_design"] = self._current_study_design()
        elif field == "outcome_type":
            data["outcome_type"] = self._current_outcome_type()
        elif field == "language":
            var = self.vars.get("language")
            data["language"] = str(var.get()) if var else self.config_model.language
        self.config_model = StudyConfig(**data)

    def _show_help(self, field: str) -> None:
        content = get_field_content(self.language, field)
        body = content.get("help", "")
        if self._has_recommended_range(field):
            body = f"{body}\n\n{t(self.language, 'range_label')} {self._range_text(field)}"
        messagebox.showinfo(t(self.language, f"field_{field}"), body or field, parent=self)

    def _design_values(self) -> list[str]:
        return [
            t(self.language, "design_parallel_two_group"),
            t(self.language, "design_pretest_posttest_control"),
            t(self.language, "design_one_group_pre_post"),
        ]

    def _workflow_values(self) -> list[str]:
        return [
            t(self.language, "workflow_plan_study"),
            t(self.language, "workflow_evaluate_done"),
            t(self.language, "workflow_evaluate_against_plan"),
        ]

    def _mode_values(self) -> list[str]:
        return [t(self.language, "mode_plan"), t(self.language, "mode_evaluate")]

    def _outcome_values(self) -> list[str]:
        if self._current_study_design() == "pretest_posttest_control":
            return [t(self.language, "outcome_continuous")]
        if self._current_study_design() == "one_group_pre_post" and self._current_analysis_mode() == "plan":
            return [t(self.language, "outcome_continuous")]
        return [t(self.language, "outcome_continuous"), t(self.language, "outcome_binary")]

    def _alternative_values(self) -> list[str]:
        return [
            t(self.language, "alternative_two_sided"),
            t(self.language, "alternative_greater"),
            t(self.language, "alternative_less"),
        ]

    def _show_field(self, field: str) -> bool:
        design = self._current_study_design()
        workflow = self._current_workflow_path()
        mode = self._current_analysis_mode()
        outcome = self._current_outcome_type()
        has_plan = workflow == "evaluate_against_plan"
        if field == "allocation_ratio":
            return design != "one_group_pre_post"
        if field == "pre_post_correlation":
            return design == "pretest_posttest_control"
        if field in {"mean_control", "mean_intervention", "sd_pooled"}:
            return mode == "plan" and outcome == "continuous" and design != "one_group_pre_post"
        if field == "effect_size_d":
            return mode == "plan" and not (design == "parallel_two_group" and outcome == "binary")
        if field in {"proportion_control", "proportion_intervention"}:
            return mode == "plan" and design == "parallel_two_group" and outcome == "binary"
        if field in {"observed_control_n", "observed_intervention_n"}:
            return mode == "evaluate" and design != "one_group_pre_post"
        if field == "observed_total_n":
            return mode == "evaluate" and design == "one_group_pre_post"
        if field in {"observed_control_events", "observed_intervention_events"}:
            return mode == "evaluate" and design == "parallel_two_group" and outcome == "binary"
        if field in {"observed_pre_success_post_failure", "observed_pre_failure_post_success"}:
            return mode == "evaluate" and design == "one_group_pre_post" and outcome == "binary"
        if field == "observed_effect_size":
            return mode == "evaluate" and outcome == "continuous"
        if field in {"planned_control_n", "planned_intervention_n"}:
            return has_plan and design != "one_group_pre_post"
        if field == "planned_total_n":
            return has_plan and design == "one_group_pre_post"
        if field in {"planned_effect_size", "planned_alpha", "planned_power"}:
            return has_plan
        if field == "control_label":
            return design != "one_group_pre_post"
        return True

    def _visible_wizard_fields(self) -> list[str]:
        fields = [
            "workflow_path",
            "study_name",
            "study_design",
            "outcome_type",
            "alpha",
            "power",
        ]
        design = self._current_study_design()
        mode = self._current_analysis_mode()
        outcome = self._current_outcome_type()
        has_plan = self._current_workflow_path() == "evaluate_against_plan"
        if mode == "plan":
            if design == "parallel_two_group":
                fields.append("allocation_ratio")
                if outcome == "binary":
                    fields.extend(["proportion_control", "proportion_intervention"])
                else:
                    fields.append("effect_size_d")
            elif design == "pretest_posttest_control":
                fields.extend(["allocation_ratio", "effect_size_d", "pre_post_correlation"])
            else:
                fields.append("effect_size_d")
            fields.extend(
                [
                    "response_rate",
                    "completion_rate",
                    "usable_data_rate",
                    "primary_comparisons",
                    "cluster_average_size",
                    "intraclass_correlation",
                ]
            )
        else:
            if has_plan:
                if design == "one_group_pre_post":
                    fields.append("planned_total_n")
                else:
                    fields.extend(["planned_control_n", "planned_intervention_n"])
                fields.extend(["planned_effect_size", "planned_alpha", "planned_power"])
            if design == "one_group_pre_post":
                fields.append("observed_total_n")
                if outcome == "binary":
                    fields.extend(["observed_pre_success_post_failure", "observed_pre_failure_post_success"])
                else:
                    fields.append("observed_effect_size")
            else:
                if design == "parallel_two_group":
                    fields.append("allocation_ratio")
                if design == "pretest_posttest_control":
                    fields.append("pre_post_correlation")
                fields.extend(["observed_control_n", "observed_intervention_n"])
                if design == "parallel_two_group" and outcome == "binary":
                    fields.extend(["observed_control_events", "observed_intervention_events"])
                else:
                    fields.append("observed_effect_size")
        return fields

    def _current_study_design(self) -> str:
        var = self.vars.get("study_design")
        if not var:
            return self.config_model.study_design
        text = str(var.get())
        mapping = {
            t(self.language, "design_parallel_two_group"): "parallel_two_group",
            t(self.language, "design_pretest_posttest_control"): "pretest_posttest_control",
            t(self.language, "design_one_group_pre_post"): "one_group_pre_post",
            "parallel_two_group": "parallel_two_group",
            "pretest_posttest_control": "pretest_posttest_control",
            "one_group_pre_post": "one_group_pre_post",
        }
        return mapping.get(text, self.config_model.study_design)

    def _current_workflow_path(self) -> str:
        var = self.vars.get("workflow_path")
        if not var:
            return self.config_model.workflow_path
        text = str(var.get())
        mapping = {
            t(self.language, "workflow_plan_study"): "plan_study",
            t(self.language, "workflow_evaluate_done"): "evaluate_done",
            t(self.language, "workflow_evaluate_against_plan"): "evaluate_against_plan",
            "plan_study": "plan_study",
            "evaluate_done": "evaluate_done",
            "evaluate_against_plan": "evaluate_against_plan",
        }
        return mapping.get(text, self.config_model.workflow_path)

    def _current_analysis_mode(self) -> str:
        workflow = self._current_workflow_path()
        if workflow == "plan_study":
            return "plan"
        if workflow in {"evaluate_done", "evaluate_against_plan"}:
            return "evaluate"
        var = self.vars.get("analysis_mode")
        if not var:
            return self.config_model.analysis_mode
        text = str(var.get())
        mapping = {
            t(self.language, "mode_plan"): "plan",
            t(self.language, "mode_evaluate"): "evaluate",
            "plan": "plan",
            "evaluate": "evaluate",
        }
        return mapping.get(text, self.config_model.analysis_mode)

    def _current_outcome_type(self) -> str:
        var = self.vars.get("outcome_type")
        if not var:
            return self.config_model.outcome_type
        text = str(var.get())
        if text in {t(self.language, "outcome_binary"), "binary"}:
            return "binary"
        return "continuous"

    def _render_wizard_step(self) -> None:
        for child in self.wizard_input.winfo_children():
            child.destroy()
        fields = self._visible_wizard_fields()
        self.wizard_index = min(self.wizard_index, len(fields) - 1)
        field = fields[self.wizard_index]
        self.wizard_progress.configure(text=f"{self.wizard_index + 1} / {len(fields)}")
        self.wizard_question.configure(text=self._wizard_question(field))
        self.wizard_why.configure(text=self._wizard_why(field))

        ttk.Label(self.wizard_input, text=t(self.language, f"field_{field}")).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        ttk.Button(self.wizard_input, text="?", width=3, command=lambda field=field: self._show_help(field)).grid(
            row=0, column=1, padx=(0, 8)
        )
        widget = self._create_wizard_input(self.wizard_input, field)
        widget.grid(row=0, column=2, sticky="ew")
        ttk.Label(
            self.wizard_input,
            text=self._range_text(field),
            wraplength=300,
            foreground="#555555",
        ).grid(row=1, column=2, sticky="w", pady=(6, 0))
        if self._has_recommended_range(field):
            override = self.range_override_vars.setdefault(
                field, tk.BooleanVar(value=field in self.config_model.range_override_fields)
            )
            ttk.Checkbutton(
                self.wizard_input,
                text=t(self.language, "range_override"),
                variable=override,
            ).grid(row=2, column=2, sticky="w", pady=(6, 0))
        self.wizard_input.columnconfigure(2, weight=1)
        self.prev_button.configure(state=tk.NORMAL if self.wizard_index > 0 else tk.DISABLED)
        self.next_button.configure(
            text=t(self.language, "finish") if self.wizard_index == len(fields) - 1 else t(self.language, "next")
        )

    def _create_wizard_input(self, parent: ttk.Frame, field: str) -> tk.Widget:
        kind = FIELD_TYPES[field]
        if kind == "bool":
            if field not in self.vars:
                self.vars[field] = tk.BooleanVar()
            return ttk.Checkbutton(parent, variable=self.vars[field])
        if field not in self.vars:
            self.vars[field] = tk.StringVar()
        if kind == "design":
            return ttk.Combobox(parent, textvariable=self.vars[field], values=self._design_values(), state="readonly")
        if kind == "workflow":
            return ttk.Combobox(parent, textvariable=self.vars[field], values=self._workflow_values(), state="readonly")
        if kind == "mode":
            return ttk.Combobox(parent, textvariable=self.vars[field], values=self._mode_values(), state="readonly")
        if kind == "outcome":
            return ttk.Combobox(parent, textvariable=self.vars[field], values=self._outcome_values(), state="readonly")
        if kind == "alternative":
            return ttk.Combobox(parent, textvariable=self.vars[field], values=self._alternative_values(), state="readonly")
        return ttk.Entry(parent, textvariable=self.vars[field])

    def _wizard_question(self, field: str) -> str:
        if field == "study_design":
            content = get_design_content(self.language, "parallel_two_group")
            return str(content.get("wizard_question", t(self.language, "field_study_design")))
        return t(self.language, f"wizard_question_{field}")

    def _wizard_why(self, field: str) -> str:
        if field == "study_design":
            content = get_design_content(self.language, "parallel_two_group")
            return str(content.get("wizard_why", t(self.language, "wizard_why_default")))
        content = get_field_content(self.language, field)
        return str(content.get("help", t(self.language, "wizard_why_default")))

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
        self._build_ui()
        self.wizard_index = min(self.wizard_index, len(self._visible_wizard_fields()) - 1)
        self._render_wizard_step()

    def _wizard_previous(self) -> None:
        self.wizard_index = max(0, self.wizard_index - 1)
        self._render_wizard_step()

    def _reset_wizard(self) -> None:
        self.wizard_index = 0
        self.config_model = StudyConfig(language=self.language)
        self._build_ui()

    def _sync_config_to_vars(self) -> None:
        for field in FIELD_TYPES:
            value = getattr(self.config_model, field)
            if field == "notes" and field in self.text_widgets:
                self.text_widgets[field].delete("1.0", tk.END)
                self.text_widgets[field].insert("1.0", value or "")
            elif field in self.vars:
                self.vars[field].set(self._display_value(field, value))
        if hasattr(self, "language_var"):
            self.language_var.set(self.config_model.language)

    def _display_value(self, field: str, value: Any) -> str:
        if value is None:
            return ""
        if field == "study_design":
            return {
                "parallel_two_group": t(self.language, "design_parallel_two_group"),
                "pretest_posttest_control": t(self.language, "design_pretest_posttest_control"),
                "one_group_pre_post": t(self.language, "design_one_group_pre_post"),
            }[str(value)]
        if field == "analysis_mode":
            return {"plan": t(self.language, "mode_plan"), "evaluate": t(self.language, "mode_evaluate")}[str(value)]
        if field == "workflow_path":
            return {
                "plan_study": t(self.language, "workflow_plan_study"),
                "evaluate_done": t(self.language, "workflow_evaluate_done"),
                "evaluate_against_plan": t(self.language, "workflow_evaluate_against_plan"),
            }[str(value)]
        if field == "outcome_type":
            return t(self.language, "outcome_binary") if value == "binary" else t(self.language, "outcome_continuous")
        if field == "alternative":
            return {
                "two_sided": t(self.language, "alternative_two_sided"),
                "greater": t(self.language, "alternative_greater"),
                "less": t(self.language, "alternative_less"),
            }[str(value)]
        return str(value)

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
            elif kind in {"float", "optional_float", "rate", "optional_rate"}:
                optional = kind == "optional_float"
                data[field] = self._parse_number(
                    raw,
                    field,
                    optional=optional or kind == "optional_rate",
                    rate=kind in {"rate", "optional_rate"},
                )
            elif kind == "workflow":
                data[field] = self._current_workflow_path()
            elif kind == "design":
                data[field] = self._current_study_design()
            elif kind == "mode":
                data[field] = self._current_analysis_mode()
            elif kind == "outcome":
                data[field] = self._current_outcome_type()
            elif kind == "alternative":
                data[field] = self._internal_alternative(str(raw))
            else:
                data[field] = str(raw)
        workflow = data.get("workflow_path", "plan_study")
        data["analysis_mode"] = "plan" if workflow == "plan_study" else "evaluate"
        data["had_planned_sample"] = workflow == "evaluate_against_plan"
        data["range_override_fields"] = [field for field, var in self.range_override_vars.items() if bool(var.get())]
        candidate = StudyConfig(**data)
        self.range_issues = self._validate_recommended_ranges(candidate)
        self.config_model = candidate

    def _validate_recommended_ranges(self, config: StudyConfig) -> list[str]:
        issues: list[str] = []
        for field in FIELD_TYPES:
            content = get_field_content(config.language, field)
            rec = content.get("recommended")
            if not rec:
                continue
            value = getattr(config, field, None)
            if value is None or isinstance(value, bool) or isinstance(value, str):
                continue
            minimum = rec.get("min")
            maximum = rec.get("max")
            out_of_range = (minimum is not None and value < minimum) or (maximum is not None and value > maximum)
            if not out_of_range:
                continue
            message = (
                f"{t(config.language, f'field_{field}')} = {value} is outside the recommended range "
                f"[{minimum}, {maximum}]. {rec.get('justification', '')}"
            )
            if field in config.range_override_fields:
                issues.append(message)
            else:
                raise PlanningError(message)
        return issues

    def _has_recommended_range(self, field: str) -> bool:
        return bool(get_field_content(self.language, field).get("recommended"))

    def _range_text(self, field: str) -> str:
        content = get_field_content(self.language, field)
        rec = content.get("recommended")
        if not rec:
            return ""
        minimum = rec.get("min")
        maximum = rec.get("max")
        typical = ", ".join(rec.get("typical", []))
        pieces = [f"[{minimum}, {maximum}]"]
        if typical:
            pieces.append(f"typical: {typical}")
        justification = rec.get("justification", "")
        if justification:
            pieces.append(justification)
        return " ".join(str(piece) for piece in pieces if piece)

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

    def _internal_alternative(self, value: str) -> str:
        if value in {t(self.language, "alternative_greater"), "greater"}:
            return "greater"
        if value in {t(self.language, "alternative_less"), "less"}:
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
        self._replace_text(self.summary_text, render_report(self.current_plan, self.language))
        for item in self.sensitivity_table.get_children():
            self.sensitivity_table.delete(item)
        for row in self.current_plan.sensitivity:
            self.sensitivity_table.insert(
                "",
                tk.END,
                values=(row.label, row.control, row.intervention, row.total, row.invited_total),
            )
        for item in self.evaluation_table.get_children():
            self.evaluation_table.delete(item)
        if self.current_plan.observed_analysis:
            obs = self.current_plan.observed_analysis
            for category, targets in (
                (t(self.language, "eval_category_plan"), obs.planned_targets),
                (t(self.language, "eval_category_benchmark"), obs.benchmark_targets),
            ):
                for target in targets:
                    self.evaluation_table.insert(
                        "",
                        tk.END,
                        values=(
                            category,
                            target.label,
                            target.required_control,
                            target.required_intervention,
                            target.required_total,
                            target.additional_total,
                            t(self.language, "eval_status_reached") if target.achieved else t(self.language, "eval_status_missing"),
                        ),
                    )
        suggestion_lines = list(self.current_plan.suggestions)
        if self.range_issues:
            suggestion_lines.append("")
            suggestion_lines.append(get_general_content(self.language, "suggestions_title", "Suggestions"))
            suggestion_lines.extend(self.range_issues)
        if self.current_plan.warnings:
            suggestion_lines.append("")
            suggestion_lines.extend(self.current_plan.warnings)
        self._replace_text(self.suggestions_text, "\n".join(suggestion_lines))
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

    def load_previous_plan(self) -> None:
        filename = filedialog.askopenfilename(
            parent=self,
            title=t(self.language, "choose_plan_json"),
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not filename:
            return
        try:
            raw = json.loads(Path(filename).read_text(encoding="utf-8"))
            source_data = raw.get("config", raw)
            source_config = config_from_dict(source_data)
            source_config.workflow_path = "plan_study"
            source_config.analysis_mode = "plan"
            source_config.had_planned_sample = False
            source_plan = calculate_plan(source_config)
            planned_sizes = raw.get("design_adjusted_valid") or {
                "control": source_plan.design_adjusted_valid.control,
                "intervention": source_plan.design_adjusted_valid.intervention,
            }
        except (OSError, json.JSONDecodeError, TypeError, ValueError, PlanningError) as exc:
            messagebox.showerror(t(self.language, "error"), str(exc), parent=self)
            return

        current = config_to_dict(self.config_model)
        current.update(
            {
                "workflow_path": "evaluate_against_plan",
                "analysis_mode": "evaluate",
                "had_planned_sample": True,
                "study_design": source_config.study_design,
                "outcome_type": source_config.outcome_type,
                "alternative": source_config.alternative,
                "alpha": source_config.alpha,
                "power": source_config.power,
                "primary_comparisons": source_config.primary_comparisons,
                "allocation_ratio": source_config.allocation_ratio,
                "pre_post_correlation": source_config.pre_post_correlation,
                "planned_effect_size": source_plan.effect_size_used,
                "planned_alpha": source_config.alpha,
                "planned_power": source_config.power,
                "intervention_label": source_config.intervention_label,
                "control_label": source_config.control_label,
            }
        )
        if source_config.study_design == "one_group_pre_post":
            current["planned_total_n"] = int(planned_sizes.get("intervention", source_plan.design_adjusted_valid.total))
            current["planned_control_n"] = None
            current["planned_intervention_n"] = None
        else:
            current["planned_control_n"] = int(planned_sizes.get("control", source_plan.design_adjusted_valid.control))
            current["planned_intervention_n"] = int(
                planned_sizes.get("intervention", source_plan.design_adjusted_valid.intervention)
            )
            current["planned_total_n"] = None
        self.config_model = config_from_dict(current)
        self._build_ui()
        messagebox.showinfo(t(self.language, "ready"), t(self.language, "previous_plan_loaded"), parent=self)

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

    def save_report_as_html(self) -> None:
        if not self.current_plan:
            self.calculate()
        if not self.current_plan:
            return
        filename = filedialog.asksaveasfilename(
            parent=self,
            title=t(self.language, "choose_html_report"),
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("All files", "*.*")],
        )
        if not filename:
            return
        save_report_html(self.current_plan, filename, self.language)
        messagebox.showinfo(t(self.language, "ready"), t(self.language, "report_saved"), parent=self)

    def save_report_as_pdf(self) -> None:
        if not self.current_plan:
            self.calculate()
        if not self.current_plan:
            return
        filename = filedialog.asksaveasfilename(
            parent=self,
            title=t(self.language, "choose_pdf_report"),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
        )
        if not filename:
            return
        save_report_pdf(self.current_plan, filename, self.language)
        messagebox.showinfo(t(self.language, "ready"), t(self.language, "report_saved"), parent=self)


def main() -> None:
    app = PlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
