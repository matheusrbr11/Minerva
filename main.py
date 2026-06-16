from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException
import customtkinter as ctk
import pandas as pd
import subprocess
import threading
import sqlite3
import os

from eop_ui import AppConfig, BaseApp
from jupiter import Siafe

class MinervaApp(BaseApp):
    def __init__(self):
        cfg = AppConfig(
            app_name="Programa Minerva",
            app_version="1.1.0",
            about_text="Programa Minerva\n Versão 1.1.0 \nDesenvolvido por: EOP / SUPCONC",
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

        self._inicializar_dicionarios()
        
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
    def atualizar_banco(self, id_registro, num_documento, tempo_contab=None):
        """Callback acionado por Siafe a cada documento finalizado"""
        try:
            with sqlite3.connect(self.DBPath) as con:
                cursor = con.cursor()
                query = '''UPDATE contabilizacoes SET num_documento = ?, tempo_contab = ?, usuario = ?, data_hora = ? WHERE id = ?'''
                cursor.execute(query, (num_documento, tempo_contab, os.getlogin(), str(pd.Timestamp.now()), id_registro))
                con.commit()
                
            self.registros_processados += 1
            valor_barra = self.registros_processados / self.total_registros 
               
            self.update_progress(valor_barra)
            
        except Exception as e:
            self.log(f"Erro ao atualizar banco ID {id_registro}: {e}")

    def execucao(self):
        """Lógica de processamento em background"""
        try:
            self.log("Verificando banco de dados...")
            if not self.DBPath.exists():
                self.log("ERRO: Banco de dados não encontrado.")
                return

            with sqlite3.connect(self.DBPath) as con:
                if "Receita (GR)" in self.opcao_selecionada:
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)", con)
                    dict_map     = self.dict_map_gr
                    metodo_siafe = self.siafe.gerar_documento
                    documento    = self.siafe.gerar_GR
                    tipo_doc     = "Guia de Recolhimento"
                    
                elif "PASEP (PD)" in self.opcao_selecionada:
                    df = pd.read_sql_query("SELECT * FROM contabilizacoes WHERE num_documento IS NULL AND tipo_id IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20)", con)
                    dict_map     = self.dict_map_pd
                    metodo_siafe = self.siafe.gerar_documento
                    documento    = self.siafe.gerar_PDT
                    tipo_doc     = "PD de Transferência"
                else:
                    self.log("Opção inválida.")
                    return

            if df.empty:
                self.log(f"Nenhum lançamento pendente encontrado para {tipo_doc}.")
                self.finalize_progress("Processado... (100%)", "Aviso", "Não há lançamentos pendentes para processar.", "info")
                self.stop_event = True
                return

            self.log(f"{len(df)} registros encontrados.")
            self.total_registros = len(df)
            self.registros_processados = 0
            
            self.reset_progress()

            self.siafe.abrir_driver()
            self.log("Iniciando navegador...")
            
            if self.stop_event: return

            self.log("Iniciando Contabilização...")
            if self.siafe.logar_siafe(self.siafeVersao, self._usuario, self._senha):

                sucesso = metodo_siafe(documento, df, dict_map, callback_sucesso=self.atualizar_banco)

                if sucesso:
                    self.log(">>> Processo concluído com Sucesso! <<<")
                    self.finalize_progress("Processado... (100%)", "Sucesso", f"{tipo_doc} contabilizadas com sucesso!", "info")

            else:
                self.log("Falha no login. Verifique suas credenciais.")
                self.stop_event = True
                self.siafe.fechar_driver()
                
                def fechar_e_voltar():
                    self.finalize_progress(label="Falha no Login")
                    self.show_login_frame(on_success=lambda u, s: self.show_config_frame())
                self.after(0, fechar_e_voltar)
                return

        except (NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException) as e:
            if self.stop_event: return
            self.log("Ocorreu um erro crítico com o navegador.\nPor favor, reinicie o programa.")
            raise e

        except Exception as e:
            if self.stop_event: return
            self.log("Ocorreu um erro inesperado.")
            print(e)
            self.messagebox_error("Erro", f"Ocorreu um erro inesperado: {e}")

        finally:
            if not self.stop_event:
                self.log("Fechando navegador...")
            if hasattr(self, 'siafe') and self.siafe.driver:
                self.siafe.fechar_driver()
            
            self.after(3000, self.show_config_frame)
            self.log("Programa encerrado. Retornando ao menu principal...")

    # =========================================================================
    # DADOS ESTRUTURAIS
    # =========================================================================
    def _inicializar_dicionarios(self):
        # Definições para GR
        self.dictGR_ANP7990 = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "4879 - COTA-PARTE DA COMP. FINANC. DOS ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - ATÉ 5% - PÓS-SAL", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990103 - Out Rec Pat - Royalties pela Produção do Petróleo - Até 5%"}
        self.dictGR_ANP9478 = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "4881 - ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - EXCEDENTE A 5%", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990105 - Out Rec Pat - Royalties pela Produção do Petróleo - Excedente a 5%"}
        self.dictGR_PEA = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5686 - COTA PARTE PART. ESPECIAL EXP. PETR. E GAS NATURAL LEI 9.478/97", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990106 - Out Rec Pat - Participação Especial Exploração do Petróleo"}
        self.dictGR_FEP = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916347", "DomicilioBancarioCompleto": "001 - 2234 - 2916347", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5723 - COTA PARTE FUNDO ESPECIAL DO PETROLEO", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1399990107 - Out Rec Pat - Fundo Especial do Petróleo - FEP"}
        self.dictGR_FPE = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916339", "DomicilioBancarioCompleto": "001 - 2234 - 2916339", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2038 - COTA-PARTE DO FUNDO DE PARTICIPAÇÃO DOS ESTADOS - FPE", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1711500101 - Cota-Parte FPE - Fundo de Participação dos Estados e do DF - Principal"}
        self.dictGR_IPI = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916363", "DomicilioBancarioCompleto": "001 - 2234 - 2916363", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2040 - COTA-PARTE DO ESTADO - IPI", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1711530101 - Cota-Parte IPI Exportação - Principal - LC 61/89"}
        self.dictGR_CFM = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916371", "DomicilioBancarioCompleto": "001 - 2234 - 2916371", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "708 - Transferência da União Referente à Compensação Financeira de Recursos Minerais", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Minerais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (708.101)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5682 - Cota-Parte da Compensação Financeira de Recursos Minerais", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1344020101 - Compensação Financeira pela Exploração de Recursos Minerais - Principal"}
        self.dictGR_CFH = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "291638X", "DomicilioBancarioCompleto": "001 - 2234 - 291638X", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "709 - Transferência da União referente à Compensação Financeira de Recursos Hídricos", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Hídricos", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (709.101)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "5722 - COTA PARTE DA COMPENSAÇÃO FINANCEIRA RECURSOS HIDRICOS", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1345032101 - Utilização de Recursos Hídricos - Demais Empresas - Principal"}
        self.dictGR_CIDE = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916509", "DomicilioBancarioCompleto": "001 - 2234 - 2916509", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "750 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "FonteRJ": "126 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (750.126)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2044 - COTA-PARTE DO ESTADO NA CONTRIBUIÇÃO DE INTERVENÇÃO NO DOMÍNIO ECONÔMICO - CIDE", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1711540101 - Cota-Parte Contribuição de Intervenção no Domínio Econômico - CIDE - Principal"}
        self.dictGR_ADO = {"ExtraOrcamentario": False, "TipoDocumento": "Orçamentário", "UG": "999900", "DomicilioBancario": "2916312", "DomicilioBancarioCompleto": "001 - 2234 - 2916312", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "501 - Outros Recursos não Vinculados", "FonteRJ": "101 - Outros Recursos não Vinculados - Ordinários Não Provenientes de Impostos-Tesouro", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (501.101)", "Convenio": "000000 - Convênio não identificado", "TipoPatrimonial": "Transferências Intergovernamentais Recebidas", "ItemPatrimonial": "2055 - DEMAIS TRANSFERÊNCIAS DA UNIÃO", "OperacaoPatrimonial": "2469 - Reconhecimento, Arrecadação e Recolhimento", "NaturezaReceita": "1719990101 - Outras Transferências da União - Principal"}

        # Definições para PD
        self.dictPD_PASEP_ROYALTIES = {"UG": "999900", "UGFavorecida": "370200", "Regularizacao": "OB Regularização Financeira", "JustificativaRegularizacao": "RETENÇÃO-PASEP", "DomicilioBancarioOrigem": "2916347", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916347", "DomicilioBancarioDestino": "BCO AUTENT", "DomicilioBancarioDestinoCompleto": "001 - 2234 - BCO AUTENT", "IEF": "1 - Recursos do Exercício Corrente", "Fonte": "704 - Transferência da União Referente a Royalties do Petróleo e Gás Natural", "FonteRJ": "104 - Transferência da União Ref. a Comp. Financ. pela Exploração de Recursos Naturais", "TipoDetalhamentoFonte": "0 - Sem Detalhamento", "DetalhamentoFonte": "000000 - Sem detalhamento - (704.104)", "Convenio": "000000 - Convênio não identificado", "Indice": "1,000", "TipoPatrimonial": "Pagamentos a Regularizar", "ItemPatrimonial": "5678 - Pagamentos (Por Ofício) a Regularizar - FONTES TESOURO", "OperacaoPatrimonial": "4962 - Pagamentos (Por Ofícios) a Regularizar - FONTES TESOURO"}
        self.dictPD_PASEP_FPE = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_FPE.update({"DomicilioBancarioOrigem": "2916339", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916339", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)"})
        self.dictPD_PASEP_IPI = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_IPI.update({"DomicilioBancarioOrigem": "2916363", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916363", "Fonte": "500 - Recursos não Vinculados de Impostos", "FonteRJ": "107 - Recursos não Vinculados de Impostos - Transferência Constitucionais de Impostos", "DetalhamentoFonte": "000000 - Sem detalhamento - (500.107)"})
        self.dictPD_PASEP_CFM = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_CFM.update({"DomicilioBancarioOrigem": "2916371", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916371", "Fonte": "708 - Transferência da União Referente à Compensação Financeira de Recursos Minerais", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Minerais", "DetalhamentoFonte": "000000 - Sem detalhamento - (708.101)"})
        self.dictPD_PASEP_CFH = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_CFH.update({"DomicilioBancarioOrigem": "291638X", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 291638X", "Fonte": "709 - Transferência da União referente à Compensação Financeira de Recursos Hídricos", "FonteRJ": "101 - Transferência da União - Compensação Financeira de Recursos Hídricos", "DetalhamentoFonte": "000000 - Sem detalhamento - (709.101)"})
        self.dictPD_PASEP_CIDE = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_CIDE.update({"DomicilioBancarioOrigem": "2916509", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916509", "Fonte": "750 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "FonteRJ": "126 - Recursos da Contribuição de Intervenção no Domínio Econômico - CIDE", "DetalhamentoFonte": "000000 - Sem detalhamento - (750.126)"})
        self.dictPD_PASEP_ADO = self.dictPD_PASEP_ROYALTIES.copy(); self.dictPD_PASEP_ADO.update({"DomicilioBancarioOrigem": "2916312", "DomicilioBancarioOrigemCompleto": "001 - 2234 - 2916312", "Fonte": "501 - Outros Recursos não Vinculados", "FonteRJ": "101 - Outros Recursos não Vinculados - Ordinários Não Provenientes de Impostos-Tesouro", "DetalhamentoFonte": "000000 - Sem detalhamento - (501.101)"})

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


if __name__ == "__main__":
    app = MinervaApp()
    app.protocol("WM_DELETE_WINDOW", lambda: app.safe_exit(app.limpar_recursos))
    app.mainloop()