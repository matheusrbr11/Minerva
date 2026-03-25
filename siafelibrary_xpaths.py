### XPATHS ###

class xpaths_login:
    """ Armazena os XPaths utilizados na tela de Login do Siafe. """
    usuario = '//*[@id="loginBox:itxUsuario::content"]'
    senha = '//*[@id="loginBox:itxSenhaAtual::content"]'
    ano = '//*[@id="loginBox:cbxExercicio::content"]'
    btn_confirmar = '//*[@id="loginBox:btnConfirmar"]'
    erro_titulo = '//*[@id="docPrincipal::msgDlg::_ttxt"]'
    erro_corpo = '//*[@id="docPrincipal::msgDlg::_ccntr"]'

class xpaths_menu:
    """ Armazena os XPaths do menu principal de navegação. """
    btn_execucao = '//*[@id="pt1:pt_np4:1:pt_cni6::disclosureAnchor"]'
    btn_execucao_financeira = '//*[@id="pt1:pt_np3:1:pt_cni4::disclosureAnchor"]'
    btn_contabilidade = '//*[@id="pt1:pt_np3:2:pt_cni4::disclosureAnchor"]'
    btn_voltar = '//*[@id="tplSip:pt_bc1:2:pt_cni7"]'

class xpaths_gr: 
    """ Armazena os XPaths da tela de Guia de Recolhimento. """
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
    """ Armazena os XPaths da tela de Nota de Aplicação e Resgate. """
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
    """ Armazena os XPaths da tela de PD Extra-Orçamentária. """
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
    """ Armazena os XPaths da tela de PD de Transferência. """
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

class xpaths_np:
    """ Armazena os XPaths da tela de Nota Patrimonial. """
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

class xpaths_ev:
    """ Armazena os XPaths da tela de Nota de Evento. """
    # Menu
    btn_ev = "//*[text()='Nota de Evento']"
    btn_inserir_ev = '//*[@id="pt1:tblDocumento:btnInsert"]'

    # Detalhamento
    data_emissao = '//*[@id="tplSip:itxDataInclusao::content"]'
    ug_emitente = '//*[@id="tplSip:lovUgEmitente:itxLovDec::content"]'
    ug_emitente_pesquisar = '//*[@id="tplSip:lovUgEmitente:cmdLov::icon"]'

    # Itens
    btn_inserir_item = "//*[text()='Inserir']"
    evento = '//*[@id="tplSip:lovEvento:itxLovDec::content"]'
    evento_pesquisar = '//*[@id="tplSip:lovEvento:cmdLov::icon"]'
    identificador_exercicio_fonte = '//*[@id="tplSip:pnlNotaEventoItem_chc_23::content"]'
    credor = '//*[@id="tplSip:pnlNotaEventoItem_chc_51::content"]'
    valor = '//*[@id="tplSip:itxValor::content"]'
    btn_confirmar_item = '//*[@id="tplSip:btnConfirmar"]'
    btn_cancelar_item = '//*[@id="tplSip:btnCancelar"]'

    # Erro
    erro_titulo = '//*[@id="docPrincipal::msgDlg::_ttxt"]'
    erro_body = '//*[@id="docPrincipal::msgDlg::_cnt"]/div/table/tbody/tr/td/table/tbody/tr/td[2]/div'
    btn_ok_erro = '//*[@id="docPrincipal::msgDlg::cancel"]'
    erro_pesquisar = '//*[@id="tplSip:lovEvento:pnlTab::_ttxt"]'
    btn_erro_pesquisar = '//*[@id="tplSip:lovEvento:frm_popup:btnCancelarLovDec"]'
    
    # Observação
    btn_inserir_observacao = '//*[@id="tplSip:slcObservacao::disAcr"]'
    observacao = '//*[@id="tplSip:itxObservacao::content"]'
    
    # Rascunho
    btn_rascunho = '//*[@id="tplSip:btnConfirmar"]'
    
    # Filtro de Pesquisa
    btn_filtro = '//*[@id="pt1:tblDocumento:sdtFilter::btn"]'
    select_propriedade = '//*[@id="pt1:tblDocumento:table_rtfFilter:0:cbx_col_sel_rtfFilter::content"]'
    select_operador = '//*[@id="pt1:tblDocumento:table_rtfFilter:0:cbx_op_sel_rtfFilter::content"]'
    valor_filtro = '//*[@id="pt1:tblDocumento:table_rtfFilter:0:in_value_rtfFilter::content"]'
    copiar_ev = '//*[@id="pt1:tblDocumento:btnCopiar"]'
    selecionar_ev = '//*[@id="pt1:tblDocumento:tabViewerDec::db"]/table/tbody/tr'
    
    # Campo de Retorno
    numero_documento_p = '//*[@id="pt1:tblDocumento:tabViewerDec::db"]/table/tbody/tr[1]/td[1]'
    numero_documento = '//*[@id="tplSip:itxNumero::content"]'