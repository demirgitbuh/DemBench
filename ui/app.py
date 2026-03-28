"""DemBench GUI — Modern Neon Dark Theme with glassmorphism effects."""

import customtkinter as ctk
import threading
import time
import math

from scoring import compute_total_score, compute_cpu_combined_score
from reporter import generate_report

# ── Theme Setup ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")

# Base
BG_BASE     = "#080b14"
BG_SURFACE  = "#0d1025"
BG_SURFACE2 = "#151937"
BG_SURFACE3 = "#1c2148"

# Accents
ACCENT         = "#00E5A0"
ACCENT_DIM     = "#007a5c"
ACCENT_GLOW    = "#00FFBB"
ACCENT_BLUE    = "#3B82F6"
ACCENT_PURPLE  = "#8B5CF6"
ACCENT_PINK    = "#EC4899"
ACCENT_ORANGE  = "#F59E0B"

# Text
TEXT_ON     = "#F0F2F5"
TEXT_DIM    = "#6B7394"
TEXT_MUTED  = "#3D4263"

# Status
ERROR_RED   = "#EF4444"
SUCCESS     = "#10B981"
WARNING     = "#F59E0B"
GOLD        = "#FFD700"

# Layout
CARD_RADIUS = 16
FONT        = "Segoe UI"
MONO_FONT   = "JetBrains Mono"

# ── Benchmark icons and colors per type ──────────────────────────────────────
BENCH_THEME = {
    "cpu":  {"icon": "\u2699\uFE0F",  "color": ACCENT_BLUE,   "label": "CPU"},
    "ram":  {"icon": "\U0001f9e0", "color": ACCENT_PURPLE, "label": "RAM"},
    "disk": {"icon": "\U0001f4be", "color": ACCENT_ORANGE, "label": "DISK"},
    "gpu":  {"icon": "\U0001f3ae", "color": ACCENT_PINK,   "label": "GPU"},
    "net":  {"icon": "\U0001f310", "color": ACCENT,        "label": "NET"},
}

LOGO_ART = (
    "  ____                  ____                  _\n"
    " |  _ \\  ___ _ __ ___ | __ )  ___ _ __   ___| |__\n"
    " | | | |/ _ \\ '_ ` _ \\|  _ \\ / _ \\ '_ \\ / __| '_ \\\n"
    " | |_| |  __/ | | | | | |_) |  __/ | | | (__| | | |\n"
    " |____/ \\___|_| |_| |_|____/ \\___|_| |_|\\___|_| |_|"
)


