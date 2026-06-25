from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException
import customtkinter as ctk
from pathlib import Path
import pandas as pd
import subprocess
import threading
import logging
import sqlite3
import os

from eop_ui import AppConfig, BaseApp
from jupiter import configurar_log, Siafe
import dicts

logger = logging.getLogger("jupiter.Minerva")

class MinervaApp(BaseApp):
    def __init__(self):
        cfg = AppConfig(
            app_name="Programa Minerva",
            app_version="1.2.0",
            window_width=500,
            window_height=650,
            login_subtitle="⚠️ Faça Login com os dados do Siafe-Rio2. ⚠️",
            login_user_label="Usuário (CPF):",
            user_max_length=11,       # Limita a entrada a 11 caracteres (CPF)
            user_digits_only=True,    # Filtra automaticamente para apenas números
            user_exact_length=True    # Habilita o botão apenas com exatos 11 dígitos
        )
        super().__init__(cfg)
        
        self.siafeVersao = 1
        self.DBPath = self.cfg.base_path / "base de dados" / "DAF.db"
        self.DAFPath = self.cfg.base_path / "DAF.py"
        
        self.siafe = Siafe()
        self.stop_event = False
        self.opcao_selecionada = None 
        
        self.show_login_frame(on_success=lambda u, s: self.show_config_frame())

    # =========================================================================
    # EVENTOS DE NAVEGAÇÃO
    # =========================================================================
    def cancelar_e_voltar(self):
        """Cancela a execução e retorna ao menu de configuração"""
        self.stop_event = True
        try: 
            if self.siafe.driver:
                self.siafe.fechar_driver()
        except: pass
        self.show_config_frame()
        
    def limpar_recursos(self):
        """Hook para encerramento limpo da aplicação (botão fechar)"""
        self.stop_event = True
        try:
            if hasattr(self, 'siafe') and self.siafe.driver:
                self.siafe.fechar_driver()
        except: pass

    # =========================================================================
    # TELA DE CONFIGURAÇÃO (MENU PRINCIPAL)
    # =========================================================================
    def show_config_frame(self):
        self.clear_frame()
        self.create_menu()
        
        self.add_back_button(lambda: self.show_login_frame(on_success=lambda u, s: self.show_config_frame()))
        self._add_logo()
        
        self.make_header_label("Minerva", pady=(20, 5))
        self.make_subtitle_label("Menu Principal", pady=(0, 20))

        # --- ÁREA 1: ATUALIZAÇÃO DE BASE (DAF) ---
        frame_daf = self.make_section_frame()
        
        self.btn_daf = self.make_primary_button(
            frame_daf, 
            text="PROCESSAR DAF", 
            command=self.iniciar_daf_thread
        )
        self.btn_daf.pack(pady=(5, 15))

        # --- ÁREA 2: CONTABILIZAÇÃO (Siafe) ---
        frame_contab = self.make_section_frame()
        
        ctk.CTkLabel(frame_contab, text="Tipo de Contabilização:", font=self.font_bold).pack(pady=(5, 5))
        self.combo_opcoes = ctk.CTkComboBox(
            frame_contab, values=["Receita (GR)", "PASEP (PD)"], 
            width=250, height=35, command=self.validar_selecao
        )
        self.combo_opcoes.set("Selecione uma opção")
        self.combo_opcoes.pack(pady=5)

        self.btn_contab = self.make_success_button(
            frame_contab, 
            text="CONTABILIZAR", 
            command=self.iniciar_execucao
        )
        self.btn_contab.pack(pady=20)
        
        self.btn_contab.configure(state="disabled", fg_color=self.cfg.color_disabled)
        self._add_footer()

    def validar_selecao(self, choice):
        if choice in ["Receita (GR)", "PASEP (PD)"]:
            self.btn_contab.configure(state="normal", fg_color=self.cfg.color_success)
            self.opcao_selecionada = choice
        else:
            self.btn_contab.configure(state="disabled", fg_color=self.cfg.color_disabled)

    def iniciar_daf_thread(self):
        self.btn_daf.configure(state="disabled")
        threading.Thread(target=subprocess.run, args=(["python", self.DAFPath],), daemon=True).start()

    def iniciar_execucao(self):
        self.show_execution_frame(on_cancel=self.cancelar_e_voltar)
        self.stop_event = False
        threading.Thread(target=self.execucao, daemon=True).start()

    # =========================================================================
    # BACKEND: BANCO DE DADOS E EXECUÇÃO
    # =========================================================================
    def atualizar_banco(self, id, num_documento, tempo_contab=None):
        """Callback acionado por Siafe a cada documento finalizado"""
        try:
            with sqlite3.connect(self.DBPath) as con:
                cursor = con.cursor()
                query = '''UPDATE contabilizacoes SET num_documento = ?, usuario_contab = ?, data_hora_contab = ?, tempo_contab = ? WHERE id = ?'''
                cursor.execute(query, (num_documento, os.getlogin(), str(pd.Timestamp.now()), tempo_contab, id))
                con.commit()
                
            self.registros_processados += 1
            valor_barra = self.registros_processados / self.total_registros 
               
            self.update_progress(valor_barra)
            
        except Exception:
            logger.error(f"Erro ao atualizar banco ID {id}", exc_info=True)

    def execucao(self):
        """Lógica de processamento em background"""
        try:
            logger.info("Verificando banco de dados.")
            if not self.DBPath.exists():
                logger.error("Banco de dados não encontrado.", exc_info=True)
                return

            with sqlite3.connect(self.DBPath) as con:
                if "Receita (GR)" in self.opcao_selecionada:
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)", con)
                    dict_map     = dicts.dict_map_gr
                    metodo_siafe = self.siafe.gerar_documento
                    documento    = self.siafe.gerar_GR
                    tipo_doc     = "Guia de Recolhimento"
                    
                elif "PASEP (PD)" in self.opcao_selecionada:
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20)", con)
                    dict_map     = dicts.dict_map_pd
                    metodo_siafe = self.siafe.gerar_documento
                    documento    = self.siafe.gerar_PDT
                    tipo_doc     = "PD de Transferência"
                else:
                    logger.warning("Opção inválida.")
                    return

            if df.empty:
                logger.warning(f"Nenhum lançamento pendente encontrado para {tipo_doc}.")
                self.finalize_progress("Processado... (100%)", "Aviso", "Não há lançamentos pendentes para processar.", "info")
                self.stop_event = True
                return

            logger.info(f"{len(df)} registros encontrados.")
            self.total_registros = len(df)
            self.registros_processados = 0
            
            self.reset_progress()

            self.siafe.abrir_driver()
            logger.info("Iniciando navegador.")
            
            if self.stop_event: return

            logger.info("Iniciando Contabilização.")
            if self.siafe.logar_siafe(self.siafeVersao, self._usuario, self._senha):

                sucesso = metodo_siafe(documento, df, dict_map, callback_sucesso=self.atualizar_banco)

                if sucesso:
                    logger.info(">>> Processo concluído com Sucesso! <<<")
                    self.finalize_progress("Processado... (100%)", "Sucesso", f"{tipo_doc} contabilizadas com sucesso!", "info")

            else:
                logger.warning("Falha no login. Verifique suas credenciais.")
                self.stop_event = True
                self.siafe.fechar_driver()
                
                def fechar_e_voltar():
                    self.finalize_progress(label="Falha no Login")
                    self.show_login_frame(on_success=lambda u, s: self.show_config_frame())
                self.after(0, fechar_e_voltar)
                return

        except (NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException):
            if self.stop_event: return
            logger.error("Ocorreu um erro crítico com o navegador.\nPor favor, reinicie o programa.", exc_info=True)
            return

        except Exception:
            if self.stop_event: return
            logger.error("Ocorreu um erro inesperado.", exc_info=True)
            self.messagebox_error("Erro", "Ocorreu um erro inesperado.")

        finally:
            self.after(0, self.mostrar_pendentes_popup)
            if not self.stop_event:
                logger.info("Fechando navegador.")
            if hasattr(self, 'siafe') and self.siafe.driver:
                self.siafe.fechar_driver()
            
            self.after(5000, self.show_config_frame)
            logger.info("Programa encerrado. Retornando ao menu principal.")

    # =========================================================================
    # POPUP: CONTABILIZAÇÕES PENDENTES
    # =========================================================================
    def mostrar_pendentes_popup(self):
        """Exibe um popup com os lançamentos não contabilizados."""
        try:
            with sqlite3.connect(self.DBPath) as con:
                df_pend = pd.read_sql_query(
                    "SELECT data, observacao, valor FROM contabilizacoes WHERE num_documento IS NULL", con
                )
        except Exception:
            logger.error("Erro ao buscar lançamentos pendentes.", exc_info=True)
            return

        if df_pend.empty:
            return 

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

        if "valor" in [c.lower() for c in df_pend.columns]:
            df_pend["valor"] = df_pend["valor"].apply(formatar_moeda)

        limite_caracteres = 140  
        if "observacao" in [c.lower() for c in df_pend.columns]:
            df_pend["observacao"] = df_pend["observacao"].apply(
                lambda x: str(x)[:limite_caracteres] + "..." if pd.notna(x) and len(str(x)) > limite_caracteres else str(x)
            )

        df_pend = df_pend.fillna("---")
        colunas = list(df_pend.columns)

        hoje = pd.Timestamp.now()
        mes_atual = hoje.month
        ano_atual = hoje.year

        mes_anterior = 12 if mes_atual == 1 else mes_atual - 1
        ano_mes_anterior = ano_atual - 1 if mes_atual == 1 else ano_atual

        # Dicionário de bloqueio contábil
        ano_prazo = ano_atual
        prazos_fechamento = {
            1: f"12/02/{ano_prazo}", 2: f"06/03/{ano_prazo}", 3: f"09/04/{ano_prazo}",
            4: f"08/05/{ano_prazo}", 5: f"09/06/{ano_prazo}", 6: f"07/07/{ano_prazo}",
            7: f"07/08/{ano_prazo}", 8: f"08/09/{ano_prazo}", 9: f"07/10/{ano_prazo}",
            10: f"09/11/{ano_prazo}", 11: f"07/12/{ano_prazo}", 12: f"08/01/{ano_prazo}"
        }
        
        data_bloq_contab = prazos_fechamento.get(mes_anterior, "Data Indefinida")
        tem_pendencia_mes_anterior = False

        if "data" in [c.lower() for c in df_pend.columns]:
            datas_dt = pd.to_datetime(df_pend['data'], dayfirst=True, errors='coerce')
            
            tem_pendencia_mes_anterior = (
                (datas_dt.dt.month == mes_anterior) & 
                (datas_dt.dt.year == ano_mes_anterior)
            ).any()

        col_widths = []
        for col in colunas:
            max_len = df_pend[col].astype(str).map(len).max()
            header_len = len(col)
            width = max(max_len, header_len) * 7 + 15 # pixels + margem
            col_widths.append(width)

        total_width = sum(col_widths) + 50 # scrollbar
        pw = int(min(max(total_width, 1100), 1600)) # largura da janela entre 1100 e 1600
        ph = 540
        
        if tem_pendencia_mes_anterior:
            ph += 55

        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws / 2) - (pw / 2))
        y = int((hs / 2) - (ph / 2))
        
        idx_obs = colunas.index("observacao") if "observacao" in colunas else -1

        # --- Estilos e Fontes ---
        fonte_titulo = ctk.CTkFont(family="Roboto", size=18, weight="bold")
        fonte_subtitulo = ctk.CTkFont(family="Roboto", size=12)
        fonte_header = ctk.CTkFont(family="Roboto", size=11, weight="bold")
        fonte_celula = ctk.CTkFont(family="Roboto", size=11)
        fonte_botao = ctk.CTkFont(family="Roboto", size=13, weight="bold")

        tema = {
            "bg_janela": "#f5f7fa", "header_bg": "#2B3A4A", "header_text": "#FFFFFF",
            "aviso_bg": "#fff3cd", "aviso_text": "#856404", "tabela_borda": "#e8edf2",
            "tabela_header": "#34495E", "linha_par": "#f0f6ff", "linha_impar": "#ffffff",
            "texto_tabela": "#2b2b2b", "btn_fechar": "#d9534f", "btn_hover": "#b52b27",
            "alerta_bg": "#f8d7da", "alerta_text": "#721c24"
        }

        popup = ctk.CTkToplevel(self)
        popup.attributes("-alpha", 0.0) 
        popup.title("Contabilizações Pendentes")
        popup.geometry('%dx%d+%d+%d' % (pw, ph, x, y))
        popup.resizable(False, False)
        popup.configure(fg_color=tema["bg_janela"])
        # --- Header ---
        header = ctk.CTkFrame(popup, fg_color=tema["header_bg"], corner_radius=0, height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Contabilizações Pendentes", font=fonte_titulo, text_color=tema["header_text"]).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(header, text=f"{len(df_pend)} pendência(s)", font=fonte_subtitulo, text_color="#A9C2D9").pack(side="right", padx=15)
        # --- Aviso de mês anterior ---
        if tem_pendencia_mes_anterior:
            alerta = ctk.CTkFrame(popup, fg_color=tema["alerta_bg"], corner_radius=0, height=50)
            alerta.pack(fill="x")
            alerta.pack_propagate(False)
            texto_critico = f"🚨 Há lançamentos do mês anterior não contabilizados! Contabilize até {data_bloq_contab}."
            ctk.CTkLabel(alerta, text=texto_critico, font=ctk.CTkFont(family="Roboto", size=12, weight="bold"), text_color=tema["alerta_text"], wraplength=pw - 40, justify="left").pack(anchor="w", padx=20, pady=13)
        # --- Aviso Padrão ---
        aviso = ctk.CTkFrame(popup, fg_color=tema["aviso_bg"], corner_radius=0, height=50)
        aviso.pack(fill="x")
        aviso.pack_propagate(False)
        ctk.CTkLabel(aviso, text="⚠️ Os lançamentos listados abaixo ainda não foram contabilizados.", font=fonte_subtitulo, text_color=tema["aviso_text"], wraplength=pw - 40, justify="left").pack(anchor="w", padx=20, pady=13)
        # --- Tabela ---
        table_outer = ctk.CTkFrame(popup, fg_color=tema["tabela_borda"], corner_radius=8)
        table_outer.pack(fill="both", expand=True, padx=12, pady=(10, 6))

        header_row = ctk.CTkFrame(table_outer, fg_color=tema["tabela_header"], corner_radius=6, height=36)
        header_row.pack(fill="x", padx=2, pady=(2, 0))
        header_row.pack_propagate(False)
        
        if idx_obs != -1: header_row.grid_columnconfigure(idx_obs, weight=1)
        
        for j, col in enumerate(colunas):
            ctk.CTkLabel(
                header_row, text=col.replace("_", " ").upper(),
                font=fonte_header, text_color="white", anchor="center", width=col_widths[j]
            ).grid(row=0, column=j, sticky="nsew", padx=1, pady=6)

        scroll_area = ctk.CTkScrollableFrame(table_outer, fg_color="transparent", corner_radius=0)
        scroll_area.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        if idx_obs != -1: scroll_area.grid_columnconfigure(idx_obs, weight=1)

        for i, (_, row) in enumerate(df_pend.iterrows()):
            bg = tema["linha_par"] if i % 2 == 0 else tema["linha_impar"]
            for j, val in enumerate(row):
                cell_text = str(val) if val is not None else "---"
                w = col_widths[j] if j != idx_obs else 0

                entry = ctk.CTkEntry(
                    scroll_area, font=fonte_celula, fg_color=bg, text_color=tema["texto_tabela"],
                    corner_radius=0, border_width=0, height=30, width=w, justify="center"
                )
                entry.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                entry.insert(0, cell_text)
                entry.configure(state="readonly")
        # --- Footer ---
        footer = ctk.CTkFrame(popup, fg_color=tema["bg_janela"], corner_radius=0, height=52)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        ctk.CTkLabel(footer, text=f"Total de pendências: {len(df_pend)} registro(s)", font=fonte_subtitulo, text_color="#666666").pack(side="left", padx=20, pady=12)
        ctk.CTkButton(footer, text="Fechar", width=120, height=34, fg_color=tema["btn_fechar"], hover_color=tema["btn_hover"], font=fonte_botao, command=popup.destroy).pack(side="right", padx=20, pady=9)

        popup.update()
        popup.attributes("-alpha", 1.0) 
        popup.grab_set()
        popup.attributes("-topmost", True)
        if self.cfg.icon_path.exists():
            popup.after(100, lambda: popup.iconbitmap(str(self.cfg.icon_path)))  

if __name__ == "__main__":
    app = MinervaApp()
    
    pasta_erros = Path(__file__).parent / "logs"
    pasta_geral = fr"\\cifs-zone1\tesouro\Programas da SUPCONC\logs\Programa Minerva"
    caminho_geral, caminho_erros = configurar_log("Programa Minerva", pasta_geral, pasta_erros, callback_interface=app.log)
    
    app.protocol("WM_DELETE_WINDOW", lambda: app.safe_exit(app.limpar_recursos))
    app.mainloop()