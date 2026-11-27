import pandas as pd, numpy as np, json
OUT = '/mnt/user-data/outputs/resultados'
PER = ['P1_2019-2021', 'P2_2022', 'P3_2023', 'P4_2024', 'P5_2025-2026']
PL = {'P1_2019-2021': '2019–2021', 'P2_2022': '2022', 'P3_2023': '2023', 'P4_2024': '2024', 'P5_2025-2026': '2025–2026'}
MED = ['BioBioChile', 'CNN Chile', 'Cooperativa', 'Emol', 'La Tercera', 'T13']
VOZL = {'P': 'Medio (P)', 'FE': 'Experta (FE)', 'FC': 'Corporativa (FC)', 'FG': 'Gobierno y política (FG)', 'FS': 'Sociedad civil (FS)', 'FI': 'Org. internacionales (FI)', 'FM': 'Mixta (FM)'}

def f(x, d=1):
    if isinstance(x, str): return x
    if x is None or (isinstance(x, float) and np.isnan(x)): return '—'
    s = f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s
def n0(x):
    return f'{int(x):,}'.replace(',', '.')
def md(rows, header):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    for r in rows:
        out.append('| ' + ' | '.join(str(c) for c in r) + ' |')
    return '\n'.join(out)

S = json.load(open(f'{OUT}/resumen.json'))
N = S['notas_codificadas']
doc = []
doc.append('# Tablas de resultados. Encuadre de la IA en seis medios digitales chilenos, 2019–2026\n')
doc.append('Generadas el 8 de octubre de 2026 desde `05 citas/registro_citas_completo.csv` (17.235 entradas, 3.762 notas con al menos un código sustantivo) y el corpus corregido (5.127 notas en rango). Los códigos por defecto (1.3.SIN, 3.1.NIN, 3.2.NEX, 3.3.NIN) no están en el registro. Base de los porcentajes por nota. Las 3.762 notas con codificación sustantiva, salvo indicación. "Estandarizado" significa estandarización directa por composición de medios (pesos iguales a la distribución de medios del conjunto de notas codificadas) o por composición de períodos, según el caso. Las pruebas son chi cuadrado de independencia con V de Cramér. Las razones de momios (OR) provienen de regresiones logísticas de la presencia del código sobre el período (referencia 2019–2021) con el medio como control (referencia La Tercera).\n')

# T1
t1 = pd.read_csv(f'{OUT}/T1a_corpus_medio_periodo.csv', index_col=0); t1c = pd.read_csv(f'{OUT}/T1b_notas_codificadas_medio_periodo.csv', index_col=0); t1s = pd.read_csv(f'{OUT}/T1c_proporcion_codificadas.csv', index_col=0)
rows = []
for m in MED + ['Total']:
    rows.append([m] + [f'{n0(t1.loc[m, p])} / {n0(t1c.loc[m, p])}' for p in PER] + [f'{n0(t1.loc[m, "Total"])} / {n0(t1c.loc[m, "Total"])}', f(t1s.loc[m, 'Total'])])
doc.append('## Tabla 1. Corpus y notas con codificación sustantiva por medio y período (notas del corpus / notas codificadas)\n')
doc.append(md(rows, ['Medio'] + [PL[p] for p in PER] + ['Total', '% codificadas']))
doc.append('')