class BenchmarkCard(ctk.CTkFrame):
    """Modern benchmark card with accent color stripe and animated progress."""

    def __init__(self, parent, key: str, title: str, weight_pct: int):
        theme = BENCH_THEME.get(key, {"icon": "\u2699", "color": ACCENT, "label": key.upper()})
        self._accent = theme["color"]
        self._key = key

        super().__init__(parent, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS,
                         border_width=1, border_color=BG_SURFACE3)

        # ── Accent stripe on top ─────────────────────────────────────────
        stripe = ctk.CTkFrame(self, fg_color=self._accent, height=3,
                              corner_radius=0)
        stripe.pack(fill="x", padx=20, pady=(0, 0))

        # ── Header row ───────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(12, 4))

        # Icon + title
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(left, text=theme["icon"], font=(FONT, 22),
                     text_color=self._accent).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(left, text=title, font=(FONT, 16, "bold"),
                     text_color=TEXT_ON).pack(side="left")

        # Right side: weight badge + status chip
        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right")

        self.weight_badge = ctk.CTkLabel(right, text=f" {weight_pct}% ",
                                         font=(MONO_FONT, 10, "bold"),
                                         text_color=TEXT_MUTED, fg_color=BG_SURFACE2,
                                         corner_radius=6)
        self.weight_badge.pack(side="left", padx=(0, 8))

        self.chip = ctk.CTkLabel(right, text=" WAITING ",
                                 font=(FONT, 10, "bold"),
                                 text_color=TEXT_MUTED, fg_color=BG_SURFACE2,
                                 corner_radius=8)
        self.chip.pack(side="left")

        # ── Progress bar ─────────────────────────────────────────────────
        self.progress = ctk.CTkProgressBar(self, height=6, corner_radius=3,
                                           fg_color=BG_SURFACE3,
                                           progress_color=self._accent)
        self.progress.pack(fill="x", padx=20, pady=(8, 4))
        self.progress.set(0)

        # ── Status text ──────────────────────────────────────────────────
        self.status = ctk.CTkLabel(self, text="Waiting to start...",
                                   font=(FONT, 11), text_color=TEXT_MUTED, anchor="w")
        self.status.pack(fill="x", padx=24, pady=(2, 2))

        # ── Result row ───────────────────────────────────────────────────
        result_row = ctk.CTkFrame(self, fg_color="transparent")
        result_row.pack(fill="x", padx=20, pady=(0, 14))

        self.result = ctk.CTkLabel(result_row, text="",
                                   font=(FONT, 12, "bold"),
                                   text_color=self._accent, anchor="w")
        self.result.pack(side="left", fill="x", expand=True)

        self.score_label = ctk.CTkLabel(result_row, text="",
                                        font=(MONO_FONT, 20, "bold"),
                                        text_color=self._accent, anchor="e")
        self.score_label.pack(side="right")

    def set_running(self):
        self.chip.configure(text=" RUNNING ", fg_color=self._accent,
                            text_color=BG_BASE)
        self.configure(border_color=self._accent)

    def update_progress(self, pct: float, status: str):
        self.progress.set(min(pct, 1.0))
        self.status.configure(text=status, text_color=TEXT_DIM)

    def set_done(self, result_text: str, score: int, skipped=False):
        if skipped:
            self.chip.configure(text=" SKIPPED ", fg_color=BG_SURFACE3,
                                text_color=TEXT_MUTED)
            self.result.configure(text=result_text, text_color=TEXT_MUTED)
            self.score_label.configure(text="—", text_color=TEXT_MUTED)
            self.configure(border_color=BG_SURFACE3)
        else:
            self.chip.configure(text=" DONE ", fg_color=SUCCESS,
                                text_color=BG_BASE)
            self.result.configure(text=result_text, text_color=TEXT_ON)
            self.score_label.configure(text=f"{score:,}", text_color=self._accent)
            self.configure(border_color=SUCCESS)
        self.progress.set(1.0)
        self.status.configure(text="Completed", text_color=SUCCESS)

    def set_error(self, msg: str):
        self.chip.configure(text=" ERROR ", fg_color=ERROR_RED,
                            text_color=BG_BASE)
        self.result.configure(text=msg, text_color=ERROR_RED)
        self.score_label.configure(text="0", text_color=ERROR_RED)
        self.progress.set(1.0)
        self.configure(border_color=ERROR_RED)


