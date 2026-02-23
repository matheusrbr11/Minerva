import subprocess
import customtkinter as ctk
from tkinter import Menu, messagebox
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException
from pathlib import Path
from PIL import Image
import pandas as pd
import threading
import sqlite3
import time
import sys
import os

from jupiter import Siafe

# Configuração Global
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue")

PROJECT_BASE_PATH = Path(__file__).parent

class MinervaApp(ctk.CTk, Siafe):
    def __init__(self):
        super().__init__()
        
        self.siafeVersao = 2  # Versão do SIAFE a ser utilizada (1 para SIAFE-Rio2 ou 2 para SIAFE-Rio2 BETA)
        
        # --- Paths ---
        self.DBPath = PROJECT_BASE_PATH / "base de dados" / "DAF.db"
        self.IconPath = PROJECT_BASE_PATH / "img/icon.ico"
        self.ImagePath = PROJECT_BASE_PATH / "img/tesouro.png"
        self.VoltarPath = PROJECT_BASE_PATH / "img/voltar.png"
        self.ManualPath = PROJECT_BASE_PATH / "Manual de Uso.pdf"
        self.DAFPath = PROJECT_BASE_PATH / "DAF.py"
        
        # --- Configuração da Janela ---
        self.title("Programa Minerva")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color="white")
        
        # --- Icone da Janela ---
        if self.IconPath.exists():
            self.iconbitmap(self.IconPath)
        
        # # --- Posicionamento da Janela ---
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (500/2)
        y = (hs/2) - (650/2)
        self.geometry('%dx%d+%d+%d' % (500, 650, x, y))

        # --- Variáveis de Estado ---
        self.siafe = Siafe()
        self.usuario_siafe = ""
        self.senha_siafe = ""
        self.stop_event = False
        self.opcao_selecionada = None # Receita (GR) ou PASEP (PD)

        # --- Dicionários Contábeis ---
        self._inicializar_dicionarios()

        # --- Fontes ---
        self.font_header = ctk.CTkFont(family="Roboto", size=24, weight="bold")
        self.font_bold = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.font_label = ctk.CTkFont(family="Roboto", size=14, weight="normal")

        # --- Container Principal ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Inicia na Tela de Login
        self.show_login_frame()

    def clear_frame(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def adicionar_btn_voltar(self, comando):
        if self.VoltarPath.exists():
            img_pil = Image.open(self.VoltarPath)
            ctk_img = ctk.CTkImage(img_pil, size=(30, 30))
            btn = ctk.CTkButton(self.main_container, image=ctk_img, text="", width=10, 
                                fg_color="#ffffff", hover_color="#eeeeee", command=comando)
            btn.place(x=0, y=0)
            
    def cancelar_e_voltar(self):
        self.stop_event = True
        try: 
            if self.driver: self.siafe.fechar_driver()
        except: pass
        self.show_config_frame()
        
    def _create_main_menu(self):
        menu_bar = Menu(self.main_container)
        self.configure(menu=menu_bar)
        menu_bar.add_cascade(label="Sobre (F1)", command=self.mostrar_sobre)
        self.bind("<F1>", lambda event: self.mostrar_sobre())
        menu_bar.add_cascade(label="Manual de Uso (F2)", command=self.mostrar_manual)
        self.bind("<F2>", lambda event: self.mostrar_manual())
        
    def mostrar_sobre(self):
        msg = "Programa Minerva\nVersão: 1.0.0 \nDesenvolvido por: EAP / SUPCONC"
        self.messagebox_info("Sobre", msg)

    def mostrar_manual(self):
        try: os.startfile(self.ManualPath)
        except: self.messagebox_error("Erro", "Manual não encontrado.")
        
    # =========================================================================
    # VALIDAÇÃO
    # =========================================================================
    def limitar_caracteres(self, P):
        """
        Validador para o campo de entrada de usuário.

        Args:
            P (str): O texto atual no campo de entrada.

        Returns:
            bool: True se a entrada for numérica e tiver no máximo 11 caracteres (ou vazia),
                  False caso contrário.
        """
        if (P.isdigit() and len(P) <= 11) or P == "":
            return True
        else:
            return False

    def verificar_campos(self, usuario_entry, senha_entry, login_button):
        """
        Monitora os campos de login em tempo real para habilitar/desabilitar o botão.

        Lógica:
            - Usuário deve ter exatamente 11 caracteres.
            - Senha não pode estar vazia.
        
        Args:
            usuario_entry (ctk.CTkEntry): Widget de entrada do usuário.
            senha_entry (ctk.CTkEntry): Widget de entrada da senha.
            login_button (ctk.CTkButton): O botão de login a ser atualizado.
        """
        usuario = usuario_entry.get()
        senha = senha_entry.get()
        is_ctk_button = isinstance(login_button, ctk.CTkButton)
        
        if len(usuario) == 11 and senha.strip():
            if is_ctk_button: login_button.configure(state="normal", fg_color="#1f6aa5")
            else: login_button.config(state="normal")
        else:
            if is_ctk_button: login_button.configure(state="disabled", fg_color="#555555")
            else: login_button.config(state="disabled")

    # =========================================================================
    # TELA 1: LOGIN
    # =========================================================================
    def show_login_frame(self):
        self.clear_frame()
        self._create_main_menu()
        
        # Imagem
        if self.ImagePath.exists():
            try:
                pil_image = Image.open(self.ImagePath)
                img_ctk = ctk.CTkImage(pil_image, size=(105, 105))
                ctk.CTkLabel(self.main_container, text="", image=img_ctk).pack(pady=(10, 5))
            except: pass

        ctk.CTkLabel(self.main_container, text="Minerva", font=self.font_header).pack(pady=(5, 5))
        ctk.CTkLabel(self.main_container, text="⚠️ Faça Login com os dados do Siafe-Rio2. ⚠️", 
                     text_color="red", font=("Roboto", 14)).pack(pady=(0, 20))

        # Body
        ctk.CTkLabel(self.main_container, text="Usuário (CPF):", font=self.font_label).pack(pady=(5, 0))
        val_cmd = self.register(self.limitar_caracteres)
        self.entry_user = ctk.CTkEntry(self.main_container, width=300, height=40, validate="key", validatecommand=(val_cmd, '%P'))
        self.entry_user.pack(pady=(2, 10))
        
        ctk.CTkLabel(self.main_container, text="Senha:", font=self.font_label).pack(pady=(5, 0))
        self.entry_pass = ctk.CTkEntry(self.main_container, width=300, height=40, show="*")
        self.entry_pass.pack(pady=(2, 20))
        
        # Button
        self.btn_login = ctk.CTkButton(self.main_container, text="LOGIN", width=300, height=45,
                                       state="disabled", fg_color="#555555", command=self.processar_login)
        self.btn_login.pack(pady=20)
        
        # Footer        
        ctk.CTkLabel(self.main_container, text="EOP / SUPCONC - Tesouro Estadual", 
                     font=("Roboto", 10), text_color="gray").pack(side="bottom", pady=10)
        
        # Binds
        self.entry_user.bind("<KeyRelease>", lambda e: self.verificar_campos(self.entry_user, self.entry_pass, self.btn_login))
        self.entry_pass.bind("<KeyRelease>", lambda e: self.verificar_campos(self.entry_user, self.entry_pass, self.btn_login))
        self.bind('<Return>', lambda event: self.processar_login())

    def processar_login(self):
        if self.btn_login.cget("state") == "disabled": return
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        self.usuario_siafe = user
        self.senha_siafe = pwd
        self.unbind('<Return>')
        self.show_config_frame()

    # =========================================================================
    # TELA 2: CONFIGURAÇÃO
    # =========================================================================
    def show_config_frame(self):
        self.clear_frame()
        self._create_main_menu()
        self.adicionar_btn_voltar(self.show_login_frame)

        # Imagem
        if self.ImagePath.exists():
            try:
                pil_image = Image.open(self.ImagePath)
                img_ctk = ctk.CTkImage(pil_image, size=(105, 105))
                ctk.CTkLabel(self.main_container, text="", image=img_ctk).pack(pady=(10, 5))
            except: pass
            
        # Header
        ctk.CTkLabel(self.main_container, text="Minerva", font=self.font_header).pack(pady=(20, 5))
        ctk.CTkLabel(self.main_container, text="Menu Principal", font=self.font_label).pack(pady=(0, 20))

        # --- ÁREA 1: ATUALIZAÇÃO DE BASE (DAF) ---
        frame_daf = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame_daf.pack(fill="x", pady=10)
        
        self.btn_daf = ctk.CTkButton(frame_daf, text="PROCESSAR DAF", width=250, height=40,
                                         font=self.font_bold, fg_color="#1f6aa5", hover_color="#144d7a",
                                         command=self.iniciar_daf_thread)
        self.btn_daf.pack(pady=(5, 15))


        # --- ÁREA 2: CONTABILIZAÇÃO (Siafe) ---
        frame_contab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame_contab.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame_contab, text="Tipo de Contabilização:", font=self.font_bold).pack(pady=(5, 5))
        self.combo_opcoes = ctk.CTkComboBox(frame_contab, values=["Receita (GR)", "PASEP (PD)"], width=250, height=35)
        self.combo_opcoes.set("Selecione uma opção")
        self.combo_opcoes.pack(pady=5)

        self.btn_contab = ctk.CTkButton(frame_contab, text="CONTABILIZAR", width=250, height=50,
                                        font=self.font_bold, fg_color="#4CAF50", hover_color="#45a049",
                                        command=self.iniciar_execucao)
        self.btn_contab.pack(pady=20)
        
        # Footer        
        ctk.CTkLabel(self.main_container, text="EOP / SUPCONC - Tesouro Estadual", 
                     font=("Roboto", 10), text_color="gray").pack(side="bottom", pady=10)
        
        self.combo_opcoes.configure(command=self.validar_selecao)
        self.btn_contab.configure(state="disabled", fg_color="#555555")

    def validar_selecao(self, choice):
        if choice in ["Receita (GR)", "PASEP (PD)"]:
            self.btn_contab.configure(state="normal", fg_color="#4CAF50")
            self.opcao_selecionada = choice
        else:
            self.btn_contab.configure(state="disabled", fg_color="#555555")

    def iniciar_daf_thread(self):
        self.btn_daf.configure(state="disabled")
        threading.Thread(target=self.executar_daf, daemon=True).start()

    def executar_daf(self):
        subprocess.run(["python", self.DAFPath])

    def iniciar_execucao(self):
        self.show_execucao_frame()
        self.stop_event = False
        threading.Thread(target=self.execucao, daemon=True).start()

    # =========================================================================
    # TELA 3: EXECUÇÃO (Log Visual)
    # =========================================================================
    def show_execucao_frame(self):
        self.clear_frame()
        self._create_main_menu()
        self.adicionar_btn_voltar(self.cancelar_e_voltar)
        
        self.label = ctk.StringVar(value="Processando... (0%)")

        # Header
        ctk.CTkLabel(self.main_container, textvariable=self.label, font=self.font_header).pack(pady=10)
        self.progress = ctk.CTkProgressBar(self.main_container, width=400, mode="determinate")
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Body
        self.log_box = ctk.CTkTextbox(self.main_container, width=450, height=350)
        self.log_box.pack(pady=10)
        self.log_box.insert("0.0", ">>> Iniciando processamento...\n")
        
        # Footer
        ctk.CTkLabel(self.main_container, text="EOP / SUPCONC - Tesouro Estadual", 
                     font=("Roboto", 10), text_color="gray").pack(side="bottom", pady=10)

    def log(self, msg):        
        if not self.winfo_exists() or not hasattr(self, 'log_box'): return
        try:
            self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_box.see("end")
        except: pass
        
    def messagebox_info(self, title, message):
        """
        Exibe uma mensagem de sucesso na interface gráfica.
        
        Args:
            title (str): O cabeçalho da mensagem.
        """
        self.attributes('-topmost', True)
        messagebox.showinfo(title, message)
        self.attributes('-topmost', False)
    
    def messagebox_warning(self, title, message):
        """
        Exibe uma mensagem de aviso na interface gráfica.
        
        Args:
            title (str): O cabeçalho da mensagem.
        """
        self.attributes('-topmost', True)
        messagebox.showwarning(title, message)
        self.attributes('-topmost', False)
        
    def messagebox_error(self, title, message):
        """
        Exibe uma mensagem de erro na interface gráfica.
        
        Args:
            title (str): O cabeçalho da mensagem.
        """
        self.attributes('-topmost', True)
        messagebox.showerror(title, message)
        self.attributes('-topmost', False)

    # =========================================================================
    # BACKEND
    # =========================================================================
    def atualizar_banco(self, id, num_documento, tempo_contab=None):
        """Callback para atualizar o banco de dados"""
        try:
            with sqlite3.connect(self.DBPath) as con:
                cursor = con.cursor()
                query = '''UPDATE contabilizacoes SET num_documento = ?, tempo_contab = ?, usuario = ?, data_hora = ? WHERE id = ?'''
                cursor.execute(query, (num_documento, tempo_contab, os.getlogin(), str(pd.Timestamp.now()), id))
                con.commit()
                
            self.registros_processados += 1
            percentual_inteiro = int((self.registros_processados / self.total_registros) * 100)  
            valor_barra = self.registros_processados / self.total_registros    
            self.label.set(f"Processando... ({percentual_inteiro}%)")
            self.progress.set(valor_barra)
            
        except Exception as e:
            self.log(f"Erro ao atualizar banco ID {id}: {e}")

    def execucao(self):
        try:
            # 1. Conexão com Banco
            self.log("Verificando banco de dados...")
            if not self.DBPath.exists():
                self.log("ERRO: Banco de dados não encontrado.")
                return

            # 2. Seleção de Dados
            with sqlite3.connect(self.DBPath) as con:
                if "Receita (GR)" in self.opcao_selecionada:
                    # IDs 1 a 10 são Receitas
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)", con)
                    dict_map = self.dict_map_gr
                    metodo_siafe = self.siafe.gerar_gr
                    tipo_doc = "Guia de Recolhimento"
                    
                elif "PASEP (PD)" in self.opcao_selecionada:
                    # IDs 11 a 20 são PDs
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20)", con)
                    dict_map = self.dict_map_pd
                    metodo_siafe = self.siafe.gerar_pdt # PD de Transferência
                    tipo_doc = "PD de Transferência"
                else:
                    self.log("Opção inválida.")
                    return

            if df.empty:
                self.log(f"Nenhum lançamento pendente encontrado para {tipo_doc}.")
                self.label.set(f"Processado... (100%)")
                self.progress.stop()
                self.progress.set(1)
                self.messagebox_info("Aviso", "Não há lançamentos pendentes para processar.")
                self.stop_event = True
                return

            self.log(f"{len(df)} registros encontrados.")
            self.total_registros = len(df)
            self.registros_processados = 0
            self.progress.set(0)

            # 3. Automação
            self.siafe.abrir_driver()
            self.log("Iniciando navegador...")
            
            if self.stop_event: return

            self.log("Iniciando Contabilização...")
            if self.siafe.logar_siafe(self.siafeVersao, self.usuario_siafe, self.senha_siafe):
                sucesso = metodo_siafe(df, dict_map, callback_sucesso=self.atualizar_banco)

                if sucesso:
                    self.log(">>> Processo concluído com Sucesso! <<<")
                    self.label.set(f"Processado... (100%)")
                    self.messagebox_info("Sucesso", f"{tipo_doc} contabilizadas com sucesso!")
            else:
                self.log("Falha no login. Verifique suas credenciais.")
                self.stop_event = True
                self.progress.stop()
                self.progress.set(1)
                self.show_login_frame()
                return

        except (NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException) as e:
            self.log(f"Ocorreu um erro crítico com o navegador.\nPor favor, reinicie o programa.")
            if self.stop_event: return
            raise e

        except Exception as e:
            if not self.stop_event:
                self.log(f"Ocorreu um erro inesperado.")
                self.messagebox_error("Erro", f"Ocorreu um erro inesperado: {e}")
                if self.stop_event: return
        
        finally:
            self.log("Fechando navegador...")
            if not df.empty:
                self.siafe.fechar_driver()
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress.set(1)
            self.log("Programa Encerrado...")
        if self.stop_event: return

    # =========================================================================
    # DADOS ESTRUTURAIS
    # =========================================================================
    def _inicializar_dicionarios(self):
        # Definições para GR
        self.dictGR_ANP7990 = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "4879 - COTA-PARTE DA COMP. FINANC. DOS ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - ATÉ 5% - PÓS-SAL", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990103 - Out Rec Pat - Royalties pela Produção do Petróleo - Até 5%"}
        self.dictGR_ANP9478 = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "4881 - ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - EXCEDENTE A 5%", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990105 - Out Rec Pat - Royalties pela Produção do Petróleo - Excedente a 5%"}
        self.dictGR_PEA = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5686 - COTA PARTE PART. ESPECIAL EXP. PETR. E GAS NATURAL LEI 9.478/97", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990106 - Out Rec Pat - Participação Especial Exploração do Petróleo"}
        self.dictGR_FEP = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5723 - COTA PARTE FUNDO ESPECIAL DO PETROLEO", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990107 - Out Rec Pat - Fundo Especial do Petróleo - FEP"}
        self.dictGR_FPE = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916339", "DomicilioBancarioCompleto": "001 - 2234 - 2916339", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2038 - COTA-PARTE DO FUNDO DE PARTICIPAÇÃO DOS ESTADOS - FPE", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1711500101 - Cota-Parte FPE - Fundo de Participação dos Estados e do DF - Principal"}
        self.dictGR_IPI = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916363", "DomicilioBancarioCompleto": "001 - 2234 - 2916363", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2040 - COTA-PARTE DO ESTADO - IPI", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1711530101 - Cota-Parte IPI Exportação - Principal - LC 61/89"}
        self.dictGR_CFM = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916371", "DomicilioBancarioCompleto": "001 - 2234 - 2916371", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "708 - Transferência da União Referente à Compensação Financeira de Recursos Minerais", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Minerais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (708.101)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5682 - Cota-Parte da Compensação Financeira de Recursos Minerais", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1344020101 - Compensação Financeira pela Exploração de Recursos Minerais - Principal"}
        self.dictGR_CFH = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "291638X", "DomicilioBancarioCompleto": "001 - 2234 - 291638X", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "709 - Transferência da União referente à Compensação Financeira de Recursos Hídricos", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Hídricos", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (709.101)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5722 - COTA PARTE DA COMPENSAÇÃO FINANCEIRA RECURSOS HIDRICOS", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1345032101 - Utilização de Recursos Hídricos - Demais Empresas - Principal"}
        self.dictGR_CIDE = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916509", "DomicilioBancarioCompleto": "001 - 2234 - 2916509", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "750 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "FonteRJ": "126 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (750.126)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2044 - COTA-PARTE DO ESTADO NA CONTRIBUIÇÃO DE INTERVENÇÃO NO DOMÍNIO ECONÔMICO - CIDE", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1711540101 - Cota-Parte Contribuição de Intervenção no Domínio Econômico - CIDE - Principal"}
        self.dictGR_ADO = {"TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916312", "DomicilioBancarioCompleto": "001 - 2234 - 2916312", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "501 - Outros Recursos não Vinculados", "FonteRJ": "101 - Outros Recursos não Vinculados - Ordinários Não Provenientes de Impostos-Tesouro", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (501.101)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2055 - DEMAIS TRANSFERÊNCIAS DA UNIÃO", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1719990101 - Outras Transferências da União - Principal"}

        # Definições para PD
        self.dictPD_PASEP_ROYALTIES = {"UG": "999900", "UGFavorecida": "370200", "Regularizacao": "OB Regularização Financeira", "JustificativaRegularizacao": "RETENÇÃO-PASEP", "DomicilioBancarioOrigem": "2916347", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916347", "DomicilioBancarioDestino": "BCO AUTENT", "DomicilioBancarioDestinoCompleto": "001 - 2234 - BCO AUTENT", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "Indice": "1,000", "TipoPatrimonial": "Pagamentos a Regularizar", "ItemPatrimonial": "5678 - Pagamentos (Por Ofício) a Regularizar - FONTES TESOURO", "OperacaoPatrimonial": "4962 - Pagamentos (Por Ofícios) a Regularizar - FONTES TESOURO"}
        self.dictPD_PASEP_FPE = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_FPE.update({"DomicilioBancarioOrigem": "2916339", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916339", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)"})
        self.dictPD_PASEP_IPI = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_IPI.update({"DomicilioBancarioOrigem": "2916363", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916363", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)"})
        self.dictPD_PASEP_CFM = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_CFM.update({"DomicilioBancarioOrigem": "2916371", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916371", "Fonte": "708 - Transferência da União Referente à Compensação Financeira de Recursos Minerais", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Minerais", "DetalhamentoFonte": "000000 - Sem detalhamento - (708.101)"})
        self.dictPD_PASEP_CFH = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_CFH.update({"DomicilioBancarioOrigem": "291638X", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 291638X", "Fonte": "709 - Transferência da União referente à Compensação Financeira de Recursos Hídricos", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Hídricos", "DetalhamentoFonte": "000000 - Sem detalhamento - (709.101)"})
        self.dictPD_PASEP_CIDE = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_CIDE.update({"DomicilioBancarioOrigem": "2916509", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916509", "Fonte": "750 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "FonteRJ": "126 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "DetalhamentoFonte": "000000 - Sem detalhamento - (750.126)"})
        self.dictPD_PASEP_ADO = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_ADO.update({"DomicilioBancarioOrigem": "2916312", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916312", "Fonte": "501 - Outros Recursos não Vinculados", "FonteRJ": "101 - Outros Recursos não Vinculados - Ordinários Não Provenientes de Impostos-Tesouro", "DetalhamentoFonte": "000000 - Sem detalhamento - (501.101)"})

        # Mapas para uso na execução
        self.dict_map_gr = {
            1: self.dictGR_ANP7990, 2: self.dictGR_ANP9478, 3: self.dictGR_PEA,
            4: self.dictGR_FEP, 5: self.dictGR_FPE, 6: self.dictGR_IPI,
            7: self.dictGR_CFM, 8: self.dictGR_CFH, 9: self.dictGR_CIDE,
            10: self.dictGR_ADO
        }
        self.dict_map_pd = {
            11: self.dictPD_PASEP_ROYALTIES, 12: self.dictPD_PASEP_ROYALTIES,
            13: self.dictPD_PASEP_ROYALTIES, 14: self.dictPD_PASEP_ROYALTIES,
            15: self.dictPD_PASEP_FPE, 16: self.dictPD_PASEP_IPI,
            17: self.dictPD_PASEP_CFM, 18: self.dictPD_PASEP_CFH,
            19: self.dictPD_PASEP_CIDE, 20: self.dictPD_PASEP_ADO
        }   

    def encerrar_app(self):
        self.stop_event = True
        try:
            if self.driver: self.siafe.fechar_driver()
        except: pass
        self.usuario_siafe = ""
        self.senha_siafe = ""
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = MinervaApp()
    app.protocol("WM_DELETE_WINDOW", app.encerrar_app)
    app.mainloop()