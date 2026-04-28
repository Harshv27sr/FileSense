import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import datetime
from database import DatabaseManager
from file_scanner import FileScanner
from similarity_detector import SimilarityDetector
from file_organizer import FileOrganizer
from trash_manager import TrashManager

# ══════════════════════════════════════════════════════
#  COLOUR PALETTE  –  Deep Navy / Teal Accent
# ══════════════════════════════════════════════════════
C = {
    "bg":           "#0e1117",
    "surface":      "#161b27",
    "card":         "#1c2333",
    "sidebar":      "#111520",
    "sidebar_sel":  "#1a2235",
    "border":       "#252d42",
    "topbar":       "#13192a",

    "teal":         "#0af0d0",
    "blue":         "#3b82f6",
    "blue_bg":      "#0d1f3c",
    "red":          "#f87171",
    "green":        "#34d399",
    "amber":        "#fbbf24",
    "purple":       "#a78bfa",

    "text":         "#e2e8f0",
    "text_muted":   "#64748b",
    "text_dim":     "#94a3b8",
}

F = {
    "title":   ("Segoe UI", 20, "bold"),
    "heading": ("Segoe UI", 11, "bold"),
    "sub":     ("Segoe UI",  9, "bold"),
    "body":    ("Segoe UI",  9),
    "nav":     ("Segoe UI", 10),
    "mono":    ("Consolas",  9),
    "stat":    ("Segoe UI", 26, "bold"),
    "badge":   ("Segoe UI",  7, "bold"),
    "topbar":  ("Segoe UI", 18, "bold"),
    "section": ("Segoe UI",  8, "bold"),
    "btn":     ("Segoe UI",  9, "bold"),
}


# ── helpers ──────────────────────────────────────────────────────────────────

def hline(parent, color=None, pady=0):
    tk.Frame(parent, bg=color or C["border"], height=1).pack(fill=tk.X, pady=pady)


def section_label(parent, text, bg=None):
    bg = bg or C["sidebar"]
    tk.Label(parent, text=text, font=F["section"],
             bg=bg, fg=C["text_muted"],
             anchor="w", padx=18, pady=5).pack(fill=tk.X)


# ── custom button ─────────────────────────────────────────────────────────────

class Btn(tk.Frame):
    STYLES = {
        "primary": ("#0af0d0", "#6ffaea", "#071e1b", "#0af0d0"),
        "ghost":   ("#94a3b8", "#e2e8f0", "#1c2333", "#252d42"),
        "danger":  ("#f87171", "#fca5a5", "#2d1515", "#f87171"),
        "success": ("#34d399", "#6ee7b7", "#0d2b20", "#34d399"),
        "amber":   ("#fbbf24", "#fcd34d", "#2d2006", "#fbbf24"),
        "purple":  ("#a78bfa", "#c4b5fd", "#1d1040", "#a78bfa"),
    }

    def __init__(self, parent, text, command=None, style="ghost", padx=12, pady=6, **kw):
        fg, fghov, bg, border = self.STYLES.get(style, self.STYLES["ghost"])
        super().__init__(parent, bg=border, padx=1, pady=1, cursor="hand2")
        self._lbl = tk.Label(self, text=text, font=F["btn"],
                             bg=bg, fg=fg, padx=padx, pady=pady)
        self._lbl.pack(fill=tk.BOTH)
        self._lbl.bind("<Enter>",    lambda e: self._lbl.config(fg=fghov))
        self._lbl.bind("<Leave>",    lambda e: self._lbl.config(fg=fg))
        self._lbl.bind("<Button-1>", lambda e: command() if command else None)


# ── sidebar nav row ───────────────────────────────────────────────────────────