class SummaryCard(ctk.CTkFrame):
    """Final results summary with score visualization."""

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS,
                         border_width=2, border_color=ACCENT)

    def show(self, results: dict, total_score: int, report_path: str):
        for w in self.winfo_children():
            w.destroy()

        # ── Header ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 4))

        ctk.CTkLabel(header, text="\u2705", font=(FONT, 28)).pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="BENCHMARK COMPLETE",
                     font=(FONT, 20, "bold"), text_color=ACCENT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(title_col, text="All tests finished. Here are your results.",
                     font=(FONT, 12), text_color=TEXT_DIM, anchor="w").pack(anchor="w")

        # Divider
        ctk.CTkFrame(self, fg_color=BG_SURFACE3, height=1).pack(fill="x", padx=30, pady=(16, 12))

        # ── Score rows ────────────────────────────────────────────────────
        cpu = results.get("cpu", {})
        ram = results.get("ram", {})
        disk = results.get("disk", {})
        gpu = results.get("gpu", {})
        net = results.get("network", {})
        cpu_combined = compute_cpu_combined_score(cpu)

        rows = [
            ("cpu",  "CPU", cpu_combined, "30%",
             f"Single: {cpu.get('single_core_score', 0):,}  |  Multi: {cpu.get('multi_core_score', 0):,}"),
            ("ram",  "RAM", ram.get("score", 0), "20%",
             f"R: {ram.get('read_mbps', 0):,.0f} MB/s  |  W: {ram.get('write_mbps', 0):,.0f} MB/s"),
            ("disk", "Disk", disk.get("score", 0), "20%",
             f"R: {disk.get('read_mbps', 0):,.0f} MB/s  |  W: {disk.get('write_mbps', 0):,.0f} MB/s"),
            ("gpu",  "GPU", gpu.get("score", 0), "20%",
             "[skipped]" if gpu.get("skipped") else
             f"Frames: {gpu.get('frames', 0):,}  |  FPS: {gpu.get('fps', 0):.0f}"),
            ("net",  "Network", net.get("score", 0), "10%",
             "[skipped]" if net.get("skipped") else
             f"DL: {net.get('download_mbps', 0):.1f}  |  UL: {net.get('upload_mbps', 0):.1f} Mbps  |  Ping: {net.get('ping_ms', 0):.0f} ms"),
        ]

        for key, label, score, weight, detail in rows:
            theme = BENCH_THEME.get(key, {"icon": "", "color": ACCENT})
            row = ctk.CTkFrame(self, fg_color=BG_SURFACE2, corner_radius=10)
            row.pack(fill="x", padx=24, pady=3)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=8)

            # Color dot + label
            ctk.CTkLabel(inner, text="\u25CF", font=(FONT, 14),
                         text_color=theme["color"], width=20).pack(side="left")
            ctk.CTkLabel(inner, text=f" {label}", font=(FONT, 13, "bold"),
                         text_color=TEXT_ON, anchor="w", width=80).pack(side="left")
            ctk.CTkLabel(inner, text=weight, font=(MONO_FONT, 10),
                         text_color=TEXT_MUTED, width=35).pack(side="left")
            ctk.CTkLabel(inner, text=detail, font=(FONT, 10),
                         text_color=TEXT_DIM, anchor="w").pack(side="left", fill="x", expand=True, padx=(8, 0))

            # Score
            score_color = theme["color"] if score > 0 else TEXT_MUTED
            ctk.CTkLabel(inner, text=f"{score:,}", font=(MONO_FONT, 15, "bold"),
                         text_color=score_color, anchor="e", width=90).pack(side="right")

        # ── Big total score ───────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color=BG_SURFACE3, height=1).pack(fill="x", padx=30, pady=(16, 16))

        score_box = ctk.CTkFrame(self, fg_color=BG_SURFACE2, corner_radius=16,
                                 border_width=2, border_color=GOLD)
        score_box.pack(padx=50, pady=(0, 8))

        inner_box = ctk.CTkFrame(score_box, fg_color="transparent")
        inner_box.pack(padx=48, pady=24)

        ctk.CTkLabel(inner_box, text="TOTAL SCORE",
                     font=(FONT, 13, "bold"), text_color=TEXT_DIM).pack()

        # Big score number
        ctk.CTkLabel(inner_box, text=f"{total_score:,}",
                     font=(MONO_FONT, 56, "bold"), text_color=GOLD).pack(pady=(6, 0))
        ctk.CTkLabel(inner_box, text="/ 100,000",
                     font=(MONO_FONT, 14), text_color=TEXT_MUTED).pack(pady=(0, 6))

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

        tier_frame = ctk.CTkFrame(inner_box, fg_color=tier_color, corner_radius=8)
        tier_frame.pack(pady=(4, 0))
        ctk.CTkLabel(tier_frame, text=f"  {tier}  ", font=(FONT, 14, "bold"),
                     text_color=BG_BASE).pack(padx=16, pady=4)

        # Report path
        ctk.CTkLabel(self, text=f"\U0001f4c4 Report saved: {report_path}",
                     font=(FONT, 11), text_color=TEXT_DIM,
                     wraplength=600).pack(pady=(12, 24))


