import getpass
from datetime import datetime

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class DashboardApp(ctk.CTk):
    def __init__(self, db, snapshot_service):
        super().__init__()
        self.db = db
        self.snapshot_service = snapshot_service

        self.title("iDraft-style Productivity Dashboard")
        self.geometry("1380x860")
        self.minsize(1180, 740)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.colors = {
            "app_bg": "#d5d5d5",
            "shell": "#e2e2e2",
            "sidebar": "#f2f2f2",
            "card": "#efefef",
            "card_dark": "#161616",
            "stroke": "#c9c9c9",
            "text": "#111111",
            "text_muted": "#606060",
            "white": "#ffffff",
            "btn": "#111111",
        }

        self.username = self.db.get_setting("username", "").strip()
        if not self.username:
            self.username = getpass.getuser().replace(".", " ").title()

        self.chart_mode = ctk.StringVar(value=self.db.get_setting("chart_mode", "Line"))
        self.todo_vars = []
        self.nav_buttons = {}
        self.integration_buttons = {}
        self.current_page = "dashboard"

        self.configure(fg_color=self.colors["app_bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_shell()
        self._build_sidebar()
        self._build_main()
        self.show_page("dashboard")
        self._write_snapshot()

    def _build_shell(self):
        self.shell = ctk.CTkFrame(
            self,
            fg_color=self.colors["shell"],
            corner_radius=28,
            border_color="#f8f8f8",
            border_width=2,
        )
        self.shell.grid(row=0, column=0, sticky="nsew", padx=26, pady=22)
        self.shell.grid_columnconfigure(0, weight=0)
        self.shell.grid_columnconfigure(1, weight=1)
        self.shell.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self.shell,
            fg_color=self.colors["sidebar"],
            corner_radius=22,
            border_color=self.colors["stroke"],
            border_width=1,
            width=220,
        )
        sidebar.grid(row=0, column=0, sticky="nsw", padx=18, pady=18)
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="iDraft",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(20, 18))

        nav_map = {
            "Dashboard": "dashboard",
            "Calendar": "calendar",
            "My Tasks": "tasks",
            "Statistics": "statistics",
            "Documents": "documents",
        }
        for i, (label, page) in enumerate(nav_map.items()):
            btn = self._sidebar_btn(sidebar, label, lambda p=page: self.show_page(p))
            btn.grid(row=i + 1, column=0, padx=18, pady=4, sticky="w")
            self.nav_buttons[page] = btn

        ctk.CTkLabel(
            sidebar,
            text="INTEGRATIONS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["text_muted"],
        ).grid(row=7, column=0, sticky="w", padx=18, pady=(26, 6))

        integration_map = {
            "Slack": "integration_slack",
            "Notion": "integration_notion",
            "Plugins": "integration_plugins",
        }
        for j, (label, page) in enumerate(integration_map.items()):
            btn = self._sidebar_btn(sidebar, f"- {label}", lambda p=page: self.show_page(p), h=30)
            btn.grid(row=8 + j, column=0, padx=18, pady=2, sticky="w")
            self.integration_buttons[page] = btn

        ctk.CTkLabel(
            sidebar,
            text="Settings",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"],
        ).grid(row=13, column=0, sticky="sw", padx=18, pady=(120, 18))

    def _sidebar_btn(self, parent, text, command, h=34):
        return ctk.CTkButton(
            parent,
            text=text,
            width=170,
            height=h,
            anchor="w",
            corner_radius=15 if h == 34 else 12,
            fg_color="transparent",
            hover_color="#dfdfdf",
            text_color=self.colors["text"],
            command=command,
        )

    def _build_main(self):
        main = ctk.CTkFrame(self.shell, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=(0, 18), pady=18)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(main, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top.grid_columnconfigure(0, weight=1)

        self.greeting_label = ctk.CTkLabel(
            top,
            text=f"Hi, {self.username}!",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=self.colors["text"],
        )
        self.greeting_label.grid(row=0, column=0, sticky="w", padx=10)

        tools = ctk.CTkFrame(top, fg_color="transparent")
        tools.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            tools,
            text="+ Create",
            width=86,
            height=34,
            corner_radius=16,
            fg_color=self.colors["btn"],
            hover_color="#2d2d2d",
            text_color="#ffffff",
        ).grid(row=0, column=0, padx=(0, 8))

        for idx, icon in enumerate(["S", "B"]):
            ctk.CTkButton(
                tools,
                text=icon,
                width=34,
                height=34,
                corner_radius=17,
                fg_color=self.colors["white"],
                hover_color="#e5e5e5",
                text_color=self.colors["text"],
            ).grid(row=0, column=idx + 1, padx=(0, 8))

        avatar = ctk.CTkFrame(tools, fg_color="#1b1b1b", width=34, height=34, corner_radius=17)
        avatar.grid(row=0, column=3)
        avatar.grid_propagate(False)
        ctk.CTkLabel(
            avatar,
            text=(self.username[0] if self.username else "U").upper(),
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")

        self.page_container = ctk.CTkFrame(main, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

    def show_page(self, page_name):
        self.current_page = page_name
        self._set_sidebar_active(page_name)
        for child in self.page_container.winfo_children():
            child.destroy()

        if page_name == "dashboard":
            self._build_dashboard_page(self.page_container)
        elif page_name == "calendar":
            self._build_calendar_page(self.page_container)
        elif page_name == "tasks":
            self._build_tasks_page(self.page_container)
        elif page_name == "statistics":
            self._build_statistics_page(self.page_container)
        elif page_name == "documents":
            self._build_documents_page(self.page_container)
        elif page_name == "integration_slack":
            self._build_integration_page(self.page_container, "Slack", "Workspace sync, channels, reminders")
        elif page_name == "integration_notion":
            self._build_integration_page(self.page_container, "Notion", "Pages, tasks, and content sync")
        elif page_name == "integration_plugins":
            self._build_integration_page(self.page_container, "Plugins", "Manage installed plugins and add-ons")

    def _set_sidebar_active(self, page_name):
        for page, btn in self.nav_buttons.items():
            is_active = page == page_name
            btn.configure(
                fg_color="#111111" if is_active else "transparent",
                hover_color="#2b2b2b" if is_active else "#dfdfdf",
                text_color="#ffffff" if is_active else self.colors["text"],
            )
        for page, btn in self.integration_buttons.items():
            is_active = page == page_name
            btn.configure(
                fg_color="#111111" if is_active else "transparent",
                hover_color="#2b2b2b" if is_active else "#dfdfdf",
                text_color="#ffffff" if is_active else self.colors["text"],
            )

    def _build_dashboard_page(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.grid(row=0, column=0, sticky="nsew")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="top")
        grid.grid_rowconfigure(0, weight=0)
        grid.grid_rowconfigure(1, weight=1)
        grid.grid_rowconfigure(2, weight=0)

        self._fill_overview(self._make_card(grid, 0, 0, 260, dark=True))
        self._fill_weekly(self._make_card(grid, 0, 1, 260))
        self._fill_month(self._make_card(grid, 0, 2, 260))
        self._fill_todo(self._make_card(grid, 1, 0, 300))
        self._fill_deadline(self._make_card(grid, 1, 1, 300))
        self._fill_journal(self._make_card(grid, 1, 2, 300))
        self._fill_projects(self._make_card(grid, 2, 0, 130, dark=True, col_span=3))

    def _build_calendar_page(self, parent):
        card = self._page_card(parent, "Calendar")
        now = datetime.now()
        ctk.CTkLabel(
            card,
            text=f"{now.strftime('%B %Y')}",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(0, weight=1)

        deadlines = self.db.list_deadlines()
        if not deadlines:
            ctk.CTkLabel(body, text="No deadlines scheduled.", text_color=self.colors["text_muted"]).grid(
                row=0, column=0, sticky="w"
            )
        for i, d in enumerate(deadlines):
            ctk.CTkLabel(
                body,
                text=f"{d['due_date']}  -  {d['title']}",
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=14),
            ).grid(row=i, column=0, sticky="w", pady=4)

    def _build_tasks_page(self, parent):
        card = self._page_card(parent, "My Tasks")
        list_frame = ctk.CTkScrollableFrame(card, fg_color="#ffffff", border_color=self.colors["stroke"], border_width=1)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))
        list_frame.grid_columnconfigure(0, weight=1)

        todos = self.db.list_todos()
        for i, t in enumerate(todos):
            var = ctk.BooleanVar(value=bool(t["done"]))
            ctk.CTkCheckBox(
                list_frame,
                text=t["text"],
                variable=var,
                command=lambda tid=t["id"], v=var: self._toggle_todo_from_page(tid, v),
            ).grid(row=i, column=0, sticky="w", pady=4, padx=8)

        actions = ctk.CTkFrame(card, fg_color="transparent", height=36)
        actions.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        actions.grid_propagate(False)
        actions.grid_columnconfigure(0, weight=1)

        self.tasks_entry = ctk.CTkEntry(actions, placeholder_text="Add task", height=32)
        self.tasks_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._icon_btn(actions, "+", self._add_task_from_tasks_page).grid(row=0, column=1, padx=(0, 6))
        self._icon_btn(actions, "x", self._delete_done_from_tasks_page, dark=False).grid(row=0, column=2)

    def _build_statistics_page(self, parent):
        card = self._page_card(parent, "Statistics")

        fig = Figure(figsize=(8.2, 4.2), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(self.colors["card"])
        ax.set_facecolor(self.colors["card"])

        todos = self.db.list_todos()
        done = sum(1 for t in todos if t["done"])
        pending = len(todos) - done
        deadlines = len(self.db.list_deadlines())

        labels = ["Done", "Pending", "Deadlines"]
        values = [done, pending, deadlines]
        bars = ax.bar(labels, values, color=["#1f1f1f", "#7a7a7a", "#b5b5b5"], width=0.5)
        ymax = max(values + [1])
        ax.set_ylim(0, ymax * 1.3 + 0.5)
        ax.grid(axis="y", linestyle="--", alpha=0.25)

        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.1, str(v), ha="center", color="#2a2a2a")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#b8b8b8")
        ax.spines["bottom"].set_color("#b8b8b8")
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

    def _build_documents_page(self, parent):
        card = self._page_card(parent, "Documents")
        ctk.CTkLabel(
            card,
            text="Document manager placeholder",
            text_color=self.colors["text_muted"],
            font=ctk.CTkFont(size=15),
        ).grid(row=1, column=0, sticky="w", padx=20, pady=12)

    def _build_integration_page(self, parent, title, subtitle):
        card = self._page_card(parent, title)
        ctk.CTkLabel(
            card,
            text=subtitle,
            text_color=self.colors["text_muted"],
            font=ctk.CTkFont(size=15),
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 14))

        rows = ctk.CTkFrame(card, fg_color="transparent")
        rows.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 18))
        rows.grid_columnconfigure(0, weight=1)

        for i, name in enumerate([f"{title} workspace A", f"{title} workspace B", f"{title} workspace C"]):
            line = ctk.CTkFrame(rows, fg_color="#ffffff", corner_radius=10, border_color=self.colors["stroke"], border_width=1)
            line.grid(row=i, column=0, sticky="ew", pady=5)
            line.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(line, text=name, text_color=self.colors["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=9)
            ctk.CTkButton(
                line,
                text="Connect",
                width=82,
                height=28,
                fg_color="#1b1b1b",
                hover_color="#2d2d2d",
                text_color="#ffffff",
            ).grid(row=0, column=1, padx=8, pady=5)

    def _page_card(self, parent, title):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=20,
            border_color=self.colors["stroke"],
            border_width=1,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            card,
            text=title,
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))
        return card

    def _make_card(self, parent, row, col, height, dark=False, col_span=1):
        fg = self.colors["card_dark"] if dark else self.colors["card"]
        card = ctk.CTkFrame(
            parent,
            fg_color=fg,
            corner_radius=20,
            border_color=self.colors["stroke"] if not dark else "#2c2c2c",
            border_width=1,
        )
        card.grid(row=row, column=col, columnspan=col_span, sticky="nsew", padx=8, pady=8)
        card.grid_propagate(False)
        card.configure(height=height)
        card.grid_columnconfigure(0, weight=1)
        return card

    def _fill_overview(self, card):
        card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(card, text="Overall Information", text_color="#f4f4f4", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4)
        )
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 10))
        body.grid_columnconfigure((0, 1, 2), weight=1)

        todos = self.db.list_todos()
        done_count = sum(1 for t in todos if t["done"])
        total = len(todos)
        deadline_count = len(self.db.list_deadlines())

        ctk.CTkLabel(body, text=str(done_count), font=ctk.CTkFont(size=40, weight="bold"), text_color="#ffffff").grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(body, text=f"{total} total", text_color="#a7a7a7").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(body, text=str(deadline_count), font=ctk.CTkFont(size=34, weight="bold"), text_color="#ffffff").grid(
            row=0, column=2, sticky="e"
        )

    def _fill_weekly(self, card):
        card.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(card, text="Weekly progress", text_color=self.colors["text"], font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8)
        )

        mode = ctk.CTkSegmentedButton(
            card,
            values=["Line", "Bar", "Pie"],
            variable=self.chart_mode,
            command=self._draw_progress,
            fg_color="#d8d8d8",
            selected_color="#121212",
            selected_hover_color="#2b2b2b",
            unselected_color="#d8d8d8",
            unselected_hover_color="#c8c8c8",
            text_color="#ffffff",
            width=200,
        )
        mode.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))

        self.weekly_figure = Figure(figsize=(3.6, 2.1), dpi=100)
        self.weekly_ax = self.weekly_figure.add_subplot(111)
        self.weekly_figure.patch.set_facecolor(self.colors["card"])
        self.weekly_ax.set_facecolor(self.colors["card"])
        self.weekly_canvas = FigureCanvasTkAgg(self.weekly_figure, master=card)
        self.weekly_canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 12))
        self._draw_progress()

    def _fill_month(self, card):
        card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(card, text="Month progress", text_color=self.colors["text"], font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 10)
        )

        done = sum(1 for t in self.db.list_todos() if t["done"])
        total = max(len(self.db.list_todos()), 1)
        pct = int((done / total) * 100)

        donut_fig = Figure(figsize=(2.6, 2.1), dpi=100)
        ax = donut_fig.add_subplot(111)
        donut_fig.patch.set_facecolor(self.colors["card"])
        ax.set_facecolor(self.colors["card"])
        ax.pie([pct, 100 - pct], startangle=90, colors=["#1f1f1f", "#bcbcbc"], wedgeprops={"width": 0.22})
        ax.text(0, 0, f"{pct}%", ha="center", va="center", fontsize=14, color="#1f1f1f", fontweight="bold")
        ax.axis("equal")
        ax.axis("off")

        canvas = FigureCanvasTkAgg(donut_fig, master=card)
        canvas.get_tk_widget().grid(row=1, column=0, pady=(2, 8))
        ctk.CTkButton(card, text="Download Report", width=140, height=30, fg_color="#ffffff", hover_color="#ececec", text_color="#1b1b1b", corner_radius=14).grid(
            row=2, column=0, pady=(0, 12)
        )

    def _fill_todo(self, card):
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=0)
        ctk.CTkLabel(card, text="Month goals", text_color=self.colors["text"], font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4)
        )

        self.todo_list_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.todo_list_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 8))

        action = ctk.CTkFrame(card, fg_color="transparent", height=36)
        action.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))
        action.grid_propagate(False)
        action.grid_columnconfigure(0, weight=1)

        self.todo_entry = ctk.CTkEntry(action, placeholder_text="Add goal", fg_color="#ffffff", border_color=self.colors["stroke"], height=32)
        self.todo_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._icon_btn(action, "+", self._add_todo).grid(row=0, column=1, padx=(0, 6))
        self._icon_btn(action, "x", self._delete_done_todo, dark=False).grid(row=0, column=2)

        self._render_todo()

    def _fill_deadline(self, card):
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=0)
        ctk.CTkLabel(card, text="Deadlines", text_color=self.colors["text"], font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4)
        )

        self.deadline_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.deadline_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 8))

        action = ctk.CTkFrame(card, fg_color="transparent", height=36)
        action.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))
        action.grid_propagate(False)
        action.grid_columnconfigure(0, weight=2)
        action.grid_columnconfigure(1, weight=1)

        self.deadline_name = ctk.CTkEntry(action, placeholder_text="Task", height=32)
        self.deadline_name.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.deadline_date = ctk.CTkEntry(action, placeholder_text="YYYY-MM-DD", height=32)
        self.deadline_date.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        self._icon_btn(action, "+", self._add_deadline).grid(row=0, column=2, padx=(0, 6))
        self._icon_btn(action, "x", self._delete_last_deadline, dark=False).grid(row=0, column=3)

        self._render_deadlines()

    def _fill_journal(self, card):
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=0)
        ctk.CTkLabel(card, text="Journal", text_color=self.colors["text"], font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4)
        )

        self.journal = ctk.CTkTextbox(card, fg_color="#ffffff", border_color=self.colors["stroke"], border_width=1, corner_radius=12)
        self.journal.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 8))
        self._load_journal()

        row = ctk.CTkFrame(card, fg_color="transparent", height=36)
        row.grid(row=2, column=0, sticky="e", padx=16, pady=(0, 12))
        row.grid_propagate(False)
        ctk.CTkButton(row, text="Save", width=78, height=32, fg_color="#1b1b1b", hover_color="#2d2d2d", text_color="#ffffff", command=self._save_journal).grid(
            row=0, column=0, padx=(0, 6)
        )
        self._icon_btn(row, "x", self._clear_journal, dark=False).grid(row=0, column=1)

    def _fill_projects(self, card):
        wrap = ctk.CTkFrame(card, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)
        for i, title in enumerate(["New Schedule", "Prototype animation", "Ai Project 2 part"]):
            block = ctk.CTkFrame(wrap, fg_color="#1f1f1f", corner_radius=14, border_color="#2f2f2f", border_width=1)
            block.grid(row=0, column=i, padx=6, sticky="nsew")
            ctk.CTkLabel(block, text=title, text_color="#ffffff", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
            ctk.CTkLabel(block, text="- In progress", text_color="#a5a5a5", font=ctk.CTkFont(size=11)).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))

    def _icon_btn(self, parent, text, command, dark=True):
        if dark:
            fg, hover, tc = "#1b1b1b", "#2d2d2d", "#ffffff"
        else:
            fg, hover, tc = "#d0d0d0", "#bfbfbf", "#1b1b1b"
        return ctk.CTkButton(parent, text=text, width=34, height=32, fg_color=fg, hover_color=hover, text_color=tc, command=command)

    def _draw_progress(self, _=None):
        self.db.set_setting("chart_mode", self.chart_mode.get())
        self.weekly_ax.clear()

        todos = self.db.list_todos()
        done = sum(1 for t in todos if t["done"])
        pending = len(todos) - done
        deadlines = len(self.db.list_deadlines())
        vals = [done, pending, deadlines]
        labels = ["Done", "Pending", "Deadlines"]

        mode = self.chart_mode.get()
        if mode == "Pie":
            safe = [v if v > 0 else 0.1 for v in vals]
            self.weekly_ax.pie(
                safe,
                labels=labels,
                startangle=90,
                colors=["#1f1f1f", "#787878", "#b7b7b7"],
                autopct="%1.0f%%",
                textprops={"color": "#202020", "fontsize": 9},
            )
            self.weekly_ax.axis("equal")
        elif mode == "Bar":
            bars = self.weekly_ax.bar(labels, vals, color="#2d2d2d", width=0.5)
            ymax = max(vals + [1])
            self.weekly_ax.set_ylim(0, ymax * 1.25 + 0.5)
            self.weekly_ax.margins(x=0.25)
            for b, v in zip(bars, vals):
                self.weekly_ax.text(b.get_x() + b.get_width() / 2, v + 0.1, str(v), ha="center", fontsize=9, color="#2a2a2a")
        else:
            xs = ["M", "T", "W", "T", "F", "S"]
            y1 = [2, 3, 5, 4, 6, done + 3]
            y2 = [1, 2, 3, 2, 4, pending + 2]
            ymax = max(y1 + y2 + [1])
            self.weekly_ax.plot(xs, y1, color="#1f1f1f", linewidth=2.2)
            self.weekly_ax.plot(xs, y2, color="#7e7e7e", linewidth=1.9)
            self.weekly_ax.set_ylim(0, ymax * 1.2)

        self.weekly_ax.spines["top"].set_visible(False)
        self.weekly_ax.spines["right"].set_visible(False)
        self.weekly_ax.spines["left"].set_color("#b8b8b8")
        self.weekly_ax.spines["bottom"].set_color("#b8b8b8")
        self.weekly_ax.set_facecolor(self.colors["card"])
        self.weekly_figure.tight_layout(pad=1.3)
        self.weekly_canvas.draw()
        self._write_snapshot()

    def _render_todo(self):
        for child in self.todo_list_frame.winfo_children():
            child.destroy()
        self.todo_vars = []
        rows = self.db.list_todos()
        for i, item in enumerate(rows):
            var = ctk.BooleanVar(value=bool(item["done"]))
            self.todo_vars.append((item["id"], var))
            ctk.CTkCheckBox(
                self.todo_list_frame,
                text=item["text"],
                variable=var,
                command=lambda tid=item["id"], v=var: self._toggle_todo(tid, v),
            ).grid(row=i, column=0, sticky="w", pady=4)

    def _render_deadlines(self):
        for child in self.deadline_frame.winfo_children():
            child.destroy()
        rows = self.db.list_deadlines()
        for i, item in enumerate(rows):
            row = ctk.CTkFrame(self.deadline_frame, fg_color="#ffffff", corner_radius=12)
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=item["title"], text_color=self.colors["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            ctk.CTkLabel(row, text=item["due_date"], text_color=self.colors["text_muted"]).grid(row=0, column=1, padx=6)
            ctk.CTkButton(
                row,
                text="x",
                width=28,
                height=24,
                fg_color="#d8d8d8",
                hover_color="#c5c5c5",
                text_color="#232323",
                command=lambda did=item["id"]: self._delete_deadline(did),
            ).grid(row=0, column=2, padx=(0, 8))

    def _toggle_todo(self, todo_id, var):
        self.db.update_todo_done(todo_id, bool(var.get()))
        self.show_page("dashboard")
        self._write_snapshot()

    def _toggle_todo_from_page(self, todo_id, var):
        self.db.update_todo_done(todo_id, bool(var.get()))
        self.show_page("tasks")
        self._write_snapshot()

    def _add_todo(self):
        text = self.todo_entry.get().strip()
        if not text:
            return
        self.db.add_todo(text)
        self.show_page("dashboard")
        self._write_snapshot()

    def _add_task_from_tasks_page(self):
        text = self.tasks_entry.get().strip()
        if not text:
            return
        self.db.add_todo(text)
        self.show_page("tasks")
        self._write_snapshot()

    def _delete_done_todo(self):
        self.db.delete_done_todos()
        self.show_page("dashboard")
        self._write_snapshot()

    def _delete_done_from_tasks_page(self):
        self.db.delete_done_todos()
        self.show_page("tasks")
        self._write_snapshot()

    def _add_deadline(self):
        task = self.deadline_name.get().strip()
        due = self.deadline_date.get().strip()
        if not task or not due or not self._valid_date(due):
            return
        self.db.add_deadline(task, due)
        self.show_page("dashboard")
        self._write_snapshot()

    def _delete_deadline(self, deadline_id):
        self.db.delete_deadline(deadline_id)
        self.show_page("dashboard")
        self._write_snapshot()

    def _delete_last_deadline(self):
        self.db.delete_last_deadline()
        self.show_page("dashboard")
        self._write_snapshot()

    def _load_journal(self):
        self.journal.delete("1.0", "end")
        self.journal.insert("1.0", self.db.get_journal() or "Write your notes for today...")

    def _save_journal(self):
        self.db.save_journal(self.journal.get("1.0", "end").strip())
        self._write_snapshot()

    def _clear_journal(self):
        self.journal.delete("1.0", "end")
        self.db.save_journal("")
        self._write_snapshot()

    def _valid_date(self, s):
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _write_snapshot(self):
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "username": self.username,
            "todos": self.db.list_todos(),
            "deadlines": self.db.list_deadlines(),
            "journal": self.db.get_journal(),
            "chart_mode": self.chart_mode.get(),
            "page": self.current_page,
        }
        self.snapshot_service.save(payload)
