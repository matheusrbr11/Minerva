from selenium.common.exceptions import (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException, WebDriverException, NoSuchElementException)
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from tkinter import messagebox
import pandas as pd
import decimal
import time

ctx = decimal.Context()
ctx.prec = 20

class Siafe:
    """
    Classe autônoma para encapsular toda a interação com o Siafe.
    Gerencia seu próprio driver e métodos de interação com o navegador.
    Esta biblioteca é genérica e não contém lógica de negócios (ex: tipo_id).
    """
    def __init__(self, driver_path='driver/msedgedriver.exe'):
        self.driver_path = driver_path
        self.driver = None
        self.wait = None

    def iniciar_driver(self):
        """Inicializa e configura o WebDriver do Edge."""
        try:
            edge_options = EdgeOptions()
            edge_options.add_argument("--start-maximized")
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            edge_service = EdgeService(self.driver_path)
            self.driver = webdriver.Edge(service=edge_service, options=edge_options)
            self.wait = WebDriverWait(self.driver, 20)
            return True
        except WebDriverException as e:
            messagebox.showerror("Erro", f"Erro ao iniciar o WebDriver. Verifique o caminho do driver: {e}")
            return False

    def abrir_url(self, url):
        if not self.driver or not self.wait:
            messagebox.showerror("Erro", "Driver nao inicializado. Nao e possivel abrir URL.")
            return False
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir URL: {url}. Erro: {e}")
            return False

    def fechar_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None
                self.wait = None

    def clicar(self, xpath):
        if self.wait:
            try:
                self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
                time.sleep(0.6)
                return True
            except Exception as e:
                raise e
        return False

    def digitar(self, xpath, texto):
        if self.wait:
            try:
                self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).send_keys(str(texto))
                time.sleep(0.6)
                return True
            except Exception as e:
                raise e
        return False

    def dldata(self, xpath, texto):
        if self.wait:
            try:
                elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                elemento.clear()
                time.sleep(0.6)
                elemento.send_keys(str(texto))
                time.sleep(0.6)
                return True
            except Exception as e:
                raise e
        return False
    
    def limpar(self, xpath):
        if self.wait:
            try:
                elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                elemento.clear()
                time.sleep(0.6)
                return True
            except Exception as e:
                raise e
        return False

    def selecionar(self, xpath, select):
        if self.wait:
            try:
                Select(self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))).select_by_visible_text(str(select))
                time.sleep(0.6)
                return True
            except Exception as e:
                raise e
        return False

    def selecionarv(self, xpath, select):
        if self.wait:
            try:
                Select(self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))).select_by_value(str(select))
                time.sleep(0.6)
                return True
            except Exception as e:
                raise e
        return False

    def obter_texto(self, xpath):
        if self.wait:
            try:
                elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                return elemento.text
            except:
                return None
        return None

    def obter_atributo(self, xpath, atributo):
        if self.wait:
            try:
                elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                return elemento.get_attribute(atributo)
            except:
                return None
        return None
    
    def is_selected(self, xpath):
        if self.wait:
            try:
                elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                return elemento.is_selected()
            except:
                return False
        return False
    
    def voltar(self):
        if self.wait:
            try:
                time.sleep(0.4)
                if self.clicar(xpaths_menu.btn_voltar):
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def verificar_texto_digitado(self, xpath, texto_esperado):
        if self.wait:
            try:
                valor_atual = self.obter_atributo(xpath, 'value')
                return valor_atual == texto_esperado
            except Exception:
                return False
        return False
    
    def obter_texto_select(self, xpath):
        if self.wait:
            try:
                elemento_select = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                select_object = Select(elemento_select)
                opcao_selecionada = select_object.first_selected_option
                return opcao_selecionada.text
            except Exception:
                return None
        return None
    
    def verificar_select(self, xpath, texto_esperado):
        if self.wait:
            try:
                texto_atual = self.obter_texto_select(xpath)
                return texto_atual == texto_esperado
            except Exception:
                return False
        return False

    def logar_siafe(self, siafeV, usuario, senha):
        url = 'https://siafe2.fazenda.rj.gov.br/Siafe/faces/login.jsp' if siafeV == 1 else 'http://10.8.237.102:8080/Siafe/faces/login.jsp'
        self.abrir_url(url)
        try:
            self.digitar(xpaths_login.usuario, usuario)
            self.digitar(xpaths_login.senha, senha)
            self.clicar(xpaths_login.btn_confirmar)
            
            try:
                erro_titulo = self.obter_texto(xpaths_login.erro_titulo)
                if erro_titulo and "Erro" in erro_titulo:
                    erro_body = self.obter_texto(xpaths_login.erro_corpo)
                    if erro_body and "Usuário e/ou senha incorretos." in erro_body:
                        messagebox.showwarning("Aviso", "Usuário ou Senha incorretos. Volte a tela de login e tente novamente.")
                        return False
                        
            except NoSuchElementException: 
                pass
                
        except Exception:
            messagebox.showerror("Erro", "Não foi possível logar no SIAFE.")
            return False
        
        return True  

    def _string_para_decimal(self, s):
        """Converte string '1.234,56' para Decimal('1234.56')."""
        return ctx.create_decimal(s.replace(".", "").replace(",", "."))

    def _decimal_para_string(self, d):
        """Converte Decimal('1234.56') para string '1234,56'."""
        quantized = d.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
        return str(quantized).replace(".", ",")

    def _preencher_item_gr_orcamentario(self, dict_contabil, valor_str):
        """Preenche um item Orçamentário da GR."""
        time.sleep(0.3)
        self.selecionar(xpaths_gr.tipo_patrimonial_orc, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_gr.item_patrimonial_orc, dict_contabil["ItemPatrimonial"])
        self.selecionar(xpaths_gr.operacao_patrimonial_orc, dict_contabil["OperacaoPatrimonial"]) 
        self.selecionar(xpaths_gr.natureza_receita_orc, dict_contabil["NaturezaReceita"])
        time.sleep(3)
        self.digitar(xpaths_gr.valor_orc, valor_str)
        time.sleep(0.3)
        
        if not self.verificar_select(xpaths_gr.operacao_patrimonial_orc, dict_contabil["OperacaoPatrimonial"]):
            raise Exception("Falha na verificação: Operacao Patrimonial (Orçamentário)")
        if not self.verificar_texto_digitado(xpaths_gr.valor_orc, valor_str):
             raise Exception("Falha na verificação: Valor (Orçamentário)")

    def _preencher_item_gr_extra_pj(self, dict_contabil, valor_str, ano):
        """Preenche um item Extra-Orçamentário da GR com Credor PJ."""
        self.selecionar(xpaths_gr.tipo_patrimonial_extra, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_gr.item_patrimonial_extra, dict_contabil["ItemPatrimonial"])
        self.selecionar(xpaths_gr.operacao_patrimonial_extra, dict_contabil["OperacaoPatrimonial"])
        self.selecionar(xpaths_gr.ano_extra, ano)
        time.sleep(0.3)
        self.digitar(xpaths_gr.valor_extra, valor_str)
        time.sleep(0.3)
        self.clicar(xpaths_gr.tipo_credor_pj_extra)
        self.digitar(xpaths_gr.credor_extra, dict_contabil["Credor"])
        self.clicar(xpaths_gr.credor_pesquisar_extra)
        self.wait.until(lambda driver: self.obter_atributo(xpaths_gr.credor_nome_extra, "value") != "")
        time.sleep(0.3)
        
        if not self.verificar_select(xpaths_gr.operacao_patrimonial_extra, dict_contabil["OperacaoPatrimonial"]):
            raise Exception("Falha na verificação: Operacao Patrimonial (Extra-Orçamentário)")
        if not self.verificar_texto_digitado(xpaths_gr.valor_extra, valor_str):
             raise Exception("Falha na verificação: Valor (Extra-Orçamentário)")
        
    def _preencher_item_gr_extra_cg(self, dict_contabil, valor_str, ano):
        """Preenche um item Extra-Orçamentário da GR com Credor CG."""
        self.selecionar(xpaths_gr.tipo_patrimonial_extra, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_gr.item_patrimonial_extra, dict_contabil["ItemPatrimonial"])
        self.selecionar(xpaths_gr.operacao_patrimonial_extra, dict_contabil["OperacaoPatrimonial"])
        self.selecionar(xpaths_gr.ano_extra, ano)
        time.sleep(0.3)
        self.digitar(xpaths_gr.valor_extra, valor_str)
        time.sleep(0.3)
        self.clicar(xpaths_gr.tipo_credor_cg_extra)
        self.digitar(xpaths_gr.credor_extra, dict_contabil["Credor"])
        self.clicar(xpaths_gr.credor_pesquisar_extra)
        self.wait.until(lambda driver: self.obter_atributo(xpaths_gr.credor_nome_extra, "value") != "")
        time.sleep(0.3)
        
        if not self.verificar_select(xpaths_gr.operacao_patrimonial_extra, dict_contabil["OperacaoPatrimonial"]):
            raise Exception("Falha na verificação: Operacao Patrimonial (Extra-Orçamentário)")
        if not self.verificar_texto_digitado(xpaths_gr.valor_extra, valor_str):
             raise Exception("Falha na verificação: Valor (Extra-Orçamentário)")

    def _preencher_item_pde(self, dict_contabil, valor_str, ano):
        """Preenche um item da PD Extra-Orçamentária."""
        self.selecionar(xpaths_pde.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_pde.item_patrimonial, dict_contabil["ItemPatrimonial"])
        self.selecionar(xpaths_pde.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
        self.selecionar(xpaths_pde.vinculacao_pagamento, dict_contabil["VinculacaoPagamento"])
        self.selecionar(xpaths_pde.ano, ano)
        time.sleep(0.3)
        self.digitar(xpaths_pde.valor, valor_str)
        
        if not self.verificar_select(xpaths_pde.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]):
             raise Exception("Falha na verificação: Operacao Patrimonial (PDE)")
        if not self.verificar_texto_digitado(xpaths_pde.valor, valor_str):
             raise Exception("Falha na verificação: Valor (PDE)")

    def _preencher_item_pdt(self, dict_contabil, valor_str):
        """Preenche um item da PD de Transferência (Seleção por TEXTO)."""
        self.selecionar(xpaths_pdt.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_pdt.item_patrimonial, dict_contabil["ItemPatrimonial"])
        self.selecionar(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
        time.sleep(0.6)
        self.digitar(xpaths_pdt.valor, valor_str)
        
        if not self.verificar_select(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]):
             raise Exception("Falha na verificação: Operacao Patrimonial (PDT)")
        if not self.verificar_texto_digitado(xpaths_pdt.valor, valor_str):
             raise Exception("Falha na verificação: Valor (PDT)")
        
    def _preencher_item_pdt_value(self, dict_contabil, valor_str):
        """Preenche um item da PD de Transferência (Seleção por VALOR)."""
        self.selecionar(xpaths_pdt.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_pdt.item_patrimonial, dict_contabil["ItemPatrimonial"])
        self.selecionarv(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
        time.sleep(0.6)
        self.digitar(xpaths_pdt.valor, valor_str)
        
        if not self.verificar_select(xpaths_pdt.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]):
             raise Exception("Falha na verificação: Operacao Patrimonial (PDT)")
        if not self.verificar_texto_digitado(xpaths_pdt.valor, valor_str):
             raise Exception("Falha na verificação: Valor (PDT)")

    def _preencher_item_np_base(self, dict_contabil, valor_str, ano):
        """Preenche os campos base de um item da NP (usado por todos os tipos de NP)."""
        self.selecionar(xpaths_np.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
        self.selecionar(xpaths_np.item_patrimonial, dict_contabil["ItemPatrimonial"])
        
        try:
            self.selecionarv(xpaths_np.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
        except Exception:
             self.selecionar(xpaths_np.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])

        self.selecionar(xpaths_np.ief, dict_contabil["IEF"])
        self.selecionar(xpaths_np.fonte, dict_contabil["Fonte"])
        self.selecionar(xpaths_np.fonte_rj, dict_contabil["FonteRJ"])
        self.selecionar(xpaths_np.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
        self.selecionar(xpaths_np.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
        self.selecionar(xpaths_np.ano, ano) 
        self.selecionar(xpaths_np.domicilio_bancario, dict_contabil["DomicilioBancario"])
        self.digitar(xpaths_np.valor, valor_str)

    def _preencher_item_np_bloqueio(self, dict_contabil, valor_str, ano):
        """Preenche um item de NP com lógica de Bloqueio."""
        self._preencher_item_np_base(dict_contabil, valor_str, ano)

        time.sleep(0.8)
        self.selecionar(xpaths_np.tipo_inscricao_generica, dict_contabil["TipoInscricaoGenerica"])
        time.sleep(0.8)
        self.digitar(xpaths_np.inscricao_generica, dict_contabil["InscricaoGenerica"])
        time.sleep(0.8)
        self.clicar(xpaths_np.valor)
        
        if dict_contabil.get("IGCompleta"):
            while True:
                elem_value = self.obter_atributo(xpaths_np.inscricao_generica, "value")
                elem_title = self.obter_atributo(xpaths_np.inscricao_generica, "title")
                if dict_contabil["IGCompleta"] in (elem_value, elem_title):
                    break
                time.sleep(0.6)

    def _preencher_item_np_desbloqueio(self, dict_contabil, valor_str, ano):
        """Preenche um item de NP com lógica de Desbloqueio."""
        self._preencher_item_np_base(dict_contabil, valor_str, ano)
        
        time.sleep(0.8)
        self.selecionar(xpaths_np.inscricao_generica, dict_contabil["InscricaoGenerica"])
        time.sleep(0.8)

        if dict_contabil.get("IGCompleta"):
            while True:
                elem_value = self.obter_atributo(xpaths_np.inscricao_generica, "value")
                elem_title = self.obter_atributo(xpaths_np.inscricao_generica, "title")
                if dict_contabil["IGCompleta"] in (elem_value, elem_title):
                    break
                time.sleep(0.6)

    def _gerar_gr_base(self, df, dict_map, callback_sucesso, item_filler_function, is_extra_orc):
        """Função base interna para GRs. Não chame diretamente."""
        try:
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_gr.btn_gr)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'Guia de Recolhimento (GR)'.")
            return False

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",")
        df["tentativas"] = 0

        while df['num_documento'].isna().any():
            for index, row in df.iterrows():
                if pd.isna(row["num_documento"]):
                    try:
                        if row["tentativas"] >= 3:
                            messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.\nVerifique o erro e tente novamente.")
                            return False

                        dict_contabil = dict_map.get(row["tipo_id"])
                        if not dict_contabil: continue

                        df.loc[index, "tentativas"] += 1
                        
                        self.clicar(xpaths_gr.btn_inserir_gr)
                        inicio = time.perf_counter()
                        self.dldata(xpaths_gr.data_emissao, row["data"])
                        self.digitar(xpaths_gr.data_recolhimento, row["data"])
                        self.selecionar(xpaths_gr.tipo_documento, dict_contabil["TipoDocumento"])
                        self.digitar(xpaths_gr.ug_emitente, dict_contabil["UG"])
                        self.clicar(xpaths_gr.ug_pesquisar)
                        
                        erro_encontrado = False
                        for _ in range(2):
                            try:
                                erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_gr.erro_pesquisar_ug))).text
                                if erro: 
                                    self.clicar(xpaths_gr.btn_erro_pesquisar_ug)
                                    erro_encontrado = True
                                    break
                            except: pass
                        if erro_encontrado: pass
                        
                        self.digitar(xpaths_gr.domicilio_bancario, dict_contabil["DomicilioBancario"])
                        self.clicar(xpaths_gr.domicilio_bancario_pesquisar)
                        
                        erro_encontrado = False
                        for _ in range(2):
                            try:
                                erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_gr.erro_pesquisar_domicilio))).text
                                if erro: 
                                    self.clicar(xpaths_gr.btn_erro_pesquisar_domicilio)
                                    erro_encontrado = True
                                    break
                            except: pass
                        if erro_encontrado: pass
                        
                        if not is_extra_orc:
                            self.digitar(xpaths_gr.ug_orcamentaria, dict_contabil["UG"])
                            self.clicar(xpaths_gr.ug_orcamentaria_pesquisar)
                            
                            erro_encontrado = False
                            for _ in range(2):
                                try:
                                    erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_gr.erro_pesquisar_ugo))).text
                                    if erro: 
                                        self.clicar(xpaths_gr.btn_erro_pesquisar_ugo)
                                        erro_encontrado = True
                                        break
                                except: pass
                            if erro_encontrado: pass
                            
                            self.selecionar(xpaths_gr.ief, dict_contabil["IEF"])

                        self.selecionar(xpaths_gr.fonte, dict_contabil["Fonte"])
                        self.selecionar(xpaths_gr.fonte_rj, dict_contabil["FonteRJ"])
                        self.selecionar(xpaths_gr.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                        if dict_contabil.get("DetalhamentoFonte"):
                            self.selecionar(xpaths_gr.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                        self.selecionar(xpaths_gr.convenio, dict_contabil["Convenio"])
                    
                        if not (self.verificar_texto_digitado(xpaths_gr.data_emissao, row["data"]) and self.verificar_texto_digitado(xpaths_gr.data_recolhimento, row["data"])):
                            self.voltar(); continue
                        if not self.verificar_select(xpaths_gr.tipo_documento, dict_contabil["TipoDocumento"]):
                            self.voltar(); continue
                        if not self.verificar_texto_digitado(xpaths_gr.domicilio_bancario, dict_contabil["DomicilioBancarioCompleto"]):
                            self.voltar(); continue

                        try:
                            if is_extra_orc:
                                self.clicar(xpaths_gr.btn_item_extraorcamentario)
                                self.clicar(xpaths_gr.btn_inserir_item_extraorcamentario)
                                item_filler_function(dict_contabil, row["valor_str"], row["data"][-4:])
                                self.clicar(xpaths_gr.btn_confirmar_item)
                            else:
                                self.clicar(xpaths_gr.btn_item_orcamentario)
                                self.clicar(xpaths_gr.btn_inserir_item_orcamentario)
                                item_filler_function(dict_contabil, row["valor_str"])
                                self.clicar(xpaths_gr.btn_confirmar_item_orc)
                        
                        except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                            raise
                        except (WebDriverException, Exception):
                            try:
                                if is_extra_orc:
                                    self.clicar(xpaths_gr.btn_cancelar_item)
                                else:
                                    self.clicar(xpaths_gr.btn_cancelar_item_orc)
                            except: pass
                            self.voltar()
                            continue       
                        
                        self.clicar(xpaths_gr.btn_inserir_observacao)
                        self.digitar(xpaths_gr.observacao, row["observacao"])
                        self.clicar(xpaths_gr.btn_contabilizar)
                        self.clicar(xpaths_gr.btn_confirmar_contabilizacao)
                        
                        try:
                            erro = self.obter_texto(xpaths_gr.erro)
                            if "Erro" in erro: self.voltar(); continue
                        except: pass
                        
                        numGR = self.obter_texto(xpaths_gr.numero_documento)
                        if numGR and numGR.strip():
                            fim = time.perf_counter()
                            tempo_contab = str(round(fim - inicio, 2))
                            tempo_contab = tempo_contab.replace(".", ",")
                            df.loc[index, "tempo_contab"] = tempo_contab
                            df.loc[index, "num_documento"] = numGR
                            if callable(callback_sucesso):
                                callback_sucesso(id=row["id"], num_documento=numGR, tempo_contab=tempo_contab)
                        else:
                            self.voltar()
                            continue
                        
                    except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                        messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.\nPor favor, reinicie o programa.")
                        return False
                    
                    except (WebDriverException, Exception):
                        self.voltar()
                        continue
                    
                    self.voltar()
                
        return True

    def gerar_gr_orcamentario(self, df, dict_map, callback_sucesso=None):
        """Gera um lote de GRs Orçamentárias."""
        return self._gerar_gr_base(df, dict_map, callback_sucesso, self._preencher_item_gr_orcamentario, is_extra_orc=False)
        
    def gerar_gr_extra_pj(self, df, dict_map, callback_sucesso=None):
        """Gera um lote de GRs Extra-Orçamentárias (Credor PJ)."""
        return self._gerar_gr_base(df, dict_map, callback_sucesso, self._preencher_item_gr_extra_pj, is_extra_orc=True)

    def gerar_gr_extra_cg(self, df, dict_map, callback_sucesso=None):
        """Gera um lote de GRs Extra-Orçamentárias (Credor CG)."""
        return self._gerar_gr_base(df, dict_map, callback_sucesso, self._preencher_item_gr_extra_cg, is_extra_orc=True)

    def gerar_na(self, df, dict_map, callback_sucesso=None):
        """Gera uma Nota de Aplicação (NA) padrão."""
        try:
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_na.btn_na)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'Nota de Aplicação (NA)'.")
            return False

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",")
        df["tentativas"] = 0
        semsaldo = 0

        while df['num_documento'].isna().any():
            for index, row in df.iterrows():
                if pd.isna(row["num_documento"]):
                    try:
                        if row["tentativas"] >= 3:
                            if semsaldo == 1:
                                messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas por saldo insuficiente.\nVerifique o erro e tente novamente.")
                            else:
                                messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.\nVerifique o erro e tente novamente.")
                            return False

                        dict_contabil = dict_map.get(row["tipo_id"])
                        if not dict_contabil:
                            df.loc[index, "tentativas"] = 3
                            continue
                        
                        df.loc[index, "tentativas"] += 1

                        self.clicar(xpaths_na.btn_inserir_na)
                        inicio = time.perf_counter()
                        self.dldata(xpaths_na.data_emissao, row["data"])
                        self.digitar(xpaths_na.ug_emitente, dict_contabil["UG"])
                        
                        self.clicar(xpaths_na.ug_emitente_pesquisar)
                        self.clicar(xpaths_na.ug_emitente_confirmar)
                        self.selecionar(xpaths_na.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
                        self.selecionar(xpaths_na.item_patrimonial, dict_contabil["ItemPatrimonial"])
                        self.selecionar(xpaths_na.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
                        self.selecionar(xpaths_na.ief, dict_contabil["IEF"])
                        self.selecionar(xpaths_na.fonte, dict_contabil["Fonte"])
                        self.selecionar(xpaths_na.fonte_rj, dict_contabil["FonteRJ"])
                        self.selecionar(xpaths_na.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                        self.selecionar(xpaths_na.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                        time.sleep(0.3)
                        self.selecionar(xpaths_na.domicilio_bancario_origem, dict_contabil["DomicilioBancario"])
                        time.sleep(0.3)
                        self.selecionar(xpaths_na.domicilio_bancario_destino, dict_contabil["DomicilioBancario"])
                        time.sleep(0.3)
                        self.digitar(xpaths_na.valor, row["valor_str"])
                        
                        if not self.verificar_texto_digitado(xpaths_na.data_emissao, row["data"]): self.voltar(); continue
                        if not self.verificar_select(xpaths_na.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]): self.voltar(); continue
                        if not (self.verificar_select(xpaths_na.domicilio_bancario_origem, dict_contabil["DomicilioBancario"]) and self.verificar_select(xpaths_na.domicilio_bancario_destino, dict_contabil["DomicilioBancario"])): self.voltar(); continue
                        if not self.verificar_texto_digitado(xpaths_na.valor, row["valor_str"]): self.voltar(); continue
                        
                        self.clicar(xpaths_na.btn_inserir_observacao)
                        self.digitar(xpaths_na.observacao, row["observacao"])
                        self.clicar(xpaths_na.btn_contabilizar)
                        self.clicar(xpaths_na.btn_confirmar_contabilizacao)
                        
                        try:
                            erro_titulo = self.obter_texto(xpaths_na.erro_titulo)
                            if erro_titulo and "Erro" in erro_titulo:
                                erro_body = self.obter_texto(xpaths_na.erro_corpo)
                                if erro_body and "Saldo insuficiente para contabilização" in erro_body: 
                                    messagebox.showwarning("Aviso", "Saldo insuficiente para contabilização. \n\nO programa tentará contabilizar este lançamento novamente. Se o saldo for suficiente, a operação será concluida. \n\nPressione OK para continuar.")
                                    semsaldo = 1
                                self.voltar()
                                continue
                        except: pass

                        numNA = self.obter_texto(xpaths_na.numero_documento)
                        if numNA and numNA.strip():
                            fim = time.perf_counter()
                            tempo_contab = str(round(fim - inicio, 2))
                            tempo_contab = tempo_contab.replace(".", ",")
                            df.loc[index, "tempo_contab"] = tempo_contab
                            df.loc[index, "num_documento"] = numNA
                            if callable(callback_sucesso):
                                callback_sucesso(id=row["id"], num_documento=numNA, tempo_contab=tempo_contab)
                        else:
                            self.voltar()
                            continue
                        
                    except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                        messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.\n\nPressione OK para voltar a tela de contabilização.")
                        return False
                    
                    except Exception:
                        self.voltar()
                        continue
                    
                    self.voltar()
        return True

    def gerar_na_estorno(self, df, dict_map, callback_sucesso=None):
        """Gera uma Nota de Aplicação (NA) de ESTORNO."""
        try:
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_na.btn_na)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'Nota de Aplicação (NA)'.")
            return False

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",")
        df["tentativas"] = 0
        semsaldo = 0

        while df['num_documento'].isna().any():
            for index, row in df.iterrows():
                if pd.isna(row["num_documento"]):
                    try:
                        if row["tentativas"] >= 3:
                            if semsaldo == 1:
                                messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas por saldo insuficiente.\nVerifique o erro e tente novamente.")
                            else:
                                messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.\nVerifique o erro e tente novamente.")
                            return False

                        dict_contabil = dict_map.get(row["tipo_id"])
                        if not dict_contabil:
                            df.loc[index, "tentativas"] = 3
                            continue
                        
                        df.loc[index, "tentativas"] += 1

                        self.clicar(xpaths_na.btn_inserir_na)
                        inicio = time.perf_counter()
                        self.dldata(xpaths_na.data_emissao, row["data"])
                        self.digitar(xpaths_na.ug_emitente, dict_contabil["UG"])
                        self.clicar(xpaths_na.estorno)
                        self.clicar(xpaths_na.ug_emitente_pesquisar)
                        self.clicar(xpaths_na.ug_emitente_confirmar)
                        self.selecionar(xpaths_na.tipo_patrimonial, dict_contabil["TipoPatrimonial"])
                        self.selecionar(xpaths_na.item_patrimonial, dict_contabil["ItemPatrimonial"])
                        self.selecionar(xpaths_na.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"])
                        self.selecionar(xpaths_na.ief, dict_contabil["IEF"])
                        self.selecionar(xpaths_na.fonte, dict_contabil["Fonte"])
                        self.selecionar(xpaths_na.fonte_rj, dict_contabil["FonteRJ"])
                        self.selecionar(xpaths_na.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                        self.selecionar(xpaths_na.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                        time.sleep(0.3)
                        self.selecionar(xpaths_na.domicilio_bancario_origem, dict_contabil["DomicilioBancario"])
                        time.sleep(0.3)
                        self.selecionar(xpaths_na.domicilio_bancario_destino, dict_contabil["DomicilioBancario"])
                        time.sleep(0.3)
                        self.digitar(xpaths_na.valor, row["valor_str"])
                        
                        if not self.verificar_texto_digitado(xpaths_na.data_emissao, row["data"]): self.voltar(); continue
                        if not self.verificar_select(xpaths_na.operacao_patrimonial, dict_contabil["OperacaoPatrimonial"]): self.voltar(); continue
                        if not (self.verificar_select(xpaths_na.domicilio_bancario_origem, dict_contabil["DomicilioBancario"]) and self.verificar_select(xpaths_na.domicilio_bancario_destino, dict_contabil["DomicilioBancario"])): self.voltar(); continue
                        if not self.verificar_texto_digitado(xpaths_na.valor, row["valor_str"]): self.voltar(); continue
                        
                        self.clicar(xpaths_na.btn_inserir_observacao)
                        self.digitar(xpaths_na.observacao, row["observacao"])
                        self.clicar(xpaths_na.btn_contabilizar)
                        self.clicar(xpaths_na.btn_confirmar_contabilizacao)
                        
                        try:
                            erro_titulo = self.obter_texto(xpaths_na.erro_titulo)
                            if erro_titulo and "Erro" in erro_titulo:
                                erro_body = self.obter_texto(xpaths_na.erro_corpo)
                                if erro_body and "Saldo insuficiente para contabilização" in erro_body: 
                                    messagebox.showwarning("Aviso", "Saldo insuficiente para contabilização. \n\nO programa tentará contabilizar este lançamento novamente. Se o saldo for suficiente, a operação será concluida. \n\nPressione OK para continuar.")
                                    semsaldo = 1
                                self.voltar()
                                continue
                        except: pass

                        numNA = self.obter_texto(xpaths_na.numero_documento)
                        if numNA and numNA.strip():
                            fim = time.perf_counter()
                            tempo_contab = str(round(fim - inicio, 2))
                            tempo_contab = tempo_contab.replace(".", ",")
                            df.loc[index, "tempo_contab"] = tempo_contab
                            df.loc[index, "num_documento"] = numNA
                            if callable(callback_sucesso):
                                callback_sucesso(id=row["id"], num_documento=numNA, tempo_contab=tempo_contab)
                        else:
                            self.voltar()
                            continue
                        
                    except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                        messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.\n\nPressione OK para voltar a tela de contabilização.")
                        return False
                    
                    except Exception:
                        self.voltar()
                        continue
                    
                    self.voltar()
        return True
        
    def gerar_pde(self, df, dict_map, callback_sucesso=None):
        """Gera PD Extra-Orçamentária."""
        try:
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_pde.btn_pde)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possível navegar para 'PD Extra-orçamentária'.")
            return False

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",")
        df["tentativas"] = 0

        while df['num_documento'].isna().any():
            for index, row in df.iterrows():
                if pd.isna(row["num_documento"]):
                    try:
                        if row["tentativas"] >= 3:
                            messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.\nVerifique o erro e tente novamente.")
                            return False
                        
                        dict_contabil = dict_map.get(row["tipo_id"])
                        if not dict_contabil: continue

                        df.loc[index, "tentativas"] += 1
                        
                        self.clicar(xpaths_pde.btn_inserir_pde)
                        inicio = time.perf_counter()
                        self.limpar(xpaths_pde.data_emissao)
                        self.digitar(xpaths_pde.data_emissao, row["data"])
                        time.sleep(0.3)
                        self.clicar(xpaths_pde.data_programacao)
                        self.digitar(xpaths_pde.data_programacao, row["data"])
                        time.sleep(0.3)
                        self.digitar(xpaths_pde.data_vencimento, row["data"])
                        self.digitar(xpaths_pde.ug_emitente, dict_contabil["UG"])
                        self.clicar(xpaths_pde.ug_emitente_pesquisar)
                        
                        if not self.is_selected(xpaths_pde.ob_regulaziracao):
                            self.clicar(xpaths_pde.ob_regulaziracao)
                        self.selecionar(xpaths_pde.regularizacao, dict_contabil["Regularizacao"])
                        
                        self.digitar(xpaths_pde.ug_pagadora, dict_contabil["UG"])
                        self.clicar(xpaths_pde.ug_pagadora_pesquisar)
                        self.digitar(xpaths_pde.domicilio_bancario_origem, dict_contabil["DomicilioBancarioOrigem"])
                        time.sleep(0.3)
                        self.clicar(xpaths_pde.domicilio_bancario_origem_pesquisar)
                        time.sleep(0.3)
                        self.selecionar(xpaths_pde.ief, dict_contabil["IEF"])
                        self.selecionar(xpaths_pde.fonte, dict_contabil["Fonte"])
                        self.selecionar(xpaths_pde.fonte_rj, dict_contabil["FonteRJ"])
                        self.selecionar(xpaths_pde.tipo_detalhamento_fonte, dict_contabil["TipoDetalhamentoFonte"])
                        self.selecionar(xpaths_pde.detalhamento_fonte, dict_contabil["DetalhamentoFonte"])
                        self.clicar(xpaths_pde.tipo_credor_pj)
                        self.digitar(xpaths_pde.credor_pj, dict_contabil["Credor"])
                        self.clicar(xpaths_pde.credor_pj_pesquisar)
                        time.sleep(0.3)
                        self.selecionar(xpaths_pde.domicilio_bancario_destino, dict_contabil["DomicilioBancarioDestino"])
                        time.sleep(0.3)
                        self.digitar(xpaths_pde.competencia, row["data"][-7:])
                        
                        if not (self.verificar_texto_digitado(xpaths_pde.data_emissao, row["data"]) and self.verificar_texto_digitado(xpaths_pde.data_programacao, row["data"]) and self.verificar_texto_digitado(xpaths_pde.data_vencimento, row["data"])):
                            self.voltar(); continue
                        if not (self.verificar_texto_digitado(xpaths_pde.domicilio_bancario_origem, dict_contabil["DomicilioBancarioOrigemCompleto"]) and self.verificar_select(xpaths_pde.domicilio_bancario_destino, dict_contabil["DomicilioBancarioDestino"])):
                            self.voltar(); continue

                        self.clicar(xpaths_pde.btn_itens)
                        self.clicar(xpaths_pde.btn_inserir_item)
                        
                        try:
                            self._preencher_item_pde(dict_contabil, row["valor_str"], row["data"][-4:])
                            self.clicar(xpaths_pde.btn_confirmar_item)
                            
                        except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                            raise
                        except (WebDriverException, Exception):
                            self.clicar(xpaths_pde.btn_cancelar_item)
                            self.voltar()
                            continue  

                        self.clicar(xpaths_pde.btn_inserir_observacao)
                        self.digitar(xpaths_pde.observacao, row["observacao"])
                        self.clicar(xpaths_pde.btn_contabilizar)
                        self.clicar(xpaths_pde.btn_confirmar_contabilizacao)
                        
                        try:
                            erro = self.obter_texto(xpaths_pde.erro)
                            if "Erro" in erro: self.voltar(); continue
                        except: pass

                        numPD = self.obter_texto(xpaths_pde.numero_documento)
                        if numPD and numPD.strip():
                            fim = time.perf_counter()
                            tempo_contab = str(round(fim - inicio, 2))
                            tempo_contab = tempo_contab.replace(".", ",")
                            df.loc[index, "tempo_contab"] = tempo_contab
                            df.loc[index, "num_documento"] = numPD
                            if callable(callback_sucesso):
                                callback_sucesso(id=row["id"], num_documento=numPD, tempo_contab=tempo_contab)
                        else:
                            self.voltar()
                            continue
                        
                    except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                        messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.\n\nPressione OK para voltar a tela de contabilização.")
                        return False
                    
                    except (Exception, WebDriverException):
                        self.voltar()
                        continue
                    
                    self.voltar()
                
        return True

    def _gerar_pdt_base(self, df, dict_map, callback_sucesso, item_filler_function):
        """Função base interna para PD de Transferência. Não chame diretamente."""
        try:
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_execucao_financeira)
            self.clicar(xpaths_pdt.btn_pdt)
        except Exception:
            messagebox.showerror("Erro", f"Não foi possivel navegar para 'PD de Transferência'.")
            return False

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",")
        df["tentativas"] = 0

        while df['num_documento'].isna().any():
            for index, row in df.iterrows():
                if pd.isna(row["num_documento"]):
                    try:
                        if row["tentativas"] >= 3:
                            messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.\nVerifique o erro e tente novamente.")
                            return False

                        dict_contabil = dict_map.get(row["tipo_id"])
                        if not dict_contabil: continue

                        df.loc[index, "tentativas"] += 1

                        self.clicar(xpaths_pdt.btn_inserir_pdt)
                        inicio = time.perf_counter()
                        self.limpar(xpaths_pdt.data_emissao)
                        self.digitar(xpaths_pdt.data_emissao, row["data"])
                        time.sleep(0.3)
                        self.clicar(xpaths_pdt.data_programacao)
                        self.digitar(xpaths_pdt.data_programacao, row["data"])
                        time.sleep(0.3)
                        self.digitar(xpaths_pdt.data_vencimento, row["data"])
                        self.digitar(xpaths_pdt.ug_emitente, dict_contabil["UG"])
                        self.clicar(xpaths_pdt.ug_emitente_pesquisar)
                        
                        erro_encontrado = False
                        for _ in range(2):
                            try:
                                erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_pdt.erro_pesquisar_uge))).text
                                if erro: 
                                    self.clicar(xpaths_pdt.btn_erro_pesquisar_uge)
                                    erro_encontrado = True
                                    break
                            except: pass
                        if erro_encontrado: pass
                        
                        ug_favorecida = dict_contabil.get("UGFavorecida", dict_contabil["UG"])
                        self.digitar(xpaths_pdt.ug_favorecida, ug_favorecida)
                        self.clicar(xpaths_pdt.ug_favorecida_pesquisar)
                        
                        erro_encontrado = False
                        for _ in range(2):
                            try:
                                erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_pdt.erro_pesquisar_ugf))).text
                                if erro: 
                                    self.clicar(xpaths_pdt.btn_erro_pesquisar_ugf)
                                    erro_encontrado = True
                                    break
                            except: pass
                        if erro_encontrado: pass
                        
                        self.digitar(xpaths_pdt.ug_pagadora, dict_contabil["UG"])
                        self.clicar(xpaths_pdt.ug_pagadora_pesquisar)
                        
                        erro_encontrado = False
                        for _ in range(2):
                            try:
                                erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_pdt.erro_pesquisar_ugp))).text
                                if erro: 
                                    self.clicar(xpaths_pdt.btn_erro_pesquisar_ugp)
                                    erro_encontrado = True
                                    break
                            except: pass
                        if erro_encontrado: pass
                        
                        if "Regularizacao" in dict_contabil:
                            if not self.is_selected(xpaths_pdt.ob_regulaziracao):
                                self.clicar(xpaths_pdt.ob_regulaziracao)
                            self.selecionar(xpaths_pdt.regularizacao, dict_contabil["Regularizacao"])
                        
                        self.digitar(xpaths_pdt.domicilio_bancario_emitente, dict_contabil["DomicilioBancarioOrigem"])
                        self.clicar(xpaths_pdt.domicilio_bancario_emitente_pesquisar)
                        
                        erro_encontrado = False
                        for _ in range(2):
                            try:
                                erro = WebDriverWait(self.driver, 1.0).until(EC.presence_of_element_located((By.XPATH, xpaths_pdt.erro_pesquisar_domicilio_origem))).text
                                if erro: 
                                    self.clicar(xpaths_pdt.btn_erro_pesquisar_domicilio_origem)
                                    erro_encontrado = True
                                    break
                            except: pass
                        if erro_encontrado: pass
                        
                        time.sleep(0.3)
                        self.selecionar(xpaths_pdt.ief_origem, dict_contabil["IEF"])
                        self.selecionar(xpaths_pdt.fonte_origem, dict_contabil["Fonte"])
                        self.selecionar(xpaths_pdt.fonte_rj_origem, dict_contabil["FonteRJ"])
                        self.selecionar(xpaths_pdt.tipo_detalhamento_fonte_origem, dict_contabil["TipoDetalhamentoFonte"])
                        self.selecionar(xpaths_pdt.detalhamento_fonte_origem, dict_contabil["DetalhamentoFonte"])
                        self.selecionar(xpaths_pdt.convenio_origem, dict_contabil["Convenio"])
                        self.digitar(xpaths_pdt.domicilio_bancario_favorecida, dict_contabil["DomicilioBancarioDestino"])
                        self.clicar(xpaths_pdt.domicilio_bancario_favorecida_pesquisar)
                        
                        if "BCO AUTENT" in dict_contabil.get("DomicilioBancarioDestinoCompleto", ""):
                            time.sleep(0.3)
                            self.clicar(xpaths_pdt.tab_bco_autent)
                            time.sleep(0.3)
                            self.clicar(xpaths_pdt.tab_ok)
                            time.sleep(0.3)

                        self.selecionar(xpaths_pdt.ief_favorecida, dict_contabil["IEF"])
                        self.selecionar(xpaths_pdt.fonte_favorecida, dict_contabil["Fonte"])
                        self.selecionar(xpaths_pdt.fonte_rj_favorecida, dict_contabil["FonteRJ"])
                        self.selecionar(xpaths_pdt.tipo_detalhamento_fonte_favorecida, dict_contabil["TipoDetalhamentoFonte"])
                        self.selecionar(xpaths_pdt.detalhamento_fonte_favorecida, dict_contabil["DetalhamentoFonte"])
                        time.sleep(0.3)
                        self.selecionar(xpaths_pdt.convenio_favorecida, dict_contabil["Convenio"])
                        time.sleep(0.6)
                        self.digitar(xpaths_pdt.competencia, row["data"][-7:])
                        
                        if dict_contabil.get("JustificativaRegularizacao"):
                            self.digitar(xpaths_pdt.justificativa_regularizacao, dict_contabil["JustificativaRegularizacao"])

                        if not (self.verificar_texto_digitado(xpaths_pdt.data_emissao, row["data"]) and self.verificar_texto_digitado(xpaths_pdt.data_programacao, row["data"]) and self.verificar_texto_digitado(xpaths_pdt.data_vencimento, row["data"])):
                            self.voltar(); continue
                        if not (self.verificar_texto_digitado(xpaths_pdt.domicilio_bancario_emitente, dict_contabil['DomicilioBancarioOrigemCompleto']) and self.verificar_texto_digitado(xpaths_pdt.domicilio_bancario_favorecida, dict_contabil['DomicilioBancarioDestinoCompleto'])):
                            self.voltar(); continue

                        self.clicar(xpaths_pdt.btn_itens)
                        self.clicar(xpaths_pdt.btn_inserir_item)
                        
                        try: 
                            item_filler_function(dict_contabil, row["valor_str"])
                            self.clicar(xpaths_pdt.btn_confirmar_item)
                            
                        except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                            raise
                        except (WebDriverException, Exception):
                            self.clicar(xpaths_pdt.btn_cancelar_item)
                            self.voltar()
                            continue

                        self.clicar(xpaths_pdt.btn_inserir_observacao)
                        self.digitar(xpaths_pdt.observacao, row["observacao"])
                        self.clicar(xpaths_pdt.btn_contabilizar)
                        self.clicar(xpaths_pdt.btn_confirmar_contabilizacao)
                        
                        try:
                            erro = self.obter_texto(xpaths_pdt.erro)
                            if "Erro" in erro: self.voltar(); continue
                        except: pass

                        numPD = self.obter_texto(xpaths_pdt.numero_documento)
                        if numPD and numPD.strip():
                            fim = time.perf_counter()
                            tempo_contab = str(round(fim - inicio, 2))
                            tempo_contab = tempo_contab.replace(".", ",")
                            df.loc[index, "tempo_contab"] = tempo_contab
                            df.loc[index, "num_documento"] = numPD
                            if callable(callback_sucesso):
                                callback_sucesso(id=row["id"], num_documento=numPD, tempo_contab=tempo_contab)
                        else:
                            self.voltar()
                            continue
                        
                    except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                        messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.\n\nPressione OK para voltar a tela de contabilização.")
                        return False
                    
                    except (WebDriverException, Exception):
                        self.voltar()
                        continue
                    
                    self.voltar()
                    
        return True

    def gerar_pdt(self, df, dict_map, callback_sucesso=None):
        """Gera PD de Transferência (seleção de operação por TEXTO)."""
        return self._gerar_pdt_base(df, dict_map, callback_sucesso, self._preencher_item_pdt)

    def gerar_pdt_value(self, df, dict_map, callback_sucesso=None):
        """Gera PD de Transferência (seleção de operação por VALOR)."""
        return self._gerar_pdt_base(df, dict_map, callback_sucesso, self._preencher_item_pdt_value)

    def _gerar_np_base(self, df, dict_map, callback_sucesso, item_filler_function):
        """Função base interna para NPs de 1 item. Não chame diretamente."""
        try:
            self.clicar(xpaths_menu.btn_execucao)
            self.clicar(xpaths_menu.btn_contabilidade)
            self.clicar(xpaths_np.btn_np)
        except Exception:
            messagebox.showerror("Erro", "Não foi possível navegar para 'Nota Patrimonial'.")
            return False

        df["valor_str"] = df["valor"].astype(str).str.replace(".", ",")
        df["tentativas"] = 0
        semsaldo = 0

        while df['num_documento'].isna().any():
            for index, row in df.iterrows():
                if pd.isna(row["num_documento"]):
                    try:
                        if row["tentativas"] >= 3:
                            if semsaldo == 1:
                                messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas por saldo insuficiente.\nVerifique o erro e tente novamente.")
                            else:
                                messagebox.showerror("Erro", f"O lançamento com ID {row['id']} excedeu o limite de 3 tentativas.\nVerifique o erro e tente novamente.")
                            return False

                        tipo_id = row["tipo_id"]
                        dict_contabil = dict_map.get(tipo_id)
                        
                        if not dict_contabil: 
                            df.loc[index, "tentativas"] = 3
                            continue

                        df.loc[index, "tentativas"] += 1
                        
                        self.clicar(xpaths_np.btn_inserir_np)
                        inicio = time.perf_counter()
                        self.dldata(xpaths_np.data_emissao, row["data"])
                        
                        ug_emitente = dict_contabil.get("UG")
                            
                        if not ug_emitente:
                            self.voltar(); continue
                            
                        self.digitar(xpaths_np.ug_emitente, ug_emitente)
                        self.clicar(xpaths_np.ug_emitente_pesquisar)
                        
                        ano_lancamento = row["data"][-4:]
                        
                        self.clicar(xpaths_np.btn_inserir_item)
                        try:
                            item_filler_function(dict_contabil, row["valor_str"], ano_lancamento)
                            time.sleep(0.6)
                            self.clicar(xpaths_np.btn_confirmar_item)
                        except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                            raise
                        except (WebDriverException, Exception):
                            self.clicar(xpaths_np.btn_cancelar_item)
                            self.voltar()
                            continue 
                        
                        self.clicar(xpaths_np.btn_inserir_observacao)
                        self.digitar(xpaths_np.observacao, row["observacao"])
                        self.clicar(xpaths_np.btn_contabilizar)
                        self.clicar(xpaths_np.btn_confirmar_contabilizacao)
                        
                        try:
                            erro_titulo = self.obter_texto(xpaths_np.erro_titulo)
                            if erro_titulo and "Erro" in erro_titulo:
                                erro_body = self.obter_texto(xpaths_np.erro_corpo)
                                if erro_body and "Saldo insuficiente para contabilização" in erro_body: 
                                    messagebox.showwarning("Aviso", "Saldo insuficiente para contabilização. \n\nO programa tentará contabilizar este lançamento novamente. Se o saldo for suficiente, a operação será concluida. \n\nPressione OK para continuar.")
                                    semsaldo = 1
                                self.voltar()
                                continue
                        except: pass
                        
                        numNP = self.obter_texto(xpaths_np.numero_documento)
                        if numNP and numNP.strip():
                            fim = time.perf_counter()
                            tempo_contab = str(round(fim - inicio, 2))
                            tempo_contab = tempo_contab.replace(".", ",")
                            df.loc[index, "tempo_contab"] = tempo_contab
                            df.loc[index, "num_documento"] = numNP
                            if callable(callback_sucesso):
                                callback_sucesso(id=row["id"], num_documento=numNP, tempo_contab=tempo_contab)
                        else:
                            self.voltar()
                            continue
                        
                    except (NoSuchWindowException, SessionNotCreatedException, InvalidSessionIdException):
                        messagebox.showerror("Erro", "Ocorreu um erro crítico com o navegador.\n\nPressione OK para voltar a tela de contabilização.")
                        return False
                    
                    except (WebDriverException, Exception):
                        self.voltar()
                        continue
                    
                    self.voltar()
                    
        return True

    def gerar_np(self, df, dict_map, callback_sucesso=None):
        """Gera NP de 1 item, sem lógica de Inscrição Genérica."""
        return self._gerar_np_base(df, dict_map, callback_sucesso, self._preencher_item_np_base)
        
    def gerar_np_bloqueio(self, df, dict_map, callback_sucesso=None):
        """Gera NP de 1 item, com lógica de Inscrição Genérica (Bloqueio)."""
        return self._gerar_np_base(df, dict_map, callback_sucesso, self._preencher_item_np_bloqueio)

    def gerar_np_desbloqueio(self, df, dict_map, callback_sucesso=None):
        """Gera NP de 1 item, com lógica de Inscrição Genérica (Desbloqueio)."""
        return self._gerar_np_base(df, dict_map, callback_sucesso, self._preencher_item_np_desbloqueio)

