from __future__ import annotations

import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from zeta_experiments import (
    perform_critical_line_scan,
    perform_random_strip_search,
    perform_zeta_spacing_experiment,
)


class ZetaExplorer(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Zeta Explorer")
        self.geometry("1100x760")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_interface()
        self._figure_canvas: FigureCanvasTkAgg | None = None

    def _build_interface(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        spacing_frame = ttk.Frame(notebook)
        scan_frame = ttk.Frame(notebook)
        strip_frame = ttk.Frame(notebook)
        notebook.add(spacing_frame, text="Spacing Statistics")
        notebook.add(scan_frame, text="Critical Line Scan")
        notebook.add(strip_frame, text="Strip Random Search")

        self._build_spacing_tab(spacing_frame)
        self._build_scan_tab(scan_frame)
        self._build_strip_search_tab(strip_frame)

        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        bottom.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(bottom, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _build_spacing_tab(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent)
        form.grid(row=0, column=0, sticky="nw", padx=12, pady=12)

        self.count_var = tk.IntVar(value=500)
        self.start_var = tk.IntVar(value=1)
        self.gue_size_var = tk.IntVar(value=500)
        self.refresh_var = tk.BooleanVar(value=False)

        self._create_form_row(form, 0, "Zeta zeros count:", self.count_var)
        self._create_form_row(form, 1, "Zero start index:", self.start_var)
        self._create_form_row(form, 2, "GUE matrix size:", self.gue_size_var)
        ttk.Checkbutton(form, text="Refresh cached zeros", variable=self.refresh_var).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(8, 8)
        )

        ttk.Button(form, text="Run spacing experiment", command=self.run_spacing).grid(
            row=4, column=0, columnspan=2, pady=(8, 0), sticky="ew"
        )

        self.spacing_summary = ScrolledText(parent, wrap="word", height=10)
        self.spacing_summary.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

    def _build_scan_tab(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent)
        form.grid(row=0, column=0, sticky="nw", padx=12, pady=12)

        self.t_min_var = tk.DoubleVar(value=10.0)
        self.t_max_var = tk.DoubleVar(value=40.0)
        self.points_var = tk.IntVar(value=900)
        self.zero_count_var = tk.IntVar(value=8)

        self._create_form_row(form, 0, "t-min:", self.t_min_var)
        self._create_form_row(form, 1, "t-max:", self.t_max_var)
        self._create_form_row(form, 2, "Points:", self.points_var)
        self._create_form_row(form, 3, "Zero count:", self.zero_count_var)

        ttk.Button(form, text="Run critical line scan", command=self.run_scan).grid(
            row=4, column=0, columnspan=2, pady=(8, 0), sticky="ew"
        )

        self.scan_summary = ScrolledText(parent, wrap="word", height=10)
        self.scan_summary.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

    def _build_strip_search_tab(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent)
        form.grid(row=0, column=0, sticky="nw", padx=12, pady=12)

        self.sigma_min_var = tk.DoubleVar(value=0.01)
        self.sigma_max_var = tk.DoubleVar(value=0.99)
        self.t_min_strip_var = tk.DoubleVar(value=10.0)
        self.t_max_strip_var = tk.DoubleVar(value=40.0)
        self.samples_var = tk.IntVar(value=2000)
        self.top_k_var = tk.IntVar(value=10)
        self.seed_var = tk.IntVar(value=7)
        self.precision_var = tk.IntVar(value=50)
        self.fix_sigma_var = tk.BooleanVar(value=False)
        self.fixed_sigma_val = tk.StringVar(value="pi/4")
        self.use_pi_over_sigma_var = tk.BooleanVar(value=False)
        self.pi_over_sigma_denom = tk.IntVar(value=4)
        self.fix_t_var = tk.BooleanVar(value=False)
        self.fixed_t_val = tk.StringVar(value="15.0")
        self.use_pi_over_t_var = tk.BooleanVar(value=False)
        self.pi_over_t_denom = tk.IntVar(value=4)

        self._create_form_row(form, 0, "sigma min:", self.sigma_min_var)
        self._create_form_row(form, 1, "sigma max:", self.sigma_max_var)
        self._create_form_row(form, 2, "t min:", self.t_min_strip_var)
        self._create_form_row(form, 3, "t max:", self.t_max_strip_var)
        self._create_form_row(form, 4, "samples:", self.samples_var)
        self._create_form_row(form, 5, "top k:", self.top_k_var)
        self._create_form_row(form, 6, "seed:", self.seed_var)
        self._create_form_row(form, 7, "precision:", self.precision_var)

        ttk.Checkbutton(form, text="Fix sigma", variable=self.fix_sigma_var).grid(
            row=8, column=0, sticky="w", pady=(6, 2)
        )
        ttk.Entry(form, textvariable=self.fixed_sigma_val, width=16).grid(
            row=8, column=1, sticky="w", padx=(8, 0), pady=(6, 2)
        )

        ttk.Checkbutton(form, text="Pi over sigma", variable=self.use_pi_over_sigma_var).grid(
            row=9, column=0, sticky="w", pady=(2, 2)
        )
        ttk.Entry(form, textvariable=self.pi_over_sigma_denom, width=8).grid(
            row=9, column=1, sticky="w", padx=(8, 0), pady=(2, 2)
        )
        ttk.Label(form, text="denominator").grid(row=9, column=2, sticky="w", padx=(4, 0), pady=(2, 2))

        ttk.Checkbutton(form, text="Fix t", variable=self.fix_t_var).grid(
            row=10, column=0, sticky="w", pady=(6, 2)
        )
        ttk.Entry(form, textvariable=self.fixed_t_val, width=16).grid(
            row=10, column=1, sticky="w", padx=(8, 0), pady=(6, 2)
        )

        ttk.Checkbutton(form, text="Pi over t", variable=self.use_pi_over_t_var).grid(
            row=11, column=0, sticky="w", pady=(2, 8)
        )
        ttk.Entry(form, textvariable=self.pi_over_t_denom, width=8).grid(
            row=11, column=1, sticky="w", padx=(8, 0), pady=(2, 8)
        )
        ttk.Label(form, text="denominator").grid(row=11, column=2, sticky="w", padx=(4, 0), pady=(2, 8))

        ttk.Button(form, text="Run strip random search", command=self.run_strip_search).grid(
            row=12, column=0, columnspan=3, pady=(8, 0), sticky="ew"
        )

        self.strip_summary = ScrolledText(parent, wrap="word", height=10)
        self.strip_summary.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

    def _create_form_row(self, parent: ttk.Frame, row: int, label_text: str, variable: tk.Variable) -> None:
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(parent, textvariable=variable, width=12)
        entry.grid(row=row, column=1, sticky="w", padx=(8, 0), pady=4)

    def set_status(self, message: str) -> None:
        self.status_label.config(text=message)

    def set_busy(self, busy: bool) -> None:
        if busy:
            self.progress.start(10)
        else:
            self.progress.stop()

    def run_spacing(self) -> None:
        try:
            params = {
                "count": int(self.count_var.get()),
                "start": int(self.start_var.get()),
                "gue_size": int(self.gue_size_var.get()),
                "refresh": bool(self.refresh_var.get()),
            }
        except tk.TclError:
            messagebox.showerror("Invalid input", "Please enter valid numeric values.")
            return

        threading.Thread(target=self._execute_spacing, args=(params,), daemon=True).start()

    def _execute_spacing(self, params: dict[str, object]) -> None:
        self.after(0, lambda: self._begin_task("Running spacing experiment..."))

        def progress_callback(text: str) -> None:
            self.after(0, lambda: self.set_status(text))

        try:
            result = perform_zeta_spacing_experiment(
                count=params["count"],
                start=params["start"],
                gue_size=params["gue_size"],
                refresh=params["refresh"],
                save=False,
                progress_callback=progress_callback,
            )
            self.after(0, lambda: self._finish_spacing(result))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))
            self.after(0, lambda: self._end_task("Ready"))

    def _finish_spacing(self, result: dict[str, object]) -> None:
        self._end_task("Spacing experiment complete.")
        self.spacing_summary.delete("1.0", "end")
        summary_text = (
            f"Zeta zeros file: {result['zeros_path']}\n"
            f"GUE sample size: {self.gue_size_var.get()}\n\n"
            f"Zeta summary:\n{result['zeta_summary']}\n\n"
            f"GUE summary:\n{result['gue_summary']}\n"
        )
        self.spacing_summary.insert("1.0", summary_text)
        self._show_figure(result["figure"])

    def run_scan(self) -> None:
        try:
            params = {
                "t_min": float(self.t_min_var.get()),
                "t_max": float(self.t_max_var.get()),
                "points": int(self.points_var.get()),
                "zero_count": int(self.zero_count_var.get()),
            }
        except tk.TclError:
            messagebox.showerror("Invalid input", "Please enter valid numeric values.")
            return

        threading.Thread(target=self._execute_scan, args=(params,), daemon=True).start()

    def _execute_scan(self, params: dict[str, object]) -> None:
        self.after(0, lambda: self._begin_task("Running critical line scan..."))

        def progress_callback(text: str) -> None:
            self.after(0, lambda: self.set_status(text))

        try:
            result = perform_critical_line_scan(
                t_min=params["t_min"],
                t_max=params["t_max"],
                points=params["points"],
                zero_count=params["zero_count"],
                save=False,
                progress_callback=progress_callback,
            )
            self.after(0, lambda: self._finish_scan(result))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))
            self.after(0, lambda: self._end_task("Ready"))

    def _finish_scan(self, result: dict[str, object]) -> None:
        self._end_task("Critical line scan complete.")
        self.scan_summary.delete("1.0", "end")
        summary_text = (
            f"Table file: {result['table_path']}\n"
            f"Found zeros in interval: {result['zeros']}\n"
            f"t range: {self.t_min_var.get()} to {self.t_max_var.get()}\n"
            f"Sample points: {self.points_var.get()}\n"
        )
        self.scan_summary.insert("1.0", summary_text)
        self._show_figure(result["figure"])

    def run_strip_search(self) -> None:
        try:
            fixed_sigma_value = None
            if self.use_pi_over_sigma_var.get():
                denom = int(self.pi_over_sigma_denom.get())
                if denom <= 0:
                    raise ValueError("Denominator must be positive.")
                fixed_sigma_value = f"pi/{denom}"
            elif self.fix_sigma_var.get():
                fixed_sigma_value = self.fixed_sigma_val.get()

            fixed_t_value = None
            if self.use_pi_over_t_var.get():
                denom = int(self.pi_over_t_denom.get())
                if denom <= 0:
                    raise ValueError("Denominator must be positive.")
                fixed_t_value = f"pi/{denom}"
            elif self.fix_t_var.get():
                fixed_t_value = self.fixed_t_val.get()

            params = {
                "sigma_min": float(self.sigma_min_var.get()),
                "sigma_max": float(self.sigma_max_var.get()),
                "t_min": float(self.t_min_strip_var.get()),
                "t_max": float(self.t_max_strip_var.get()),
                "samples": int(self.samples_var.get()),
                "top_k": int(self.top_k_var.get()),
                "seed": int(self.seed_var.get()),
                "precision": int(self.precision_var.get()),
                "fixed_sigma": fixed_sigma_value,
                "fixed_t": fixed_t_value,
            }
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid input", "Please enter valid numeric values and denominators.")
            return

        threading.Thread(target=self._execute_strip_search, args=(params,), daemon=True).start()

    def _execute_strip_search(self, params: dict[str, object]) -> None:
        self.after(0, lambda: self._begin_task("Running strip random search..."))

        def progress_callback(text: str) -> None:
            self.after(0, lambda: self.set_status(text))

        try:
            result = perform_random_strip_search(
                sigma_min=params["sigma_min"],
                sigma_max=params["sigma_max"],
                t_min=params["t_min"],
                t_max=params["t_max"],
                samples=params["samples"],
                top_k=params["top_k"],
                seed=params["seed"],
                precision=params["precision"],
                fixed_sigma=params.get("fixed_sigma"),
                fixed_t=params.get("fixed_t"),
                save=False,
                progress_callback=progress_callback,
            )
            self.after(0, lambda: self._finish_strip_search(result))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))
            self.after(0, lambda: self._end_task("Ready"))

    def _finish_strip_search(self, result: dict[str, object]) -> None:
        self._end_task("Strip random search complete.")
        self.strip_summary.delete("1.0", "end")
        summary_text = (
            f"Best candidates (lowest |zeta|):\n"
            + "\n".join(
                [
                    f"{idx+1}. sigma={candidate['sigma']:.6f}, t={candidate['t']:.6f}, |zeta|={candidate['abs']:.4e}"
                    for idx, candidate in enumerate(result["candidates"])
                ]
            )
        )
        self.strip_summary.insert("1.0", summary_text)
        self._show_figure(result["figure"])

    def _begin_task(self, message: str) -> None:
        self.set_status(message)
        self.set_busy(True)

    def _end_task(self, message: str) -> None:
        self.set_busy(False)
        self.set_status(message)

    def _show_figure(self, figure: Figure) -> None:
        if self._figure_canvas is not None:
            self._figure_canvas.get_tk_widget().destroy()

        self._figure_canvas = FigureCanvasTkAgg(figure, master=self)
        self._figure_canvas.draw()
        widget = self._figure_canvas.get_tk_widget()
        widget.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 8), pady=8)
        self.columnconfigure(1, weight=1)


def main() -> None:
    app = ZetaExplorer()
    app.mainloop()


if __name__ == "__main__":
    main()