# T2 indicadores
t2i = pd.read_csv(f'{OUT}/T2b_frecuencia_indicadores.csv', index_col=0, dtype={'ind': str}); t2i.index = t2i.index.astype(str); t2d = pd.read_csv(f'{OUT}/T2c_frecuencia_dimensiones.csv', index_col=0); t2d.index = t2d.index.astype(int)
IND = {'1.1': 'Agente impulsor', '1.2': 'Motor atribuido', '1.3': 'Narrativa temporal del origen', '2.1': 'Naturaleza atribuida', '2.2': 'Oportunidad', '2.3': 'Riesgo o amenaza', '2.4': 'Condicionalidad', '2.5': 'Relativización', '2.6': 'Caracterizaciones emergentes', '3.1': 'Futuro proyectado', '3.2': 'Modalidad del futuro', '3.3': 'Acción prescrita', '3.4': 'Actor responsable de actuar', '3.5': 'Imperativo de adopción'}
rows = [[f'D{d}', {'1': 'Origen', '2': 'Carácter', '3': 'Horizonte'}[d], n0(t2d.loc[int(d), 'notas']), f(t2d.loc[int(d), 'pct_notas'])] for d in ['1', '2', '3']]
doc.append('## Tabla 2a. Notas con al menos un código sustantivo por dimensión\n'); doc.append(md(rows, ['Dimensión', 'Nombre', 'Notas', '% de 3.762'])); doc.append('')
rows = [[i, IND[i], n0(t2i.loc[i, 'notas']), f(t2i.loc[i, 'pct_notas'])] for i in sorted(t2i.index)]
doc.append('## Tabla 2b. Notas con al menos un código sustantivo por indicador\n'); doc.append(md(rows, ['Indicador', 'Nombre', 'Notas', '% de 3.762'])); doc.append('')
t2 = pd.read_csv(f'{OUT}/T2_frecuencia_codigos.csv').sort_values('notas', ascending=False)
rows = []
for r in t2.itertuples():
    val = ', '.join(f'{k} {int(getattr(r, k2))}' for k, k2 in [('+', '_7'), ('−', '_8'), ('A', 'A'), ('C', 'C'), ('D', 'D'), ('NA', 'NA')] if int(getattr(r, k2)) > 0) if False else ''
    rows.append([f'`{r.cod}`', r.nombre, n0(r.notas), f(r.pct_notas), n0(r.entradas), int(r._7) if hasattr(r, '_7') else '', ])
# simpler construction
rows = []
for _, r in t2.iterrows():
    vals = []
    for k in ['+', '-', 'A', 'C', 'D', 'NA']:
        if int(r[k]) > 0: vals.append(f'{"−" if k == "-" else k} {int(r[k])}')
    rows.append([f'`{r.cod}`', r.nombre, n0(r.notas), f(r.pct_notas), n0(r.entradas), ', '.join(vals)])
doc.append('## Tabla 2c. Frecuencia de los códigos sustantivos (notas en que aparece, entradas y valoraciones de las entradas)\n'); doc.append(md(rows, ['Código', 'Nombre', 'Notas', '% de 3.762', 'Entradas', 'Valoraciones'])); doc.append('')

# T3 valoración
t3p = pd.read_csv(f'{OUT}/T3b_valoracion_por_periodo.csv', index_col=0)
rows = [[PL[p], n0(t3p.loc[p, 'total']), f(t3p.loc[p, 'pct_+']), f(t3p.loc[p, 'pct_-']), f(t3p.loc[p, 'pct_A'] + t3p.loc[p, 'pct_C']), f(t3p.loc[p, 'pct_D']), f(t3p.loc[p, 'valencia'], 2)] for p in PER]
doc.append('## Tabla 3a. Valoración de las entradas con valoración aplicable, por período (excluye NA)\n'); doc.append(md(rows, ['Período', 'Entradas', '% positiva', '% negativa', '% ambivalente o contingente', '% descriptiva', 'Índice de valencia (+ − −)/(+ + −)'])); doc.append('')
sub = pd.read_csv('/mnt/user-data/outputs/corregido2/registro_citas_completo.csv', keep_default_na=False, dtype=str)
pol = sub[sub.v.isin(['+', '-'])]
rows = []
for ind, name in [('2.1', 'Naturaleza atribuida (2.1)'), ('3.1', 'Futuro proyectado (3.1)'), ('1.1', 'Agente impulsor (1.1)'), ('3.3', 'Acción prescrita (3.3)')]:
    d = pol[pol.cod.str.startswith(ind)]
    cells = []
    for p in PER:
        dp = d[d.periodo == p]
        cells.append(f'{f((dp.v == "+").mean() * 100)} ({len(dp)})')
    cells.append(f'{f((d.v == "+").mean() * 100)} ({len(d)})')
    rows.append([name] + cells)
doc.append('## Tabla 3b. Porcentaje de valoraciones positivas entre las entradas polares (+ o −) de los indicadores con valoración mixta, por período (n entre paréntesis)\n'); doc.append(md(rows, ['Indicador'] + [PL[p] for p in PER] + ['Total'])); doc.append('')