class xpaths_login:
    """ XPaths para a tela de login. """
    usuario = '//*[@id="loginBox:itxUsuario::content"]'
    senha = '//*[@id="loginBox:itxSenhaAtual::content"]'
    btn_confirmar = '//*[@id="loginBox:btnConfirmar"]'
    erro_titulo = '//*[@id="docPrincipal::msgDlg::_ttxt"]'
    erro_corpo = '//*[@id="docPrincipal::msgDlg::_ccntr"]'

class xpaths_menu:
    """ XPaths para os menus principais de navegação. """
    btn_execucao = '//*[@id="pt1:pt_np4:1:pt_cni6::disclosureAnchor"]'
    btn_execucao_financeira = '//*[@id="pt1:pt_np3:1:pt_cni4::disclosureAnchor"]'
    btn_contabilidade = '//*[@id="pt1:pt_np3:2:pt_cni4::disclosureAnchor"]'
    btn_voltar = '//*[@id="tplSip:pt_bc1:2:pt_cni7"]'

class xpaths_gr: 
    """ XPaths para a tela de Guia de Recolhimento (GR). """
    
    # Menu
    btn_gr = "//*[text()='Guia de Recolhimento']"
    btn_inserir_gr = '//*[@id="pt1:tblGuiaRecolhimento:btnInsert"]'
    
    # Detalhamento
    data_emissao = '//*[@id="tplSip:itxDataInclusao::content"]'
    data_recolhimento = '//*[@id="tplSip:itxDataRecolhimento::content"]'
    tipo_documento = '//*[@id="tplSip:cbxTipoDocumento::content"]'
    ug_emitente = '//*[@id="tplSip:lovUgEmitente:itxLovDec::content"]'
    ug_pesquisar = '//*[@id="tplSip:lovUgEmitente:cmdLov::icon"]'
    estorno = '//*[@id="tplSip:chkEstorno::content"]'
    domicilio_bancario = '//*[@id="tplSip:lovDomicilioBancario:itxLovDec::content"]'
    domicilio_bancario_pesquisar = '//*[@id="tplSip:lovDomicilioBancario:cmdLov::icon"]' 
    ug_2 =  '//*[@id="tplSip:lovUgFavorecida:itxLovDec::content"]'
    ug_2_pesquisar = '//*[@id="tplSip:lovUgFavorecida:cmdLov::icon"]'
    domicilio_bancario_2 = '//*[@id="tplSip:lovDomicilioBancarioUgFavorecida:itxLovDec::content"]'
    domicilio_bancario_2_pesquisar = '//*[@id="tplSip:lovDomicilioBancarioUgFavorecida:cmdLov::icon"]'
    ug_orcamentaria = '//*[@id="tplSip:lovUgOrcamentaria:itxLovDec::content"]'
    ug_orcamentaria_pesquisar = '//*[@id="tplSip:lovUgOrcamentaria:cmdLov::icon"]'
    ief = '//*[@id="tplSip:pnlClassificacao_chc_23::content"]'
    fonte = '//*[@id="tplSip:pnlClassificacao_chc_28::content"]'
    fonte_rj = '//*[@id="tplSip:pnlClassificacao_chc_24::content"]'
    tipo_detalhamento_fonte = '//*[@id="tplSip:pnlClassificacao_chc_186::content"]'
    detalhamento_fonte = '//*[@id="tplSip:pnlClassificacao_chc_159::content"]'
    convenio = '//*[@id="tplSip:pnlClassificacao_chc_38::content"]'
    
    # Item Orçamentário
    btn_item_orcamentario = '//*[@id="tplSip:slcItOrcamentario::disAcr"]'
    btn_inserir_item_orcamentario = '//*[@id="tplSip:btnInserirItemOrcamentario"]'
    tipo_patrimonial_orc = '//*[@id="tplSip:pnlClassificacaoItemOrcamentario_chc_116::content"]'
    item_patrimonial_orc = '//*[@id="tplSip:pnlClassificacaoItemOrcamentario_chc_109::content"]'
    operacao_patrimonial_orc = '//*[@id="tplSip:pnlClassificacaoItemOrcamentario_chc_115::content"]'
    natureza_receita_orc = '//*[@id="tplSip:pnlClassificacaoItemOrcamentario_chc_53::content"]'
    valor_orc = '//*[@id="tplSip:itxValorItemOrcamentario::content"]'
    btn_confirmar_item_orc = '//*[@id="tplSip:ditorc::ok"]'
    btn_cancelar_item_orc = '//*[@id="tplSip:ditorc::cancel"]'
    
    # Item Extraorçamentário
    btn_item_extraorcamentario = '//*[@id="tplSip:slcItExtraOrcamentario::disAcr"]'
    btn_inserir_item_extraorcamentario = '//*[@id="tplSip:btnInserirItemExtraOrcamentario"]'
    tipo_patrimonial_extra = '//*[@id="tplSip:pnlClassificacaoItemExtraOrcamentario_chc_116::content"]'
    item_patrimonial_extra = '//*[@id="tplSip:pnlClassificacaoItemExtraOrcamentario_chc_109::content"]'
    operacao_patrimonial_extra = '//*[@id="tplSip:pnlClassificacaoItemExtraOrcamentario_chc_115::content"]'
    ano_extra = '//*[@id="tplSip:pnlClassificacaoItemExtraOrcamentario_chc_81::content"]'
    tipo_credor_pf_extra = '//*[@id="tplSip:radTipoCredorExtra:_0"]'
    tipo_credor_pj_extra = '//*[@id="tplSip:radTipoCredorExtra:_1"]'
    tipo_credor_cg_extra = '//*[@id="tplSip:radTipoCredorExtra:_2"]'
    tipo_credor_ug_extra = '//*[@id="tplSip:radTipoCredorExtra:_3"]'
    credor_extra = '//*[@id="tplSip:lovCredorExtra:itxLovDec::content"]'
    credor_pesquisar_extra = '//*[@id="tplSip:lovCredorExtra:cmdLov::icon"]'
    credor_nome_extra = '//*[@id="tplSip:lovCredorExtraNome:itxLovDec::content"]'
    valor_extra = '//*[@id="tplSip:itxValorItemExtraOrcamentario::content"]'
    btn_confirmar_item = '//*[@id="tplSip:ditext::ok"]'
    btn_cancelar_item = '//*[@id="tplSip:ditext::cancel"]'
    
    # Observação
    btn_inserir_observacao = '//*[@id="tplSip:slcObservacao::disAcr"]'
    observacao = '//*[@id="tplSip:itxObservacao::content"]'
    
    # Contabilização
    btn_contabilizar = '//*[@id="tplSip:btnContabilizar"]'
    btn_confirmar_contabilizacao = '//*[@id="tplSip:popContabilizarconfirmButton"]'
    
    # Campos de Retorno
    numero_documento = '//*[@id="tplSip:itxNumero::content"]'
    erro = '//*[@id="docPrincipal::msgDlg::_ttxt"]'
    erro_pesquisar_ug = '//*[@id="tplSip:lovUgEmitente:pnlTab::_ttxt"]'
    btn_erro_pesquisar_ug = '//*[@id="tplSip:lovUgEmitente:frm_popup:btnCancelarLovDec"]'
    erro_pesquisar_domicilio = '//*[@id="tplSip:lovDomicilioBancario:pnlTab::_ttxt"]'
    btn_erro_pesquisar_domicilio = '//*[@id="tplSip:lovDomicilioBancario:frm_popup:btnCancelarLovDec"]'
    erro_pesquisar_ugo = '//*[@id="tplSip:lovUgOrcamentaria:pnlTab::_ttxt"]'
    btn_erro_pesquisar_ugo = '//*[@id="tplSip:lovUgOrcamentaria:frm_popup:btnCancelarLovDec"]'

