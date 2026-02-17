"""
Python JSON News Generator – GUI-Tool für Website-Beiträge
==========================================================
Zweck:
Dieses Programm dient zur strukturierten Erstellung von JSON-Beiträgen
für meine persönliche Website. Es ersetzt manuelles Schreiben von JSON
und minimiert Formatierungs- und Escape-Fehler.

Funktionsweise:
- GUI-basierte Eingabe aller relevanten Felder (topic, subtopic, date, title, content, images).
- Automatische Generierung einer eindeutigen ID (Datum + Topic + Subtopic + Uhrzeit).
- Markdown-Hilfsfunktionen für schnellen Text-Workflow.
- Bildverwaltung mit festem Asset-Prefix.
- JSON-Ausgabe korrekt escaped und direkt per Klick kopierbar.

Ziel:
Schneller, konsistenter und fehlerfreier Workflow zur Pflege
der dynamischen News-Sektion meiner Website.



Python JSON News Generator – GUI Tool for Website Posts
========================================================

Purpose:
This application provides a structured way to generate JSON-based
news posts for my personal website. It replaces manual JSON editing
and reduces formatting and escaping errors.

How it works:
- GUI-based input for all required fields (topic, subtopic, date, title, content, images).
- Automatic generation of a unique ID (date + topic + subtopic + time).
- Markdown helper functions for faster content formatting.
- Image management with a fixed asset prefix.
- Properly escaped JSON output that can be copied with a single click.

Goal:
A fast, consistent, and reliable workflow for maintaining
the dynamic news section of my website.
"""





import json
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime, date


ASSET_PREFIX = "../assets/img/"

TOPICS = {
    "": [""],  # leere Auswahl erlaubt
    "botanik": ["", "raspberry", "ribisl", "fig"],
    "making": ["", "3dprint"],
    "code": ["", "html", "python", "cpp"],
    "words": ["", "communication", "history", "linguistics", "literature", "philosophy", "poetry"],
    "electronics": ["", "mesh"],
}