class DemBenchApp:
    """DemBench Modern Neon GUI application."""

    def __init__(self, skip_gpu=False, skip_network=False, output_path=None):
        self.skip_gpu = skip_gpu
        self.skip_network = skip_network
        self.output_path = output_path
        self.results = {}
        self._animation_running = False

        self.root = ctk.CTk()
        self.root.title("DemBench v2.0 — DemirArch")
        self.root.configure(fg_color=BG_BASE)

        # Fullscreen / maximized
        try:
            self.root.state("zoomed")
        except Exception:
            try:
                self.root.attributes("-zoomed", True)
            except Exception:
                pass
        self.root.minsize(1100, 760)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

        self._build()

    def _build(self):
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self.root, fg_color=BG_BASE,
                                             scrollbar_button_color=BG_SURFACE3,
                                             scrollbar_button_hover_color=ACCENT_DIM)
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Center content
        self.content = ctk.CTkFrame(self.scroll, fg_color="transparent", width=820)
        self.content.pack(expand=True, pady=10)

        # ── Header ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self.content, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS,
                              border_width=1, border_color=BG_SURFACE3)
        header.pack(fill="x", padx=16, pady=(16, 6))

        # Accent stripe
        ctk.CTkFrame(header, fg_color=ACCENT, height=3, corner_radius=0).pack(
            fill="x", padx=24, pady=(0, 0))

        # Logo
        ctk.CTkLabel(header, text=LOGO_ART, font=(MONO_FONT, 11),
                     text_color=ACCENT, justify="center").pack(padx=20, pady=(16, 4))

        # Subtitle row
        sub_frame = ctk.CTkFrame(header, fg_color="transparent")
        sub_frame.pack(pady=(2, 4))

        ctk.CTkLabel(sub_frame, text="DemirArch", font=(FONT, 13, "bold"),
                     text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(sub_frame, text="  \u2022  ", font=(FONT, 13),
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(sub_frame, text="DemBench v2.0", font=(FONT, 13),
                     text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(sub_frame, text="  \u2022  ", font=(FONT, 13),
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(sub_frame, text="System Benchmark", font=(FONT, 13),
                     text_color=TEXT_DIM).pack(side="left")

        # Run mode
        run_mode = []
        if self.skip_gpu:
            run_mode.append("GPU skipped")
        if self.skip_network:
            run_mode.append("Network skipped")
        mode_text = ", ".join(run_mode) if run_mode else "Full benchmark"

        mode_badge = ctk.CTkFrame(header, fg_color="transparent")
        mode_badge.pack(pady=(2, 14))
        ctk.CTkLabel(mode_badge, text=f" {mode_text} ",
                     font=(MONO_FONT, 10, "bold"),
                     text_color=TEXT_DIM, fg_color=BG_SURFACE2,
                     corner_radius=8).pack()

        # ── Benchmark cards ───────────────────────────────────────────────
        self.cards = {}
        bench_info = [
            ("cpu",  "CPU Benchmark",     30),
            ("ram",  "RAM Benchmark",     20),
            ("disk", "Disk Benchmark",    20),
            ("gpu",  "GPU Benchmark",     20),
            ("net",  "Network Benchmark", 10),
        ]
        for key, title, weight in bench_info:
            card = BenchmarkCard(self.content, key, title, weight)
            card.pack(fill="x", padx=16, pady=5)
            self.cards[key] = card

        # ── Overall progress ──────────────────────────────────────────────
        overall = ctk.CTkFrame(self.content, fg_color=BG_SURFACE, corner_radius=CARD_RADIUS,
                               border_width=1, border_color=BG_SURFACE3)
        overall.pack(fill="x", padx=16, pady=(8, 5))

        overall_top = ctk.CTkFrame(overall, fg_color="transparent")
        overall_top.pack(fill="x", padx=20, pady=(14, 6))

        ctk.CTkLabel(overall_top, text="\u26A1", font=(FONT, 16)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(overall_top, text="Overall Progress", font=(FONT, 14, "bold"),
                     text_color=TEXT_ON).pack(side="left")

        self.overall_pct = ctk.CTkLabel(overall_top, text="0%",
                                        font=(MONO_FONT, 13, "bold"),
                                        text_color=ACCENT)
        self.overall_pct.pack(side="right")

        self.overall_progress = ctk.CTkProgressBar(overall, height=8, corner_radius=4,
                                                   fg_color=BG_SURFACE3,
                                                   progress_color=ACCENT)
        self.overall_progress.pack(fill="x", padx=20, pady=(0, 4))
        self.overall_progress.set(0)

        self.overall_status = ctk.CTkLabel(overall, text="Initializing...",
                                           font=(FONT, 11), text_color=TEXT_MUTED, anchor="w")
        self.overall_status.pack(fill="x", padx=24, pady=(0, 12))

        # ── Summary (hidden) ──────────────────────────────────────────────
        self.summary = SummaryCard(self.content)

        # ── Bottom bar ────────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom.pack(fill="x", padx=16, pady=(10, 24))

        self.quit_btn = ctk.CTkButton(bottom, text="  Quit  (Q / Esc)  ",
                                      font=(FONT, 12, "bold"),
                                      fg_color=BG_SURFACE2, hover_color=ERROR_RED,
                                      text_color=TEXT_DIM, corner_radius=10,
                                      border_width=1, border_color=BG_SURFACE3,
                                      height=40, command=self._quit)
        self.quit_btn.pack(side="right")

        # Version label
        ctk.CTkLabel(bottom, text="DemBench v2.0  \u2022  GPL-3.0-or-later",
                     font=(FONT, 10), text_color=TEXT_MUTED).pack(side="left")

        self.root.bind("<q>", lambda e: self._quit())
        self.root.bind("<Q>", lambda e: self._quit())
        self.root.bind("<Escape>", lambda e: self._quit())

    # ── Thread-safe helpers ───────────────────────────────────────────────

    def _safe(self, fn, *args):
        try:
            if self.root.winfo_exists():
                self.root.after(0, fn, *args)
        except Exception:
            pass

    def _make_cb(self, key: str):
        card = self.cards[key]
        def cb(pct, status):
            self._safe(card.update_progress, pct, status)
        return cb

    # ── Benchmark runners ─────────────────────────────────────────────────

    def _set_overall_progress(self, pct: float, status: str):
        pct = max(0.0, min(1.0, pct))
        self.overall_progress.set(pct)
        self.overall_pct.configure(text=f"{int(pct * 100)}%")
        self.overall_status.configure(text=status, text_color=TEXT_DIM)

    def _run_all(self):
        steps = [
            ("cpu", "CPU benchmark running...", self._bench_cpu),
            ("ram", "RAM benchmark running...", self._bench_ram),
            ("disk", "Disk benchmark running...", self._bench_disk),
            ("gpu", "GPU benchmark running...", self._bench_gpu),
            ("net", "Network benchmark running...", self._bench_net),
        ]
        total = len(steps)
        for index, (key, status, fn) in enumerate(steps, start=1):
            self._safe(self._set_overall_progress, (index - 1) / total, status)
            fn()
            done_msg = f"Completed {index}/{total}: {BENCH_THEME.get(key, {}).get('label', key.upper())}"
            self._safe(self._set_overall_progress, index / total, done_msg)

        self._safe(self._set_overall_progress, 1.0, "All benchmarks completed!")
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
                       f"Single: {r['single_core_score']:,}  \u2022  "
                       f"Multi: {r['multi_core_score']:,}  \u2022  "
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
                       f"Read: {r['read_mbps']:,.0f} MB/s  \u2022  "
                       f"Write: {r['write_mbps']:,.0f} MB/s  \u2022  "
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
                       f"Read: {r['read_mbps']:,.0f} MB/s  \u2022  "
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
                fps = r.get('fps', 0)
                fps_text = f"  \u2022  {fps:.0f} FPS" if fps else ""
                self._safe(card.set_done,
                           f"Frames: {r.get('frames', 0):,}{fps_text}",
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
                           f"DL: {r['download_mbps']:.1f} Mbps  \u2022  "
                           f"UL: {r['upload_mbps']:.1f} Mbps  \u2022  "
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
        self.summary.pack(fill="x", padx=16, pady=(10, 8))

    # ── Run ───────────────────────────────────────────────────────────────

    def _quit(self):
        self._animation_running = False
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