class xpaths_na: 
    # Menu
    btn_na = "//*[text()='Nota de Aplicação e Resgate']"
    btn_inserir_na = '//*[@id="pt1:tblNotaAplicacaoResgate:btnInsert"]'
    
    # Detalhamento
    data_emissao = '//*[@id="tplSip:itxDataInclusao::content"]'
    ug_emitente = '//*[@id="tplSip:lovUgEmitente::content"]'
    ug_emitente_pesquisar = '//*[@id="tplSip:lovUgEmitente::lovIconId"]'
    ug_emitente_confirmar = '//*[@id="tplSip:lovUgEmitente_afrLovDialogId::ok"]'
    estorno = '//*[@id="tplSip:chkEstorno::content"]'
    tipo_patrimonial = '//*[@id="tplSip:pnlClassificacao_chc_116::content"]'
    item_patrimonial = '//*[@id="tplSip:pnlClassificacao_chc_109::content"]'
    operacao_patrimonial = '//*[@id="tplSip:pnlClassificacao_chc_115::content"]'
    ief = '//*[@id="tplSip:pnlClassificacao_chc_23::content"]'
    fonte = '//*[@id="tplSip:pnlClassificacao_chc_28::content"]'
    fonte_rj = '//*[@id="tplSip:pnlClassificacao_chc_24::content"]'
    tipo_detalhamento_fonte = '//*[@id="tplSip:pnlClassificacao_chc_186::content"]'
    detalhamento_fonte = '//*[@id="tplSip:pnlClassificacao_chc_159::content"]'
    domicilio_bancario_origem = '//*[@id="tplSip:cbxDomicilioBancarioOrigem::content"]'
    domicilio_bancario_destino = '//*[@id="tplSip:cbxDomicilioBancarioDestino::content"]'
    valor = '//*[@id="tplSip:itxValorDocumento::content"]'
    
    # Botões de Item
    btn_itens = '//*[@id="tplSip:sdi1::disAcr"]' 
    btn_inserir_item = '//*[@id="tplSip:pidd1:tabItens:btnInsert"]'
    btn_confirmar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::yes"]'
    btn_cancelar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::no"]'

    # Observação
    observacao = '//*[@id="tplSip:itxObservacao::content"]'
    btn_inserir_observacao = '//*[@id="tplSip:slcObservacao::disAcr"]'
    
    # Contabilização
    btn_contabilizar = '//*[@id="tplSip:btnContabilizar"]'
    btn_confirmar_contabilizacao = '//*[@id="tplSip:popContabilizarconfirmButton"]'
    
    # Campos de Retorno
    numero_documento = '//*[@id="tplSip:itxNumero::content"]'
    erro_titulo = '//*[@id="docDocumento::msgDlg::_ttxt"]'
    erro_corpo = '//*[@id="docDocumento::msgDlg::_ccntr"]'
    