class NavBtn(tk.Frame):
    def __init__(self, parent, icon, text, command, indent=0, accent=None):
        accent = accent or C["teal"]
        super().__init__(parent, bg=C["sidebar"], cursor="hand2")
        self.pack(fill=tk.X)

        inner = tk.Frame(self, bg=C["sidebar"])
        inner.pack(fill=tk.X)

        if indent:
            tk.Frame(inner, bg=C["sidebar"], width=indent).pack(side=tk.LEFT)

        self._bar = tk.Frame(inner, bg=C["sidebar"], width=3)
        self._bar.pack(side=tk.LEFT, fill=tk.Y)

        self._icon = tk.Label(inner, text=icon, font=("Segoe UI Emoji", 11),
                              bg=C["sidebar"], fg=accent, padx=10, pady=9)
        self._icon.pack(side=tk.LEFT)

        self._txt = tk.Label(inner, text=text, font=F["nav"],
                             bg=C["sidebar"], fg=C["text_dim"], anchor="w")
        self._txt.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=9)

        self._inner = inner
        self._accent = accent

        for w in (inner, self._icon, self._txt, self._bar):
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>",    lambda e: self._hover(True))
            w.bind("<Leave>",    lambda e: self._hover(False))

    def _hover(self, on):
        bg = C["sidebar_sel"] if on else C["sidebar"]
        for w in (self._inner, self._icon, self._txt, self._bar):
            w.config(bg=bg)
        self._txt.config(fg=C["text"] if on else C["text_dim"])
        self._bar.config(bg=self._accent if on else bg)


# ── stat card ─────────────────────────────────────────────────────────────────

class StatCard(tk.Frame):
    def __init__(self, parent, icon, title, value, accent, sub_left, sub_right):
        super().__init__(parent, bg=accent, padx=1, pady=1)   # border

        face = tk.Frame(self, bg=C["card"])
        face.pack(fill=tk.BOTH, expand=True)

        tk.Frame(face, bg=accent, height=3).pack(fill=tk.X)   # top stripe

        body = tk.Frame(face, bg=C["card"])
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # icon + value
        top = tk.Frame(body, bg=C["card"])
        top.pack(fill=tk.X)

        pill = tk.Frame(top, bg=C["surface"], padx=6, pady=4)
        pill.pack(side=tk.LEFT)
        tk.Label(pill, text=icon, font=("Segoe UI Emoji", 18),
                 bg=C["surface"], fg=accent).pack()

        self.val_lbl = tk.Label(top, text=value, font=F["stat"],
                                 bg=C["card"], fg=accent)
        self.val_lbl.pack(side=tk.RIGHT, padx=2)

        tk.Label(body, text=title, font=F["sub"],
                 bg=C["card"], fg=C["text_muted"], anchor="w").pack(fill=tk.X, pady=(6, 0))

        hline(body, C["border"], 5)

        foot = tk.Frame(body, bg=C["card"])
        foot.pack(fill=tk.X)
        tk.Label(foot, text=sub_left, font=F["body"],
                 bg=C["card"], fg=C["text_muted"]).pack(side=tk.LEFT)
        self.sub_lbl = tk.Label(foot, text=sub_right, font=F["sub"],
                                 bg=C["card"], fg=accent)
        self.sub_lbl.pack(side=tk.RIGHT)


# ══════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════

