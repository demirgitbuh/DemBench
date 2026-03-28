"""DemBench GUI — Modern Material Design 3 interface using CustomTkinter."""

import customtkinter as ctk
import threading

from scoring import compute_total_score, compute_cpu_combined_score
from reporter import generate_report

# ── Material Design 3 Dark Theme ──────────────────────────────────────────────
ctk.set_appearance_mode("dark")

BG_BASE = "#0f0f17"
BG_SURFACE = "#1a1b2e"
BG_SURFACE2 = "#232440"
ACCENT = "#00D4AA"
ACCENT_DIM = "#007a63"
ACCENT_GLOW = "#00FFcc"
TEXT_ON = "#e8eaed"
TEXT_DIM = "#8b8fa3"
ERROR_RED = "#f2777a"
GOLD = "#FFD700"
CARD_RADIUS = 20
FONT = "Segoe UI"

LOGO_TEXT = (
    "  ____                  ____                  _\n"
    " |  _ \\  ___ _ __ ___ | __ )  ___ _ __   ___| |__\n"
    " | | | |/ _ \\ '_ ` _ \\|  _ \\ / _ \\ '_ \\ / __| '_ \\\n"
    " | |_| |  __/ | | | | | |_) |  __/ | | | (__| | | |\n"
    " |____/ \\___|_| |_| |_|____/ \\___|_| |_|\\___|_| |_|"
)


class BenchmarkCard(ctk.CTkFrame):
    """Material 3 elevated card for a single benchmark."""

    def __init__(self, parent, title: str, icon: str, weight_pct: int):
        super().__init__(parent, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS)

        # Top row
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(18, 6))

        ctk.CTkLabel(top, text=icon, font=(FONT, 24),
                     text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text=f"  {title}", font=(FONT, 17, "bold"),
                     text_color=TEXT_ON).pack(side="left")
        ctk.CTkLabel(top, text=f"{weight_pct}%", font=(FONT, 12),
                     text_color=TEXT_DIM).pack(side="right", padx=(0, 4))

        self.chip = ctk.CTkLabel(top, text="  WAITING  ",
                                 font=(FONT, 11, "bold"),
                                 text_color=BG_BASE, fg_color=TEXT_DIM,
                                 corner_radius=10)
        self.chip.pack(side="right", padx=(0, 10))

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, height=8, corner_radius=4,
                                           fg_color=BG_SURFACE2,
                                           progress_color=ACCENT)
        self.progress.pack(fill="x", padx=24, pady=(4, 6))
        self.progress.set(0)

        # Status
        self.status = ctk.CTkLabel(self, text="Waiting to start...",
                                   font=(FONT, 12), text_color=TEXT_DIM, anchor="w")
        self.status.pack(fill="x", padx=28, pady=(0, 2))

        # Result + Score side by side
        result_row = ctk.CTkFrame(self, fg_color="transparent")
        result_row.pack(fill="x", padx=24, pady=(0, 16))

        self.result = ctk.CTkLabel(result_row, text="",
                                   font=(FONT, 13, "bold"),
                                   text_color=ACCENT, anchor="w")
        self.result.pack(side="left", fill="x", expand=True)

        self.score_label = ctk.CTkLabel(result_row, text="",
                                        font=("Consolas", 18, "bold"),
                                        text_color=ACCENT, anchor="e")
        self.score_label.pack(side="right")

    def set_running(self):
        self.chip.configure(text="  RUNNING  ", fg_color=ACCENT, text_color=BG_BASE)

    def update_progress(self, pct: float, status: str):
        self.progress.set(min(pct, 1.0))
        self.status.configure(text=status)

    def set_done(self, result_text: str, score: int, skipped=False):
        if skipped:
            self.chip.configure(text="  SKIPPED  ", fg_color="#5c5c7a", text_color=TEXT_DIM)
            self.result.configure(text=result_text, text_color=TEXT_DIM)
            self.score_label.configure(text="—", text_color=TEXT_DIM)
        else:
            self.chip.configure(text="  DONE  ", fg_color=ACCENT, text_color=BG_BASE)
            self.result.configure(text=result_text, text_color=TEXT_ON)
            self.score_label.configure(text=f"{score:,}", text_color=ACCENT)
        self.progress.set(1.0)
        self.status.configure(text="Completed")

    def set_error(self, msg: str):
        self.chip.configure(text="  ERROR  ", fg_color=ERROR_RED, text_color=BG_BASE)
        self.result.configure(text=msg, text_color=ERROR_RED)
        self.score_label.configure(text="0", text_color=ERROR_RED)
        self.progress.set(1.0)