class xpaths_pde: 
    # Menu
    btn_pde = "//*[text()='PD Extra-orçamentária']"
    btn_inserir_pde = '//*[@id="pt1:tblPDExtra:btnInsert"]'

    # Detalhamento
    data_emissao = '//*[@id="tplSip:itxDataInclusao::content"]'
    data_programacao = '//*[@id="tplSip:itxDataProgramacao::content"]'
    data_vencimento = '//*[@id="tplSip:itxDataVencimento::content"]'
    ug_emitente = '//*[@id="tplSip:lovUgEmitente:itxLovDec::content"]'
    ug_emitente_pesquisar = '//*[@id="tplSip:lovUgEmitente:cmdLov::icon"]'
    ob_regulaziracao = '//*[@id="tplSip:chkPdRegularizacao::content"]'
    regularizacao = '//*[@id="tplSip:cbxTipoRegularizacao::content"]'
    ug_2 = '//*[@id="tplSip:lovUgDespesa:itxLovDec::content"]'
    ug_2_pesquisar = '//*[@id="tplSip:lovUgDespesa:cmdLov::icon"]'
    ug_pagadora = '//*[@id="tplSip:lovUgPagadora:itxLovDec::content"]'
    ug_pagadora_pesquisar = '//*[@id="tplSip:lovUgPagadora:cmdLov::icon"]'
    domicilio_bancario_origem = '//*[@id="tplSip:lovDomicilioBancarioOrigem:itxLovDec::content"]'
    domicilio_bancario_origem_pesquisar = '//*[@id="tplSip:lovDomicilioBancarioOrigem:cmdLov::icon"]'
    ief = '//*[@id="tplSip:pnlClassificacao_chc_23::content"]'
    fonte = '//*[@id="tplSip:pnlClassificacao_chc_28::content"]'
    fonte_rj = '//*[@id="tplSip:pnlClassificacao_chc_24::content"]'
    tipo_detalhamento_fonte = '//*[@id="tplSip:pnlClassificacao_chc_186::content"]'
    detalhamento_fonte = '//*[@id="tplSip:pnlClassificacao_chc_159::content"]'
    competencia = '//*[@id="tplSip:itxCompetencia::content"]'
    tipo_credor_pf = '//*[@id="tplSip:radTipoCredor:_0"]'
    tipo_credor_pj = '//*[@id="tplSip:radTipoCredor:_1"]'
    tipo_credor_cg = '//*[@id="tplSip:radTipoCredor:_2"]'
    tipo_credor_ug = '//*[@id="tplSip:radTipoCredor:_3"]'
    credor_pf = '//*[@id="tplSip:lovPF:itxLovDec::content"]'
    credor_pj = '//*[@id="tplSip:lovPJ:itxLovDec::content"]'
    credor_cg = '//*[@id="tplSip:lovIG:itxLovDec::content"]'
    credor_ug = '//*[@id="tplSip:lovUG:itxLovDec::content"]'
    credor_pf_pesquisar = '//*[@id="tplSip:lovPF:cmdLov::icon"]'
    credor_pj_pesquisar = '//*[@id="tplSip:lovPJ:cmdLov::icon"]'
    credor_cg_pesquisar = '//*[@id="tplSip:lovIG:cmdLov::icon"]'
    credor_ug_pesquisar = '//*[@id="tplSip:lovUG:cmdLov::icon"]'
    domicilio_bancario_destino = '//*[@id="tplSip:cbxDomicilioBancarioDestino::content"]'
    
    # Itens
    btn_itens = '//*[@id="tplSip:sdi1::disAcr"]' 
    btn_inserir_item = '//*[@id="tplSip:pidd1:tabItens:btnInsert"]'
    tipo_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_116::content"]'
    item_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_109::content"]'
    operacao_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_115::content"]'
    vinculacao_pagamento = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_207::content"]'
    ano = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_81::content"]'
    valor = '//*[@id="tplSip:pidd1:tabItens:itxValorItem::content"]'
    btn_confirmar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::yes"]'
    btn_cancelar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::no"]'

    # Observação
    observacao = '//*[@id="tplSip:itxObservacao::content"]'
    btn_inserir_observacao = '//*[@id="tplSip:slcObservacao::disAcr"]'
    
    # Contabilização
    btn_contabilizar = '//*[@id="tplSip:btnContabilizar"]'
    btn_confirmar_contabilizacao = '//*[@id="tplSip:popContabilizarconfirmButton"]'
    
    # Campo de Retorno
    numero_documento = '//*[@id="tplSip:itxNumero::content"]'
    erro = '//*[@id="docPrincipal::msgDlg::_ttxt"]'
    
