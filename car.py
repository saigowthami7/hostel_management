import tkinter as tk
from tkinter import ttk, messagebox
import pymysql


BG        = "#0d1117"
PANEL     = "#161b22"
ACCENT    = "#1f6feb"
GREEN     = "#238636"
RED       = "#da3633"
GREY      = "#4a5568"
TEXT      = "#e6edf3"
SUBTEXT   = "#8b949e"
ENTRY_BG  = "#21262d"
BORDER    = "#30363d"

FONT_MAIN  = ("Segoe UI", 11)
FONT_BOLD  = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_CARDV = ("Segoe UI", 28, "bold")
FONT_CARDL = ("Segoe UI", 9,  "bold")


def make_button(parent, text, command, color=ACCENT, width=22):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg="white", activebackground=color,
        activeforeground="white", relief="flat",
        font=FONT_BOLD, cursor="hand2",
        bd=0, padx=10, pady=8, width=width
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def _lighten(hex_color):
    """Return a slightly lighter version of a hex color."""
    r = min(255, int(hex_color[1:3], 16) + 30)
    g = min(255, int(hex_color[3:5], 16) + 30)
    b = min(255, int(hex_color[5:7], 16) + 30)
    return f"#{r:02x}{g:02x}{b:02x}"

def make_entry(parent, width=30):
    e = tk.Entry(
        parent, width=width, bg=ENTRY_BG, fg=TEXT,
        insertbackground=TEXT, relief="flat",
        font=FONT_MAIN, highlightthickness=1,
        highlightcolor=ACCENT, highlightbackground=BORDER
    )
    return e

def section_label(parent, text):
    tk.Label(parent, text=text, bg=PANEL, fg=SUBTEXT,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(10, 2))



