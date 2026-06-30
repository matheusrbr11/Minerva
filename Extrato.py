import pathlib
import sys
import os
import sqlite3
import pandas as pd
import numpy as np
import tkinter
from tkinter import messagebox
from pathlib import Path
from decimal import Decimal, ROUND_DOWN

project_root_directory = Path(__file__).parent
sys.path.insert(0, str(project_root_directory))

DB_PATH = project_root_directory / "base de dados/DAF.db"
CSV_FILENAME = "demonstrativoDAF.csv"

OBS_MAP_CSV = {
    # --- Receitas (tipo_id 1-10) ---
    1: 'REGISTRO DA RECEITA PROVENIENTE DOS ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - ATÉ 5% - LEI 7990/89, REFERENTE A ',
    2: 'REGISTRO DA RECEITA PROVENIENTE DOS ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - EXCEDENTE A 5% - LEI 9478/97, REFERENTE A ',
    3: 'REGISTRO DA RECEITA PROVENIENTE DA PARTICIPAÇÃO ESPECIAL DO PETRÓLEO - PEA, REFERENTE A ',
    4: 'REGISTRO DA RECEITA PROVENIENTE DA COTA PARTE DO FUNDO ESPECIAL DO PETRÓLEO - FEP, REFERENTE A ',
    5: 'REGISTRO DA RECEITA PROVENIENTE DO FUNDO DE PARTICIPAÇÃO DOS ESTADOS - FPE, REFERENTE A ',
    6: 'REGISTRO DA RECEITA PROVENIENTE DO IMPOSTO SOBRE PRODUTOS INDUSTRIALIZADOS - IPI EXPORTAÇÃO, REFERENTE A ',
    7: 'REGISTRO DA RECEITA PROVENIENTE DA COMPENSAÇÃO FINANCEIRA PELA EXPLORAÇÃO MINERAL - CFM, REFERENTE A ',
    8: 'REGISTRO DA RECEITA PROVENIENTE DA COMPENSAÇÃO FINANCEIRA PELA UTILIZAÇÃO DE RECURSOS HÍDRICOS - CFH, REFERENTE A ',
    9: 'REGISTRO DA RECEITA PROVENIENTE DA CONTRIBUIÇÃO DE INTERVENÇÃO NO DOMÍNIO ECONÔMICO - CIDE, REFERENTE A ',
    10: 'REGISTRO DA RECEITA PROVENIENTE DA LC 176/2020 (ADO25), REFERENTE A ',
    
    # --- PASEP (tipo_id 11-20) ---
    11: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - ATÉ 5% - LEI 7990/89, A ENCARGOS GERAIS, REFERENTE A ',
    12: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - ROYALTIES PELA PRODUÇÃO DO PETRÓLEO - EXCEDENTE A 5% - LEI 9478/97, A ENCARGOS GERAIS, REFERENTE A ',
    13: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - PARTICIPAÇÃO ESPECIAL DO PETRÓLEO - PEA, A ENCARGOS GERAIS, REFERENTE A ',
    14: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - FUNDO ESPECIAL DO PETRÓLEO - FEP, A ENCARGOS GERAIS, REFERENTE A ',
    15: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - FUNDO DE PARTICIPAÇÃO DOS ESTADOS - FPE, A ENCARGOS GERAIS, REFERENTE A ',
    16: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - IMPOSTO SOBRE PRODUTOS INDUSTRIALIZADOS - IPI EXPORTAÇÃO, A ENCARGOS GERAIS, REFERENTE A ',
    17: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - COMPENSAÇÃO FINANCEIRA PELA EXPLORAÇÃO MINERAL - CFM, A ENCARGOS GERAIS, REFERENTE A ',
    18: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - COMPENSAÇÃO FINANCEIRA PELA UTILIZAÇÃO DE RECURSOS HÍDRICOS - CFH, A ENCARGOS GERAIS, REFERENTE A ',
    19: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - CONTRIBUIÇÃO DE INTERVENÇÃO NO DOMÍNIO ECONÔMICO - CIDE, A ENCARGOS GERAIS, REFERENTE A ',
    20: 'REGISTRO DA TRANSFERÊNCIA DA RETENÇÃO DO PASEP - LC 176/2020 (ADO25), A ENCARGOS GERAIS, REFERENTE A ',
}