class xpaths_pdt: 
    # Menu
    btn_pdt = "//*[text()='PD de Transferência']"
    btn_inserir_pdt = '//*[@id="pt1:tblPDTransferencia:btnInsert"]'

    # Detalhamento
    data_emissao = '//*[@id="tplSip:itxDataInclusao::content"]'
    data_programacao = '//*[@id="tplSip:itxDataProgramacao::content"]'
    data_vencimento = '//*[@id="tplSip:itxDataVencimento::content"]'
    ug_emitente = '//*[@id="tplSip:lovUgEmitente:itxLovDec::content"]'
    ug_emitente_pesquisar = '//*[@id="tplSip:lovUgEmitente:cmdLov::icon"]'
    ug_favorecida = '//*[@id="tplSip:lovUgFavorecida:itxLovDec::content"]'
    ug_favorecida_pesquisar = '//*[@id="tplSip:lovUgFavorecida:cmdLov::icon"]'
    ug_pagadora = '//*[@id="tplSip:lovUgPagadora:itxLovDec::content"]'
    ug_pagadora_pesquisar = '//*[@id="tplSip:lovUgPagadora:cmdLov::icon"]'
    ob_regulaziracao = '//*[@id="tplSip:chkPdRegularizacao::content"]'
    regularizacao = '//*[@id="tplSip:cbxTipoRegularizacao::content"]'
    justificativa_regularizacao = '//*[@id="tplSip:itxJustificativaRegularizacao::content"]'
    competencia = '//*[@id="tplSip:itxCompetencia::content"]'
    indice = '//*[@id="tplSip:itxIndiceConversao::content"]'
    
    # Classificação Origem
    domicilio_bancario_emitente = '//*[@id="tplSip:lovDomicilioBancarioOrigem:itxLovDec::content"]'
    domicilio_bancario_emitente_pesquisar = '//*[@id="tplSip:lovDomicilioBancarioOrigem:cmdLov::icon"]'
    ief_origem = '//*[@id="tplSip:pnlClassificacaoOrigem_chc_23::content"]'
    fonte_origem = '//*[@id="tplSip:pnlClassificacaoOrigem_chc_28::content"]'
    fonte_rj_origem = '//*[@id="tplSip:pnlClassificacaoOrigem_chc_24::content"]'
    tipo_detalhamento_fonte_origem = '//*[@id="tplSip:pnlClassificacaoOrigem_chc_186::content"]'
    detalhamento_fonte_origem = '//*[@id="tplSip:pnlClassificacaoOrigem_chc_159::content"]'
    convenio_origem = '//*[@id="tplSip:pnlClassificacaoOrigem_chc_38::content"]'

    # Classificação Destino
    domicilio_bancario_favorecida = '//*[@id="tplSip:lovDomicilioBancarioDestino:itxLovDec::content"]'
    domicilio_bancario_favorecida_pesquisar = '//*[@id="tplSip:lovDomicilioBancarioDestino:cmdLov::icon"]'
    ief_favorecida = '//*[@id="tplSip:pnlClassificacaoDestino_chc_23::content"]'  
    fonte_favorecida = '//*[@id="tplSip:pnlClassificacaoDestino_chc_28::content"]'
    fonte_rj_favorecida = '//*[@id="tplSip:pnlClassificacaoDestino_chc_24::content"]'
    tipo_detalhamento_fonte_favorecida = '//*[@id="tplSip:pnlClassificacaoDestino_chc_186::content"]'
    detalhamento_fonte_favorecida = '//*[@id="tplSip:pnlClassificacaoDestino_chc_159::content"]'
    convenio_favorecida = '//*[@id="tplSip:pnlClassificacaoDestino_chc_38::content"]'
    tab_bco_autent = '//*[@id="tplSip:lovDomicilioBancarioDestino:frm_popup:tabLovDec:tabViewerDec::db"]/table/tbody/tr[2]/td[1]'
    tab_ok = '//*[@id="tplSip:lovDomicilioBancarioDestino:frm_popup:btnOkLovDec"]'
    
    # Itens
    btn_itens = '//*[@id="tplSip:sdi1::disAcr"]'
    btn_inserir_item = '//*[@id="tplSip:pidd1:tabItens:btnInsert"]'
    tipo_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_116::content"]'
    item_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_109::content"]'
    operacao_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_115::content"]'
    valor = '//*[@id="tplSip:pidd1:tabItens:itxValorItem::content"]'
    btn_confirmar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::yes"]'
    btn_cancelar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::no"]'

    # Observação
    observacao = '//*[@id="tplSip:itxObservacao::content"]'
    btn_inserir_observacao = '//*[@id="tplSip:slcObservacao::disAcr"]'
    
    # Contabilização
    btn_contabilizar = '//*[@id="tplSip:btnContabilizar"]'
    btn_confirmar_contabilizacao = '//*[@id="tplSip:popContabilizarconfirmButton"]'
    
    # Campo de Retorno
    numero_documento = '//*[@id="tplSip:itxNumero::content"]'
    erro = '//*[@id="docDocumento::msgDlg::_ttxt"]'
    erro_pesquisar_uge = '//*[@id="tplSip:lovUgEmitente:pnlTab::_ttxt"]'
    btn_erro_pesquisar_uge = '//*[@id="tplSip:lovUgEmitente:frm_popup:btnCancelarLovDec"]'
    erro_pesquisar_ugf = '//*[@id="tplSip:lovUgFavorecida:pnlTab::_ttxt"]'
    btn_erro_pesquisar_ugf = '//*[@id="tplSip:lovUgFavorecida:frm_popup:btnCancelarLovDec"]'
    erro_pesquisar_ugp = '//*[@id="tplSip:lovUgPagadora:pnlTab::_ttxt"]'
    btn_erro_pesquisar_ugp = '//*[@id="tplSip:lovUgPagadora:frm_popup:btnCancelarLovDec"]'
    erro_pesquisar_domicilio_origem = '//*[@id="tplSip:lovDomicilioBancarioOrigem:pnlTab::_ttxt"]'
    btn_erro_pesquisar_domicilio_origem = '//*[@id="tplSip:lovDomicilioBancarioOrigem:frm_popup:btnCancelarLovDec"]'
    erro_pesquisar_domicilio_destino = '//*[@id="tplSip:lovDomicilioBancarioDestino:pnlTab::_ttxt"]'
    btn_erro_pesquisar_domicilio_destino = '//*[@id="tplSip:lovDomicilioBancarioDestino:frm_popup:btnCancelarLovDec"]'
    
       