class FileManagerUI:
    def __init__(self, root):
        self.root = root
        self.db   = DatabaseManager()
        self.scanner             = FileScanner()
        self.similarity_detector = SimilarityDetector()
        self.organizer           = FileOrganizer()
        self.trash               = TrashManager()

        self.clear_previous_files()
        self.current_files = []
        self._configure_ttk()
        self.setup_ui()
        self.update_dashboard_stats()

    # ── init helpers ─────────────────────────────────────────────────────────

    def clear_previous_files(self):
        try:
            self.db.clear_all_files()
        except Exception as e:
            print(f"⚠️  {e}")

    def _configure_ttk(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("T.Treeview",
                    background=C["surface"], foreground=C["text"],
                    fieldbackground=C["surface"], rowheight=26,
                    font=F["body"], borderwidth=0)
        s.configure("T.Treeview.Heading",
                    background=C["card"], foreground=C["teal"],
                    font=F["sub"], relief="flat", borderwidth=0)
        s.map("T.Treeview",
              background=[("selected", C["blue_bg"])],
              foreground=[("selected", C["teal"])])

        s.configure("TScrollbar",
                    background=C["card"], troughcolor=C["surface"],
                    borderwidth=0, arrowcolor=C["text_muted"])

        s.configure("Tab.TNotebook", background=C["bg"], borderwidth=0, tabmargins=0)
        s.configure("Tab.TNotebook.Tab",
                    background=C["card"], foreground=C["text_muted"],
                    font=F["body"], padding=[14, 7])
        s.map("Tab.TNotebook.Tab",
              background=[("selected", C["surface"])],
              foreground=[("selected", C["teal"])],
              expand=[("selected", [1, 1, 1, 0])])

    # ── main layout ──────────────────────────────────────────────────────────

    def setup_ui(self):
        self.root.title("AI Smart FILE MANAGER")
        self.root.geometry("1380x820")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1100, 700)

        base = tk.Frame(self.root, bg=C["bg"])
        base.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(base)
        tk.Frame(base, bg=C["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)
        self._build_main(base)
        self._build_menu()
        self.log("AI Smart FILE MANAGER initialised")

    # ── SIDEBAR ──────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=C["sidebar"], width=235)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        # brand block
        brand = tk.Frame(sb, bg=C["bg"], height=100)
        brand.pack(fill=tk.X)
        brand.pack_propagate(False)
        tk.Label(brand, text="⬡  FileSense", font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["teal"]).place(relx=.5, rely=.38, anchor="center")

        hline(sb, C["border"])
        section_label(sb, "NAVIGATION")

        NavBtn(sb, "🗂", "Smart Folders",  self.show_files_tab,       accent=C["teal"])
        NavBtn(sb, "📄", "All Files",       self.show_files_tab,   18, accent=C["blue"])
        NavBtn(sb, "🤖", "AI Organizer",    self.show_organizer,   18, accent=C["purple"])
        NavBtn(sb, "📝", "Content Based",   self.show_similar_tab, 18, accent=C["teal"])
        NavBtn(sb, "🔄", "Duplicates",      self.show_duplicates_tab,18, accent=C["red"])
        NavBtn(sb, "💾", "Storage",         self.show_storage,     18, accent=C["amber"])
        NavBtn(sb, "📈", "Analytics",       self.show_analytics,   18, accent=C["green"])
        NavBtn(sb, "🗑", "Recycle Bin",     self.show_trash_tab,   18, accent=C["red"])

        hline(sb, C["border"])
        section_label(sb, "QUICK ACTIONS")

        for icon, label, cmd, sty in [
            ("⚡", "Auto Organize",   self.auto_organize,   "primary"),
            ("🔍", "Find Duplicates", self.find_duplicates, "ghost"),
            ("🧠", "Deep Analysis",   self.find_similar,    "ghost"),
        ]:
            row = tk.Frame(sb, bg=C["sidebar"])
            row.pack(fill=tk.X, padx=10, pady=2)
            Btn(row, f"{icon}  {label}", command=cmd, style=sty, padx=10, pady=6).pack(fill=tk.X)

        hline(sb, C["border"])
        section_label(sb, "RECENT ACTIVITY")

        lw = tk.Frame(sb, bg=C["bg"], padx=1, pady=1)
        lw.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.sidebar_recent = tk.Listbox(
            lw, height=7, bg=C["bg"], fg=C["text_muted"],
            font=F["mono"], bd=0, highlightthickness=0,
            selectbackground=C["sidebar_sel"], selectforeground=C["teal"],
            relief="flat")
        self.sidebar_recent.pack(fill=tk.X)

        # status strip
        status = tk.Frame(sb, bg=C["bg"], height=30)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        hline(status, C["border"])
        si = tk.Frame(status, bg=C["bg"])
        si.pack(fill=tk.X, padx=14, pady=6)
        tk.Frame(si, bg=C["green"], width=8, height=8).pack(side=tk.LEFT)
        tk.Label(si, text="  SYSTEM ONLINE", font=("Segoe UI", 8, "bold"),
                 bg=C["bg"], fg=C["green"]).pack(side=tk.LEFT)

    # ── MAIN CONTENT ─────────────────────────────────────────────────────────

    def _build_main(self, parent):
        main = tk.Frame(parent, bg=C["bg"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # top bar
        topbar = tk.Frame(main, bg=C["topbar"], height=55)
        topbar.pack(fill=tk.X)
        topbar.pack_propagate(False)

        tbi = tk.Frame(topbar, bg=C["topbar"])
        tbi.pack(fill=tk.BOTH, expand=True, padx=22)

        tk.Label(tbi, text="Dashboard", font=F["topbar"],
                 bg=C["topbar"], fg=C["text"]).pack(side=tk.LEFT, pady=10)

        for txt, cmd, sty in [
            ("🗑  Empty Trash",    self.empty_trash,    "danger"),
            ("⊕  Scan Directory", self.scan_directory, "primary"),
            ("+  Add Files",       self.add_files,      "ghost"),
        ]:
            Btn(tbi, txt, command=cmd, style=sty, padx=11, pady=5).pack(
                side=tk.RIGHT, padx=4, pady=10)

        hline(main, C["border"])

        # ── 4 stat cards in ONE row ─────────────────────────────────────────
        cards_row = tk.Frame(main, bg=C["bg"])
        cards_row.pack(fill=tk.X, padx=18, pady=12)

        self.card_total = StatCard(cards_row, "📄", "TOTAL FILES",   "0", C["blue"],   "indexed",        "0 files")
        self.card_dupes = StatCard(cards_row, "🔄", "DUPLICATES",    "0", C["red"],    "wasted space",   "0 KB")
        self.card_ai    = StatCard(cards_row, "🤖", "AI ORGANISED",  "0", C["green"],  "categories used","0")
        self.card_trash = StatCard(cards_row, "🗑", "RECYCLE BIN",   "0", C["purple"], "awaiting action","0 items")

        for card in (self.card_total, self.card_dupes, self.card_ai, self.card_trash):
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        # ── slim storage bar ────────────────────────────────────────────────
        sb_card = tk.Frame(main, bg=C["card"])
        sb_card.pack(fill=tk.X, padx=18, pady=(0, 8))

        sb_inner = tk.Frame(sb_card, bg=C["card"])
        sb_inner.pack(fill=tk.X, padx=16, pady=8)

        tk.Label(sb_inner, text="💾  STORAGE USED", font=F["sub"],
                 bg=C["card"], fg=C["text_muted"]).pack(side=tk.LEFT)

        self.storage_stats_lbl = tk.Label(sb_inner, text="0 files · 0 KB",
                                           font=F["body"], bg=C["card"], fg=C["text_muted"])
        self.storage_stats_lbl.pack(side=tk.RIGHT)

        self.storage_pct_lbl = tk.Label(sb_inner, text="0%",
                                         font=("Segoe UI", 9, "bold"),
                                         bg=C["card"], fg=C["amber"])
        self.storage_pct_lbl.pack(side=tk.RIGHT, padx=14)

        # progress track
        track_wrap = tk.Frame(main, bg=C["border"], height=4)
        track_wrap.pack(fill=tk.X, padx=18)
        self.storage_bar = tk.Frame(track_wrap, bg=C["amber"], height=4)
        self.storage_bar.place(x=0, y=0, relheight=1, relwidth=0)

        # ── notebook ────────────────────────────────────────────────────────
        nb_border = tk.Frame(main, bg=C["border"], padx=1, pady=1)
        nb_border.pack(fill=tk.BOTH, expand=True, padx=18, pady=(8, 14))

        self.notebook = ttk.Notebook(nb_border, style="Tab.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        for attr, label in [
            ("files_frame",      "  All Files  "),
            ("organizer_frame",  "  AI Organizer  "),
            ("similar_frame",    "  Content Based  "),
            ("duplicates_frame", "  Duplicates  "),
            ("storage_frame",    "  Storage  "),
            ("analytics_frame",  "  Analytics  "),
            ("trash_frame",      "  Recycle Bin  "),
        ]:
            f = tk.Frame(self.notebook, bg=C["surface"])
            setattr(self, attr, f)
            self.notebook.add(f, text=label)

        self._setup_files_tab()
        self._setup_organizer_tab()
        self._setup_similar_tab()
        self._setup_duplicates_tab()
        self._setup_storage_tab()
        self._setup_analytics_tab()
        self._setup_trash_tab()

    # ── TAB HELPERS ──────────────────────────────────────────────────────────

    def _tree_with_scroll(self, parent, cols, widths):
        wrap = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        wrap.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(wrap, bg=C["surface"])
        inner.pack(fill=tk.BOTH, expand=True)

        tv = ttk.Treeview(inner, columns=cols, show="headings", style="T.Treeview")
        sb = ttk.Scrollbar(inner, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=sb.set)

        for col, w in zip(cols, widths):
            tv.heading(col, text=col)
            tv.column(col, width=w, minwidth=40)

        tv.tag_configure("even", background=C["card"])
        tv.tag_configure("odd",  background=C["surface"])

        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        return tv

    def _btn_bar(self, parent, buttons):
        row = tk.Frame(parent, bg=C["surface"])
        row.pack(fill=tk.X, pady=(7, 0))
        for txt, cmd, sty in buttons:
            Btn(row, txt, command=cmd, style=sty, padx=12, pady=6).pack(side=tk.LEFT, padx=(0, 5))

    # ── INDIVIDUAL TABS ──────────────────────────────────────────────────────

    def _setup_files_tab(self):
        cols   = ("ID", "Filename", "Type", "Size (KB)", "Category", "Duplicate")
        widths = [40, 330, 70, 85, 110, 70]
        self.files_tree = self._tree_with_scroll(self.files_frame, cols, widths)
        self._btn_bar(self.files_frame, [
            ("📁  Scan Directory",  self.scan_directory, "primary"),
            ("+  Add Files",        self.add_files,       "ghost"),
            ("↻  Refresh",          self.refresh_files,   "ghost"),
            ("✕  Delete Selected",  self.delete_selected, "danger"),
        ])

    def _setup_organizer_tab(self):
        hdr = tk.Frame(self.organizer_frame, bg=C["card"])
        hdr.pack(fill=tk.X, pady=(0, 6))
        hi = tk.Frame(hdr, bg=C["card"])
        hi.pack(fill=tk.X, padx=16, pady=10)
        tk.Label(hi, text="🤖  AI SMART ORGANIZER", font=F["heading"],
                 bg=C["card"], fg=C["green"]).pack(side=tk.LEFT)
        Btn(hi, "▶  Start Organization", command=self.organize_files,
            style="success", padx=12, pady=5).pack(side=tk.RIGHT)

        for accent, icon, text in [
            (C["teal"],   "⊕", "Automatically categorise files by type and content"),
            (C["blue"],   "◈", "Create intelligent nested folder structures"),
            (C["purple"], "→", "Move files with smart conflict resolution"),
            (C["amber"],  "⚡", "Handle duplicate filenames automatically"),
        ]:
            bdr = tk.Frame(self.organizer_frame, bg=C["border"], padx=1, pady=1)
            bdr.pack(fill=tk.X, pady=1, padx=1)
            ri = tk.Frame(bdr, bg=C["card"])
            ri.pack(fill=tk.X, padx=14, pady=8)
            tk.Label(ri, text=icon, font=F["body"], bg=C["card"], fg=accent, width=2).pack(side=tk.LEFT)
            tk.Label(ri, text=text,  font=F["body"], bg=C["card"], fg=C["text_dim"]).pack(side=tk.LEFT, padx=6)

        lh = tk.Frame(self.organizer_frame, bg=C["surface"])
        lh.pack(fill=tk.X, pady=(8, 2))
        tk.Label(lh, text="OPERATION LOG", font=F["section"],
                 bg=C["surface"], fg=C["text_muted"]).pack(side=tk.LEFT)

        lb = tk.Frame(self.organizer_frame, bg=C["border"], padx=1, pady=1)
        lb.pack(fill=tk.BOTH, expand=True)
        self.org_log = scrolledtext.ScrolledText(
            lb, bg=C["bg"], fg=C["green"],
            font=F["mono"], insertbackground=C["teal"],
            relief="flat", bd=0)
        self.org_log.pack(fill=tk.BOTH, expand=True)

    def _setup_duplicates_tab(self):
        cols   = ("Group", "Filename", "Path", "Size (KB)")
        widths = [55, 230, 420, 85]
        self.duplicates_tree = self._tree_with_scroll(self.duplicates_frame, cols, widths)
        self._btn_bar(self.duplicates_frame, [
            ("🔍  Find Duplicates",  self.find_duplicates,   "primary"),
            ("✕  Delete Duplicates", self.delete_duplicates, "danger"),
            ("📅  Keep Latest Only", self.keep_latest,        "ghost"),
        ])

    def _setup_similar_tab(self):
        cols   = ("File 1", "File 2", "Combined Sim", "Content Sim", "Name Sim")
        widths = [230, 230, 110, 110, 110]
        self.similar_tree = self._tree_with_scroll(self.similar_frame, cols, widths)
        self._btn_bar(self.similar_frame, [
            ("🧠  Find Similar Files", self.find_similar, "primary"),
        ])

    def _setup_storage_tab(self):
        wrap = tk.Frame(self.storage_frame, bg=C["card"], padx=1, pady=1)
        wrap.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(wrap, bg=C["card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        tk.Label(inner, text="STORAGE ANALYTICS", font=F["heading"],
                 bg=C["card"], fg=C["amber"]).pack(anchor="w")
        hline(inner, C["border"], 8)
        self.storage_detail_label = tk.Label(inner, text="", font=("Segoe UI", 10),
                                              bg=C["card"], fg=C["text_dim"], justify=tk.LEFT)
        self.storage_detail_label.pack(anchor="w")

    def _setup_analytics_tab(self):
        wrap = tk.Frame(self.analytics_frame, bg=C["card"], padx=1, pady=1)
        wrap.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(wrap, bg=C["card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        tk.Label(inner, text="FILE ANALYTICS", font=F["heading"],
                 bg=C["card"], fg=C["teal"]).pack(anchor="w")
        hline(inner, C["border"], 8)
        self.analytics_stats = tk.Label(inner, text="", font=("Consolas", 10),
                                         bg=C["card"], fg=C["text_dim"], justify=tk.LEFT)
        self.analytics_stats.pack(anchor="w")

    def _setup_trash_tab(self):
        cols   = ("Filename", "Deleted Date", "Size (KB)", "Original Path")
        widths = [200, 145, 85, 390]
        self.trash_tree = self._tree_with_scroll(self.trash_frame, cols, widths)
        self._btn_bar(self.trash_frame, [
            ("↻  Refresh",           self.refresh_trash,      "ghost"),
            ("↩  Restore Selected",  self.restore_from_trash, "success"),
            ("🗑  Empty Trash",       self.empty_trash,        "danger"),
        ])

    # ── STATS UPDATE ─────────────────────────────────────────────────────────

    def update_dashboard_stats(self):
        files = self.db.get_all_files()
        total = len(files)
        dupes = sum(1 for f in files if f[7])
        orged = len([f for f in files if f[6] != "Other"])
        total_bytes = sum(f[4] for f in files if f[4])
        kb = total_bytes // 1024
        mb = total_bytes / (1024 * 1024)
        pct = min(100, int((mb / 100) * 100))
        trash_count = len(self.trash.get_trash_contents())

        if hasattr(self, "card_total"):
            self.card_total.val_lbl.config(text=str(total))
            self.card_total.sub_lbl.config(text=f"{total} files")
            self.card_dupes.val_lbl.config(text=str(dupes))
            self.card_dupes.sub_lbl.config(text=f"{kb} KB")
            self.card_ai.val_lbl.config(text=str(orged))
            self.card_ai.sub_lbl.config(text=str(orged))
            self.card_trash.val_lbl.config(text=str(trash_count))
            self.card_trash.sub_lbl.config(text=f"{trash_count} items")

        if hasattr(self, "storage_bar"):
            self.storage_pct_lbl.config(text=f"{pct}%")
            self.storage_stats_lbl.config(text=f"{total} files · {kb} KB · {mb:.2f} MB")
            self.storage_bar.place(relwidth=min(pct / 100, 1))

        if hasattr(self, "analytics_stats"):
            self.analytics_stats.config(text=(
                f"  Total Files Indexed   :  {total}\n"
                f"  Duplicate Files       :  {dupes}\n"
                f"  AI Organised Files    :  {orged}\n"
                f"  Items in Recycle Bin  :  {trash_count}\n"
                f"  Storage Used          :  {mb:.2f} MB  ({kb} KB)\n"
            ))
        if hasattr(self, "storage_detail_label"):
            self.storage_detail_label.config(text=(
                f"  Files tracked  :  {total}\n"
                f"  Storage used   :  {mb:.2f} MB\n"
                f"  Avg file size  :  {(kb // total if total else 0)} KB\n"
            ))

    # ── LOG ──────────────────────────────────────────────────────────────────

    def log(self, message, tag="info"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if hasattr(self, "sidebar_recent"):
            self.sidebar_recent.insert(0, f"{ts}  {message}")
            if self.sidebar_recent.size() > 12:
                self.sidebar_recent.delete(12)

    # ── REFRESH ──────────────────────────────────────────────────────────────

    def refresh_files(self):
        for row in self.files_tree.get_children():
            self.files_tree.delete(row)
        for i, f in enumerate(self.db.get_all_files()):
            kb  = f[4] // 1024 if f[4] else 0
            dup = "Yes" if f[7] else "No"
            self.files_tree.insert("", tk.END,
                                   values=(f[0], f[1], f[3], kb, f[6], dup),
                                   tags=("even" if i % 2 == 0 else "odd",))
        self.update_dashboard_stats()

    def refresh_trash(self):
        for row in self.trash_tree.get_children():
            self.trash_tree.delete(row)
        for i, f in enumerate(self.trash.get_trash_contents()):
            self.trash_tree.insert("", tk.END,
                                   values=(f["filename"], f["deleted_date"],
                                           f["size"] // 1024, f["trash_path"]),
                                   tags=("even" if i % 2 == 0 else "odd",))

    # ── MENU ─────────────────────────────────────────────────────────────────

    def _build_menu(self):
        mb = tk.Menu(self.root, bg=C["card"], fg=C["text"],
                     activebackground=C["sidebar_sel"], activeforeground=C["teal"],
                     relief="flat", bd=0)
        self.root.config(menu=mb)

        for label, items in [
            ("File", [
                ("New Session",    self.start_new_session),
                None,
                ("Scan Directory", self.scan_directory),
                ("Add Files",      self.add_files),
                None,
                ("Exit",           self.root.quit),
            ]),
            ("Tools", [
                ("Find Duplicates",    self.find_duplicates),
                ("Find Similar Files", self.find_similar),
                ("Organize Files",     self.organize_files),
                None,
                ("Empty Recycle Bin",  self.empty_trash),
            ]),
            ("Help", [("About", self.show_about)]),
        ]:
            m = tk.Menu(mb, tearoff=0, bg=C["card"], fg=C["text"],
                        activebackground=C["sidebar_sel"], activeforeground=C["teal"])
            mb.add_cascade(label=label, menu=m)
            for item in items:
                if item is None:
                    m.add_separator()
                else:
                    m.add_command(label=item[0], command=item[1])

    # ── NAVIGATION ───────────────────────────────────────────────────────────

    def show_files_tab(self):      self.notebook.select(self.files_frame);      self.refresh_files()
    def show_organizer(self):      self.notebook.select(self.organizer_frame)
    def show_similar_tab(self):    self.notebook.select(self.similar_frame)
    def show_duplicates_tab(self): self.notebook.select(self.duplicates_frame)
    def show_storage(self):        self.notebook.select(self.storage_frame);     self.update_dashboard_stats()
    def show_analytics(self):      self.notebook.select(self.analytics_frame);   self.update_dashboard_stats()
    def show_trash_tab(self):      self.notebook.select(self.trash_frame);       self.refresh_trash()
    def auto_organize(self):       self.organize_files()

    # ── ACTIONS (wire up your logic) ─────────────────────────────────────────

    def start_new_session(self):
        if messagebox.askyesno("New Session",
                               "Clear all current files? Recycle Bin is preserved."):
            self.clear_previous_files()
            self.refresh_files(); self.refresh_trash()
            self.update_dashboard_stats()
            self.log("New session started")

    def scan_directory(self):
        d = filedialog.askdirectory(title="Select Directory to Scan")
        if d:
            self.log(f"Scanning: {d}")

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select Files")
        if files:
            self.log(f"Adding {len(files)} file(s)")

    def find_duplicates(self):
        self.log("Searching for duplicates …")
        self.update_dashboard_stats()

    def find_similar(self):
        self.log("Analysing similar files …")

    def organize_files(self):
        self.log("AI organisation started …")
        self.update_dashboard_stats()

    def delete_selected(self):   pass
    def delete_duplicates(self): pass
    def keep_latest(self):       pass

    def restore_from_trash(self):
        if not self.trash_tree.selection():
            messagebox.showwarning("No Selection", "Please select a file to restore.")
            return

    def empty_trash(self):
        if messagebox.askyesno("Empty Recycle Bin",
                               "Permanently delete all files in Recycle Bin?",
                               icon="warning"):
            ok, msg = self.trash.empty_trash()
            if ok:
                self.log("Recycle Bin emptied")
                self.refresh_trash(); self.update_dashboard_stats()
            else:
                self.log(f"Error: {msg}")

    def show_about(self):
        messagebox.showinfo("About", (
            "AI Smart FILE MANAGER  v2.0\n\n"
            "• Smart File Organisation\n"
            "• Duplicate Detection\n"
            "• Content Similarity Analysis\n"
            "• Recycle Bin Management\n"
            "• Real-time Analytics"
        ))