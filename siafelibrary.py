"""
Módulo de Automação do SIAFE (siafelibrary.py)
==============================================

Biblioteca desenvolvida para encapsular e automatizar tarefas repetitivas 
no Sistema Integrado de Gestão Orçamentária, Financeira e Contábil (Siafe-Rio2), utilizando a 
biblioteca base `automaweb`.

Esta biblioteca é genérica, focada na interação com a interface web do Siafe 
(cliques, preenchimentos, extração de dados) e não contém regras de negócios 
rígidas (ex: contas, fontes ou IDs específicos). As regras são injetadas nas 
funções via dicionários (`dict_map`).

Classes Principais:
    - Siafe: Herda de `automaweb.Navegador` e fornece os métodos operacionais.
    - xpaths_*: Classes de agrupamento de seletores (XPath) para cada tela do sistema.

Dependências:
    - automaweb
    - pandas
    - selenium
"""

from datetime import datetime

from siafelibrary_xpaths import *

import automaweb
import pandas as pd
from tkinter import messagebox

from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import decimal
import time

ctx = decimal.Context()
ctx.prec = 20

class Siafe(automaweb.Navegador):
    """
    Classe autônoma para encapsular toda a interação com o Siafe.
    
    Gerencia seu próprio WebDriver (herança) e fornece métodos especializados 
    para navegação, login e geração de documentos contábeis (GR, PD, NA e NP).
    """

    def __init__(self):
        """
        Inicializa a instância do navegador Siafe com um tempo de stun 
        (pausa padrão entre ações) de 0.3 segundos.
        """
        super().__init__(tempo_stun=0.3)
    
    def _voltar(self):
        """
        Clica no botão de "Voltar" padrão do Siafe para retornar à tela de listagem de documentos.
        
        Utilizado principalmente após um erro de preenchimento para abortar 
        a operação atual e tentar a próxima.

        Returns:
            bool: True se o clique foi bem-sucedido, False caso contrário.
            
        Raises:
            Exception: Se houver falha ao localizar ou clicar no botão.
        """
        try:

            #antes de voltar, clicar em botões de cancelar
            botoes_cancelar = self.encontrar_elementos('//*[text()="Cancelar"]')
            num_botoes = len(botoes_cancelar)
            for i in range(num_botoes, 0, -1):
                if i > 2: #evita cancelar a contabilizacao (cancelar apenas os popups de erro)
                    cancelar = self.encontrar_elemento(f'(//*[text()="Cancelar"])[{i-1}]')
                    self.driver.execute_script("arguments[0].click();", cancelar)

            if self.clicar(xpaths_menu.btn_voltar):
                return True
            else:
                return False
        
        except Exception:
            print(f"Erro ao voltar!")
            raise

    def _aguardar_siafe(self):
        """
        Aguarda até que o cursor do mouse (css 'cursor') retorne de 'wait' (carregando) 
        para o estado normal. Previne interações prematuras durante o processamento do servidor.
        """
        self.wait.until(lambda driver: driver.find_element(By.XPATH, '/html/body').value_of_css_property('cursor') != 'wait')

    def _formatar_valor(self, valor):
        valor_float = float(valor.replace(',', '.'))
        valor_formatado = f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return valor_formatado
    
    def _verificar_erro(self, xpath_erro):

        #retorna FALSE caso não tenha erro.

        if self.verifica_visivel(xpath_erro): # Verifica se ocorreu algum erro
            erro = self.obter_texto(xpath_erro)
            print(erro)
            if "Erro" in erro:
                erro_body = self.obter_texto(xpath_erro)
                if erro_body and "Saldo insuficiente para contabilização" in erro_body:
                    messagebox.showwarning("Aviso", "Saldo insuficiente. O programa tentará novamente.")
                    self.semsaldo = 1
                self._voltar()
                return True
            else:
                return False
        else:
            return False

    def _digitar_competência(self, xpath_competencia, competencia):

        competencia_texto = competencia[-7:]
        while self.verificar_texto_digitado(xpath_competencia, competencia_texto) == False:
            try:
                self.digitar(xpaths_pdt.competencia, Keys.ESCAPE); self._aguardar_siafe()
                self.digitar(xpaths_pdt.competencia, competencia_texto)
            except Exception as e:
                print(f"Erro na competência: {e}")

    def logar_siafe(self, versaoSiafe, usuario, senha, ano: str = datetime.today().year):
        """
        Abre o navegador, acessa a URL e realiza a autenticação no sistema.

        Args:
            versaoSiafe (int): Define o ambiente (1 para ambiente de produção, 2 para ambiente de testes (Beta)).
            usuario (str): Credencial de acesso (CPF).
            senha (str): Senha de acesso.

        Returns:
            bool: True se o login foi bem-sucedido. False em caso de erro de credenciais 
                  (identificado via leitura do pop-up de erro) ou falha de conexão.
        """
        # Define a URL base dependendo do ambiente escolhido
        if versaoSiafe == 1:
            url = 'https://siafe2.fazenda.rj.gov.br/Siafe/faces/login.jsp'
        if versaoSiafe == 2:
            url = 'http://10.8.237.102:8080/Siafe/faces/login.jsp'
        
        # Abre o navegador instanciado na classe e navega até a URL definida
        self.abrir_url(url)
        try:
            # Preenche os campos de credenciais e clica no botão de entrar
            self.digitar(xpaths_login.usuario, usuario)
            self.digitar(xpaths_login.senha, senha)
            self.selecionar_texto(xpaths_login.ano, str(ano))
            self.clicar(xpaths_login.btn_confirmar)
            
            # Após clicar em confirmar, este bloco tenta ler um possível pop-up de "Usuário e/ou senha incorretos."
            try:
                if self.verifica_visivel(xpaths_login.erro_titulo):
                    erro_titulo = self.obter_texto(xpaths_login.erro_titulo)
                    if erro_titulo and "Erro" in erro_titulo:
                        erro_body = self.obter_texto(xpaths_login.erro_corpo)
                        # Se o pop-up existir e contiver a mensagem, alerta o usuário e interrompe a execução.
                        if erro_body and "Usuário e/ou senha incorretos." in erro_body:
                            messagebox.showwarning("Aviso", "Usuário ou Senha incorretos. Volte a tela de login e tente novamente.")
                            return False   
            except Exception: 
                # Se o elemento NÃO for encontrado, significa que não houve erro de credenciais.
                pass
        
        except Exception:
            # Captura falhas genéricas do WebDriver (ex: página não carregou, elemento não renderizou a tempo) e alerta o usuário sobre a falha de conexão.
            messagebox.showerror("Erro", "Não foi possível logar no SIAFE.")
            return False
        # Se passou por todos os blocos sem retornar False, o login teve sucesso.
        return True  


