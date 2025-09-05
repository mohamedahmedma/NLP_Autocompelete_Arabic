from GloblaImport import *;
# Part 4: GUI INTERFACE
class ArabicAutocompleteGUI:
    def __init__(self, model):
        self.model = model
        self.root = tk.Tk()

        # State variables
        self.current_suggestions = []
        self._debounce_timer = None
        self.dark_mode = False
        self.logical_text = ""  # store Arabic in logical order
        self.reshaper = arabic_reshaper.ArabicReshaper(
            {'delete_harakat': False, 'support_ligatures': True}
        )

        # Setup GUI
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.setup_layout()

    # ----------------- Window & Styles -----------------
    def setup_window(self):
        self.root.title("Arabic Autocomplete System")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)

        self.colors_light = {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F5F7',
            'bg_tertiary': '#FBFBFD',
            'accent_blue': '#007AFF',
            'accent_blue_hover': '#0056CC',
            'text_primary': '#1D1D1F',
            'text_secondary': '#86868B',
            'border': '#D2D2D7',
            'success': '#34C759'
        }

        self.colors_dark = {
            'bg_primary': '#1D1D1F',
            'bg_secondary': '#2C2C2E',
            'bg_tertiary': '#3A3A3C',
            'accent_blue': '#0A84FF',
            'accent_blue_hover': '#0056CC',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0',
            'border': '#3A3A3C',
            'success': '#30D158'
        }

        self.colors = self.colors_light
        self.root.configure(bg=self.colors['bg_secondary'])

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.apply_theme()

    def apply_theme(self):
        c = self.colors
        self.style.configure('Card.TFrame', background=c['bg_primary'], relief='flat')
        self.style.configure('Title.TLabel', font=('Segoe UI', 28, 'bold'),
                             background=c['bg_primary'], foreground=c['text_primary'])
        self.style.configure('Subtitle.TLabel', font=('Segoe UI', 16),
                             background=c['bg_primary'], foreground=c['text_secondary'])
        self.style.configure('SectionTitle.TLabel', font=('Segoe UI', 18, 'bold'),
                             background=c['bg_primary'], foreground=c['text_primary'])
        self.style.configure('Stats.TLabel', font=('Consolas', 12),
                             background=c['bg_secondary'], foreground=c['text_secondary'])
        self.style.configure('Suggestion.TButton', font=('Segoe UI', 14),
                             background=c['bg_tertiary'], foreground=c['text_primary'],
                             borderwidth=1, relief='flat', padding=(15, 10))
        self.style.map('Suggestion.TButton',
                       background=[('active', c['accent_blue']), ('pressed', c['accent_blue_hover'])],
                       foreground=[('active', 'white'), ('pressed', 'white')])

    # ----------------- Variables & Layout -----------------
    def setup_variables(self):
        self.suggestion_vars = [tk.StringVar() for _ in range(5)]

    def setup_layout(self):
        main_container = ttk.Frame(self.root, style='Card.TFrame', padding=30)
        main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        self.setup_header(main_container)
        self.setup_input_section(main_container)
        self.setup_suggestions_section(main_container)
        self.setup_stats_section(main_container)

    # ----------------- Sections -----------------
    def setup_header(self, parent):
        header = ttk.Frame(parent, style='Card.TFrame')
        header.grid(row=0, column=0, sticky='ew', pady=(0, 30))
        header.grid_columnconfigure(0, weight=1)

        ttk.Label(header, text="Arabic Autocomplete", style='Title.TLabel').grid(row=0, column=0, pady=(0, 10))
        ttk.Label(header, text="Intelligent Arabic text prediction powered by N-gram modeling",
                  style='Subtitle.TLabel').grid(row=1, column=0)

        toggle_btn = ttk.Button(header, text="🌙 Toggle Theme", command=self.toggle_theme)
        toggle_btn.grid(row=0, column=1, padx=10)

    def setup_input_section(self, parent):
        container = ttk.Frame(parent, style='Card.TFrame')
        container.grid(row=1, column=0, sticky='nsew', pady=(0, 20))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Text widget (no built-in scrollbar)
        self.text_input = tk.Text(
            container, font=('Segoe UI', 16), wrap=tk.WORD,
            relief='flat', bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_blue'], insertwidth=2,
            selectbackground=self.colors['accent_blue'], selectforeground='white',
            padx=20, pady=15
        )
        self.text_input.grid(row=0, column=0, sticky='nsew')

        # External scrollbar (initially hidden)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=self._on_scroll)

        # RTL setup
        self.text_input.tag_configure("rtl", justify="right")
        self._render_visual()

        # Bindings
        self.text_input.bind("<Key>", self._on_keypress)
        self.text_input.bind("<FocusIn>", lambda e: self.text_input.configure(bg=self.colors['bg_primary']))
        self.text_input.bind("<FocusOut>", lambda e: self.text_input.configure(bg=self.colors['bg_tertiary']))
        self.text_input.bind("<<Paste>>", self._on_paste)


    def _on_scroll(self, *args):
        # Handle scrollbar correctly
        if args[0] in ("scroll", "moveto"):
            self.text_input.yview(*args)
        else:
            # Convert raw numbers like "0.0" into a moveto command
            self.text_input.yview("moveto", args[0])


    def setup_suggestions_section(self, parent):
        container = ttk.Frame(parent, style='Card.TFrame')
        container.grid(row=2, column=0, sticky='ew', pady=(0, 20))
        container.grid_columnconfigure(0, weight=1)

        ttk.Label(container, text="Suggestions", style='SectionTitle.TLabel').grid(row=0, column=0, sticky='w')

        self.suggestions_frame = ttk.Frame(container, style='Card.TFrame')
        self.suggestions_frame.grid(row=1, column=0, sticky='ew')
        for i in range(5):
            self.suggestions_frame.grid_columnconfigure(i, weight=1, uniform="suggestions")

        self.suggestion_buttons = []
        for i, var in enumerate(self.suggestion_vars):
            col = len(self.suggestion_vars) - 1 - i  # highest prob → rightmost
            btn = ttk.Button(self.suggestions_frame, textvariable=var,
                             style='Suggestion.TButton',
                             command=partial(self.apply_suggestion, i),
                             state='disabled', takefocus=False)
            btn.grid(row=0, column=col, sticky='ew', padx=5)
            self.suggestion_buttons.append(btn)

    def setup_stats_section(self, parent):
        stats = ttk.Frame(self.root, style='Card.TFrame', padding=15)
        stats.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 20))
        self.stats_label = ttk.Label(stats, text="", style='Stats.TLabel')
        self.stats_label.pack()

    # ----------------- Logic -----------------
    def _shape(self, s: str) -> str:
        return get_display(self.reshaper.reshape(s))

    def _render_visual(self):
        # Save logical cursor position (in chars from start)
        cursor_index = self.text_input.index(tk.INSERT)
        logical_cursor = int(cursor_index.split('.')[1])  # column offset (ignoring lines for now)

        # Render reshaped visual text
        visual = self._shape(self.logical_text)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", visual)
        self.text_input.tag_add("rtl", "1.0", tk.END)

        # Restore cursor position (approximate)
        try:
            self.text_input.mark_set(tk.INSERT, f"1.{logical_cursor}")
        except Exception:
            self.text_input.mark_set(tk.INSERT, tk.END)

        self.text_input.see(tk.INSERT)

    def _on_keypress(self, e):
        if (e.state & 0x4):  # Ctrl combos
            return

        ks, ch = e.keysym, e.char
        if ks == "BackSpace":
            self.logical_text = self.logical_text[:-1]
            self._render_visual()
            self.on_text_changed_debounced()
            return "break"
        if ks in ("Return", "KP_Enter"):
            self.logical_text += "\n"
            self._render_visual()
            self.on_text_changed_debounced()
            return "break"
        if len(ch) == 1:
            self.logical_text += ch
            self._render_visual()
            self.on_text_changed_debounced()
            return "break"

    def _on_paste(self, e):
        try:
            clip = self.root.clipboard_get()
        except Exception:
            clip = ""
        if clip:
            self.logical_text += clip
            self._render_visual()
            self.on_text_changed_debounced()
        return "break"

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.colors = self.colors_dark if self.dark_mode else self.colors_light
        self.apply_theme()
        self.root.configure(bg=self.colors['bg_secondary'])
        self.text_input.configure(bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'])

    def on_text_changed_debounced(self, event=None):
        if self._debounce_timer:
            self.root.after_cancel(self._debounce_timer)
        self._debounce_timer = self.root.after(300, self.on_text_changed)

    def on_text_changed(self):
        text = self.logical_text.strip()
        if text:
            self.current_suggestions = self.model.predict_next_words(text)
        else:
            self.current_suggestions = []
        self.update_suggestions()

    def update_suggestions(self):
        sorted_suggestions = sorted(self.current_suggestions, key=lambda x: x[1], reverse=True)
        for i, (var, btn) in enumerate(zip(self.suggestion_vars, self.suggestion_buttons)):
            if i < len(sorted_suggestions):
                word, prob = sorted_suggestions[i]
                var.set(f"{word} ({prob:.2f})")
                btn.configure(state='normal')
            else:
                var.set("")
                btn.configure(state='disabled')

    def apply_suggestion(self, index):
        sorted_suggestions = sorted(self.current_suggestions, key=lambda x: x[1], reverse=True)
        if index < len(sorted_suggestions):
            word, _ = sorted_suggestions[index]
            if self.logical_text and not self.logical_text.endswith(' '):
                self.logical_text += f" {word}"
            else:
                self.logical_text += word
            self._render_visual()
            self.on_text_changed()

    def update_stats(self, vocab_size):
        model_n = getattr(self.model, 'n', 3)
        self.stats_label.configure(
            text=f"Model: N-gram (N={model_n}) • Vocabulary: {vocab_size:,} words • Active",
            foreground=self.colors['success']
        )
        self.root.after(1000, lambda: self.stats_label.configure(foreground=self.colors['text_secondary']))

    def run(self):
        vocab_size = len(getattr(self.model, 'vocab', []))
        self.update_stats(vocab_size)
        self.center_window()
        self.root.mainloop()

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