def sanitize_token(s: str) -> str:
    """
    - trim
    - spaces -> underscores
    - collapse multiple underscores
    - remove leading/trailing underscores
    """
    s = (s or "").strip().replace(" ", "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


class JsonPostGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Website JSON Beitrag Generator")
        self.geometry("1100x720")
        self.minsize(980, 640)

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(0, weight=1)

        left = ttk.Frame(root)
        right = ttk.Frame(root)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right.grid(row=0, column=1, sticky="nsew")

        for i in range(12):
            left.rowconfigure(i, weight=0)
        left.rowconfigure(7, weight=1)   # content grows

        # --- Vars ---
        self.var_id = tk.StringVar()  # auto-generated, read-only in UI
        self.var_topic = tk.StringVar(value="")
        self.var_subtopic = tk.StringVar(value="")
        self.var_date = tk.StringVar(value="")
        self.var_title = tk.StringVar(value="")
        self.var_format = tk.StringVar(value="markdown")

        # --- ID (readonly) ---
        row = 0
        ttk.Label(left, text="id (auto)").grid(row=row, column=0, sticky="w", pady=(6, 2))
        e_id = ttk.Entry(left, textvariable=self.var_id, state="readonly")
        e_id.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        row += 1

        # --- topic dropdown ---
        ttk.Label(left, text="topic").grid(row=row, column=0, sticky="w", pady=(6, 2))
        self.cmb_topic = ttk.Combobox(left, textvariable=self.var_topic, state="readonly",
                                      values=list(TOPICS.keys()))
        self.cmb_topic.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        self.cmb_topic.bind("<<ComboboxSelected>>", self._on_topic_changed)
        row += 1

        # --- subtopic dropdown (depends on topic) ---
        ttk.Label(left, text="subtopic").grid(row=row, column=0, sticky="w", pady=(6, 2))
        self.cmb_subtopic = ttk.Combobox(left, textvariable=self.var_subtopic, state="readonly",
                                         values=TOPICS.get(self.var_topic.get(), [""]))
        self.cmb_subtopic.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        row += 1

        # --- date + heute ---
        ttk.Label(left, text="date").grid(row=row, column=0, sticky="w", pady=(6, 2))
        date_row = ttk.Frame(left)
        date_row.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        date_row.columnconfigure(0, weight=1)

        ttk.Entry(date_row, textvariable=self.var_date).grid(row=0, column=0, sticky="ew")
        ttk.Button(date_row, text="heute", command=self._fill_today).grid(row=0, column=1, padx=(8, 0))
        row += 1

        # --- title ---
        row = self._labeled_entry(left, row, "title", self.var_title)

        # --- format ---
        ttk.Label(left, text="format").grid(row=row, column=0, sticky="w", pady=(6, 2))
        fmt = ttk.Combobox(left, textvariable=self.var_format, values=["markdown", "html", "text"], state="readonly")
        fmt.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        row += 1

        # --- content + formatting buttons ---
        ttk.Label(left, text="content").grid(row=row, column=0, sticky="nw", pady=(6, 2))
        content_area = ttk.Frame(left)
        content_area.grid(row=row, column=1, sticky="nsew", pady=(6, 2))
        content_area.rowconfigure(1, weight=1)
        content_area.columnconfigure(0, weight=1)

        btns = ttk.Frame(content_area)
        btns.grid(row=0, column=0, sticky="ew")
        ttk.Button(btns, text="**fett**", command=lambda: self._wrap_selection("**", "**")).pack(side="left")
        ttk.Button(btns, text="*kursiv*", command=lambda: self._wrap_selection("*", "*")).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="~Zitat~", command=lambda: self._wrap_selection("~", "~")).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="Liste (-)", command=self._make_list).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="Leerzeile", command=lambda: self._insert_at_cursor("\n\n")).pack(side="left", padx=(6, 0))

        self.txt_content = ScrolledText(content_area, height=14, wrap="word")
        self.txt_content.grid(row=1, column=0, sticky="nsew")

        row += 1

        # --- Images ---
        ttk.Label(left, text="images").grid(row=row, column=0, sticky="nw", pady=(6, 2))
        img_area = ttk.Frame(left)
        img_area.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        img_area.columnconfigure(0, weight=1)

        hint = ttk.Label(img_area, text=f"Pfad-Prefix ist fix: {ASSET_PREFIX}…", foreground="#666")
        hint.grid(row=0, column=0, sticky="w", pady=(0, 6))

        add_row = ttk.Frame(img_area)
        add_row.grid(row=1, column=0, sticky="ew")
        add_row.columnconfigure(1, weight=1)

        ttk.Label(add_row, text="Dateiname").grid(row=0, column=0, sticky="w")
        self.var_img_file = tk.StringVar()
        ttk.Entry(add_row, textvariable=self.var_img_file).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ttk.Button(add_row, text="Add", command=self._add_image).grid(row=0, column=2)

        add_row2 = ttk.Frame(img_area)
        add_row2.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        add_row2.columnconfigure(1, weight=1)
        ttk.Label(add_row2, text="alt").grid(row=0, column=0, sticky="w")
        self.var_img_alt = tk.StringVar()
        ttk.Entry(add_row2, textvariable=self.var_img_alt).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        list_row = ttk.Frame(img_area)
        list_row.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        list_row.columnconfigure(0, weight=1)

        self.lst_images = tk.Listbox(list_row, height=5)
        self.lst_images.grid(row=0, column=0, sticky="nsew")
        sc = ttk.Scrollbar(list_row, orient="vertical", command=self.lst_images.yview)
        sc.grid(row=0, column=1, sticky="ns")
        self.lst_images.configure(yscrollcommand=sc.set)

        rm_row = ttk.Frame(img_area)
        rm_row.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(rm_row, text="Remove selected", command=self._remove_selected_image).pack(side="left")

        row += 1

        # --- Generate + status ---
        action_row = ttk.Frame(left)
        action_row.grid(row=row, column=1, sticky="ew", pady=(10, 0))
        ttk.Button(action_row, text="Generate", command=self._generate).pack(side="left")

        self.lbl_status = ttk.Label(action_row, text="", foreground="#2a7")
        self.lbl_status.pack(side="left", padx=(10, 0))

        # ---------- Right: Output ----------
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Output (click to copy)").grid(row=0, column=0, sticky="w")
        self.txt_output = ScrolledText(right, wrap="none")
        self.txt_output.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.txt_output.bind("<Button-1>", self._copy_output_on_click)
        self.txt_output.bind("<FocusIn>", self._copy_output_on_click)

        ttk.Label(
            right,
            text="Tipp: content wird im JSON korrekt escaped (\\n, \\\" usw.).",
            foreground="#666",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

        # --- Reactive ID updates ---
        self.var_date.trace_add("write", lambda *_: self._update_id())
        self.var_topic.trace_add("write", lambda *_: self._update_id())
        self.var_subtopic.trace_add("write", lambda *_: self._update_id())

        # Initial id
        self._update_id()

    def _labeled_entry(self, parent, row, label, var):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(6, 2))
        e = ttk.Entry(parent, textvariable=var)
        e.grid(row=row, column=1, sticky="ew", pady=(6, 2))
        parent.columnconfigure(1, weight=1)
        return row + 1

    # ---------- Topic/Subtopic logic ----------
    def _on_topic_changed(self, _evt=None):
        topic = self.var_topic.get()
        allowed = TOPICS.get(topic, [""])
        self.cmb_subtopic.configure(values=allowed)

        # If current subtopic not allowed anymore -> reset to ""
        if self.var_subtopic.get() not in allowed:
            self.var_subtopic.set("")

        self._update_id()

    # ---------- ID logic ----------
    def _update_id(self):
        """
        id = date + topic + subtopic + hh_mm
        joined with underscores, no spaces, empty parts allowed but not emitted as empty underscores.
        date expected: YYYY-MM-DD (if empty -> omitted)
        time part always emitted.
        """
        d = sanitize_token(self.var_date.get())
        t = sanitize_token(self.var_topic.get())
        s = sanitize_token(self.var_subtopic.get())
        hh_mm = datetime.now().strftime("%H_%M")

        parts = [p for p in [d, t, s, hh_mm] if p]
        new_id = "_".join(parts) if parts else hh_mm

        # Set readonly entry
        self.var_id.set(new_id)

    # ---------- Helpers ----------
    def _fill_today(self):
        self.var_date.set(date.today().isoformat())

    def _insert_at_cursor(self, text):
        self.txt_content.insert("insert", text)
        self.txt_content.focus_set()

    def _wrap_selection(self, left, right):
        try:
            start = self.txt_content.index("sel.first")
            end = self.txt_content.index("sel.last")
        except tk.TclError:
            self.txt_content.insert("insert", left + right)
            self.txt_content.mark_set("insert", f"insert-{len(right)}c")
            self.txt_content.focus_set()
            return

        selected = self.txt_content.get(start, end)
        self.txt_content.delete(start, end)
        self.txt_content.insert(start, f"{left}{selected}{right}")
        self.txt_content.tag_remove("sel", "1.0", "end")
        self.txt_content.focus_set()

    def _make_list(self):
        try:
            start = self.txt_content.index("sel.first")
            end = self.txt_content.index("sel.last")
            start_line = int(start.split(".")[0])
            end_line = int(end.split(".")[0])

            for line in range(start_line, end_line + 1):
                line_start = f"{line}.0"
                line_text = self.txt_content.get(line_start, f"{line}.end")
                if line_text.strip() == "":
                    continue
                if not line_text.startswith("- "):
                    self.txt_content.insert(line_start, "- ")
        except tk.TclError:
            self._insert_at_cursor("- ")

        self.txt_content.focus_set()

    def _add_image(self):
        filename = (self.var_img_file.get() or "").strip()
        alt = (self.var_img_alt.get() or "").strip() or "image"

        if not filename:
            self._flash("Kein Dateiname.", ok=False)
            return

        src = ASSET_PREFIX + filename
        self.lst_images.insert("end", f"{src} | {alt}")
        self.var_img_file.set("")

    def _remove_selected_image(self):
        sel = list(self.lst_images.curselection())
        for idx in reversed(sel):
            self.lst_images.delete(idx)

    def _collect_images(self):
        images = []
        for i in range(self.lst_images.size()):
            item = self.lst_images.get(i)
            if " | " in item:
                src, alt = item.split(" | ", 1)
            else:
                src, alt = item, "image"
            images.append({"src": src.strip(), "alt": alt.strip()})
        return images

    def _generate(self):
        # always refresh id at generation time (time-part!)
        self._update_id()

        post = {
            "id": self.var_id.get(),
            "topic": self.var_topic.get(),
            "subtopic": self.var_subtopic.get(),
            "date": self.var_date.get().strip(),
            "title": self.var_title.get().strip(),
            "format": self.var_format.get().strip(),
            "content": self.txt_content.get("1.0", "end-1c"),
            "images": self._collect_images(),
        }

        out = json.dumps(post, ensure_ascii=False, indent=2)
        self.txt_output.delete("1.0", "end")
        self.txt_output.insert("1.0", out)
        self._flash("Generiert. Klick ins Output-Feld kopiert.", ok=True)

    def _copy_output_on_click(self, _event=None):
        text = self.txt_output.get("1.0", "end-1c").strip()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self._flash("In Zwischenablage kopiert.", ok=True)

    def _flash(self, msg, ok=True):
        self.lbl_status.configure(text=msg, foreground=("#2a7" if ok else "#b33"))
        self.after(1600, lambda: self.lbl_status.configure(text=""))


if __name__ == "__main__":
    app = JsonPostGui()
    app.mainloop()