### Guia de Recolhimento (GR) ###
    
    def gerar_gr(self, df, dict_map, callback_sucesso=None):
        """
        Contabiliza Guias de Recolhimento (GR) orçamentárias ou extraorçamentárias.

        Args:
            df (pd.DataFrame): Tabela contendo os lançamentos. No formato: 'id', 'data', 'valor', 'observacao', 'tipo_id', 'num_documento' (inicialmente vazio) e 'tempo_contab' (inicialmente vazio).
            dict_map (dict): Dicionário contendo os dados de preenchimento para contabilização. No formato: {tipo_id: {"TipoDocumento": str, "UG": str, "DomicilioBancario": str, "DomicilioBancarioCompleto": str, "IEF": str, "Fonte": str, "FonteRJ": str, "TipoDetalhamentoFonte": str, "DetalhamentoFonte": str, "Convenio": str, "TipoPatrimonial": str, "ItemPatrimonial": str, "OperacaoPatrimonial": str, "NaturezaReceita": str (somente para orçamentário), "TipoCredor": str (PJ, CG, PF ou UG) (somente para extra-orçamentário), "Credor": str}}.
            callback_sucesso (callable, optional): Função a ser chamada quando uma GR é gerada com sucesso. 
                                                   Recebe o id, num_documento e tempo_contab.
        
        Returns:
            bool: True se processar a planilha sem erros críticos do WebDriver. 
                  False se exceder tentativas ou ocorrer erro grave.
     
        Obs:
            Para Padrão: Orçamentária.
            Para Extra-Orçamentária: Adicione "ExtraOrcamentario": True no dict_map.
        """
        
    # REESTRUTURAÇÃO DO DATAFRAME E NAVEGAÇÃO PARA CONTABILIZAÇÃO ---

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",") # Formata o valor
        df["tentativas"] = 0 # Cria uma coluna de tentativas para controle de falhas

        try: # navega para Guia de Recolhimento.
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_gr.btn_gr)

        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'Guia de Recolhimento (GR)'.")
            return False


    # LOOP DE CONTABILIZAÇÃO (ENQUANTO EXISTIREM LANÇAMENTOS NÃO CONTABILIZADOS) ---

        while df['num_documento'].isna().any():

            for index, row in df[df['num_documento'].isna()].iterrows():


            # PREPARO DE DADOS ---

                if row["tentativas"] >= 3:
                    messagebox.showerror(
                        "Erro",
                        f'''O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.
                        Verifique o erro e tente novamente.''')
                    return False
                
                df.loc[index, "tentativas"] += 1 # Incrementa o contador de tentativas
                dict_contabil = dict_map.get(row["tipo_id"]) # Busca as regras contábeis definidas no dicionário.
                if not dict_contabil:
                    continue
                else:
                    is_extra = dict_contabil.get("ExtraOrcamentario") is True
                

            #  INÍCIO DA CONTABILIZAÇÃO ---

                try:

                    self.clicar(xpaths_gr.btn_inserir_gr)
                    inicio = time.perf_counter() #cronômetro


                # IDENTIFICAÇÃO (COM VALIDAÇÃO) ---

                    self.limpar(xpaths_gr.data_emissao)
                    self.digitar(xpaths_gr.data_emissao, row["data"]);self._aguardar_siafe()
                    self.digitar(xpaths_gr.data_recolhimento, row["data"]);self._aguardar_siafe()
                    self.selecionar_texto(xpaths_gr.tipo_documento, dict_contabil["TipoDocumento"])
                    self.digitar(xpaths_gr.ug_emitente, dict_contabil["UG"])
                    self.clicar(xpaths_gr.ug_pesquisar);self._aguardar_siafe()
                    self.digitar(xpaths_gr.domicilio_bancario, dict_contabil["DomicilioBancario"])
                    self.clicar(xpaths_gr.domicilio_bancario_pesquisar);self._aguardar_siafe()
                    if not is_extra:
                        self.digitar(xpaths_gr.ug_orcamentaria, dict_contabil["UG"])
                        self.clicar(xpaths_gr.ug_orcamentaria_pesquisar);self._aguardar_siafe()

                    # bloco de validação
                    validacoes = (
                        (self.obter_atributo(xpaths_gr.data_emissao, "value") == row["data"]) and
                        (self.obter_atributo(xpaths_gr.data_recolhimento, "value") == row["data"]) and
                        self.verificar_texto_selecionado(xpaths_gr.tipo_documento, dict_contabil["TipoDocumento"]) and
                        (self.obter_atributo(xpaths_gr.ug_emitente, 'value') == dict_contabil["UG"]) and
                        (self.obter_atributo(xpaths_gr.domicilio_bancario, 'value') == dict_contabil["DomicilioBancarioCompleto"])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # DETALHAMENTO (COM VALIDAÇÃO) ---

                    self.selecionar_texto(xpaths_gr.ief, dict_contabil["IEF"])
                    self.selecionar_texto(xpaths_gr.fonte, dict_contabil["Fonte"])
                    self.selecionar_texto(xpaths_gr.fonte_rj, dict_contabil["FonteRJ"])
                    self.selecionar_texto(xpaths_gr.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                    if dict_contabil.get("DetalhamentoFonte"):
                        self.selecionar_texto(xpaths_gr.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                    self.selecionar_texto(xpaths_gr.convenio, dict_contabil["Convenio"])

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_digitado(xpaths_gr.data_emissao, row["data"]) and
                        self.verificar_texto_digitado(xpaths_gr.data_recolhimento, row["data"]) and
                        self.verificar_texto_selecionado(xpaths_gr.tipo_documento, dict_contabil["TipoDocumento"]) and
                        self.verificar_texto_digitado(xpaths_gr.domicilio_bancario, dict_contabil["DomicilioBancarioCompleto"])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # PREENCHIMENTO DO ITEM (COM VALIDAÇÃO) ---

                    # GR Extra-Orçamentária
                    if is_extra:

                        self.clicar(xpaths_gr.btn_item_extraorcamentario)
                        self.clicar(xpaths_gr.btn_inserir_item_extraorcamentario)
                        self.selecionar_texto(xpaths_gr.tipo_patrimonial_extra, dict_contabil["TipoPatrimonial"])
                        self.selecionar_texto(xpaths_gr.item_patrimonial_extra, dict_contabil["ItemPatrimonial"])
                        self.selecionar_texto(xpaths_gr.operacao_patrimonial_extra, dict_contabil["OperacaoPatrimonial"])
                        self.selecionar_texto(xpaths_gr.ano_extra, row["data"][-4:]); self._aguardar_siafe()
                        self.digitar(xpaths_gr.valor_extra, row["valor_str"])
                        tipo_credor = dict_contabil.get("TipoCredor", "PJ") # Padrão PJ
                        mapa_credor = {
                            "PJ": xpaths_gr.tipo_credor_pj_extra,
                            "CG": xpaths_gr.tipo_credor_cg_extra,
                            "PF": xpaths_gr.tipo_credor_pf_extra,
                            "UG": xpaths_gr.tipo_credor_ug_extra
                        }
                        if tipo_credor in mapa_credor:
                            self.clicar(mapa_credor[tipo_credor]); self._aguardar_siafe()
                        self.digitar(xpaths_gr.credor_extra, dict_contabil["Credor"]); self._aguardar_siafe()
                        self.clicar(xpaths_gr.credor_pesquisar_extra)
                        time.sleep(3);self._aguardar_siafe() #debug (avaliar o time.sleep())

                        #bloco de validação
                        validacoes = (
                            self.verificar_texto_selecionado(xpaths_gr.operacao_patrimonial_extra, dict_contabil["OperacaoPatrimonial"]) and 
                            self.verificar_texto_digitado(xpaths_gr.valor_extra, self._formatar_valor(row["valor_str"]))
                        )
                        if not validacoes:
                            self._voltar()
                            continue
                        else:
                            self.clicar(xpaths_gr.btn_confirmar_item)

                    # GR Orçamentária
                    else:
                        
                        self.clicar(xpaths_gr.btn_item_orcamentario)
                        self.clicar(xpaths_gr.btn_inserir_item_orcamentario)
                        self.selecionar_texto(xpaths_gr.tipo_patrimonial_orc, dict_contabil["TipoPatrimonial"])
                        self.selecionar_texto(xpaths_gr.item_patrimonial_orc, dict_contabil["ItemPatrimonial"])
                        self.selecionar_texto(xpaths_gr.operacao_patrimonial_orc, dict_contabil["OperacaoPatrimonial"]) 
                        self.selecionar_texto(xpaths_gr.natureza_receita_orc, dict_contabil["NaturezaReceita"])
                        #self._aguardar_siafe()
                        time.sleep(2)
                        self.digitar(xpaths_gr.valor_orc, row["valor_str"])
                        time.sleep(2)
                        # bloco de validação
                        validacoes = (
                            self.verificar_texto_selecionado(xpaths_gr.operacao_patrimonial_orc, dict_contabil["OperacaoPatrimonial"])# and 
                            #self.verificar_texto_digitado(xpaths_gr.valor_orc, self._formatar_valor(row["valor_str"]))
                        )
                        if not validacoes:
                            self._voltar()
                            continue
                        else:
                            self.clicar(xpaths_gr.btn_confirmar_item_orc)


                # FINALIZAÇÃO E CONTABILIZAÇÃO (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_gr.btn_inserir_observacao)
                    self.digitar(xpaths_gr.observacao, row["observacao"])

                    # bloco de validação
                    if not self.verificar_texto_digitado(xpaths_gr.observacao, row["observacao"]):
                        self._voltar()
                        continue
                    else:
                        self.clicar(xpaths_gr.btn_contabilizar)
                        self.clicar(xpaths_gr.btn_confirmar_contabilizacao); self._aguardar_siafe()

                    # bloco de verificação
                    if self._verificar_erro(xpaths_gr.erro):
                        continue
                        

                # ATUALIZAÇÃO DO DATAFRAME (COM VALIDAÇÃO) ---

                    try:

                        numGR = self.obter_texto(xpaths_gr.numero_documento) # obtém o número da GR
                        tempo_contab = str(round(time.perf_counter() - inicio, 2)).replace(".", ",") # calcula o tempo de contabilização
                        df.loc[index, "num_documento"] = numGR
                        df.loc[index, "tempo_contab"] = tempo_contab

                        if callback_sucesso is not None:
                            callback_sucesso(id=row["id"], num_documento=numGR, tempo_contab=tempo_contab)

                    except Exception:
                        messagebox.showerror(
                            "Erro", 
                            '''Ocorreu um erro crítico com a integração com o banco de dados.
                            Comunique o erro à Equipe de Desenvolvimento!''')
                        return False

                except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                    messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.")
                    return False

                except (WebDriverException, Exception):
                    self._voltar()
                    continue
                
                else:
                    self._voltar()

        return True
    
### PD Extra-Orçamentária ###
    def gerar_pde(self, df, dict_map, callback_sucesso=None):
        """
        Contabiliza Programações de Desembolso (PD) Extra-Orçamentárias.

        Args:
            df (pd.DataFrame): Tabela contendo os lançamentos. No formato: 'id', 'data', 'valor', 'observacao', 'tipo_id', 'num_documento' (inicialmente vazio) e 'tempo_contab' (inicialmente vazio).
            dict_map (dict): Dicionário contendo os dados de preenchimento para contabilização. No formato: {tipo_id: {"TipoDocumento": str, "UG": str, "DomicilioBancario": str, "DomicilioBancarioCompleto": str, "IEF": str, "Fonte": str, "FonteRJ": str, "TipoDetalhamentoFonte": str, "DetalhamentoFonte": str, "Convenio": str, "TipoPatrimonial": str, "ItemPatrimonial": str, "OperacaoPatrimonial": str, "NaturezaReceita": str (somente para orçamentário), "TipoCredor": str (PJ, CG, PF ou UG) (somente para extra-orçamentário), "Credor": str}}.
            # CONVERSAR COM O JOÃO A RESPEITO DA LINHA A CIMA! - FORMATO IMPREVISÍVEL
            
            callback_sucesso (callable, optional): Função a ser chamada quando uma PD é gerada com sucesso. 
                                                   Recebe o id, num_documento e tempo_contab.
        
        Returns:
            bool: True se processar a planilha sem erros críticos do WebDriver. 
                  False se exceder tentativas ou ocorrer erro grave.

        Obs:
            Para Regularização: Adicione "Regularizacao": <valor> no dict_map.
        """

    # REESTRUTURAÇÃO DO DATAFRAME E NAVEGAÇÃO PARA CONTABILIZAÇÃO ---

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",") # Formata o valor
        df["tentativas"] = 0 # Cria uma coluna de tentativas para controle de falhas

        try: # Navega para PD Extra-orçamentária.
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_pde.btn_pde)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'PD Extra-orçamentária'.")
            return False


    # LOOP DE CONTABILIZAÇÃO (ENQUANTO EXISTIREM LANÇAMENTOS NÃO CONTABILIZADOS) ---

        while df['num_documento'].isna().any():

            for index, row in df[df['num_documento'].isna()].iterrows():


            # PREPARO DE DADOS ---

                if row["tentativas"] >= 3:
                    messagebox.showerror(
                        "Erro",
                        f'''O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.
                        Verifique o erro e tente novamente.''')
                    return False

                dict_contabil = dict_map.get(row["tipo_id"]) # Busca as regras contábeis definidas no dicionário.
                if not dict_contabil:
                    continue

                df.loc[index, "tentativas"] += 1 # Incrementa o contador de tentativas


            # INÍCIO DA CONTABILIZAÇÃO ---

                try:

                    self.clicar(xpaths_pde.btn_inserir_pde)
                    inicio = time.perf_counter() # cronômetro


                # IDENTIFICAÇÃO (COM VALIDAÇÃO) ---

                    self.limpar(xpaths_pde.data_emissao)
                    self.digitar(xpaths_pde.data_emissao, row["data"]); self._aguardar_siafe()
                    self.clicar(xpaths_pde.data_programacao)
                    self.digitar(xpaths_pde.data_programacao, row["data"]); self._aguardar_siafe()
                    self.digitar(xpaths_pde.data_vencimento, row["data"]); self._aguardar_siafe()
                    self.digitar(xpaths_pde.ug_emitente, dict_contabil["UG"])
                    self.clicar(xpaths_pde.ug_emitente_pesquisar); self._aguardar_siafe()

                    # Lógica de Regularização (via flag "Regularizacao" no dicionário)
                    if "Regularizacao" in dict_contabil:
                        if not self.verifica_selecionado(xpaths_pde.ob_regulaziracao):
                            self.clicar(xpaths_pde.ob_regulaziracao)
                        self.selecionar_texto(xpaths_pde.regularizacao, dict_contabil["Regularizacao"])
                    else:
                        # Garante que o campo de Regularização esteja desmarcado para PDs que não são de Regularização
                        if self.verifica_selecionado(xpaths_pde.ob_regulaziracao):
                            self.clicar(xpaths_pde.ob_regulaziracao)

                    self.digitar(xpaths_pde.ug_pagadora, dict_contabil["UG"])
                    self.clicar(xpaths_pde.ug_pagadora_pesquisar); self._aguardar_siafe()
                    self.digitar(xpaths_pde.domicilio_bancario_origem, dict_contabil["DomicilioBancarioOrigem"]); self._aguardar_siafe()
                    self.clicar(xpaths_pde.domicilio_bancario_origem_pesquisar); self._aguardar_siafe()

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_digitado(xpaths_pde.data_emissao, row["data"]) and
                        self.verificar_texto_digitado(xpaths_pde.data_programacao, row["data"]) and
                        self.verificar_texto_digitado(xpaths_pde.data_vencimento, row["data"]) and
                        self.verificar_texto_digitado(xpaths_pde.domicilio_bancario_origem, dict_contabil["DomicilioBancarioOrigemCompleto"])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # DETALHAMENTO (COM VALIDAÇÃO) ---

                    self.selecionar_texto(xpaths_pde.ief, dict_contabil["IEF"])
                    self.selecionar_texto(xpaths_pde.fonte, dict_contabil["Fonte"])
                    self.selecionar_texto(xpaths_pde.fonte_rj, dict_contabil["FonteRJ"])
                    self.selecionar_texto(xpaths_pde.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                    self.selecionar_texto(xpaths_pde.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                    self.clicar(xpaths_pde.tipo_credor_pj)
                    self.digitar(xpaths_pde.credor_pj, dict_contabil["Credor"])
                    self.clicar(xpaths_pde.credor_pj_pesquisar); self._aguardar_siafe()
                    self.selecionar_texto(xpaths_pde.domicilio_bancario_destino, dict_contabil["DomicilioBancarioDestino"]); self._aguardar_siafe()
                    self._digitar_competência(xpaths_pde.competencia, row["data"])

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_selecionado(xpaths_pde.domicilio_bancario_destino, dict_contabil["DomicilioBancarioDestino"])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # PREENCHIMENTO DO ITEM (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_pde.btn_itens)
                    self.clicar(xpaths_pde.btn_inserir_item)

                    try:
                        self.selecionar_texto(xpaths_pde.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
                        self.selecionar_texto(xpaths_pde.item_patrimonial, dict_contabil["ItemPatrimonial"])
                        self.selecionar_texto(xpaths_pde.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
                        self.selecionar_texto(xpaths_pde.vinculacao_pagamento, dict_contabil["VinculacaoPagamento"])
                        self.selecionar_texto(xpaths_pde.ano, row["data"][-4:]); self._aguardar_siafe()
                        self.digitar(xpaths_pde.valor, row["valor_str"])

                        # bloco de validação
                        validacoes = (
                            self.verificar_texto_selecionado(xpaths_pde.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]) and
                            self.verificar_texto_digitado(xpaths_pde.valor, row["valor_str"])
                        )
                        if not validacoes:
                            raise Exception("Falha na verificação do item (PDE)")

                        self.clicar(xpaths_pde.btn_confirmar_item)

                    except (Exception, WebDriverException):
                        # Cancela o item se houver erro no preenchimento ou na confirmação, e pula pra próxima tentativa.
                        self.clicar(xpaths_pde.btn_cancelar_item)
                        self._voltar()
                        continue


                # FINALIZAÇÃO E CONTABILIZAÇÃO (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_pde.btn_inserir_observacao)
                    self.digitar(xpaths_pde.observacao, row["observacao"])
                    
                    # bloco de validação
                    if not self.verificar_texto_digitado(xpaths_pde.observacao, row["observacao"]):
                        self._voltar()
                        continue
                    else:
                        self.clicar(xpaths_pde.btn_contabilizar)
                        self.clicar(xpaths_pde.btn_confirmar_contabilizacao); self._aguardar_siafe()

                    # bloco de verificação
                    if self._verificar_erro(xpaths_pde.erro):
                        continue


                # ATUALIZAÇÃO DO DATAFRAME (COM VALIDAÇÃO) ---

                    try:

                        numPD = self.obter_texto(xpaths_pde.numero_documento) # Obtém o número da PD
                        tempo_contab = str(round(time.perf_counter() - inicio, 2)).replace(".", ",") # Calcula o tempo de contabilização
                        df.loc[index, "num_documento"] = numPD
                        df.loc[index, "tempo_contab"] = tempo_contab

                        if callback_sucesso is not None:
                            callback_sucesso(id=row["id"], num_documento=numPD, tempo_contab=tempo_contab)

                    except Exception:
                        messagebox.showerror(
                            "Erro",
                            '''Ocorreu um erro crítico com a integração com o banco de dados.
                            Comunique o erro à Equipe de Desenvolvimento!''')
                        return False

                except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                    messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.")
                    return False

                except (WebDriverException, Exception):
                    self._voltar()
                    continue

                else:
                    self._voltar()

        return True
    
### PD de Transferência ###
    def gerar_pdt(self, df, dict_map, callback_sucesso=None):
        """
        Contabiliza Programações de Desembolso (PD) de Transferência.

        Inclui lógicas específicas para:
        - Seleção de Operação Patrimonial via valor ou texto (flag 'SelecaoPorValor').
        - Tratamento especial para domicílios de destino do tipo "BCO AUTENT".
        - Revalidação do campo de competência (devido a bugs da interface do Siafe).

        Args:
            df (pd.DataFrame): Tabela contendo os lançamentos. No formato: 'id', 'data', 'valor', 'observacao', 'tipo_id', 'num_documento' (inicialmente vazio) e 'tempo_contab' (inicialmente vazio).
            dict_map (dict): Dicionário contendo os dados de preenchimento para contabilização. No formato: {tipo_id: {"TipoDocumento": str, "UG": str, "DomicilioBancario": str, "DomicilioBancarioCompleto": str, "IEF": str, "Fonte": str, "FonteRJ": str, "TipoDetalhamentoFonte": str, "DetalhamentoFonte": str, "Convenio": str, "TipoPatrimonial": str, "ItemPatrimonial": str, "OperacaoPatrimonial": str, "NaturezaReceita": str (somente para orçamentário), "TipoCredor": str (PJ, CG, PF ou UG) (somente para extra-orçamentário), "Credor": str}}.
            # CONVERSAR COM O JOÃO A RESPEITO DA LINHA A CIMA! - FORMATO IMPREVISÍVEL
            
            callback_sucesso (callable, optional): Função a ser chamada quando uma PD é gerada com sucesso. 
                                                   Recebe o id, num_documento e tempo_contab.
        
        Returns:
            bool: True se processar a planilha sem erros críticos do WebDriver. 
                  False se exceder tentativas ou ocorrer erro grave.

        Obs:
            Para Regularização: Adicione "Regularizacao": <valor> no dict_map.
            Para Operação Patrimonial por código: Adicione "SelecaoPorValor": True no dict_map.
        """

    # REESTRUTURAÇÃO DO DATAFRAME E NAVEGAÇÃO PARA CONTABILIZAÇÃO ---

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",") # Formata o valor
        df["tentativas"] = 0 # Cria uma coluna de tentativas para controle de falhas

        try: # Navega para PD de Transferência.
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_pdt.btn_pdt)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possivel navegar para 'PD de Transferência'.")
            return False


    # LOOP DE CONTABILIZAÇÃO (ENQUANTO EXISTIREM LANÇAMENTOS NÃO CONTABILIZADOS) ---

        while df['num_documento'].isna().any():

            for index, row in df[df['num_documento'].isna()].iterrows():


            # PREPARO DE DADOS ---

                if row["tentativas"] >= 3:
                    messagebox.showerror(
                        "Erro",
                        f'''O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.
                        Verifique o erro e tente novamente.''')
                    return False

                dict_contabil = dict_map.get(row["tipo_id"]) # Busca as regras contábeis definidas no dicionário.
                if not dict_contabil:
                    continue

                df.loc[index, "tentativas"] += 1 # Incrementa o contador de tentativas


            # INÍCIO DA CONTABILIZAÇÃO ---

                try:

                    self.clicar(xpaths_pdt.btn_inserir_pdt)
                    inicio = time.perf_counter() # cronômetro


                # IDENTIFICAÇÃO (COM VALIDAÇÃO) ---

                    self.limpar(xpaths_pdt.data_emissao)
                    self.digitar(xpaths_pdt.data_emissao, row["data"]); self._aguardar_siafe()
                    self.clicar(xpaths_pdt.data_programacao)
                    self.digitar(xpaths_pdt.data_programacao, row["data"]); self._aguardar_siafe()
                    self.digitar(xpaths_pdt.data_vencimento, row["data"]); self._aguardar_siafe()
                    self.digitar(xpaths_pdt.ug_emitente, dict_contabil["UG"])
                    self.clicar(xpaths_pdt.ug_emitente_pesquisar); self._aguardar_siafe()
                    ug_favorecida = dict_contabil.get("UGFavorecida", dict_contabil["UG"])
                    self.digitar(xpaths_pdt.ug_favorecida, ug_favorecida)
                    self.clicar(xpaths_pdt.ug_favorecida_pesquisar); self._aguardar_siafe()
                    self.digitar(xpaths_pdt.ug_pagadora, dict_contabil["UG"])
                    self.clicar(xpaths_pdt.ug_pagadora_pesquisar); self._aguardar_siafe()

                    # Lógica de Regularização (via flag "Regularizacao" no dicionário)
                    if "Regularizacao" in dict_contabil:
                        if not self.verifica_selecionado(xpaths_pdt.ob_regulaziracao):
                            self.clicar(xpaths_pdt.ob_regulaziracao)
                        self.selecionar_texto(xpaths_pdt.regularizacao, dict_contabil["Regularizacao"])
                    else:
                        # Garante que o campo de Regularização esteja desmarcado para PDs que não são de Regularização
                        if self.verifica_selecionado(xpaths_pdt.ob_regulaziracao):
                            self.clicar(xpaths_pdt.ob_regulaziracao)

                    self.digitar(xpaths_pdt.domicilio_bancario_emitente, dict_contabil["DomicilioBancarioOrigem"])
                    self.clicar(xpaths_pdt.domicilio_bancario_emitente_pesquisar); self._aguardar_siafe()

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_digitado(xpaths_pdt.data_emissao, row["data"]) and
                        self.verificar_texto_digitado(xpaths_pdt.data_programacao, row["data"]) and
                        self.verificar_texto_digitado(xpaths_pdt.data_vencimento, row["data"]) and
                        self.verificar_texto_digitado(xpaths_pdt.domicilio_bancario_emitente, dict_contabil['DomicilioBancarioOrigemCompleto'])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # DETALHAMENTO (COM VALIDAÇÃO) ---

                    time.sleep(0.3)
                    self.selecionar_texto(xpaths_pdt.ief_origem, dict_contabil["IEF"])
                    self.selecionar_texto(xpaths_pdt.fonte_origem, dict_contabil["Fonte"])
                    self.selecionar_texto(xpaths_pdt.fonte_rj_origem, dict_contabil["FonteRJ"])
                    self.selecionar_texto(xpaths_pdt.tipo_detalhamento_fonte_origem, dict_contabil["TipoDetalhamentoFonte"])
                    self.selecionar_texto(xpaths_pdt.detalhamento_fonte_origem, dict_contabil["DetalhamentoFonte"])
                    self.selecionar_texto(xpaths_pdt.convenio_origem, dict_contabil["Convenio"])
                    self.digitar(xpaths_pdt.domicilio_bancario_favorecida, dict_contabil["DomicilioBancarioDestino"])
                    self.clicar(xpaths_pdt.domicilio_bancario_favorecida_pesquisar); self._aguardar_siafe()

                    # Lógica Exclusiva: Se o domicílio bancário de destino contiver "BCO AUTENT", clicar na aba específica para Banco Autent.
                    if "BCO AUTENT" in dict_contabil.get("DomicilioBancarioDestinoCompleto", ""):
                        time.sleep(0.3); self.clicar(xpaths_pdt.tab_bco_autent); time.sleep(0.3); self.clicar(xpaths_pdt.tab_ok); time.sleep(0.3)
                        # time.aguardar_siafe(); self.clicar(xpaths_pdt.tab_bco_autent); time.aguardar_siafe(); self.clicar(xpaths_pdt.tab_ok); time.aguardar_siafe() #debug 

                    time.sleep(0.6) # >>> n sei pq tem esse sleep mas tem algum motivo <<<
                    self.selecionar_texto(xpaths_pdt.ief_favorecida, dict_contabil["IEF"])
                    self.selecionar_texto(xpaths_pdt.fonte_favorecida, dict_contabil["Fonte"])
                    self.selecionar_texto(xpaths_pdt.fonte_rj_favorecida, dict_contabil["FonteRJ"])
                    self.selecionar_texto(xpaths_pdt.tipo_detalhamento_fonte_favorecida, dict_contabil["TipoDetalhamentoFonte"])
                    self.selecionar_texto(xpaths_pdt.detalhamento_fonte_favorecida, dict_contabil["DetalhamentoFonte"]); self._aguardar_siafe()
                    self.selecionar_texto(xpaths_pdt.convenio_favorecida, dict_contabil["Convenio"])
                    self._digitar_competência(xpaths_pdt.competencia, row["data"])

                    if dict_contabil.get("JustificativaRegularizacao"):
                        self.digitar(xpaths_pdt.justificativa_regularizacao, dict_contabil["JustificativaRegularizacao"])

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_digitado(xpaths_pdt.domicilio_bancario_favorecida, dict_contabil['DomicilioBancarioDestinoCompleto'])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # PREENCHIMENTO DO ITEM (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_pdt.btn_itens)
                    self.clicar(xpaths_pdt.btn_inserir_item)

                    try:
                        self.selecionar_texto(xpaths_pdt.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
                        self.selecionar_texto(xpaths_pdt.item_patrimonial, dict_contabil["ItemPatrimonial"])

                        # Lógica: Seleção por Valor ou Texto (via flag SelecaoPorValor = True no dicionário).
                        # Permite a flexibilidade de selecionar a operação patrimonial pelo seu código ou pela seu texto.
                        if dict_contabil.get("SelecaoPorValor") is True:
                            self.selecionar_valor(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
                        else:
                            self.selecionar_texto(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])

                        time.sleep(1)
                        self.digitar(xpaths_pdt.valor, row["valor_str"])

                        # bloco de validação
                        validacoes = (
                            self.verificar_texto_selecionado(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]) and
                            self.verificar_texto_digitado(xpaths_pdt.valor, row["valor_str"])
                        )
                        if not validacoes:
                            raise Exception("Falha na verificação do item (PDT)")

                        self.clicar(xpaths_pdt.btn_confirmar_item)

                    except (Exception, WebDriverException):
                        # Cancela o item se houver erro no preenchimento ou na confirmação, e pula pra próxima tentativa.
                        self.clicar(xpaths_pdt.btn_cancelar_item)
                        self._voltar()
                        continue


                # FINALIZAÇÃO E CONTABILIZAÇÃO (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_pdt.btn_inserir_observacao)
                    self.digitar(xpaths_pdt.observacao, row["observacao"])
                    
                    # bloco de validação
                    if not self.verificar_texto_digitado(xpaths_pdt.observacao, row["observacao"]):
                        self._voltar()
                        continue
                    else:
                        self.clicar(xpaths_pdt.btn_contabilizar)
                        self.clicar(xpaths_pdt.btn_confirmar_contabilizacao); self._aguardar_siafe()
                    
                    # bloco de verificação
                    if self._verificar_erro(xpaths_pdt.erro):
                        continue


                # ATUALIZAÇÃO DO DATAFRAME (COM VALIDAÇÃO) ---

                    try:

                        numPD = self.obter_texto(xpaths_pdt.numero_documento) # Obtém o número da PD
                        tempo_contab = str(round(time.perf_counter() - inicio, 2)).replace(".", ",") # Calcula o tempo de contabilização
                        df.loc[index, "num_documento"] = numPD
                        df.loc[index, "tempo_contab"] = tempo_contab
                        
                        if callback_sucesso is not None:
                            callback_sucesso(id=row["id"], num_documento=numPD, tempo_contab=tempo_contab)
    
                    except Exception:
                        messagebox.showerror(
                            "Erro",
                            '''Ocorreu um erro crítico com a integração com o banco de dados.
                            Comunique o erro à Equipe de Desenvolvimento!''')
                        return False

                except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                    messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.")
                    return False

                except (WebDriverException, Exception):
                    self._voltar()
                    continue

                else:
                    self._voltar()

        return True
   
### Nota Patrimonial (NP) ###
    def gerar_np(self, df, dict_map, callback_sucesso=None):
        """
        Contabiliza Notas Patrimoniais (NP).

        Inclui lógicas específicas para:
        - Seleção de Operação Patrimonial via valor ou texto (flag 'SelecaoPorValor').
        - Preenchimento de Inscrição Genérica com validação de conclusão (flags 'InscricaoGenerica', 'TipoInscricaoGenerica', 'IGCompleta').

        Args:
            df (pd.DataFrame): Tabela contendo os lançamentos. No formato: 'id', 'data', 'valor', 'observacao', 'tipo_id', 'num_documento' (inicialmente vazio) e 'tempo_contab' (inicialmente vazio).
            dict_map (dict): Dicionário contendo os dados de preenchimento para contabilização. No formato: {tipo_id: {"TipoDocumento": str, "UG": str, "DomicilioBancario": str, "DomicilioBancarioCompleto": str, "IEF": str, "Fonte": str, "FonteRJ": str, "TipoDetalhamentoFonte": str, "DetalhamentoFonte": str, "Convenio": str, "TipoPatrimonial": str, "ItemPatrimonial": str, "OperacaoPatrimonial": str, "NaturezaReceita": str (somente para orçamentário), "TipoCredor": str (PJ, CG, PF ou UG) (somente para extra-orçamentário), "Credor": str}}.
            # CONVERSAR COM O JOÃO A RESPEITO DA LINHA A CIMA! - FORMATO IMPREVISÍVEL
            
            callback_sucesso (callable, optional): Função a ser chamada quando uma NP é gerada com sucesso. 
                                                   Recebe o id, num_documento e tempo_contab.
        
        Returns:
            bool: True se processar a planilha sem erros críticos do WebDriver. 
                  False se exceder tentativas ou ocorrer erro grave.

        Obs:
            Para Operação Patrimonial por código: Adicione "SelecaoPorValor": True no dict_map.
            Para Inscrição Genérica: Adicione "InscricaoGenerica": <valor> (e opcionalmente "TipoInscricaoGenerica" e "IGCompleta") no dict_map.
        """

    # REESTRUTURAÇÃO DO DATAFRAME E NAVEGAÇÃO PARA CONTABILIZAÇÃO ---

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",") # Formata o valor
        df["tentativas"] = 0 # Cria uma coluna de tentativas para controle de falhas
        self.semsaldo = 0 # Flag para rastrear se a falha ocorreu especificamente por falta de saldo

        try: # Navega para Nota Patrimonial.
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_contabilidade)
            self.clicar(xpaths_np.btn_np)
        except Exception:
            messagebox.showerror("Erro", "Não foi possível navegar para 'Nota Patrimonial'.")
            return False


    # LOOP DE CONTABILIZAÇÃO (ENQUANTO EXISTIREM LANÇAMENTOS NÃO CONTABILIZADOS) ---

        while df['num_documento'].isna().any():

            for index, row in df[df['num_documento'].isna()].iterrows():


            # PREPARO DE DADOS ---

                if row["tentativas"] >= 3:
                    if self.semsaldo == 1:
                        messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas por saldo insuficiente.\nVerifique o erro e tente novamente.")
                    else:
                        messagebox.showerror(
                            "Erro",
                            f'''O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.
                            Verifique o erro e tente novamente.''')
                    return False

                dict_contabil = dict_map.get(row["tipo_id"]) # Busca as regras contábeis definidas no dicionário.
                if not dict_contabil:
                    df.loc[index, "tentativas"] = 3
                    continue

                df.loc[index, "tentativas"] += 1 # Incrementa o contador de tentativas


            # INÍCIO DA CONTABILIZAÇÃO ---

                try:

                    self.clicar(xpaths_np.btn_inserir_np)
                    inicio = time.perf_counter() # cronômetro


                # IDENTIFICAÇÃO (COM VALIDAÇÃO) ---

                    self.limpar(xpaths_np.data_emissao)
                    self.digitar(xpaths_np.data_emissao, row["data"]); self._aguardar_siafe()
                    ug_emitente = dict_contabil.get("UG")
                    if not ug_emitente: self._voltar(); continue
                    self.digitar(xpaths_np.ug_emitente, ug_emitente)
                    self.clicar(xpaths_np.ug_emitente_pesquisar); self._aguardar_siafe()

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_digitado(xpaths_np.data_emissao, row["data"]) and
                        self.verificar_texto_digitado(xpaths_np.ug_emitente, ug_emitente)
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # PREENCHIMENTO DO ITEM (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_np.btn_inserir_item)

                    try:
                        self.selecionar_texto(xpaths_np.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
                        self.selecionar_texto(xpaths_np.item_patrimonial, dict_contabil["ItemPatrimonial"])

                        # Lógica: Seleção por Valor ou Texto (via flag SelecaoPorValor = True no dicionário).
                        # Permite a flexibilidade de selecionar a operação patrimonial pelo seu código ou pelo seu texto.
                        if dict_contabil.get("SelecaoPorValor") is True:
                            self.selecionar_valor(xpaths_np.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
                        else:
                            self.selecionar_texto(xpaths_np.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])

                        # --- DETALHAMENTO ---
                        self.selecionar_texto(xpaths_np.ief, dict_contabil["IEF"])
                        self.selecionar_texto(xpaths_np.fonte, dict_contabil["Fonte"])
                        self.selecionar_texto(xpaths_np.fonte_rj, dict_contabil["FonteRJ"])
                        self.selecionar_texto(xpaths_np.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                        self.selecionar_texto(xpaths_np.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                        self.selecionar_texto(xpaths_np.ano, row["data"][-4:])
                        self.selecionar_texto(xpaths_np.domicilio_bancario, dict_contabil["DomicilioBancario"])
                        self.digitar(xpaths_np.valor, row["valor_str"])

                        # Lógica de Inscrição Genérica (Bloqueio/Desbloqueio)
                        if "InscricaoGenerica" in dict_contabil:
                            time.sleep(0.8)
                            if "TipoInscricaoGenerica" in dict_contabil:
                                self.selecionar_texto(xpaths_np.tipo_inscricao_generica, dict_contabil["TipoInscricaoGenerica"])
                                time.sleep(0.8)
                            self.digitar(xpaths_np.inscricao_generica, dict_contabil["InscricaoGenerica"])
                            time.sleep(0.8)
                            self.clicar(xpaths_np.valor) # Clica fora para validar

                        # Validação Inscrição Genérica Completa
                        if dict_contabil.get("IGCompleta"):
                            for _ in range(10):
                                elem_value = self.obter_atributo(xpaths_np.inscricao_generica, "value")
                                elem_title = self.obter_atributo(xpaths_np.inscricao_generica, "title")
                                if dict_contabil["IGCompleta"] in (str(elem_value), str(elem_title)):
                                    break
                                time.sleep(0.6)

                        time.sleep(0.6)
                        self.clicar(xpaths_np.btn_confirmar_item)

                    except (Exception, WebDriverException):
                        # Cancela o item se houver erro no preenchimento ou na confirmação, e pula pra próxima tentativa.
                        self.clicar(xpaths_np.btn_cancelar_item)
                        self._voltar()
                        continue


                # FINALIZAÇÃO E CONTABILIZAÇÃO (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_np.btn_inserir_observacao)
                    self.digitar(xpaths_np.observacao, row["observacao"])
                    
                    # bloco de validação
                    if not self.verificar_texto_digitado(xpaths_np.observacao, row["observacao"]):
                        self._voltar()
                        continue
                    else:
                        self.clicar(xpaths_np.btn_contabilizar)
                        self.clicar(xpaths_np.btn_confirmar_contabilizacao); self._aguardar_siafe()
                    
                    # bloco de verificação
                    if self._verificar_erro(xpaths_np.erro):
                        continue


                # ATUALIZAÇÃO DO DATAFRAME (COM VALIDAÇÃO) ---

                    try:

                        numNP = self.obter_texto(xpaths_np.numero_documento) # Obtém o número da NP
                        tempo_contab = str(round(time.perf_counter() - inicio, 2)).replace(".", ",") # Calcula o tempo de contabilização
                        df.loc[index, "num_documento"] = numNP
                        df.loc[index, "tempo_contab"] = tempo_contab

                        if callback_sucesso is not None:
                            callback_sucesso(id=row["id"], num_documento=numNP, tempo_contab=tempo_contab)

                    except Exception:
                        messagebox.showerror(
                            "Erro",
                            '''Ocorreu um erro crítico com a integração com o banco de dados.
                            Comunique o erro à Equipe de Desenvolvimento!''')
                        return False

                except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                    messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.")
                    return False

                except (WebDriverException, Exception):
                    self._voltar()
                    continue

                else:
                    self._voltar()

        return True
    
### Nota de Aplicação (NA) ###
    def gerar_na(self, df, dict_map, callback_sucesso=None):
        """
        Contabiliza Notas de Aplicação e Resgate (NA).

        Args:
            df (pd.DataFrame): Tabela contendo os lançamentos. No formato: 'id', 'data', 'valor', 'observacao', 'tipo_id', 'num_documento' (inicialmente vazio) e 'tempo_contab' (inicialmente vazio).
            dict_map (dict): Dicionário contendo os dados de preenchimento para contabilização. No formato: {tipo_id: {"TipoDocumento": str, "UG": str, "DomicilioBancario": str, "DomicilioBancarioCompleto": str, "IEF": str, "Fonte": str, "FonteRJ": str, "TipoDetalhamentoFonte": str, "DetalhamentoFonte": str, "Convenio": str, "TipoPatrimonial": str, "ItemPatrimonial": str, "OperacaoPatrimonial": str, "NaturezaReceita": str (somente para orçamentário), "TipoCredor": str (PJ, CG, PF ou UG) (somente para extra-orçamentário), "Credor": str}}.
            # CONVERSAR COM O JOÃO A RESPEITO DA LINHA A CIMA! - FORMATO IMPREVISÍVEL
            
            callback_sucesso (callable, optional): Função a ser chamada quando uma NA é gerada com sucesso. 
                                                   Recebe o id, num_documento e tempo_contab.
        
        Returns:
            bool: True se processar a planilha sem erros críticos do WebDriver. 
                  False se exceder tentativas ou ocorrer erro grave.

        Obs:
            Para Estorno: Adicione "Estorno": True no dict_map.
        """

    # REESTRUTURAÇÃO DO DATAFRAME E NAVEGAÇÃO PARA CONTABILIZAÇÃO ---

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",") # Formata o valor
        df["tentativas"] = 0 # Cria uma coluna de tentativas para controle de falhas
        self.semsaldo = 0 # Flag para rastrear se a falha ocorreu especificamente por falta de saldo

        try: # Navega para Nota de Aplicação e Resgate.
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_na.btn_na)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'Nota de Aplicação (NA)'.")
            return False


    # LOOP DE CONTABILIZAÇÃO (ENQUANTO EXISTIREM LANÇAMENTOS NÃO CONTABILIZADOS) ---

        while df['num_documento'].isna().any():

            for index, row in df[df['num_documento'].isna()].iterrows():


            # PREPARO DE DADOS ---

                if row["tentativas"] >= 3:
                    if self.semsaldo == 1:
                        messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas por saldo insuficiente.\nVerifique o erro e tente novamente.")
                    else:
                        messagebox.showerror(
                            "Erro",
                            f'''O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.
                            Verifique o erro e tente novamente.''')
                    return False

                dict_contabil = dict_map.get(row["tipo_id"]) # Busca as regras contábeis definidas no dicionário.
                if not dict_contabil:
                    df.loc[index, "tentativas"] = 3
                    continue

                df.loc[index, "tentativas"] += 1 # Incrementa o contador de tentativas


            # INÍCIO DA CONTABILIZAÇÃO ---

                try:

                    self.clicar(xpaths_na.btn_inserir_na)
                    inicio = time.perf_counter() # cronômetro


                # IDENTIFICAÇÃO (COM VALIDAÇÃO) ---

                    self.limpar(xpaths_na.data_emissao)
                    self.digitar(xpaths_na.data_emissao, row["data"]); self._aguardar_siafe()
                    self.digitar(xpaths_na.ug_emitente, dict_contabil["UG"])

                    # Lógica de Estorno (Via flag Estorno = True no dicionário)
                    if dict_contabil.get("Estorno") is True:
                        self.clicar(xpaths_na.estorno)

                    self.clicar(xpaths_na.ug_emitente_pesquisar); self._aguardar_siafe()
                    self.clicar(xpaths_na.ug_emitente_confirmar)

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_digitado(xpaths_na.data_emissao, row["data"])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # PREENCHIMENTO DO ITEM (COM VALIDAÇÃO) ---

                    self.selecionar_texto(xpaths_na.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
                    self.selecionar_texto(xpaths_na.item_patrimonial, dict_contabil["ItemPatrimonial"])
                    self.selecionar_texto(xpaths_na.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
                    self.selecionar_texto(xpaths_na.ief, dict_contabil["IEF"])
                    self.selecionar_texto(xpaths_na.fonte, dict_contabil["Fonte"])
                    self.selecionar_texto(xpaths_na.fonte_rj, dict_contabil["FonteRJ"])
                    self.selecionar_texto(xpaths_na.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                    self.selecionar_texto(xpaths_na.detalhamento_fonte, dict_contabil["DetalhamentoFonte"]); self._aguardar_siafe()
                    self.selecionar_texto(xpaths_na.domicilio_bancario_origem, dict_contabil["DomicilioBancario"]); self._aguardar_siafe()
                    self.selecionar_texto(xpaths_na.domicilio_bancario_destino, dict_contabil["DomicilioBancario"]); self._aguardar_siafe()
                    self.digitar(xpaths_na.valor, row["valor_str"])

                    # bloco de validação
                    validacoes = (
                        self.verificar_texto_selecionado(xpaths_na.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]) and
                        self.verificar_texto_selecionado(xpaths_na.domicilio_bancario_origem, dict_contabil["DomicilioBancario"]) and
                        self.verificar_texto_selecionado(xpaths_na.domicilio_bancario_destino, dict_contabil["DomicilioBancario"]) and
                        self.verificar_texto_digitado(xpaths_na.valor, row["valor_str"])
                    )
                    if not validacoes:
                        self._voltar()
                        continue


                # FINALIZAÇÃO E CONTABILIZAÇÃO (COM VALIDAÇÃO) ---

                    self.clicar(xpaths_na.btn_inserir_observacao)
                    self.digitar(xpaths_na.observacao, row["observacao"])

                    # bloco de validação
                    if not self.verificar_texto_digitado(xpaths_na.observacao, row["observacao"]):
                        self._voltar()
                        continue
                    else:
                        self.clicar(xpaths_na.btn_contabilizar)
                        self.clicar(xpaths_na.btn_confirmar_contabilizacao); self._aguardar_siafe()
                    
                    # bloco de verificação
                    if self._verificar_erro(xpaths_na.erro):
                        continue


                # ATUALIZAÇÃO DO DATAFRAME (COM VALIDAÇÃO) ---

                    try:

                        numNA = self.obter_texto(xpaths_na.numero_documento) # Obtém o número da NA
                        tempo_contab = str(round(time.perf_counter() - inicio, 2)).replace(".", ",") # Calcula o tempo de contabilização
                        df.loc[index, "num_documento"] = numNA
                        df.loc[index, "tempo_contab"] = tempo_contab
                        
                        if callback_sucesso is not None:
                            callback_sucesso(id=row["id"], num_documento=numNA, tempo_contab=tempo_contab)

                    except Exception:
                        messagebox.showerror(
                            "Erro",
                            '''Ocorreu um erro crítico com a integração com o banco de dados.
                            Comunique o erro à Equipe de Desenvolvimento!''')
                        return False

                except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                    messagebox.showerror("Erro", "Erro crítico no navegador.")
                    return False

                except (WebDriverException, Exception):
                    self._voltar()
                    continue

                else:
                    self._voltar()

        return True