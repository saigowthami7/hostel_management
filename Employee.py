import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
BG        = "#0f1923"   # Deep navy background
SURFACE   = "#16232f"   # Card/panel surface
SURFACE2  = "#1e2f3e"   # Elevated element
SURFACE3  = "#243647"   # Highest elevation / hover
CYAN      = "#00c8e0"   # Primary accent — electric cyan
CYAN_DIM  = "#007f8c"   # Dimmer cyan
CYAN_DARK = "#003d45"   # Very dark cyan (pressed)
GREEN     = "#00b37a"   # Success
GREEN_DK  = "#005c3d"
RED       = "#e05252"   # Danger
RED_DK    = "#6b1c1c"
AMBER     = "#e0a832"   # Warning / edit
AMBER_DK  = "#6b4d0e"
VIOLET    = "#8a6fe8"   # Secondary accent
VIOLET_DK = "#3d2e7a"
TEXT      = "#d8eaf5"   # Primary text
SUBTEXT   = "#5a7a8e"   # Muted label text
BORDER    = "#253545"   # Subtle border
ENTRY_BG  = "#111e29"   # Input background
SEL_BG    = "#1a3a4a"   # Row selection

FONT_HERO  = ("Segoe UI", 22, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 9, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_MONO  = ("Consolas", 10)

#  HELPERS
def _hover_color(hex_color, amount=28):
    r = min(255, int(hex_color[1:3], 16) + amount)
    g = min(255, int(hex_color[3:5], 16) + amount)
    b = min(255, int(hex_color[5:7], 16) + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def flat_btn(parent, text, cmd, bg=CYAN, fg=BG, w=15):
    """Flat hover button."""
    hov = _hover_color(bg)
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
        relief="flat", font=FONT_TITLE, cursor="hand2",
        bd=0, padx=10, pady=8, width=w
    )
    b.bind("<Enter>", lambda e: b.config(bg=hov))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def styled_entry(parent, textvariable=None, width=22, show=None):
    kw = dict(
        bg=ENTRY_BG, fg=TEXT, insertbackground=CYAN,
        relief="flat", font=FONT_BODY, width=width,
        highlightthickness=1, highlightcolor=CYAN,
        highlightbackground=BORDER
    )
    if textvariable:
        kw["textvariable"] = textvariable
    if show:
        kw["show"] = show
    return tk.Entry(parent, **kw)


def form_row(parent, label_text, bg=SURFACE):
    """Returns a frame with a label already packed, ready for a widget."""
    row = tk.Frame(parent, bg=bg)
    row.pack(fill="x", padx=20, pady=5)
    tk.Label(row, text=label_text, bg=bg, fg=SUBTEXT,
             font=FONT_LABEL, width=14, anchor="w").pack(side="left")
    return row


def divider(parent, bg=SURFACE):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=16, pady=6)


def section_tag(parent, text, color=CYAN, bg=SURFACE):
    f = tk.Frame(parent, bg=bg)
    f.pack(fill="x", padx=16, pady=(10, 2))
    tk.Frame(f, bg=color, width=4).pack(side="left", fill="y")
    tk.Label(f, text=f"  {text}", bg=bg, fg=color,
             font=FONT_LABEL, padx=4, pady=4).pack(side="left")
