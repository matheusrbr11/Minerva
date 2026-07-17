from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import os

from automaweb import Navegador, aguardar_arquivo, excluir_arquivo

def baixar_daf(nav: Navegador, data_inicial: str, data_final: str):
    '''
    baixa o demonstrativo de arrecadação federal baseado nas datas inicial e final
    '''
    nav.abrir_url('https://demonstrativos.apps.bb.com.br/arrecadacao-federal')

    WebDriverWait(nav.driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.ng-pristine[formcontrolname='nomeBeneficiarioEntrada']")
        )
    ).send_keys('RIO DE JANEIRO')

    nav.clicar('//*[@id="angular-component-container"]/apw-ng-app/app-template/bb-layout/div[1]/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf/form/div/div/div/bb-card/bb-card-footer/bb-button-group/div[2]')

    inputs = WebDriverWait(nav.driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[placeholder='DD/MM/AAAA']"))
    )

    # certifique-se de que temos pelo menos dois elementos
    if len(inputs) >= 2:
        data_inicial_input = inputs[0]
        data_inicial_input.click()
        data_inicial_input.clear()
        data_inicial_input.send_keys(data_inicial)

        data_final_input = inputs[1]
        data_final_input.click()
        data_final_input.clear()
        data_final_input.send_keys(data_final)
        data_final_input.send_keys(Keys.ESCAPE)

    # clicar fora (necessário somente com headless = False)
    #nav.clicar('//*[@id="angular-component-container"]/apw-ng-app/app-template/bb-layout/div[1]/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf-selecao/div/div[2]/div/div/form/bb-card/bb-card-footer/bb-button-group')

    botao_continuar = WebDriverWait(nav.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="angular-component-container"]/apw-ng-app/app-template/bb-layout/div[1]/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf-selecao/div/div[2]/div/div/form/bb-card/bb-card-footer/bb-button-group/div/button[2]')))
    nav.driver.execute_script("arguments[0].click();", botao_continuar)

    # clicar no botão download
    nav.clicar('//*[@id="angular-component-container"]/apw-ng-app/app-template/bb-layout/div[1]/div/div/div/div/bb-layout-column/ng-component/div/div/div/app-demonstrativo-daf-final/div/div[2]/div/div/bb-card/bb-card-header/bb-card-header-action/bb-icon-button/bb-icon')

    # setar a extensão do arquivo
    nav.clicar('//*[contains(text(), "CSV")]')

# -----------------------------------------------
# parâmetros
# -----------------------------------------------

caminho_arquivo_csv = fr'C:\Users\{os.getlogin()}\Downloads\demonstrativoDAF.csv'

ano = datetime.now().year
dia = datetime.now().day
mes = datetime.now().month

# -----------------------------------------------
# execução
# -----------------------------------------------

# remove o DAF antigo antes de baixar um novo
excluir_arquivo(caminho_arquivo_csv)

nav = Navegador(navegador="edge")
nav.abrir_driver(headless=True)

try:
    baixar_daf(nav, f'01/{mes:02d}/{ano}', f'{dia:02d}/{mes:02d}/{ano}')
    aguardar_arquivo(caminho_arquivo_csv)
finally:
    nav.fechar_driver()

PROJECT_BASE_PATH = Path(__file__).parent
subprocess.run([sys.executable, PROJECT_BASE_PATH / 'extrato.py'])