class CarRental:  

    def __init__(self, root):
        self.root = root
        self.root.title("Car Rental Management")
        self.root.geometry("1200x700")
        self.root.minsize(950, 580)
        self.root.config(bg=BG)
        self._build_header()
        self._build_body()
        self.load_data()

    
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=PANEL, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🚗  Car Rental Management",
                 bg=PANEL, fg=TEXT, font=FONT_TITLE).pack(side="left", padx=24)

        cards = tk.Frame(hdr, bg=PANEL)
        cards.pack(side="right", padx=20)

        self.totalVal    = self._stat_chip(cards, "Total Cars", ACCENT, 0)
        self.availVal    = self._stat_chip(cards, "Available",  GREEN,  1)
        self.reservedVal = self._stat_chip(cards, "Reserved",   RED,    2)

    def _stat_chip(self, parent, label, color, col):
        chip = tk.Frame(parent, bg=color, padx=18, pady=6)
        chip.grid(row=0, column=col, padx=6, pady=10)
        val = tk.Label(chip, text="0", bg=color, fg="white", font=FONT_CARDV)
        val.pack()
        tk.Label(chip, text=label, bg=color, fg="white", font=FONT_CARDL).pack()
        return val

    
    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=14)
        self._build_sidebar(body)
        self._build_table_panel(body)

    
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=PANEL, width=210)
        sb.pack(side="left", fill="y", padx=(0, 12))
        sb.pack_propagate(False)

        tk.Label(sb, text="ACTIONS", bg=PANEL, fg=SUBTEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 12))

        btns = [
            ("🔑  Reserve Car", self.reserve_window, ACCENT),
            ("↩  Return Car",  self.return_window,  GREEN),
            ("🔄  Refresh",     self.load_data,      GREY),
            ("✖  Exit",        self.root.destroy,   RED),
        ]
        for txt, cmd, col in btns:
            b = make_button(sb, txt, cmd, color=col, width=20)
            b.pack(pady=6, padx=14, fill="x")

        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=16, pady=14)
        tk.Label(sb, text="TIPS", bg=PANEL, fg=SUBTEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(0, 6))
        tips = [
            "• Click a row, then Reserve",
            "• or Return to pre-fill",
            "• Green row = Available",
            "• Red row = Reserved",
            "• Click a column to sort",
        ]
        for t in tips:
            tk.Label(sb, text=t, bg=PANEL, fg=SUBTEXT,
                     font=("Segoe UI", 9), justify="left").pack(anchor="w", padx=20, pady=1)

   
    def _build_table_panel(self, parent):
        panel = tk.Frame(parent, bg=PANEL)
        panel.pack(side="right", fill="both", expand=True)

        
        search_row = tk.Frame(panel, bg=PANEL)
        search_row.pack(fill="x", padx=14, pady=(14, 6))

        tk.Label(search_row, text="🔍", bg=PANEL, fg=SUBTEXT,
                 font=("Segoe UI", 13)).pack(side="left")

        self.searchEntry = make_entry(search_row, width=34)
        self.searchEntry.pack(side="left", padx=8, ipady=5)
        self.searchEntry.bind("<Return>", lambda e: self.search_car())

        make_button(search_row, "Search", self.search_car, width=10).pack(side="left", padx=4)
        make_button(search_row, "Clear",  self._clear_search, color=GREY, width=8).pack(side="left", padx=2)

       
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Car.Treeview",
                         background=ENTRY_BG, foreground=TEXT,
                         fieldbackground=ENTRY_BG, rowheight=32,
                         font=FONT_MAIN, borderwidth=0)
        style.configure("Car.Treeview.Heading",
                         background="#1c2128", foreground=SUBTEXT,
                         font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Car.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        tree_frame = tk.Frame(panel, bg=PANEL)
        tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        cols = ("reg", "car", "rent", "status")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", style="Car.Treeview")

        heads = [("reg", "Reg No", 120), ("car", "Car Name", 280),
                 ("rent", "Rent / Day (₹)", 150), ("status", "Status", 120)]
        for col, lbl, w in heads:
            self.tree.heading(col, text=lbl, command=lambda c=col: self._sort_col(c))
            self.tree.column(col, width=w, anchor="center")

        self.tree.tag_configure("avail",    background="#0d2818", foreground="#3fb950")
        self.tree.tag_configure("reserved", background="#2d1117", foreground="#f85149")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.statusVar = tk.StringVar(value="Ready")
        tk.Label(panel, textvariable=self.statusVar, bg=PANEL, fg=SUBTEXT,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=14, pady=(0, 8))

    
    def _sort_col(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children()]
        data.sort()
        for idx, (_, k) in enumerate(data):
            self.tree.move(k, "", idx)

    def _clear_search(self):
        self.searchEntry.delete(0, tk.END)
        self.load_data()

    
    def db_connect(self):
        self.con = pymysql.connect(
            host="localhost", user="root",
            password="#$aigow12345", database="car"
        )
        self.cur = self.con.cursor()

    def load_data(self):
        try:
            self.db_connect()
            self.tree.delete(*self.tree.get_children())
            self.cur.execute("SELECT * FROM car")
            rows = self.cur.fetchall()
            total = len(rows)
            available = reserved = 0
            for row in rows:
                tag = "avail" if row[3] == "Avail" else "reserved"
                self.tree.insert("", tk.END, values=row, tags=(tag,))
                if row[3] == "Avail":
                    available += 1
                else:
                    reserved += 1
            self.totalVal.config(text=str(total))
            self.availVal.config(text=str(available))
            self.reservedVal.config(text=str(reserved))
            self.statusVar.set(
                f"Loaded {total} cars  ·  {available} available  ·  {reserved} reserved"
            )
            self.cur.close()
            self.con.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))

    def search_car(self):
        keyword = self.searchEntry.get().strip()
        if not keyword:
            self.load_data()
            return
        try:
            self.db_connect()
            self.cur.execute(
                "SELECT * FROM car WHERE car LIKE %s OR regNo LIKE %s",
                (f"%{keyword}%", f"%{keyword}%")
            )
            rows = self.cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                tag = "avail" if row[3] == "Avail" else "reserved"
                self.tree.insert("", tk.END, values=row, tags=(tag,))
            self.statusVar.set(f"Found {len(rows)} result(s) for '{keyword}'")
            self.cur.close()
            self.con.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))

    
    def reserve_window(self):
        win = self._popup("Reserve a Car", 400, 310)

        tk.Label(win, text="🔑  Reserve Car", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(18, 10))

        section_label(win, "REGISTRATION NUMBER")
        regEntry = make_entry(win, 32)
        regEntry.pack(padx=18, ipady=6, pady=(0, 4), fill="x")

        section_label(win, "NUMBER OF DAYS")
        dayEntry = make_entry(win, 32)
        dayEntry.pack(padx=18, ipady=6, pady=(0, 4), fill="x")

        sel = self.tree.selection()
        if sel:
            regEntry.insert(0, self.tree.item(sel[0])["values"][0])

        def reserve_now():
            try:
                reg  = int(regEntry.get())
                days = int(dayEntry.get())
                if days <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter valid positive numbers.", parent=win)
                return
            try:
                self.db_connect()
                self.cur.execute(
                    "SELECT rent, status FROM car WHERE regNo=%s", (reg,)
                )
                row = self.cur.fetchone()
                if row:
                    if row[1] == "Avail":
                        amount = row[0] * days
                        self.cur.execute(
                            "UPDATE car SET status='Reserved' WHERE regNo=%s", (reg,)
                        )
                        self.con.commit()
                        messagebox.showinfo(
                            "Reserved ✅",
                            f"Car #{reg} reserved for {days} day(s).\n\nTotal Amount: ₹{amount:,}",
                            parent=win
                        )
                        self.load_data()
                        win.destroy()
                    else:
                        messagebox.showerror("Unavailable", "This car is already reserved.", parent=win)
                else:
                    messagebox.showerror("Not Found", f"No car with Reg No {reg}.", parent=win)
                self.cur.close()
                self.con.close()
            except Exception as ex:
                messagebox.showerror("DB Error", str(ex), parent=win)

        make_button(win, "✔  Confirm Reservation", reserve_now, width=28).pack(pady=16, padx=18, fill="x")

   
    def return_window(self):
        win = self._popup("Return a Car", 400, 240)

        tk.Label(win, text="↩  Return Car", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(18, 10))

        section_label(win, "REGISTRATION NUMBER")
        regEntry = make_entry(win, 32)
        regEntry.pack(padx=18, ipady=6, pady=(0, 4), fill="x")

        sel = self.tree.selection()
        if sel:
            regEntry.insert(0, self.tree.item(sel[0])["values"][0])

        def return_now():
            try:
                reg = int(regEntry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid registration number.", parent=win)
                return
            try:
                self.db_connect()
                self.cur.execute(
                    "UPDATE car SET status='Avail' WHERE regNo=%s", (reg,)
                )
                self.con.commit()
                messagebox.showinfo("Returned ✅", f"Car #{reg} returned successfully.", parent=win)
                self.load_data()
                win.destroy()
                self.cur.close()
                self.con.close()
            except Exception as ex:
                messagebox.showerror("DB Error", str(ex), parent=win)

        make_button(win, "✔  Confirm Return", return_now, color=GREEN, width=26).pack(pady=16, padx=18, fill="x")

    
    def _popup(self, title, w, h):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.config(bg=PANEL)
        win.resizable(False, False)
        win.grab_set()
        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - w) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{rx}+{ry}")
        return win
root = tk.Tk()
root.resizable(True, True)
obj = CarRental(root)
root.mainloop()