#  MAIN APPLICATION
class Employee:

    def __init__(self, root):
        self.root = root
        self.root.title("◈  Ignitiz Solutions  —  Employee Management")
        self.root.geometry("1380x760")
        self.root.minsize(1100, 640)
        self.root.config(bg=BG)

        self._apply_styles()

        # Tkinter vars
        self.eid      = tk.StringVar()
        self.ename    = tk.StringVar()
        self.edesig   = tk.StringVar()
        self.esal     = tk.StringVar()
        self.egender  = tk.StringVar()
        self.searchBy = tk.StringVar()
        self.searchTx = tk.StringVar()

        self._build_topbar()
        self._build_body()
        self.get_data()

    #TTK STYLES
    def _apply_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("Emp.Treeview",
                     background=ENTRY_BG, foreground=TEXT,
                     fieldbackground=ENTRY_BG, rowheight=34,
                     font=FONT_BODY, borderwidth=0)
        s.configure("Emp.Treeview.Heading",
                     background=SURFACE3, foreground=CYAN,
                     font=FONT_LABEL, relief="flat", padding=(8, 7))
        s.map("Emp.Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", CYAN)])

        s.configure("Emp.Vertical.TScrollbar",
                     background=SURFACE2, troughcolor=BG,
                     arrowcolor=CYAN, borderwidth=0)
        s.configure("Emp.Horizontal.TScrollbar",
                     background=SURFACE2, troughcolor=BG,
                     arrowcolor=CYAN, borderwidth=0)

        s.configure("TCombobox",
                     fieldbackground=ENTRY_BG, background=ENTRY_BG,
                     foreground=TEXT, arrowcolor=CYAN,
                     selectbackground=SURFACE3, selectforeground=CYAN,
                     borderwidth=1, relief="flat")
        s.map("TCombobox",
              fieldbackground=[("readonly", ENTRY_BG)],
              foreground=[("readonly", TEXT)])

        self.root.option_add("*TCombobox*Listbox.background", SURFACE2)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", CYAN_DARK)
        self.root.option_add("*TCombobox*Listbox.font", FONT_BODY)

    #TOP BAR
    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=68)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Cyan accent line at bottom of topbar
        tk.Frame(self.root, bg=CYAN, height=2).pack(fill="x")

        # Brand
        brand = tk.Frame(bar, bg=SURFACE)
        brand.pack(side="left", padx=22, pady=10)
        tk.Label(brand, text="◈ IGNITIZ SOLUTIONS", bg=SURFACE,
                 fg=CYAN, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(brand, text="Employee Management System", bg=SURFACE,
                 fg=SUBTEXT, font=FONT_SMALL).pack(anchor="w")

        tk.Frame(bar, bg=BORDER, width=1).pack(side="left", fill="y", padx=(0, 22), pady=14)

        # Stat chips — right side
        chips_frame = tk.Frame(bar, bg=SURFACE)
        chips_frame.pack(side="right", padx=22)

        self._total_chip = self._make_stat_chip(chips_frame, "Total Employees", CYAN)
        tk.Frame(chips_frame, bg=BORDER, width=1).pack(side="left", fill="y", padx=12, pady=14)
        self._male_chip  = self._make_stat_chip(chips_frame, "Male", VIOLET)
        tk.Frame(chips_frame, bg=BORDER, width=1).pack(side="left", fill="y", padx=12, pady=14)
        self._fem_chip   = self._make_stat_chip(chips_frame, "Female", GREEN)

    def _make_stat_chip(self, parent, label, color):
        f = tk.Frame(parent, bg=SURFACE)
        f.pack(side="left", padx=6)
        val = tk.Label(f, text="—", bg=SURFACE, fg=color,
                       font=("Consolas", 18, "bold"))
        val.pack()
        tk.Label(f, text=label, bg=SURFACE, fg=SUBTEXT, font=FONT_SMALL).pack()
        return val

    #BODY
    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=10)
        self._build_left_panel(body)
        self._build_right_panel(body)

    # LEFT PANEL (form)
    def _build_left_panel(self, parent):
        panel = tk.Frame(parent, bg=SURFACE, width=300)
        panel.pack(side="left", fill="y", padx=(0, 12))
        panel.pack_propagate(False)

        # Cyan top bar
        tk.Frame(panel, bg=CYAN, height=3).pack(fill="x")

        # Header
        hdr = tk.Frame(panel, bg=SURFACE)
        hdr.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(hdr, text="Employee Details", bg=SURFACE,
                 fg=TEXT, font=FONT_HERO).pack(anchor="w")
        tk.Label(hdr, text="Add · Edit · Remove", bg=SURFACE,
                 fg=SUBTEXT, font=FONT_SMALL).pack(anchor="w")

        divider(panel)
        section_tag(panel, "PERSONAL INFO", CYAN)

        #Form fields
        fields = [
            ("Employee ID",   self.eid,    False),
            ("Full Name",     self.ename,  False),
            ("Designation",   self.edesig, False),
            ("Salary (₹)",    self.esal,   False),
        ]
        for label, var, is_pass in fields:
            row = form_row(panel, label)
            e = styled_entry(row, textvariable=var, width=18)
            if is_pass:
                e.config(show="*")
            e.pack(side="left", ipady=5)

        # Gender dropdown
        row = form_row(panel, "Gender")
        gender_cb = ttk.Combobox(row, textvariable=self.egender,
                                  values=("Male", "Female", "Other"),
                                  state="readonly", font=FONT_BODY, width=16)
        gender_cb.pack(side="left", ipady=3)

        # Address
        section_tag(panel, "ADDRESS", CYAN)
        addr_wrap = tk.Frame(panel, bg=BORDER, padx=1, pady=1)
        addr_wrap.pack(fill="x", padx=20, pady=4)
        self.addrIn = tk.Text(
            addr_wrap, width=26, height=4,
            font=FONT_BODY, bg=ENTRY_BG, fg=TEXT,
            insertbackground=CYAN, relief="flat",
            highlightthickness=0, padx=6, pady=4
        )
        self.addrIn.pack()

        divider(panel)

        # ── Action Buttons ──
        section_tag(panel, "ACTIONS", CYAN)
        btn_grid = tk.Frame(panel, bg=SURFACE)
        btn_grid.pack(fill="x", padx=16, pady=(6, 10))

        btns = [
            ("＋  Add",    self.add,    GREEN,  BG,   0, 0),
            ("✎  Update", self.update, AMBER,  BG,   0, 1),
            ("✕  Delete", self.delete, RED,    TEXT, 1, 0),
            ("⊘  Clear",  self.clear,  SURFACE3, SUBTEXT, 1, 1),
        ]
        for txt, cmd, bg, fg, r, c in btns:
            hov = _hover_color(bg)
            b = tk.Button(btn_grid, text=txt, command=cmd,
                          bg=bg, fg=fg,
                          activebackground=hov, activeforeground=fg,
                          relief="flat", font=FONT_TITLE,
                          cursor="hand2", bd=0,
                          padx=8, pady=9, width=11)
            b.grid(row=r, column=c, padx=5, pady=4, sticky="ew")
            b.bind("<Enter>", lambda e, btn=b, h=hov: btn.config(bg=h))
            b.bind("<Leave>", lambda e, btn=b, orig=bg: btn.config(bg=orig))

        btn_grid.grid_columnconfigure(0, weight=1)
        btn_grid.grid_columnconfigure(1, weight=1)

    #RIGHT PANEL (table)
    def _build_right_panel(self, parent):
        panel = tk.Frame(parent, bg=SURFACE)
        panel.pack(side="right", fill="both", expand=True)
        tk.Frame(panel, bg=CYAN, height=3).pack(fill="x")

        # ── Search bar ──
        search_bar = tk.Frame(panel, bg=SURFACE)
        search_bar.pack(fill="x", padx=14, pady=12)

        tk.Label(search_bar, text="Search by:", bg=SURFACE,
                 fg=SUBTEXT, font=FONT_LABEL).pack(side="left", padx=(0, 6))

        by_cb = ttk.Combobox(search_bar, textvariable=self.searchBy,
                              values=("ID", "Name"),
                              state="readonly", font=FONT_BODY, width=9)
        by_cb.pack(side="left", ipady=4, padx=(0, 8))

        # Search input wrapped in border
        sw = tk.Frame(search_bar, bg=BORDER, padx=1, pady=1)
        sw.pack(side="left")
        tk.Label(sw, text=" 🔍", bg=ENTRY_BG, fg=SUBTEXT, font=FONT_BODY).pack(side="left")
        se = styled_entry(sw, textvariable=self.searchTx, width=22)
        se.pack(side="left", ipady=5)
        se.bind("<Return>", lambda e: self.search())

        flat_btn(search_bar, "Search",      self.search,   CYAN,     BG,   9).pack(side="left", padx=8)
        flat_btn(search_bar, "Show All",    self.get_data, SURFACE3, TEXT, 9).pack(side="left", padx=0)

        # Status label
        self._status_var = tk.StringVar(value="")
        tk.Label(panel, textvariable=self._status_var, bg=SURFACE,
                 fg=SUBTEXT, font=FONT_SMALL, anchor="w").pack(fill="x", padx=16)

        #Treeview
        tree_wrap = tk.Frame(panel, bg=SURFACE)
        tree_wrap.pack(fill="both", expand=True, padx=14, pady=(4, 10))

        cols = ("id", "name", "desig", "sal", "gender", "addr")
        self.table = ttk.Treeview(
            tree_wrap, columns=cols,
            show="headings", style="Emp.Treeview",
            selectmode="browse"
        )
        heads = [
            ("id",     "Emp ID",      90),
            ("name",   "Full Name",   190),
            ("desig",  "Designation", 175),
            ("sal",    "Salary (₹)",  130),
            ("gender", "Gender",      100),
            ("addr",   "Address",     260),
        ]
        for col, hdr, w in heads:
            self.table.heading(col, text=hdr,
                               command=lambda c=col: self._sort(c))
            self.table.column(col, width=w, anchor="center")

        # Alternating row colours
        self.table.tag_configure("odd",  background="#131e28")
        self.table.tag_configure("even", background=ENTRY_BG)

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",
                             command=self.table.yview,
                             style="Emp.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal",
                             command=self.table.xview,
                             style="Emp.Horizontal.TScrollbar")
        self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.table.pack(fill="both", expand=True)

        self.table.bind("<ButtonRelease-1>", self.get_cursor)

    #DB
    def db_connect(self):
        return pymysql.connect(
            host="localhost", user="root",
            password="#$aigow12345", database="emp"
        )

    #CRUD
    def add(self):
        try:
            con = self.db_connect(); cur = con.cursor()
            cur.execute(
                "INSERT INTO emp VALUES(%s,%s,%s,%s,%s,%s)",
                (self.eid.get(), self.ename.get(), self.edesig.get(),
                 self.esal.get(), self.egender.get(),
                 self.addrIn.get("1.0", tk.END).strip())
            )
            con.commit(); con.close()
            self.get_data(); self.clear()
            messagebox.showinfo("Success", "✅  Employee added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update(self):
        try:
            con = self.db_connect(); cur = con.cursor()
            cur.execute(
                "UPDATE emp SET name=%s,desig=%s,sal=%s,gender=%s,address=%s WHERE id=%s",
                (self.ename.get(), self.edesig.get(), self.esal.get(),
                 self.egender.get(), self.addrIn.get("1.0", tk.END).strip(),
                 self.eid.get())
            )
            con.commit(); con.close()
            self.get_data(); self.clear()
            messagebox.showinfo("Updated", "✅  Record updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        if not messagebox.askyesno("Confirm Delete",
                                    f"Delete employee ID {self.eid.get()}?"):
            return
        try:
            con = self.db_connect(); cur = con.cursor()
            cur.execute("DELETE FROM emp WHERE id=%s", (self.eid.get(),))
            con.commit(); con.close()
            self.get_data(); self.clear()
            messagebox.showinfo("Deleted", "🗑  Record deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear(self):
        self.eid.set("")
        self.ename.set("")
        self.edesig.set("")
        self.esal.set("")
        self.egender.set("")
        self.addrIn.delete("1.0", tk.END)

    def get_data(self):
        try:
            con = self.db_connect(); cur = con.cursor()
            cur.execute("SELECT * FROM emp")
            rows = cur.fetchall(); con.close()
            self.table.delete(*self.table.get_children())
            male = female = 0
            for i, row in enumerate(rows):
                tag = "odd" if i % 2 else "even"
                self.table.insert("", tk.END, values=row, tags=(tag,))
                g = str(row[4]).lower()
                if g == "male":   male   += 1
                elif g == "female": female += 1
            self._total_chip.config(text=str(len(rows)))
            self._male_chip.config(text=str(male))
            self._fem_chip.config(text=str(female))
            self._status_var.set(f"  {len(rows)} employee(s) loaded")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_cursor(self, ev):
        row_id = self.table.focus()
        data   = self.table.item(row_id)["values"]
        if data:
            self.eid.set(data[0])
            self.ename.set(data[1])
            self.edesig.set(data[2])
            self.esal.set(data[3])
            self.egender.set(data[4])
            self.addrIn.delete("1.0", tk.END)
            self.addrIn.insert(tk.END, data[5])

    def search(self):
        try:
            con = self.db_connect(); cur = con.cursor()
            by  = self.searchBy.get()
            txt = self.searchTx.get().strip()
            if not by or not txt:
                messagebox.showwarning("Search", "Choose a field and enter search text.")
                return
            if by == "ID":
                cur.execute("SELECT * FROM emp WHERE id=%s", (txt,))
            else:
                cur.execute("SELECT * FROM emp WHERE name LIKE %s", (f"%{txt}%",))
            rows = cur.fetchall(); con.close()
            self.table.delete(*self.table.get_children())
            if rows:
                for i, row in enumerate(rows):
                    tag = "odd" if i % 2 else "even"
                    self.table.insert("", tk.END, values=row, tags=(tag,))
                self._status_var.set(f"  {len(rows)} result(s) found")
            else:
                messagebox.showinfo("No Results", "No matching records found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _sort(self, col):
        data = [(self.table.set(k, col), k) for k in self.table.get_children()]
        try:
            data.sort(key=lambda t: float(t[0].replace("₹", "").replace(",", "")))
        except ValueError:
            data.sort()
        for idx, (_, k) in enumerate(data):
            self.table.move(k, "", idx)
            tag = "odd" if idx % 2 else "even"
            self.table.item(k, tags=(tag,)) ##tag
#  ENTRY POINT
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)
    Employee(root)
    root.mainloop()