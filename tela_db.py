import tkinter.font as tkfont  
import customtkinter as ctk
import tkinter as tk
import pandas as pd
import logging
import sqlite3

logger = logging.getLogger("jupiter.Minerva")

NOMES_COLUNAS = {
    "programa": "Programa",
    "num_documento": "Nº do documento",
    "tipo_documento": "Tipo de documento",
    "tipo_descricao": "Descrição",
    "data": "Data de Emissão",
    "valor": "Valor",
    "usuario_inclusao": "Usuário de inclusão",
    "data_hora_inclusao": "Data da inclusão",
    "usuario_contab": "Usuário de contabilização",
    "data_hora_contab": "Data da contabilização",
}

COLUNA_ELASTICA = "tipo_descricao"

def construir_tela_db(app, programa_nome="", tipo_ids=None, pagina_inicial="contabilizados"):
    tipo_ids = tipo_ids or []

    def _ler(query):
        try:
            with sqlite3.connect(app.DBPath) as con:
                df = pd.read_sql_query(query, con)
                logger.info(f"[DB] Query retornou {len(df)} registros")
                return df
        except Exception as e:
            logger.error(f"Erro ao consultar o banco de dados: {e}", exc_info=True)
            return pd.DataFrame()

    def carregar_contabilizados():
        ids_str = ",".join(str(int(t)) for t in tipo_ids) if tipo_ids else "NULL"
        query = f"""
            SELECT c.num_documento    AS num_documento,
                   d.tipo_descricao   AS tipo_descricao,
                   c.data             AS data,
                   c.valor            AS valor,
                   c.usuario_contab   AS usuario_contab,
                   c.data_hora_contab AS data_hora_contab
            FROM contabilizacoes c
            LEFT JOIN documentos d ON c.tipo_id = d.tipo_id
            WHERE c.num_documento IS NOT NULL
              AND c.tipo_id IN ({ids_str})
            ORDER BY SUBSTR(c.data, 7, 4) DESC, SUBSTR(c.data, 4, 2) DESC, SUBSTR(c.data, 1, 2) DESC
            LIMIT 5000
        """
        df = _ler(query)
        if df.empty:
            logger.info("[DB] Tentando sem filtro de data...")
            query = f"""
                SELECT c.num_documento    AS num_documento,
                       d.tipo_descricao   AS tipo_descricao,
                       c.data             AS data,
                       c.valor            AS valor,
                       c.usuario_contab   AS usuario_contab,
                       c.data_hora_contab AS data_hora_contab
                FROM contabilizacoes c
                LEFT JOIN documentos d ON c.tipo_id = d.tipo_id
                WHERE c.num_documento IS NOT NULL
                  AND c.tipo_id IN ({ids_str})
                ORDER BY SUBSTR(c.data, 7, 4) DESC, SUBSTR(c.data, 4, 2) DESC, SUBSTR(c.data, 1, 2) DESC
                LIMIT 5000
            """
            df = _ler(query)
        return df

    def carregar_pendentes():
        query = """
            SELECT d.programa           AS programa,
                   d.tipo_documento     AS tipo_documento,
                   d.tipo_descricao     AS tipo_descricao,
                   c.data               AS data,
                   c.valor              AS valor,
                   c.usuario_inclusao   AS usuario_inclusao,
                   c.data_hora_inclusao AS data_hora_inclusao
            FROM contabilizacoes c
            LEFT JOIN documentos d ON c.tipo_id = d.tipo_id
            WHERE c.num_documento IS NULL
            ORDER BY SUBSTR(c.data, 7, 4) DESC, SUBSTR(c.data, 4, 2) DESC, SUBSTR(c.data, 1, 2) DESC
            LIMIT 5000
        """
        return _ler(query)

    def formatar_moeda(val):
        if pd.isna(val) or val is None or val == "":
            return "---"
        try:
            if isinstance(val, str):
                val = val.replace(".", "").replace(",", ".")
            v = float(val)
            s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {s}"
        except Exception:
            return str(val)

    def preparar(df):
        if "valor" in df.columns:
            df["valor"] = df["valor"].apply(formatar_moeda)
        return df.fillna("---")

    # ── TEMA E FONTES ──
    fonte_titulo   = ctk.CTkFont(family="Roboto", size=18, weight="bold")
    fonte_subtitulo= ctk.CTkFont(family="Roboto", size=12)
    fonte_header   = ctk.CTkFont(family="Roboto", size=11, weight="bold")
    fonte_celula   = ctk.CTkFont(family="Roboto", size=11)
    fonte_botao    = ctk.CTkFont(family="Roboto", size=13, weight="bold")
    fonte_toggle   = ctk.CTkFont(family="Roboto", size=12, weight="bold")

    tema = {
        "bg_janela": "#f5f7fa", "header_bg": "#2B3A4A", "header_text": "#FFFFFF",
        "tabela_borda": "#e8edf2", "tabela_header": "#34495E",
        "linha_par": "#f0f6ff", "linha_impar": "#ffffff", "texto_tabela": "#2b2b2b",
        "btn_fechar": "#d9534f", "btn_hover": "#b52b27", "vazio_text": "#8a97a5",
        "selecao_bg": "#A9C2D9", "selecao_text": "#000000",
    }

    pw, ph = 1450, 640
    ws = app.winfo_screenwidth()
    hs = app.winfo_screenheight()
    x = int((ws / 2) - (pw / 2))
    y = int((hs / 2) - (ph / 2))

    # ═══════════════════════════════════════════════════════
    #  CRIAÇÃO DA JANELA
    # ═══════════════════════════════════════════════════════
    popup = ctk.CTkToplevel(app)
    popup.title("Banco de Dados")
    popup.geometry('%dx%d+%d+%d' % (pw, ph, x, y))
    popup.resizable(True, True)
    popup.configure(fg_color=tema["bg_janela"])
    popup.transient(app)
    popup.lift()
    popup.focus_force()
    popup.deiconify()

    titulo_txt = f"Banco de Dados — {programa_nome}" if programa_nome else "Banco de Dados"
    header = ctk.CTkFrame(popup, fg_color=tema["header_bg"], corner_radius=0, height=65)
    header.pack(fill="x")
    header.pack_propagate(False)
    ctk.CTkLabel(header, text=titulo_txt, font=fonte_titulo, text_color=tema["header_text"]).pack(side="left", padx=20, pady=15)
    lbl_contador = ctk.CTkLabel(header, text="", font=fonte_subtitulo, text_color="#A9C2D9")
    lbl_contador.pack(side="right", padx=15)

    opt_contab = f"   Contabilizados · {programa_nome}   " if programa_nome else "   Contabilizados   "
    opt_pend = "   Pendentes · Todos os programas   "

    barra = ctk.CTkFrame(popup, fg_color=tema["bg_janela"], corner_radius=0, height=52)
    barra.pack(fill="x", padx=12, pady=(10, 0))
    barra.pack_propagate(False)
    seletor = ctk.CTkSegmentedButton(
        barra, values=[opt_contab, opt_pend], font=fonte_toggle,
        height=34, command=lambda escolha: trocar_view(escolha)
    )
    seletor.pack(side="left", padx=8, pady=8)

    # ── CONTAINER DA TABELA ──
    table_outer = ctk.CTkFrame(popup, fg_color=tema["tabela_borda"], corner_radius=8)
    table_outer.pack(fill="both", expand=True, padx=12, pady=(8, 6))

    footer = ctk.CTkFrame(popup, fg_color=tema["bg_janela"], corner_radius=0, height=52)
    footer.pack(fill="x")
    footer.pack_propagate(False)
    lbl_total = ctk.CTkLabel(footer, text="", font=fonte_subtitulo, text_color="#666666")
    lbl_total.pack(side="left", padx=20, pady=12)
    ctk.CTkButton(footer, text="Fechar", width=120, height=34,
                  fg_color=tema["btn_fechar"], hover_color=tema["btn_hover"],
                  font=fonte_botao, command=popup.destroy).pack(side="right", padx=20, pady=9)

    # ═══════════════════════════════════════════════════════
    #  CLASSE DA TABELA VIRTUALIZADA — CANVAS
    # ═══════════════════════════════════════════════════════
    class TabelaVirtual(tk.Frame):
        ALTURA_LINHA = 28
        ALTURA_HEADER = 34
        PADX_CELULA = 14          
        LARGURA_MINIMA = 30       
        RESPIRO_EXTRA = 25

        def __init__(self, master, **kwargs):
            kwargs.pop("fg_color", None)
            super().__init__(master, **kwargs)
            self.df = pd.DataFrame()
            self.colunas = []
            self.col_widths = []
            self._cache_texto = {}
            self._linha_selecionada = -1
            self._scroll_job = None   

            self.canvas = tk.Canvas(
                self, bg=tema["bg_janela"], highlightthickness=0,
                borderwidth=0
            )
            self.vsb = tk.Scrollbar(self, orient="vertical", command=self._on_scroll)
            self.canvas.configure(yscrollcommand=self._on_yscroll)

            self.vsb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            self.canvas.bind("<MouseWheel>", self._on_mousewheel)
            self.canvas.bind("<Button-4>", self._on_mousewheel)
            self.canvas.bind("<Button-5>", self._on_mousewheel)
            self.canvas.bind("<Button-1>", self._on_click)
            self.canvas.bind("<Double-Button-1>", self._on_double_click)
            self.canvas.bind("<Configure>", self._on_configure)

            self.canvas.configure(height=400)

        def carregar_dados(self, df: pd.DataFrame):
            logger.info(f"[Tabela] Carregando {len(df)} registros...")
            self.df = df.reset_index(drop=True)
            self.colunas = list(df.columns)
            self._linha_selecionada = -1
            self._calcular_larguras()
            self._ajustar_scrollregion()
            self._desenhar()

        def _medir_texto(self, texto, fonte_tupla):
            """Mede o texto usando a engine do Tkinter puro, igual ao que o Canvas renderiza"""
            chave = (texto, fonte_tupla)
            if chave not in self._cache_texto:
                weight = fonte_tupla[2] if len(fonte_tupla) > 2 else "normal"
                f_nativa = tkfont.Font(family=fonte_tupla[0], size=fonte_tupla[1], weight=weight)
                self._cache_texto[chave] = f_nativa.measure(str(texto))
            return self._cache_texto[chave]

        def _calcular_larguras(self):
            self.col_widths = []
            
            tupla_header = (fonte_header.cget("family"), fonte_header.cget("size"), "bold")
            tupla_celula = (fonte_celula.cget("family"), fonte_celula.cget("size"), "normal")
            
            for col in self.colunas:
                header_txt = NOMES_COLUNAS.get(col, col.replace("_", " ").upper())
                w_header = self._medir_texto(header_txt, tupla_header)
                
                w_cells = 0
                if not self.df.empty:
                    valores_unicos = self.df[col].astype(str).unique()
                    if len(valores_unicos) > 0:
                        w_cells = max(self._medir_texto(v, tupla_celula) for v in valores_unicos)
                
                largura = max(self.LARGURA_MINIMA, max(w_header, w_cells) + self.PADX_CELULA * 2 + self.RESPIRO_EXTRA)
                self.col_widths.append(largura)
            
            logger.info(f"[Tabela] Larguras calculadas com precisão nativa: {self.col_widths}")

        def _ajustar_scrollregion(self):
            altura_total = self.ALTURA_HEADER + max(0, len(self.df)) * self.ALTURA_LINHA
            largura_total = sum(self.col_widths) + 20
            self.canvas.configure(scrollregion=(0, 0, largura_total, altura_total))

        def _on_configure(self, event=None):
            self._desenhar()

        def _on_scroll(self, *args):
            self.canvas.yview(*args)
            if self._scroll_job:
                self.after_cancel(self._scroll_job)
            self._scroll_job = self.after(5, self._desenhar)

        def _on_yscroll(self, *args):
            self.vsb.set(*args)
            if self._scroll_job:
                self.after_cancel(self._scroll_job)
            self._scroll_job = self.after(5, self._desenhar)

        def _on_mousewheel(self, event):
            if hasattr(event, 'delta'):
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(3, "units")
            self._desenhar()

        def _y_visivel(self):
            return (self.canvas.canvasy(0), self.canvas.canvasy(self.winfo_height()))

        def _desenhar(self):
            self.canvas.delete("all")
            if self.df.empty:
                self.canvas.create_text(
                    30, 60, anchor="nw",
                    text="Nenhum registro encontrado.",
                    font=(fonte_subtitulo.cget("family"), fonte_subtitulo.cget("size")),
                    fill=tema["vazio_text"]
                )
                return

            y1_vis, y2_vis = self._y_visivel()

            # ── HEADER ──
            x = 0
            for j, col in enumerate(self.colunas):
                w = self.col_widths[j]
                self.canvas.create_rectangle(
                    x, 0, x + w, self.ALTURA_HEADER,
                    fill=tema["tabela_header"], outline=""
                )
                txt = NOMES_COLUNAS.get(col, col.replace("_", " ").upper())
                self.canvas.create_text(
                    x + w // 2, self.ALTURA_HEADER // 2,
                    text=txt, font=(fonte_header.cget("family"), fonte_header.cget("size"), "bold"),
                    fill="white", anchor="center"
                )
                x += w

            # ── LINHAS VISÍVEIS ──
            linha_inicio = max(0, int((y1_vis - self.ALTURA_HEADER) // self.ALTURA_LINHA))
            linha_fim = min(len(self.df), int((y2_vis - self.ALTURA_HEADER) // self.ALTURA_LINHA) + 2)

            for i in range(linha_inicio, linha_fim):
                y_top = self.ALTURA_HEADER + i * self.ALTURA_LINHA
                y_bottom = y_top + self.ALTURA_LINHA
                bg = tema["linha_par"] if i % 2 == 0 else tema["linha_impar"]
                if i == self._linha_selecionada:
                    bg = tema["selecao_bg"]

                x = 0
                row = self.df.iloc[i]
                for j, col in enumerate(self.colunas):
                    w = self.col_widths[j]
                    self.canvas.create_rectangle(
                        x, y_top, x + w, y_bottom,
                        fill=bg, outline=tema["tabela_borda"]
                    )
                    val = str(row[col]) if row[col] is not None else "---"
                    anchor = "w" if col == COLUNA_ELASTICA else "center"
                    tx = x + self.PADX_CELULA if col == COLUNA_ELASTICA else x + w // 2
                    cor_texto = tema["selecao_text"] if i == self._linha_selecionada else tema["texto_tabela"]
                    self.canvas.create_text(
                        tx, y_top + self.ALTURA_LINHA // 2,
                        text=val, font=(fonte_celula.cget("family"), fonte_celula.cget("size")),
                        fill=cor_texto, anchor=anchor
                    )
                    x += w

        def _on_click(self, event):
            y = self.canvas.canvasy(event.y)
            if y < self.ALTURA_HEADER:
                return
            idx = int((y - self.ALTURA_HEADER) // self.ALTURA_LINHA)
            if 0 <= idx < len(self.df):
                self._linha_selecionada = idx
                self._desenhar()

        def _on_double_click(self, event):
            y = self.canvas.canvasy(event.y)
            x = self.canvas.canvasx(event.x)
            if y < self.ALTURA_HEADER:
                return
            idx = int((y - self.ALTURA_HEADER) // self.ALTURA_LINHA)
            if not (0 <= idx < len(self.df)):
                return
            acum = 0
            col_idx = 0
            for j, w in enumerate(self.col_widths):
                if acum <= x < acum + w:
                    col_idx = j
                    break
                acum += w
            val = str(self.df.iloc[idx, col_idx])
            popup.clipboard_clear()
            popup.clipboard_append(val)
            popup.update()

    tabela = TabelaVirtual(table_outer)
    tabela.pack(fill="both", expand=True, padx=2, pady=2)

    def trocar_view(escolha):
        if escolha == opt_pend:
            df = preparar(carregar_pendentes())
        else:
            df = preparar(carregar_contabilizados())
        tabela.carregar_dados(df)
        lbl_contador.configure(text=f"{len(df)} registro(s)")
        lbl_total.configure(text=f"Total: {len(df)} registro(s)")

    # ── INICIALIZAÇÃO BASEADA NO PARÂMETRO ──
    if pagina_inicial.lower() == "pendentes":
        aba_padrao = opt_pend
        df_inicial = preparar(carregar_pendentes())
    else:
        aba_padrao = opt_contab
        df_inicial = preparar(carregar_contabilizados())

    seletor.set(aba_padrao)
    tabela.carregar_dados(df_inicial)
    lbl_contador.configure(text=f"{len(df_inicial)} registro(s)")
    lbl_total.configure(text=f"Total: {len(df_inicial)} registro(s)")

    popup.update_idletasks()
    popup.deiconify()
    popup.lift()
    popup.focus_force()
    popup.grab_set()
    popup.attributes("-topmost", True)

    try:
        if hasattr(app, 'cfg') and hasattr(app.cfg, 'icon_path') and app.cfg.icon_path.exists():
            popup.after(200, lambda: popup.iconbitmap(str(app.cfg.icon_path)))
    except Exception:
        pass