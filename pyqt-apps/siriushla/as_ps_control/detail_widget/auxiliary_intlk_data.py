"""Temporary auxiliary interlock data module."""


INTERLOCK_LABELS_Q1234 = {
    'IntlkSoftLabels-Cte': (
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha de leitura da corrente na carga do DCCT 1',
        'Falha de leitura da corrente na carga do DCCT 2',
        'Alta diferença entre a corrente dos IGBTs',
        'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31'),
    'IntlkHardLabels-Cte': (
        'Sobre-corrente na carga',
        'Sobre-tensao na carga',
        'Sobre-tensao no DC-Link',
        'Sub-tensao no DC-Link',
        'Contator de entrada do DC-Link colado',
        'Abertura do contator de entrada do DC-Link',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Interlock da placa IIB', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31'),
    'IntlkIIBLabels-Cte': (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente do driver do IGBT 1',
        'Sobre-corrente do driver do IGBT 2', 'Erro no driver do IGBT 1',
        'Erro no driver do IGBT 2', 'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Falha no contator de entrada do DC-Link',
        'Contator de entrada do DC-Link colado', 'Interlock externo',
        'Interlock do rack', 'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31'),
    'AlarmsIIBLabels-Cte': (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador', 'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31'),
}