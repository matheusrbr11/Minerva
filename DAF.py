import os
import time
import shutil
import json
import subprocess
import sys
from office365.sharepoint.client_context import ClientContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#funções
# -----------------------------------------------
def clicar(xpath):
    '''
    clica em um elemento identificado pelo xpath
    '''
    elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elemento.click()

def digitar(xpath, texto):
    '''
    digita um texto em um elemento identificado pelo xpath
    '''
    elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elemento.clear()
    elemento.send_keys(texto)
    
def aguardar_arquivo(caminho_arquivo, timeout=20):
    '''
    aguarda até que um arquivo exista no caminho especificado ou até que o tempo limite seja atingido
    '''
    inicio = time.time()
    while not os.path.exists(caminho_arquivo):
        if time.time() - inicio > timeout:
            raise TimeoutError(f"O arquivo {caminho_arquivo} não foi encontrado dentro do tempo limite de {timeout} segundos.")
        time.sleep(1)

def baixar_daf(data_inicial, data_final):
    '''
    baixa o demonstrativo de arrecadação federal baseado nas datas inicial e final
    '''
    #abrir navegador
    driver.get('https://demonstrativos.apps.bb.com.br/arrecadacao-federal')

    #preencher nome do Estado
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.ng-pristine[formcontrolname='nomeBeneficiarioEntrada']"))).send_keys('RIO DE JANEIRO')
    clicar('//*[@id="angular-component-container"]/apw-ng-app/app-template/bb-layout/div/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf/form/div/div/div/bb-card/bb-card-footer/div[2]/button')

    inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[placeholder='DD / MM / AAAA']")))

    # Certifique-se de que temos pelo menos dois elementos
    if len(inputs) >= 2:
        # Clicar no primeiro campo de data
        data_inicial_input = inputs[0]
        data_inicial_input.click()
        data_inicial_input.clear()  # Limpa o campo
        data_inicial_input.send_keys(data_inicial)  # Preenche com a data inicial

        # Clicar no segundo campo de data
        data_final_input = inputs[1]
        data_final_input.click()
        data_final_input.clear()  # Limpa o campo
        data_final_input.send_keys(data_final)  # Preenche com a data final

    # Clicar no botão continuar (usando XPath baseado no texto)
    clicar('//*[@id="__next"]/div[3]/div/div/div/div/apw-ng-app/app-template/bb-layout/div[1]/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf-selecao/div/div[2]/div/div/form/bb-card/bb-card-footer/div/button[2]')

    # Clicar no botão download
    clicar('//*[@id="__next"]/div[3]/div/div/div/div/apw-ng-app/app-template/bb-layout/div[1]/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf-final/div/div[2]/div/div/bb-card/bb-card-header/bb-card-header-action/button/bb-icon')
    # Setar a extensão do arquivo
    clicar('//*[contains(text(), "CSV")]')
        
# -----------------------------------------------
#parâmetros
# -----------------------------------------------

#define o caminho do arquivo baixado
caminho_arquivo_csv = fr'C:\Users\{os.getlogin()}\Downloads\demonstrativoDAF.csv'

#configurações iniciais do Edge
service = Service()
edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--headless")
edge_options.add_argument("--log-level=3")
driver = webdriver.Edge(service=service, options=edge_options)
driver.maximize_window()

#define as datas a serem usadas
ano = datetime.now().year
dia = datetime.now().day
mes = datetime.now().month

# -----------------------------------------------
#execução
# -----------------------------------------------

try:
    if os.path.exists(caminho_arquivo_csv):
        os.remove(caminho_arquivo_csv)
except Exception as e:
    print(f"AVISO: Não foi possível excluir os arquivos DAF antigos. Erro: {e}")

#baixa e ronomeia o DAF do mês atual
baixar_daf(f'01/{mes:02d}/{ano}', f'{dia:02d}/{mes:02d}/{ano}')
aguardar_arquivo(caminho_arquivo_csv)

#finaliza o navegador
driver.quit()

subprocess.run(['python', 'extrato.py'])