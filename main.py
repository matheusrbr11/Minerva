from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException
import customtkinter as ctk
from pathlib import Path
import pandas as pd
import subprocess
import threading
import traceback
import logging
import sqlite3
import json
import os

from eop_ui import AppConfig, BaseApp
from jupiter import configurar_log, Siafe, GraphAPI
from tela_db import construir_tela_db
import dicts

logger = logging.getLogger("jupiter.Minerva")
tipo_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

class ColetorErros(logging.Handler):
    """Acumula os registros de ERRO da sessão (do app e da biblioteca) para o resumo enviado ao fechar."""

    def __init__(self, destino: list, level=logging.ERROR):
        super().__init__(level=level)
        self._destino = destino  # lista onde os erros vão sendo guardados

    def emit(self, record):
        # chamado pelo logging a cada erro; guarda os dados num dict pra montar o resumo depois
        try:
            # se tiver exceção, formata o traceback completo em texto
            tb = "".join(traceback.format_exception(*record.exc_info)) if record.exc_info else ""
            self._destino.append({
                "timestamp": pd.Timestamp.fromtimestamp(record.created).strftime("%d/%m/%Y %H:%M:%S"),
                "origem": record.name,
                "mensagem": record.getMessage(),
                "traceback": tb,
            })
        except Exception:
            self.handleError(record)

class MinervaApp(BaseApp):
    def __init__(self):
        cfg = AppConfig(
            app_name="Programa Minerva",
            app_version="1.3.0",
            window_width=500,
            window_height=650,
            login_subtitle="⚠️ Faça Login com os dados do Siafe-Rio2. ⚠️",
            login_user_label="Usuário (CPF):",
            user_max_length=11,       # Limita a entrada a 11 caracteres (CPF)
            user_digits_only=True,    # Filtra automaticamente para apenas números
            user_exact_length=True    # Habilita o botão apenas com exatos 11 dígitos
        )
        super().__init__(cfg)
        
        self.siafeVersao = 2             # 1 = Prod | 2 = Beta
        
        self.DBPath = self.cfg.base_path / "base de dados" / "DAF.db"
        self.DAFPath = self.cfg.base_path / "DAF.py"
        
        self.siafe = Siafe()             # controla o navegador/sessão do siafe
        self.stop_event = False          # vira True quando o usuário cancela a rotina
        self.opcao_selecionada = None    # tipo de contabilização escolhido no combo
        
        self.graph = None                # GraphAPI; definido em __main__ após configurar_log
        self.dev_emails = []             # destinatários do e-mail de erro
        self.teams_webhook = None        # webhook do Teams (opcional)
        self.erros_acumulados = []       # falhas críticas da sessão; resumo enviado ao fechar
        
        self.show_login_frame(on_success=lambda u, s: self.show_config_frame())
        
    def _enviar_resumo_erros(self):
        """Envia, uma única vez ao fechar, um resumo dos erros da sessão por e-mail e/ou Teams."""
        # sem graph configurado ou sem erros, não há o que enviar
        if not self.graph or not self.erros_acumulados:
            return

        total = len(self.erros_acumulados)
        # monta o corpo da mensagem linha a linha
        linhas = [
            "Resumo de erros — Programa Minerva",
            f"Usuário: {os.getlogin()}",
            f"Total de erros na sessão: {total}",
        ]
        for i, err in enumerate(self.erros_acumulados, 1):
            linhas.append("")
            linhas.append(f"[{i}] {err['timestamp']} — {err['origem']}")
            linhas.append(err["mensagem"])
            if err["traceback"]:
                linhas.append(err["traceback"].strip())
        mensagem = "\n".join(linhas)
        titulo = f"[Minerva] {total} erro(s) na execução"

        try:
            # manda por e-mail e/ou teams, conforme o que estiver configurado
            if self.dev_emails:
                self.graph.enviar_email(titulo=titulo, mensagem=mensagem, destinatarios=self.dev_emails)
            if self.teams_webhook:
                self.graph.enviar_mensagem(self.teams_webhook, f"{titulo}\n\n{mensagem}", self.dev_emails)
        except Exception:
            # se falhar o envio, não deixa isso derrubar o fechamento do app
            logger.error("Falha ao enviar o resumo de erros aos desenvolvedores", exc_info=True)

    def report_callback_exception(self, exc, val, tb):
        """Erros não tratados na interface (Tkinter) — logados e capturados para o resumo."""
        logger.error("Erro não tratado na interface", exc_info=(exc, val, tb))

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
        
        self.make_primary_button(
            frame_daf, text="BANCO DE DADOS",
            command=lambda: self.mostrar_pendentes_popup("Programa Minerva", tipo_ids)
        ).pack(pady=5)

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
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 21)", con)
                    dict_map     = dicts.dict_map_gr
                    metodo_siafe = self.siafe.gerar_documento
                    documento    = self.siafe.gerar_GR
                    tipo_doc     = "Guia de Recolhimento"
                    
                elif "PASEP (PD)" in self.opcao_selecionada:
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22)", con)
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
            self.after(0, self.mostrar_pendentes_popup("Programa Minerva", tipo_ids, pagina_inicial="pendentes"))
            if not self.stop_event:
                logger.info("Fechando navegador.")
            if hasattr(self, 'siafe') and self.siafe.driver:
                self.siafe.fechar_driver()
            
            self.after(5000, self.show_config_frame)
            logger.info("Programa encerrado. Retornando ao menu principal.")

    # =========================================================================
    # POPUP: CONTABILIZAÇÕES PENDENTES
    # =========================================================================
    def mostrar_pendentes_popup(self, programa_nome, tipo_ids, pagina_inicial):

        # constrói e exibe o popup de consulta ao banco (código em tela_db.py)
        # programa_nome/tipo_ids definem a visão inicial (contabilizados do programa atual)
        construir_tela_db(self, programa_nome, tipo_ids, pagina_inicial=pagina_inicial) 

if __name__ == "__main__":
    app = MinervaApp()
    
    pasta_erros = Path(__file__).parent / "logs"
    pasta_geral = fr"\\cifs-zone1\tesouro\Programas da SUPCONC\logs\Programa Minerva"
    caminho_geral, caminho_erros = configurar_log("Programa Minerva", pasta_geral, pasta_erros, callback_interface=app.log)
    
    # Coleta automática de todo logger.error() (do app e da biblioteca) para o resumo enviado ao fechar
    logging.getLogger("jupiter").addHandler(ColetorErros(app.erros_acumulados))

    # Notificação de erros aos desenvolvedores: credenciais em config.json (gitignored).
    # Se o arquivo faltar/estiver incompleto, a notificação apenas fica desativada.
    try:
        config = json.loads((Path(__file__).parent / "config.json").read_text(encoding="utf-8"))
        app.dev_emails = config.get("desenvolvedores", [])
        app.teams_webhook = config.get("webhook_teams") or None
        # só cria o GraphAPI se todas as credenciais estiverem presentes
        if all(config.get("graph_api", {}).get(k) for k in ("tenant_id", "client_id", "client_secret", "conta_corporativa")):
            app.graph = GraphAPI(**config["graph_api"])
    except Exception:
        logger.warning("Notificação de erros desativada (config.json ausente ou inválido)", exc_info=True)

    def ao_fechar():
        # ao fechar a janela: envia o resumo e só então encerra liberando os recursos
        app._enviar_resumo_erros()  # resumo dos erros acumulados na sessão (se houver)
        app.safe_exit(app.limpar_recursos)

    # liga o clique no "X" da janela à rotina de fechamento e inicia o loop da interface
    app.protocol("WM_DELETE_WINDOW", ao_fechar)
    app.mainloop()