class SummaryCard(ctk.CTkFrame):
    """Final results summary with big total score display."""

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS,
                         border_width=2, border_color=ACCENT)

    def show(self, results: dict, total_score: int, report_path: str):
        for w in self.winfo_children():
            w.destroy()

        # ── Title ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="BENCHMARK COMPLETE",
                     font=(FONT, 22, "bold"), text_color=ACCENT).pack(pady=(24, 4))
        ctk.CTkLabel(self, text="All tests finished. Here are your results.",
                     font=(FONT, 13), text_color=TEXT_DIM).pack(pady=(0, 16))

        ctk.CTkFrame(self, fg_color=ACCENT_DIM, height=1).pack(fill="x", padx=40, pady=(0, 16))

        # ── Score rows ────────────────────────────────────────────────────────
        cpu = results.get("cpu", {})
        ram = results.get("ram", {})
        disk = results.get("disk", {})
        gpu = results.get("gpu", {})
        net = results.get("network", {})
        cpu_combined = compute_cpu_combined_score(cpu)

        rows = [
            ("\u2699  CPU", cpu_combined, "30%",
             f"Single: {cpu.get('single_core_score', 0):,}  |  Multi: {cpu.get('multi_core_score', 0):,}"),
            ("\U0001f9e0  RAM", ram.get("score", 0), "20%",
             f"R: {ram.get('read_mbps', 0):,.0f} MB/s  |  W: {ram.get('write_mbps', 0):,.0f} MB/s"),
            ("\U0001f4be  Disk", disk.get("score", 0), "20%",
             f"R: {disk.get('read_mbps', 0):,.0f} MB/s  |  W: {disk.get('write_mbps', 0):,.0f} MB/s"),
            ("\U0001f3ae  GPU", gpu.get("score", 0), "20%",
             "[skipped]" if gpu.get("skipped") else f"Frames: {gpu.get('frames', 0):,}"),
            ("\U0001f310  Network", net.get("score", 0), "10%",
             "[skipped]" if net.get("skipped") else
             f"DL: {net.get('download_mbps', 0):.1f}  |  UL: {net.get('upload_mbps', 0):.1f} Mbps  |  Ping: {net.get('ping_ms', 0):.0f} ms"),
        ]

        for label, score, weight, detail in rows:
            row = ctk.CTkFrame(self, fg_color=BG_SURFACE2, corner_radius=12)
            row.pack(fill="x", padx=30, pady=4)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=10)

            ctk.CTkLabel(inner, text=label, font=(FONT, 14, "bold"),
                         text_color=TEXT_ON, anchor="w", width=120).pack(side="left")
            ctk.CTkLabel(inner, text=weight, font=(FONT, 11),
                         text_color=TEXT_DIM, width=40).pack(side="left")
            ctk.CTkLabel(inner, text=detail, font=(FONT, 11),
                         text_color=TEXT_DIM, anchor="w").pack(side="left", fill="x", expand=True, padx=(8, 0))
            ctk.CTkLabel(inner, text=f"{score:,}", font=("Consolas", 16, "bold"),
                         text_color=ACCENT, anchor="e", width=90).pack(side="right")

        # ── Big total score ───────────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color=ACCENT_DIM, height=1).pack(fill="x", padx=40, pady=(16, 20))

        score_box = ctk.CTkFrame(self, fg_color=BG_SURFACE2, corner_radius=16)
        score_box.pack(padx=60, pady=(0, 10))

        inner_box = ctk.CTkFrame(score_box, fg_color="transparent")
        inner_box.pack(padx=40, pady=20)

        ctk.CTkLabel(inner_box, text="TOTAL SCORE",
                     font=(FONT, 14, "bold"), text_color=TEXT_DIM).pack()
        ctk.CTkLabel(inner_box, text=f"{total_score:,}",
                     font=(FONT, 52, "bold"), text_color=GOLD).pack(pady=(4, 0))
        ctk.CTkLabel(inner_box, text="/ 100,000",
                     font=(FONT, 16), text_color=TEXT_DIM).pack(pady=(0, 4))

        # Score tier
        if total_score >= 80000:
            tier, tier_color = "EXCELLENT", GOLD
        elif total_score >= 60000:
            tier, tier_color = "GREAT", ACCENT_GLOW
        elif total_score >= 40000:
            tier, tier_color = "GOOD", ACCENT
        elif total_score >= 20000:
            tier, tier_color = "AVERAGE", TEXT_ON
        else:
            tier, tier_color = "LOW", ERROR_RED

        ctk.CTkLabel(inner_box, text=tier, font=(FONT, 18, "bold"),
                     text_color=tier_color).pack(pady=(2, 0))

        # Report path
        ctk.CTkLabel(self, text=f"Report saved: {report_path}",
                     font=(FONT, 11), text_color=TEXT_DIM,
                     wraplength=600).pack(pady=(10, 24))


