select
	p.IDPROD as 'Codigo do Produto',
	ddt.ANO,
    ddt.TRIMESTRE,
    dtp.TOTAL_PEDIDO as 'Demanda Real',
    dpd.DEMANDA_PROJETADA as 'Demanda Projetada',
    dci.NS as 'Nivel de Seguranca',
    dci.NRS as 'Nivel de Ressuprimento',
    dci.TPA as 'Tempo de Procura e Aquisição'

FROM
	PRODUTO p
    INNER JOIN DW_TOTAL_PEDIDO dtp on dtp.IDPROD = p.IDPROD
    INNER JOIN DW_DIMENSAO_TEMPO ddt on ddt.ID = dtp.IDTEMPO
    JOIN DW_PROJECAO_DEMANDA dpd on dpd.IDPROD = p.IDPROD AND dpd.IDTEMPO = ddt.ID
    INNER JOIN DW_CONTROLE_INVENTARIO dci on dci.IDPROD = p.IDPROD AND dci.IDTEMPO = ddt.ID
    
ORDER BY
	p.IDPROD,
    ddt.ANO,
    ddt.TRIMESTRE