ALL_TIPO_IDS = tuple(OBS_MAP_CSV.keys())

MESES_MAP = {
    1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
    5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
    9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
}

def limpar_valor_monetario(valor_str: str) -> Decimal:
    """
    Converte uma string monetária (ex: 1.234_56C ou 912.922_01D) para Decimal.
    SEMPRE RETORNA UM VALOR POSITIVO.
    """
    if not isinstance(valor_str, str):
        return Decimal('0.0')

    valor_limpo = valor_str.strip().replace('D', '').replace('C', '')
    valor_limpo = valor_limpo.replace('.', '').replace('_', '.').replace(',', '.')

    if not valor_limpo:
        return Decimal('0.0')
    
    try:
        return Decimal(valor_limpo)
    
    except Exception:
        return Decimal('0.0')

def truncar(valor: Decimal) -> Decimal:
    """
    Trunca um Decimal para 2 casas decimais (ex: 1.0099 -> 1.00)
    """
    return (valor * Decimal('100')).to_integral_value(rounding=ROUND_DOWN) / Decimal('100')

def processar_arquivos_csv(pasta_raiz: str):
    """
    Processa o 'demonstrativoDAF.csv'.
    Retorna dois DataFrames:
    1. vfinal_daf1: Dados para a tabela 'contabilizacoes'.
    2. lista_daf: Dados para a tabela 'daf'.
    """
    
    def _processar_dia(data_dia: str, df_dia: pd.DataFrame) -> list:
        anp_7990, anp_9478, anp_7990E, anp_9478E, pea, fep = [], [], [], [], [], []
        fpe, ipi, cfm, cid, ado, cfh = [], [], [], [], [], []
        pasep_fpe, pasep_ipi, pasep_cfm, pasep_cid, pasep_ado, pasep_cfh = [], [], [], [], [], []
        
        grupo = None
        retencao_pasep = None
        pasep_estado = None
        
        lancamentos = []

        for row in df_dia.to_dict('records'):
            parcela = row['parcela']
            valor_decimal = row['valor_decimal']
            
            if parcela == 'RETENCAO PASEP' and grupo is None:
                retencao_pasep = (valor_decimal, row['fundo'])
                continue
            if parcela == 'PASEP ESTADO' and grupo is None:
                pasep_estado = (valor_decimal, row['fundo'])
                continue

            if parcela == 'ANP-LEI 7990/89': anp_7990.append(valor_decimal)
            elif parcela == 'ANP-LEI 9478/97': anp_9478.append(valor_decimal)
            elif parcela == 'ANP-LEI 7990/89-12858/13': anp_7990E.append(valor_decimal)
            elif parcela == 'ANP-LEI 9478/97-12858/13': anp_9478E.append(valor_decimal)
            elif parcela == 'PART.ESP.ANP': pea.append(valor_decimal)
            elif parcela == 'COTA-PARTE': fep.append(valor_decimal)

            elif parcela == 'PARCELA DE IPI' or parcela == 'PARCELA DE IR':
                fpe.append(valor_decimal)
                grupo = 'FPE'
            elif parcela == 'IPI - ESTADO' or parcela == 'IPI-MUNICIPIOS':
                ipi.append(valor_decimal)
                grupo = 'IPI'

            elif parcela == 'CFM-PRD.MINERAL':
                cfm.append(valor_decimal)
                if retencao_pasep is not None:
                    pasep_cfm.append(retencao_pasep[0])
                    retencao_pasep = None
                    
            elif parcela == 'CFH-REC.HIDRICO':
                cfh.append(valor_decimal)
                if retencao_pasep is not None:
                    pasep_cfh.append(retencao_pasep[0])
                    retencao_pasep = None
                    
            elif parcela == 'CIDE-ESTADO' or parcela == 'CIDE-MUNICIPIO':
                cid.append(valor_decimal)
                if pasep_estado is not None:
                    pasep_cid.append(pasep_estado[0])
                    pasep_estado = None
                    
            elif parcela == 'LC 176/2020':
                ado.append(valor_decimal)
                if retencao_pasep is not None:
                    pasep_ado.append(retencao_pasep[0])
                    retencao_pasep = None

            elif parcela == 'RETENCAO PASEP':
                if grupo == 'FPE':
                    pasep_fpe.append(valor_decimal)
                grupo = None
                
            elif parcela == 'PASEP ESTADO':
                if grupo == 'IPI':
                    pasep_ipi.append(valor_decimal)
                grupo = None
            else:
                grupo = None

        def _add_royalty(valor_lista: list, tipo_id: int, pasep_percent: Decimal, pasep_tipo_id: int):
            valor_sum = sum(valor_lista)
            if valor_sum > 0:
                lancamentos.append({'data': data_dia, 'valor': valor_sum, 'tipo_id': tipo_id})
                pasep_valor = truncar(valor_sum * pasep_percent)
                if pasep_valor > 0:
                    lancamentos.append({'data': data_dia, 'valor': pasep_valor, 'tipo_id': pasep_tipo_id})

        def _add_outro(valor_principal: list, tipo_id: int, valor_pasep: list, pasep_tipo_id: int):
            valor_sum = sum(valor_principal)
            if valor_sum > 0:
                lancamentos.append({'data': data_dia, 'valor': valor_sum, 'tipo_id': tipo_id})
            pasep_sum = sum(valor_pasep)
            if pasep_sum > 0:
                lancamentos.append({'data': data_dia, 'valor': pasep_sum, 'tipo_id': pasep_tipo_id})

        _add_royalty(anp_7990, 1, Decimal('0.0075'), 11)
        _add_royalty(anp_9478, 2, Decimal('0.01'), 12)
        _add_royalty(anp_7990E, 1, Decimal('0.0075'), 11)
        _add_royalty(anp_9478E, 2, Decimal('0.01'), 12)
        _add_royalty(pea, 3, Decimal('0.01'), 13)
        _add_royalty(fep, 4, Decimal('0.01'), 14)
        
        _add_outro(fpe, 5, pasep_fpe, 15)
        _add_outro(ipi, 6, pasep_ipi, 16)
        _add_outro(cfm, 7, pasep_cfm, 17)
        _add_outro(cfh, 8, pasep_cfh, 18)
        _add_outro(cid, 9, pasep_cid, 19)
        _add_outro(ado, 10, pasep_ado, 20)

        return lancamentos

    lancamentos_total = []
    dados_daf_total = []
    
    try:
        arquivos_csv = list(Path(pasta_raiz).rglob(CSV_FILENAME))
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível processar os arquivos.\nErro: {e}")
        return pd.DataFrame(), pd.DataFrame()

    if not arquivos_csv:
        messagebox.showwarning("Aviso", "Nenhum arquivo foi encontrado.")
        return pd.DataFrame(), pd.DataFrame()

    for arquivo in arquivos_csv:
        try:
            df = pd.read_csv(arquivo, sep=',', encoding='windows-1252', header=None, dtype=str, names=[0, 1, 2])
            if df.empty:
                continue
            
            indices_validos = []
            ignorar = False

            for index, row in df.iterrows():
                col0 = str(row[0]) if pd.notna(row[0]) else ""
                
                if ' - ' in col0 and col0.isupper(): 
                    ignorar = False
                
                if 'TOTAL POR PARCELA / NATUREZA' in col0:
                    ignorar = True
                
                if not ignorar:
                    indices_validos.append(index)

            df = df.loc[indices_validos].copy()

            df['fundo'] = np.where(df[0].str.contains(' - ', na=False), df[0].str.strip(), np.nan)
            df['fundo'] = df['fundo'].ffill()
            
            df = df.rename(columns={0:'data', 1:'parcela', 2:'valor_str'})
            df['data'] = df['data'].str.strip().replace('', np.nan)
            df['data'] = df['data'].str.replace('.', '/', regex=False)
            df['parcela'] = df['parcela'].str.strip()
            df['valor_str'] = df['valor_str'].str.strip()

            df = df.dropna(subset=['parcela', 'valor_str'])
            linhas_a_remover = ['PARCELA', 'TOTAL POR PARCELA / NATUREZA', 'TOTAL NA DATA', '']
            df = df[~df['parcela'].isin(linhas_a_remover)]
            df = df[df['valor_str'] != '']
            
            df['data'] = df['data'].ffill() 
            df = df.dropna(subset=['data', 'fundo'])
            
            if df.empty:
                continue
            
            df['valor_decimal'] = df['valor_str'].apply(limpar_valor_monetario)
            df['tipo'] = np.where(df['valor_str'].str.endswith('D'), 'D', 'C')

            dados_daf_arquivo = df[['fundo', 'data', 'parcela', 'valor_decimal', 'tipo']].copy()
            dados_daf_arquivo = dados_daf_arquivo.rename(columns={'valor_decimal': 'valor'})
            
            dados_daf_total.extend(dados_daf_arquivo.to_dict('records'))
            
            lancamentos_arquivo = []
            for data_dia, df_dia in df.groupby('data'):
                lancamentos = _processar_dia(data_dia, df_dia)
                lancamentos_arquivo.extend(lancamentos)
            
            lancamentos_total.extend(lancamentos_arquivo)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar {arquivo}: {e}")

    vfinal_daf1 = pd.DataFrame(lancamentos_total)
    if not vfinal_daf1.empty:
        vfinal_daf1 = vfinal_daf1[vfinal_daf1['valor'] > 0].copy()
        
        if not vfinal_daf1.empty:
            data_dt = pd.to_datetime(vfinal_daf1['data'].astype(str), format='%d/%m/%Y')
            vfinal_daf1['data'] = data_dt.dt.strftime('%d/%m/%Y')
            mes = data_dt.dt.month.map(MESES_MAP)
            ano = data_dt.dt.year.astype(str)
            competencia = mes + ' DE ' + ano
            
            vfinal_daf1['observacao'] = vfinal_daf1['tipo_id'].map(OBS_MAP_CSV) + competencia
            vfinal_daf1['valor'] = vfinal_daf1['valor'].apply(lambda d: f"{d:.2f}")

            vfinal_daf1 = vfinal_daf1.drop_duplicates()
        else:
            vfinal_daf1 = pd.DataFrame()
    
    vfinal_daf = pd.DataFrame(dados_daf_total)
    if not vfinal_daf.empty:
        vfinal_daf = vfinal_daf.drop_duplicates()

    return vfinal_daf1, vfinal_daf