# T4 voz
t4 = pd.read_csv(f'{OUT}/T4_voz.csv', index_col=0); t4p = pd.read_csv(f'{OUT}/T4b_voz_periodo_pct.csv', index_col=0); t4pn = pd.read_csv(f'{OUT}/T4b_voz_periodo_n.csv', index_col=0)
rows = [[VOZL[v], n0(t4.loc[v, 'entradas']), f(t4.loc[v, 'pct'])] + [f(t4p.loc[p, v]) for p in PER] for v in ['P', 'FE', 'FC', 'FG', 'FS', 'FI', 'FM']]
rows.append(['Entradas (n)', n0(t4.entradas.sum()), '100'] + [n0(t4pn.loc[p].sum()) for p in PER])
doc.append('## Tabla 4a. Voz que enuncia el fragmento codificado. Total y distribución porcentual por período\n'); doc.append(md(rows, ['Voz', 'Entradas', '% total'] + [PL[p] for p in PER])); doc.append('')
t4m = pd.read_csv(f'{OUT}/T4c_voz_medio_pct.csv', index_col=0); t4mn = pd.read_csv(f'{OUT}/T4c_voz_medio_n.csv', index_col=0)
rows = [[m] + [f(t4m.loc[m, v]) for v in ['P', 'FE', 'FC', 'FG', 'FS', 'FI']] + [n0(t4mn.loc[m].sum())] for m in MED]
doc.append('## Tabla 4b. Distribución porcentual de las voces por medio\n'); doc.append(md(rows, ['Medio', 'P', 'FE', 'FC', 'FG', 'FS', 'FI', 'Entradas'])); doc.append('')
t4g = pd.read_csv(f'{OUT}/T4g_voz_por_familia_codigos.csv', index_col=0)
rows = [[i] + [f(t4g.loc[i, v]) for v in ['P', 'FE', 'FC', 'FG', 'FS', 'FI']] + [n0(t4g.loc[i, 'n'])] for i in t4g.index]
doc.append('## Tabla 4c. Quién enuncia cada familia de códigos (porcentaje de las entradas de la familia)\n'); doc.append(md(rows, ['Familia de códigos', 'P', 'FE', 'FC', 'FG', 'FS', 'FI', 'Entradas'])); doc.append('')
t4v = pd.read_csv(f'{OUT}/T4e_voz_valoracion.csv', index_col=0)
d21 = pol[pol.cod.str.startswith('2.1')]
rows = []
for v in ['FC', 'FG', 'P', 'FI', 'FE', 'FS']:
    dv = d21[d21.voz == v]
    rows.append([VOZL[v], n0(t4v.loc[v, '+'] + t4v.loc[v, '-']), f(t4v.loc[v, 'pct_pos']), n0(len(dv)), f((dv.v == '+').mean() * 100) if len(dv) else '—'])
doc.append('## Tabla 4d. Porcentaje de valoraciones positivas entre las entradas polares, por voz. Todas las entradas polares y solo las del indicador 2.1 (naturaleza atribuida)\n'); doc.append(md(rows, ['Voz', 'Entradas polares', '% positiva', 'Entradas polares 2.1', '% positiva en 2.1'])); doc.append('')

# T5 trayectorias
tr = pd.read_csv(f'{OUT}/T5_trayectorias_periodo.csv'); lg = pd.read_csv(f'{OUT}/T5b_logit_periodo_ajustado_medio.csv').set_index('variable')
sel = ['I_1.1', 'I_1.2', 'I_2.1', 'I_2.2', 'I_2.3', 'I_2.4', 'I_2.5', 'I_2.6', 'I_3.1', 'I_3.2', 'I_3.3', 'I_3.5', 'I_22solo', 'I_22y23', 'I_23solo', 'I_ni22ni23', 'I_33_regcon', 'I_33_adop',
       'C_1.1.CIE', 'C_1.1.CORP', 'C_1.1.DIF', 'C_1.1.EST', 'C_1.2.GEO', 'C_2.1.HER', 'C_2.1.INN', 'C_2.1.AGE', 'C_2.1.REV', 'C_2.1.MER', 'C_2.1.LIM', 'C_2.2.ECO', 'C_2.2.LAB', 'C_2.2.SAL', 'C_2.3.EMP', 'C_2.3.DEM', 'C_2.3.PRI', 'C_2.3.SEG', 'C_2.3.DES', 'C_2.3.HUM',
       'C_2.5.HYP', 'C_2.5.ALA', 'C_3.1.CON', 'C_3.1.INC', 'C_3.2.INE', 'C_3.3.ADO', 'C_3.3.ADA', 'C_3.3.REG', 'C_3.3.GOB', 'C_3.3.CON', 'C_3.3.PRO', 'C_3.3.LIB', 'C_3.4.EST', 'C_3.4.EMP', 'C_3.4.IND', 'C_3.5.REZ']