class xpaths_np:
    # Menu
    btn_np = "//*[text()='Nota Patrimonial']"
    btn_inserir_np = '//*[@id="pt1:tblDocumento:btnInsert"]'

    # Detalhamento
    data_emissao = '//*[@id="tplSip:itxDataEmissao::content"]'
    ug_emitente = '//*[@id="tplSip:lovUgEmitente:itxLovDec::content"]'
    ug_emitente_pesquisar = '//*[@id="tplSip:lovUgEmitente:cmdLov::icon"]'
    ug_2 = '//*[@id="tplSip:lovUgFavorecida:itxLovDec::content"]'
    ug_2_pesquisar = '//*[@id="tplSip:lovUgFavorecida:cmdLov::icon"]'
    estorno = '//*[@id="tplSip:ckEstorno::content"]'
    
    # Itens
    btn_inserir_item = '//*[@id="tplSip:pidd1:tabItens:btnInsert"]'
    tipo_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_116::content"]'
    item_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_109::content"]'
    operacao_patrimonial = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_115::content"]'
    ief = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_23::content"]'
    fonte = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_28::content"]'
    fonte_rj = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_24::content"]'
    tipo_detalhamento_fonte = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_186::content"]'
    detalhamento_fonte = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_159::content"]' 
    ano = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_81::content"]'
    domicilio_bancario = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_101::content"]'
    tipo_inscricao_generica = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_166::content"]'
    inscricao_generica = '//*[@id="tplSip:pidd1:tabItens:pnlClassificacaoItem_chc_164::content"]'
    valor = '//*[@id="tplSip:pidd1:tabItens:itxValorItem::content"]'
    btn_confirmar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::yes"]'
    btn_cancelar_item = '//*[@id="tplSip:pidd1:tabItens:pnlItemWindow::no"]'

    # Observação
    observacao = '//*[@id="tplSip:painelObservacao:itxObservacao::content"]'
    btn_inserir_observacao = '//*[@id="tplSip:slcObservacao::disAcr"]'
    
    # Contabilização
    btn_contabilizar = '//*[@id="tplSip:btnContabilizar"]'
    btn_confirmar_contabilizacao = '//*[@id="tplSip:popContabilizarconfirmButton"]'
    
    # Campo de Retorno
    numero_documento = '//*[@id="tplSip:itxNumero::content"]'
    erro_titulo = '//*[@id="docDocumento::msgDlg::_ttxt"]'
    erro_corpo = '//*[@id="docDocumento::msgDlg::_ccntr"]'