def carregar_no_banco_de_dados(vfinal_total: pd.DataFrame) -> int:
    """
    Limpa o DataFrame final e insere os novos
    lançamentos na tabela 'contabilizacoes'.
    """    
    if vfinal_total is None or vfinal_total.empty:
        return 0
    
    vfinal_total['data'] = vfinal_total['data'].str.strip()
    vfinal_total['observacao'] = vfinal_total['observacao'].str.strip()
    vfinal_total = vfinal_total[vfinal_total['valor'] != '0.00']
    vfinal_total = vfinal_total.dropna(subset=['data', 'valor', 'tipo_id', 'observacao'])
    vfinal_total = vfinal_total.drop_duplicates(subset=['data', 'valor', 'tipo_id', 'observacao'])
    
    if vfinal_total.empty:
        return 0

    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()

        key_columns = ['data', 'valor', 'tipo_id', 'observacao']
        query_tipos = f"SELECT * FROM contabilizacoes WHERE tipo_id IN {ALL_TIPO_IDS}"
        contabilizacoes = pd.read_sql_query(query_tipos, con)
        novos_lancamentos = pd.DataFrame()

        if not contabilizacoes.empty:
            contabilizacoes['valor'] = contabilizacoes['valor'].apply(lambda x: f"{Decimal(str(x)):.2f}")
            contabilizacoes['tipo_id'] = contabilizacoes['tipo_id'].astype(int)
            vfinal_total['tipo_id'] = vfinal_total['tipo_id'].astype(int)
            
            db_keys = contabilizacoes[key_columns].copy()
            db_keys['in_db'] = True
            
            vfinal_merged = pd.merge(vfinal_total, db_keys, on=key_columns, how='left')
            novos_lancamentos = vfinal_merged[vfinal_merged['in_db'].isna()].copy()
            
        else:
            novos_lancamentos = vfinal_total.copy()

        
        if novos_lancamentos.empty:
            con.close()
            return 0
        
        user = os.getlogin()
        data_hora = str(pd.Timestamp.now())
        insercoes_feitas = 0

        for index, row in novos_lancamentos.iterrows():
            cursor.execute('''
                INSERT INTO contabilizacoes (data, valor, observacao, num_documento, tipo_id, usuario_inclusao, data_hora_inclusao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [row['data'], row['valor'], row['observacao'], None, int(row['tipo_id']), user, data_hora])
            con.commit()
            insercoes_feitas += 1
                
        con.close()
        return insercoes_feitas

    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
        return 0
    except Exception as e:
        messagebox.showerror("Erro)", f"Erro inesperado ao carregar dados: {e}")
        return 0

def carregar_tabela_daf(vfinal_daf: pd.DataFrame) -> int:
    """
    Insere dados na tabela 'daf', evitando duplicatas.
    """
    
    if vfinal_daf.empty:
        return 0
        
    vfinal_daf['valor'] = vfinal_daf['valor'].astype(float)
    vfinal_daf = vfinal_daf[vfinal_daf['valor'] > 0].copy()
    vfinal_daf = vfinal_daf.drop_duplicates()
    
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        
        daf_existente = pd.read_sql_query("SELECT * FROM DAF", con)
        novos_lancamentos_daf = pd.DataFrame()
        key_columns = ['fundo', 'data', 'parcela', 'valor', 'tipo']

        if not daf_existente.empty:
            daf_existente['valor'] = daf_existente['valor'].astype(float)
            db_keys = daf_existente[key_columns].copy()
            db_keys['in_db'] = True
            vfinal_merged = pd.merge(vfinal_daf, db_keys, on=key_columns, how='left')
            novos_lancamentos_daf = vfinal_merged[vfinal_merged['in_db'].isna()].copy()
            
            if 'in_db' in novos_lancamentos_daf.columns:
                novos_lancamentos_daf = novos_lancamentos_daf.drop(columns=['in_db'])
            
        else:
            novos_lancamentos_daf = vfinal_daf.copy()
        
        
        if novos_lancamentos_daf.empty:
            con.close()
            return 0
        
        data_tuples = novos_lancamentos_daf.to_records(index=False)
        
        cursor.executemany(
            '''
            INSERT INTO daf (fundo, data, parcela, valor, tipo)
            VALUES (?, ?, ?, ?, ?)
            ''',
            data_tuples
        )
        con.commit()
        
        insercoes_feitas = len(novos_lancamentos_daf)
        con.close()
        return insercoes_feitas

    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
        return 0
    except Exception as e:
        messagebox.showerror("Erro", f"Erro inesperado ao carregar dados: {e}")
        return 0

def main():
    """
    Função principal para o processo ETL de CSV.
    """
    root = tkinter.Tk()
    root.withdraw()

    try:
        pasta_raiz = pathlib.Path.home() / "Downloads"
        
        if not os.path.isdir(pasta_raiz):
            messagebox.showerror("Erro", f"A pasta de Downloads não foi encontrada: {pasta_raiz}")
            return

        df_daf1, df_daf = processar_arquivos_csv(pasta_raiz)

        if df_daf1.empty and df_daf.empty:
            messagebox.showinfo("Info", "Nenhum lançamento do DAF para processar.")
            return
        
        insercoes_contabilizacoes = carregar_no_banco_de_dados(df_daf1)
        insercoes_daf = carregar_tabela_daf(df_daf)
        
        messagebox.showinfo(
            "Sucesso",
            f"Processamento do DAF concluído!\n\n"
            f"Tabela 'contabilizacoes': {insercoes_contabilizacoes} novas linhas.\n"
            f"Tabela 'daf': {insercoes_daf} novas linhas."
        )

    except Exception as e:
        messagebox.showerror("Erro", f"Um erro inesperado encerrou o programa: {e}")
    
    finally:
        if root:
            root.destroy()

if __name__ == "__main__":
    main()