tr = tr.set_index('variable')
rows = []
for v in sel:
    r = tr.loc[v]
    orp = lg.loc[v, 'P5_2025-2026_OR'] if v in lg.index else np.nan
    ic = (lg.loc[v, 'P5_2025-2026_IC'].replace('.', ',') if v in lg.index else '—')
    if isinstance(orp, float) and (np.isnan(orp) or orp > 1000): orp, ic = '—', '—'
    rows.append([r.etiqueta.replace('Indicador ', 'Ind. '), f(r.pct_total)] + [f(r[p + '_estand']) for p in PER] + [f(r.dif_P5_P1_estand), f(r.cramer_v, 3), f(orp, 2) if orp != '—' else '—', ic])
doc.append('## Tabla 5. Trayectorias por período. Porcentaje de notas con el código, estandarizado por composición de medios, V de Cramér (período × presencia) y razón de momios 2025–2026 frente a 2019–2021 ajustada por medio\n')
doc.append(md(rows, ['Variable', '% total'] + [PL[p] for p in PER] + ['Dif. P5 − P1', 'V de Cramér', 'OR P5 vs P1', 'IC 95 %']))
doc.append('\nNota. Las tasas crudas por período están en `T5_trayectorias_periodo.csv`. Las diferencias entre tasas crudas y estandarizadas no superan 3,3 puntos porcentuales en ninguna variable de esta tabla, lo que indica que la composición de medios por período no explica las trayectorias. Los OR con intervalos muy amplios corresponden a códigos poco frecuentes y no deben interpretarse.\n')
ty = pd.read_csv(f'{OUT}/T5c_indicadores_por_anio.csv')
rows = [[int(r.anio), n0(r.n), f(r['I_2.2']), f(r['I_2.3']), f(r['I_22y23']), f(r['I_3.3']), f(r['I_33_regcon']), f(r['I_33_adop']), f(r['C_2.1.MER']), f(r['I_2.5'])] for _, r in ty.iterrows()]
doc.append('## Tabla 5b. Indicadores seleccionados por año (porcentaje crudo de las notas codificadas del año)\n'); doc.append(md(rows, ['Año', 'Notas', '2.2 oportunidad', '2.3 riesgo', 'ambas', '3.3 acción', '3.3 regulación y control', '3.3 adopción y adaptación', '2.1.MER', '2.5 relativización'])); doc.append('')

# T6 medios
t6 = pd.read_csv(f'{OUT}/T6_perfiles_por_medio.csv').set_index('variable')
sel6 = ['I_2.1', 'I_2.2', 'I_2.3', 'I_22y23', 'I_2.4', 'I_2.5', 'I_3.1', 'I_3.3', 'I_33_regcon', 'I_33_adop', 'C_1.1.CORP', 'C_2.1.HER', 'C_2.1.INN', 'C_2.1.LIM', 'C_2.1.MER', 'C_2.1.AGE', 'C_2.2.ECO', 'C_2.2.SAL', 'C_2.3.SEG', 'C_2.3.PRI', 'C_2.5.HYP', 'C_2.5.ALA', 'C_3.3.REG', 'C_3.3.CON', 'C_3.4.EST', 'C_3.4.EMP', 'C_3.5.REZ']
rows = [[t6.loc[v, 'etiqueta'].replace('Indicador ', 'Ind. ')] + [f(t6.loc[v, m + '_estand']) for m in MED] + [f(t6.loc[v, 'cramer_v'], 3)] for v in sel6]
doc.append('## Tabla 6. Perfiles por medio. Porcentaje de notas con el código, estandarizado por composición de períodos, y V de Cramér (medio × presencia)\n'); doc.append(md(rows, ['Variable'] + MED + ['V de Cramér'])); doc.append('\nNota. T13 solo tiene notas de 2024 a 2026 (56 codificadas), por lo que su estandarización se apoya en dos períodos y sus cifras deben leerse con cautela. Las tasas crudas están en `T6_perfiles_por_medio.csv`.\n')
t3dm = pd.read_csv(f'{OUT}/T3d_pct_positivo_D2_medio_periodo.csv', index_col=0)
d21m = d21.groupby('medio').v.apply(lambda s: (s == '+').mean() * 100)
rows = [[m, f(d21m.get(m, np.nan)), n0(len(d21[d21.medio == m]))] for m in MED]
doc.append('## Tabla 6b. Porcentaje de valoraciones positivas entre las entradas polares del indicador 2.1, por medio\n'); doc.append(md(rows, ['Medio', '% positiva en 2.1', 'Entradas polares 2.1'])); doc.append('')