class DemBenchApp:
    """DemBench Material 3 fullscreen GUI application."""

    def __init__(self, skip_gpu=False, skip_network=False, output_path=None):
        self.skip_gpu = skip_gpu
        self.skip_network = skip_network
        self.output_path = output_path
        self.results = {}

        self.root = ctk.CTk()
        self.root.title("DemBench v1.0 — DemirArch")
        self.root.configure(fg_color=BG_BASE)

        # Fullscreen / maximized (cross-platform)
        try:
            self.root.state("zoomed")  # Windows
        except Exception:
            try:
                self.root.attributes("-zoomed", True)  # Linux
            except Exception:
                pass
        self.root.minsize(1100, 760)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

        self._build()

    def _build(self):
        # Scrollable container — fills the entire screen
        self.scroll = ctk.CTkScrollableFrame(self.root, fg_color=BG_BASE,
                                             scrollbar_button_color=ACCENT_DIM,
                                             scrollbar_button_hover_color=ACCENT)
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Center content with max width
        self.content = ctk.CTkFrame(self.scroll, fg_color="transparent", width=800)
        self.content.pack(expand=True, pady=10)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self.content, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS)
        header.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(header, text=LOGO_TEXT, font=("Consolas", 11),
                     text_color=ACCENT, justify="center").pack(padx=20, pady=(20, 6))
        ctk.CTkLabel(header, text="DemirArch  •  DemBench v1.0  •  System Benchmark",
                     font=(FONT, 14), text_color=TEXT_DIM).pack(pady=(0, 2))
        run_mode = []
        if self.skip_gpu:
            run_mode.append("GPU skipped")
        if self.skip_network:
            run_mode.append("Network skipped")
        mode_text = "Run mode: " + (", ".join(run_mode) if run_mode else "Full benchmark")
        ctk.CTkLabel(header, text=mode_text,
                     font=(FONT, 12), text_color=TEXT_DIM).pack(pady=(0, 14))

        # ── Benchmark cards ───────────────────────────────────────────────────
        self.cards = {}
        bench_info = [
            ("cpu",  "CPU Benchmark",     "\u2699",       30),
            ("ram",  "RAM Benchmark",     "\U0001f9e0",   20),
            ("disk", "Disk Benchmark",    "\U0001f4be",   20),
            ("gpu",  "GPU Benchmark",     "\U0001f3ae",   20),
            ("net",  "Network Benchmark", "\U0001f310",   10),
        ]
        for key, title, icon, weight in bench_info:
            card = BenchmarkCard(self.content, title, icon, weight)
            card.pack(fill="x", padx=16, pady=6)
            self.cards[key] = card

        # ── Overall progress ───────────────────────────────────────────────────
        overall = ctk.CTkFrame(self.content, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS)
        overall.pack(fill="x", padx=16, pady=(10, 6))

        overall_row = ctk.CTkFrame(overall, fg_color="transparent")
        overall_row.pack(fill="x", padx=24, pady=(14, 8))
        ctk.CTkLabel(overall_row, text="Overall Progress", font=(FONT, 14, "bold"),
                     text_color=TEXT_ON).pack(side="left")
        self.overall_pct = ctk.CTkLabel(overall_row, text="0%", font=(FONT, 12), text_color=TEXT_DIM)
        self.overall_pct.pack(side="right")

        self.overall_progress = ctk.CTkProgressBar(overall, height=9, corner_radius=5,
                                                   fg_color=BG_SURFACE2, progress_color=ACCENT)
        self.overall_progress.pack(fill="x", padx=24, pady=(0, 6))
        self.overall_progress.set(0)

        self.overall_status = ctk.CTkLabel(overall, text="Waiting to start...",
                                           font=(FONT, 12), text_color=TEXT_DIM, anchor="w")
        self.overall_status.pack(fill="x", padx=28, pady=(0, 14))

        # ── Summary (hidden until done) ───────────────────────────────────────
        self.summary = SummaryCard(self.content)

        # ── Bottom bar ────────────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom.pack(fill="x", padx=16, pady=(12, 24))

        self.quit_btn = ctk.CTkButton(bottom, text="  Quit  (Q / Esc)  ",
                                      font=(FONT, 13, "bold"),
                                      fg_color=BG_SURFACE2, hover_color=ACCENT_DIM,
                                      text_color=TEXT_ON, corner_radius=12,
                                      height=44, command=self._quit)
        self.quit_btn.pack(side="right")

        self.root.bind("<q>", lambda e: self._quit())
        self.root.bind("<Q>", lambda e: self._quit())
        self.root.bind("<Escape>", lambda e: self._quit())

    # ── Thread-safe helpers ───────────────────────────────────────────────────

    def _safe(self, fn, *args):
        try:
            self.root.after(0, fn, *args)
        except Exception:
            pass

    def _make_cb(self, key: str):
        card = self.cards[key]
        def cb(pct, status):
            self._safe(card.update_progress, pct, status)
        return cb

    # ── Benchmark runners ─────────────────────────────────────────────────────

    def _set_overall_progress(self, pct: float, status: str):
        pct = max(0.0, min(1.0, pct))
        self.overall_progress.set(pct)
        self.overall_pct.configure(text=f"{int(pct * 100)}%")
        self.overall_status.configure(text=status)

    def _run_all(self):
        steps = [
            ("CPU benchmark running...", self._bench_cpu),
            ("RAM benchmark running...", self._bench_ram),
            ("Disk benchmark running...", self._bench_disk),
            ("GPU benchmark running...", self._bench_gpu),
            ("Network benchmark running...", self._bench_net),
        ]
        total = len(steps)
        for index, (status, fn) in enumerate(steps, start=1):
            self._safe(self._set_overall_progress, (index - 1) / total, status)
            fn()
            self._safe(self._set_overall_progress, index / total, f"Completed: {status}")
        self._safe(self._set_overall_progress, 1.0, "All benchmarks completed.")
        self._safe(self._show_summary)

    def _bench_cpu(self):
        card = self.cards["cpu"]
        self._safe(card.set_running)
        try:
            from benchmarks.cpu import run
            r = run(progress_callback=self._make_cb("cpu"))
            self.results["cpu"] = r
            cpu_avg = (r["single_core_score"] + r["multi_core_score"]) // 2
            self._safe(card.set_done,
                       f"Single: {r['single_core_score']:,}  •  "
                       f"Multi: {r['multi_core_score']:,}  •  "
                       f"{r['duration_s']:.1f}s",
                       cpu_avg)
        except Exception as e:
            self.results["cpu"] = {"single_core_score": 0, "multi_core_score": 0, "duration_s": 0}
            self._safe(card.set_error, str(e))

    def _bench_ram(self):
        card = self.cards["ram"]
        self._safe(card.set_running)
        try:
            from benchmarks.ram import run
            r = run(progress_callback=self._make_cb("ram"))
            self.results["ram"] = r
            self._safe(card.set_done,
                       f"Read: {r['read_mbps']:,.0f} MB/s  •  "
                       f"Write: {r['write_mbps']:,.0f} MB/s  •  "
                       f"Total: {r.get('total_gb', 0):.0f} GB",
                       r["score"])
        except Exception as e:
            self.results["ram"] = {"read_mbps": 0, "write_mbps": 0, "score": 0}
            self._safe(card.set_error, str(e))

    def _bench_disk(self):
        card = self.cards["disk"]
        self._safe(card.set_running)
        try:
            from benchmarks.disk import run
            r = run(progress_callback=self._make_cb("disk"))
            self.results["disk"] = r
            self._safe(card.set_done,
                       f"Read: {r['read_mbps']:,.0f} MB/s  •  "
                       f"Write: {r['write_mbps']:,.0f} MB/s",
                       r["score"])
        except Exception as e:
            self.results["disk"] = {"read_mbps": 0, "write_mbps": 0, "score": 0}
            self._safe(card.set_error, str(e))

    def _bench_gpu(self):
        card = self.cards["gpu"]
        self._safe(card.set_running)
        try:
            from benchmarks.gpu import run
            r = run(progress_callback=self._make_cb("gpu"), skip=self.skip_gpu)
            self.results["gpu"] = r
            if r.get("skipped"):
                self._safe(card.set_done, "GPU test skipped", 0, True)
            else:
                self._safe(card.set_done,
                           f"Frames: {r.get('frames', 0):,}",
                           r["score"])
        except Exception as e:
            self.results["gpu"] = {"score": 0, "skipped": True}
            self._safe(card.set_error, str(e))

    def _bench_net(self):
        card = self.cards["net"]
        self._safe(card.set_running)
        try:
            from benchmarks.network import run
            r = run(progress_callback=self._make_cb("net"), skip=self.skip_network)
            self.results["network"] = r
            if r.get("skipped"):
                self._safe(card.set_done, "Network test skipped", 0, True)
            else:
                self._safe(card.set_done,
                           f"DL: {r['download_mbps']:.1f} Mbps  •  "
                           f"UL: {r['upload_mbps']:.1f} Mbps  •  "
                           f"Ping: {r['ping_ms']:.0f} ms",
                           r["score"])
        except Exception as e:
            self.results["network"] = {"download_mbps": 0, "upload_mbps": 0,
                                       "ping_ms": 0, "score": 0, "skipped": False}
            self._safe(card.set_error, str(e))

    def _show_summary(self):
        total = compute_total_score(self.results)
        path = generate_report(self.results, self.output_path)
        self.summary.show(self.results, total, path)
        self.summary.pack(fill="x", padx=16, pady=(12, 8))

    # ── Run ───────────────────────────────────────────────────────────────────

    def _quit(self):
        try:
            if self.root.winfo_exists():
                self.root.destroy()
        except Exception:
            pass

    def run(self):
        self._set_overall_progress(0.0, "Initializing benchmark engine...")
        self.root.after(400, lambda: threading.Thread(
            target=self._run_all, daemon=True).start())
        self.root.mainloop()