# T7 centralidad y densidad
t7 = pd.read_csv(f'{OUT}/T7_centralidad_periodo.csv', index_col=0); t7b = pd.read_csv(f'{OUT}/T7b_codigos_por_nota_periodo.csv', index_col=0)
rows = [[PL[p], n0(t7.loc[p, 'central']), n0(t7.loc[p, 'secundaria']), f(t7.loc[p, 'pct_central']), f(t7b.loc[p, 'mean'], 2)] for p in PER]
doc.append('## Tabla 7. Centralidad de la IA en las notas codificadas y códigos sustantivos por nota, por período\n'); doc.append(md(rows, ['Período', 'Central', 'Secundaria', '% central', 'Códigos por nota (media)'])); doc.append('')

# T8 modificadores
e = pd.read_csv(f'{OUT}/T8b_escala_11_periodo.csv', index_col=0); r_ = pd.read_csv(f'{OUT}/T8d_resp_23_periodo.csv', index_col=0); g = pd.read_csv(f'{OUT}/T8e_intensidad_23_periodo.csv', index_col=0)
rows = [[PL[p], n0(e.loc[p].sum()), f(e.loc[p, 'Chile'] / e.loc[p].sum() * 100), f(e.loc[p, 'global'] / e.loc[p].sum() * 100)] for p in PER] + [['Total', n0(e.values.sum()), f(e['Chile'].sum() / e.values.sum() * 100), f(e['global'].sum() / e.values.sum() * 100)]]
doc.append('## Tabla 8a. Escala del agente impulsor (códigos 1.1.CIE, 1.1.CORP y 1.1.EST con modificador `escala`)\n'); doc.append(md(rows, ['Período', 'Entradas', '% Chile', '% global'])); doc.append('')
RESP = {'RTE': 'propiedad de la tecnología', 'RMA': 'uso malicioso', 'RDI': 'sin autor ni intención', 'RCO': 'decisiones de empresas', 'RUS': 'usuarios o sociedad', 'RES': 'Estado o falta de regulación'}
rows = [[PL[p], n0(r_.loc[p].sum())] + [f(r_.loc[p, k] / r_.loc[p].sum() * 100) for k in ['RTE', 'RMA', 'RDI', 'RCO', 'RUS', 'RES']] for p in PER] + [['Total', n0(r_.values.sum())] + [f(r_[k].sum() / r_.values.sum() * 100) for k in ['RTE', 'RMA', 'RDI', 'RCO', 'RUS', 'RES']]]
doc.append('## Tabla 8b. A quién se atribuye el daño en los códigos de riesgo (modificador `resp` de 2.3), porcentaje por período\n'); doc.append(md(rows, ['Período', 'Entradas'] + [f'{k} ({RESP[k]})' for k in ['RTE', 'RMA', 'RDI', 'RCO', 'RUS', 'RES']])); doc.append('')
rows = [[PL[p], n0(g.loc[p].sum())] + [f(g.loc[p, k] / g.loc[p].sum() * 100) for k in ['G1', 'G2', 'G3']] for p in PER] + [['Total', n0(g.values.sum())] + [f(g[k].sum() / g.values.sum() * 100) for k in ['G1', 'G2', 'G3']]]
doc.append('## Tabla 8c. Intensidad del daño (modificador `g` de 2.3), porcentaje por período\n'); doc.append(md(rows, ['Período', 'Entradas', 'G1 riesgo acotado', 'G2 amenaza grave o sistémica', 'G3 pérdida de control'])); doc.append('')

doc.append('## Figuras\n\n- `figura1_oportunidad_riesgo_prescripcion_anio.png`. Oportunidad (2.2), riesgo (2.3), acción prescrita (3.3) y coocurrencia de oportunidad y riesgo, por año.\n- `figura2_voces_periodo.png`. Distribución de las voces por período.\n- `figura3_trayectorias_codigos.png`. Ocho códigos con mayor cambio entre períodos, tasas crudas y estandarizadas por medio.\n- `figura4_valoracion_21_voz_periodo.png`. Porcentaje de valoraciones positivas en 2.1 por voz y período (las voces FG y FS tienen pocos casos por período).\n')
open(f'{OUT}/TABLAS_resultados_2026-10-08.md', 'w', encoding='utf-8').write('\n'.join(doc))
print('ok', len('\n'.join(doc).split()))
