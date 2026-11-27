"""Construcción de resultados desde el registro de citas y el corpus corregido.
Salidas en /mnt/user-data/outputs/resultados/ (CSV, JSON y tablas en Markdown)."""
import re, glob, os, json, collections
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

CORP = '/mnt/user-data/outputs/corregido2'
OUT = '/mnt/user-data/outputs/resultados'
os.makedirs(OUT, exist_ok=True)

PER_ORDER = ['P1_2019-2021', 'P2_2022', 'P3_2023', 'P4_2024', 'P5_2025-2026']
PER_LABEL = {'P1_2019-2021': 'P1 2019–2021', 'P2_2022': 'P2 2022', 'P3_2023': 'P3 2023', 'P4_2024': 'P4 2024', 'P5_2025-2026': 'P5 2025–2026'}
MED_ORDER = ['BioBioChile', 'CNN Chile', 'Cooperativa', 'Emol', 'La Tercera', 'T13']
DEF = {'1.3.SIN', '3.1.NIN', '3.2.NEX', '3.3.NIN'}
NOMBRE = {
 '1.1.CIE': 'Comunidad científico-técnica', '1.1.CORP': 'Corporaciones tecnológicas', '1.1.EST': 'Estados y potencias', '1.1.USU': 'Usuarios y demanda social', '1.1.DIF': 'Agencia difusa o ausente',
 '1.2.CON': 'Conocimiento e innovación', '1.2.ECO': 'Lógica económica', '1.2.GEO': 'Competencia geopolítica', '1.2.CTR': 'Control y dominación', '1.2.NEC': 'Necesidad social', '1.2.INE': 'Tendencia inevitable',
 '1.3.IRR': 'Irrupción súbita', '1.3.TRA': 'Trayectoria larga', '1.3.SIN': 'Sin referencia al origen',
 '2.1.HER': 'Instrumento', '2.1.INN': 'Avance o novedad', '2.1.AGE': 'Entidad con agencia', '2.1.REV': 'Transformación estructural', '2.1.MER': 'Producto o negocio', '2.1.LIM': 'Tecnología limitada o falible',
 '2.2.ECO': 'Oportunidad económica', '2.2.LAB': 'Oportunidad laboral', '2.2.EDU': 'Oportunidad educativa', '2.2.SAL': 'Oportunidad en salud y ciencia', '2.2.EST': 'Oportunidad para el Estado', '2.2.SEG': 'Oportunidad en seguridad', '2.2.AMB': 'Oportunidad ambiental', '2.2.CUL': 'Oportunidad cultural', '2.2.OTR': 'Otra oportunidad',
 '2.3.EMP': 'Riesgo para el empleo', '2.3.DEM': 'Riesgo democrático e informativo', '2.3.PRI': 'Riesgo para la privacidad', '2.3.SEG': 'Riesgo para la seguridad', '2.3.DES': 'Riesgo de desinformación', '2.3.CUL': 'Riesgo cultural y creativo', '2.3.SAL': 'Riesgo para la salud', '2.3.AMB': 'Riesgo ambiental', '2.3.EST': 'Riesgo para el Estado', '2.3.HUM': 'Riesgo para lo humano', '2.3.OTR': 'Otro riesgo',
 '2.4.USO': 'Depende del uso', '2.4.DIS': 'Depende del diseño', '2.4.REG': 'Depende de la regulación', '2.4.CTX': 'Depende del contexto',
 '2.5.HYP': 'Exageración (hype)', '2.5.ALA': 'Alarmismo', '2.5.AMB': 'Ambivalencia',
 '2.6.REC': 'Caracterización emergente REC', '2.6.IMI': 'Caracterización emergente IMI', '2.6.PCH': 'Caracterización emergente PCH', '2.6.FAH': 'Caracterización emergente FAH', '2.6.ACT': 'Caracterización emergente ACT',
 '3.1.CON': 'Futuro de continuidad', '3.1.EST': 'Futuro de estancamiento', '3.1.RUP': 'Futuro de ruptura', '3.1.INC': 'Futuro incierto', '3.1.NIN': 'Sin futuro proyectado',
 '3.2.INE': 'Futuro inevitable', '3.2.DEC': 'Futuro decidible', '3.2.NEX': 'Modalidad no explícita',
 '3.3.ADO': 'Adoptar', '3.3.ADA': 'Adaptarse o capacitarse', '3.3.REG': 'Regular', '3.3.GOB': 'Gobernar o coordinar', '3.3.LIB': 'Liberar o no regular', '3.3.CON': 'Controlar', '3.3.PRO': 'Prohibir o pausar', '3.3.NIN': 'Sin acción prescrita',
 '3.4.EST': 'Estado', '3.4.EMP': 'Empresas', '3.4.ACA': 'Academia', '3.4.SOC': 'Sociedad civil', '3.4.IND': 'Individuos', '3.4.INT': 'Organismos internacionales', '3.4.NES': 'Ejecutor no especificado',
 '3.5.REZ': 'Imperativo de adopción y rezago'}
VOZ_LABEL = {'P': 'Medio (periodista)', 'FE': 'Fuente experta', 'FC': 'Fuente corporativa', 'FG': 'Gobierno y política', 'FS': 'Sociedad civil', 'FI': 'Organismos internacionales', 'FM': 'Fuentes mixtas'}
VOZ_ORDER = ['P', 'FE', 'FC', 'FG', 'FS', 'FI', 'FM']

def periodo(a):
    a = int(a)
    return 'P1_2019-2021' if a <= 2021 else {2022: 'P2_2022', 2023: 'P3_2023', 2024: 'P4_2024'}.get(a, 'P5_2025-2026')

# ---------------------------------------------------------------- 1. corpus
rows = []
for f in sorted(glob.glob(f'{CORP}/*.md')):
    base = os.path.basename(f)
    if not re.match(r'(BBC|CNN|COOP|EMOL|LT|T13)_\d{4}\.md$', base):
        continue
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'<!-- ===== (\S+) \| (\d{4}-\d{2}-\d{2}) ===== -->', txt)
    for i in range(1, len(parts) - 2, 3):
        nid, fch, body = parts[i], parts[i + 1], parts[i + 2]
        m = re.search(r'\n---\n(.*?)\n---\n', body, re.S)
        meta = {}
        if m:
            for l in m.group(1).split('\n'):
                k, _, v = l.partition(': ')
                meta[k.strip()] = v.strip().strip('"')
            text = body[m.end():]
        else:
            text = body
        text = re.sub(r'^\s*# .*?\n', '', text, count=1).strip()
        rows.append(dict(id=nid, fecha=fch, medio=meta.get('medio', ''), anio=int(fch[:4]), periodo=periodo(fch[:4]),
                         tipo=meta.get('tipo', ''), subtipo=meta.get('subtipo', ''), metodo=meta.get('metodo_descubrimiento', ''),
                         autor=meta.get('autor', ''), palabras=len(text.split()), archivo=base))
corpus = pd.DataFrame(rows)
assert corpus.id.is_unique
corpus.to_csv(f'{OUT}/corpus_indice_5127.csv', index=False, encoding='utf-8')
print('corpus', len(corpus), corpus.medio.value_counts().to_dict())

# ---------------------------------------------------------------- 2. registro
reg = pd.read_csv(f'{CORP}/registro_citas_completo.csv', keep_default_na=False, dtype=str)
reg['calidad'] = reg.calidad.astype(int)
reg['anio'] = reg.anio.astype(int)
assert set(reg.id) <= set(corpus.id)
reg['ind'] = reg.cod.str[:3]
reg['dim'] = reg.cod.str[0]
sub = reg[~reg.cod.isin(DEF)].copy()
notes = sub.groupby('id').agg(medio=('medio', 'first'), anio=('anio', 'first'), periodo=('periodo', 'first'), c1=('c1', 'first'), n_cod=('cod', 'size')).reset_index()
N = len(notes)
print('notas con codigo', N, '| entradas', len(sub), '| defaults en registro', int(reg.cod.isin(DEF).sum()))

# ---------------------------------------------------------------- 3. tablas descriptivas
def pct(a, b):
    return round(100 * a / b, 1) if b else np.nan

# T1 corpus por medio x periodo, y notas con código
t1 = pd.crosstab(corpus.medio, corpus.periodo).reindex(index=MED_ORDER, columns=PER_ORDER, fill_value=0)
t1['Total'] = t1.sum(1); t1.loc['Total'] = t1.sum(0)
t1c = pd.crosstab(notes.medio, notes.periodo).reindex(index=MED_ORDER, columns=PER_ORDER, fill_value=0)
t1c['Total'] = t1c.sum(1); t1c.loc['Total'] = t1c.sum(0)
t1_share = (t1c / t1 * 100).round(1)
t1.to_csv(f'{OUT}/T1a_corpus_medio_periodo.csv'); t1c.to_csv(f'{OUT}/T1b_notas_codificadas_medio_periodo.csv'); t1_share.to_csv(f'{OUT}/T1c_proporcion_codificadas.csv')
t1y = pd.crosstab(corpus.medio, corpus.anio).reindex(index=MED_ORDER, fill_value=0); t1y.loc['Total'] = t1y.sum(0)
t1y.to_csv(f'{OUT}/T1d_corpus_medio_anio.csv')
t1cy = pd.crosstab(notes.medio, notes.anio).reindex(index=MED_ORDER, fill_value=0); t1cy.loc['Total'] = t1cy.sum(0)
t1cy.to_csv(f'{OUT}/T1e_codificadas_medio_anio.csv')

# T2 frecuencia de codigos (notas) con valoraciones
pres = sub.groupby(['id', 'cod']).size().reset_index()[['id', 'cod']]
pres = pres.merge(notes[['id', 'medio', 'periodo', 'anio']], on='id')
t2 = pres.groupby('cod').size().rename('notas').to_frame()
t2['pct_notas'] = (t2.notas / N * 100).round(1)
t2['entradas'] = sub.groupby('cod').size()
vc = sub.groupby(['cod', 'v']).size().unstack(fill_value=0)
for c in ['+', '-', 'A', 'C', 'D', 'NA']:
    if c not in vc: vc[c] = 0
t2 = t2.join(vc[['+', '-', 'A', 'C', 'D', 'NA']])
t2['nombre'] = [NOMBRE.get(c, '') for c in t2.index]
t2['indicador'] = t2.index.str[:3]
t2 = t2.sort_index()
t2.to_csv(f'{OUT}/T2_frecuencia_codigos.csv')
# por indicador (nota con al menos un código del indicador) y dimensión
pres['ind'] = pres.cod.str[:3]; pres['dim'] = pres.cod.str[0]
t2i = pres.groupby(['id', 'ind']).size().reset_index().groupby('ind').size().rename('notas').to_frame()
t2i['pct_notas'] = (t2i.notas / N * 100).round(1)
t2d = pres.groupby(['id', 'dim']).size().reset_index().groupby('dim').size().rename('notas').to_frame()
t2d['pct_notas'] = (t2d.notas / N * 100).round(1)
t2i.to_csv(f'{OUT}/T2b_frecuencia_indicadores.csv'); t2d.to_csv(f'{OUT}/T2c_frecuencia_dimensiones.csv')

# T3 valoracion
val = sub[sub.v.isin(['+', '-', 'A', 'C', 'D'])].copy()
t3 = pd.crosstab(val.ind, val.v).reindex(columns=['+', '-', 'A', 'C', 'D'], fill_value=0)
t3['total'] = t3.sum(1)
t3['pct_pos'] = (t3['+'] / t3.total * 100).round(1); t3['pct_neg'] = (t3['-'] / t3.total * 100).round(1); t3['pct_D'] = (t3['D'] / t3.total * 100).round(1)
pol = t3['+'] + t3['-']
t3['valencia'] = ((t3['+'] - t3['-']) / pol).round(3)
t3.to_csv(f'{OUT}/T3_valoracion_por_indicador.csv')
t3p = pd.crosstab(val.periodo, val.v).reindex(index=PER_ORDER, columns=['+', '-', 'A', 'C', 'D'], fill_value=0)
t3p['total'] = t3p.sum(1)
for c in ['+', '-', 'A', 'C', 'D']:
    t3p['pct_' + c] = (t3p[c] / t3p.total * 100).round(1)
t3p['valencia'] = ((t3p['+'] - t3p['-']) / (t3p['+'] + t3p['-'])).round(3)
t3p.to_csv(f'{OUT}/T3b_valoracion_por_periodo.csv')
# valencia por periodo y dimension (solo entradas polares)
polar = val[val.v.isin(['+', '-'])].copy()
polar['pos'] = (polar.v == '+').astype(int)
t3pd = polar.groupby(['dim', 'periodo']).pos.agg(['mean', 'size']).reset_index()
t3pd['mean'] = (t3pd['mean'] * 100).round(1)
t3pd = t3pd.pivot(index='dim', columns='periodo', values=['mean', 'size']).reindex(columns=pd.MultiIndex.from_product([['mean', 'size'], PER_ORDER]))
t3pd.to_csv(f'{OUT}/T3c_pct_positivo_dim_periodo.csv')
# valencia por periodo y medio (D2 entradas polares)
t3pm = polar[polar.dim == '2'].groupby(['medio', 'periodo']).pos.agg(['mean', 'size']).reset_index()
t3pm['mean'] = (t3pm['mean'] * 100).round(1)
t3pm.pivot(index='medio', columns='periodo', values='mean').reindex(index=MED_ORDER, columns=PER_ORDER).to_csv(f'{OUT}/T3d_pct_positivo_D2_medio_periodo.csv')
t3pm.pivot(index='medio', columns='periodo', values='size').reindex(index=MED_ORDER, columns=PER_ORDER).to_csv(f'{OUT}/T3d_n_polar_D2_medio_periodo.csv')

# T4 voz
t4 = sub.voz.value_counts().reindex(VOZ_ORDER, fill_value=0).to_frame('entradas')
t4['pct'] = (t4.entradas / len(sub) * 100).round(1)
t4['nombre'] = [VOZ_LABEL[v] for v in t4.index]
t4.to_csv(f'{OUT}/T4_voz.csv')
t4p = pd.crosstab(sub.periodo, sub.voz).reindex(index=PER_ORDER, columns=VOZ_ORDER, fill_value=0)
t4p_pct = (t4p.div(t4p.sum(1), axis=0) * 100).round(1)
t4p.to_csv(f'{OUT}/T4b_voz_periodo_n.csv'); t4p_pct.to_csv(f'{OUT}/T4b_voz_periodo_pct.csv')
t4m = pd.crosstab(sub.medio, sub.voz).reindex(index=MED_ORDER, columns=VOZ_ORDER, fill_value=0)
(t4m.div(t4m.sum(1), axis=0) * 100).round(1).to_csv(f'{OUT}/T4c_voz_medio_pct.csv'); t4m.to_csv(f'{OUT}/T4c_voz_medio_n.csv')
# voz por indicador (quién habla de qué)
t4i = pd.crosstab(sub.ind, sub.voz).reindex(columns=VOZ_ORDER, fill_value=0)
(t4i.div(t4i.sum(1), axis=0) * 100).round(1).to_csv(f'{OUT}/T4d_voz_por_indicador_pct.csv'); t4i.to_csv(f'{OUT}/T4d_voz_por_indicador_n.csv')
# voz x valoracion (entradas polares)
t4v = pd.crosstab(polar.voz, polar.v).reindex(index=VOZ_ORDER, fill_value=0)
t4v['pct_pos'] = (t4v['+'] / (t4v['+'] + t4v['-']) * 100).round(1)
t4v.to_csv(f'{OUT}/T4e_voz_valoracion.csv')
# voz x valoracion por periodo (pct positivo entre polares, por voz)
t4vp = polar.groupby(['voz', 'periodo']).pos.agg(['mean', 'size']).reset_index(); t4vp['mean'] = (t4vp['mean'] * 100).round(1)
t4vp.pivot(index='voz', columns='periodo', values='mean').reindex(index=VOZ_ORDER, columns=PER_ORDER).to_csv(f'{OUT}/T4f_pct_positivo_voz_periodo.csv')
t4vp.pivot(index='voz', columns='periodo', values='size').reindex(index=VOZ_ORDER, columns=PER_ORDER).to_csv(f'{OUT}/T4f_n_polar_voz_periodo.csv')
# quién enuncia oportunidad (2.2) vs riesgo (2.3) vs prescripción (3.3)
def voz_share(mask, name):
    s = sub[mask].voz.value_counts().reindex(VOZ_ORDER, fill_value=0)
    return pd.Series((s / s.sum() * 100).round(1), name=name), int(s.sum())
rows_v = []; ns = {}
for name, mask in [('2.2 oportunidad', sub.ind == '2.2'), ('2.3 riesgo', sub.ind == '2.3'), ('2.1.INN avance', sub.cod == '2.1.INN'), ('2.1.LIM falible', sub.cod == '2.1.LIM'), ('2.5 relativización', sub.ind == '2.5'),
                   ('3.3 regulación/control (REG,GOB,CON,PRO)', sub.cod.isin(['3.3.REG', '3.3.GOB', '3.3.CON', '3.3.PRO'])), ('3.3 adopción (ADO,ADA)', sub.cod.isin(['3.3.ADO', '3.3.ADA'])), ('3.5.REZ rezago', sub.cod == '3.5.REZ')]:
    s, n = voz_share(mask, name); s['n'] = n; rows_v.append(s)
t4g = pd.DataFrame(rows_v); t4g.to_csv(f'{OUT}/T4g_voz_por_familia_codigos.csv')

# ---------------------------------------------------------------- 4. trayectorias temporales
# matriz nota x indicador / codigo (presencia)
inds = sorted(pres.ind.unique()); cods = sorted(pres.cod.unique())
M = notes.set_index('id')[['medio', 'periodo', 'anio', 'c1']].copy()
for i in inds:
    M['I_' + i] = 0
for c in cods:
    M['C_' + c] = 0
pi = pres.groupby(['id', 'ind']).size().reset_index()
for r in pi.itertuples():
    M.at[r.id, 'I_' + r.ind] = 1
for r in pres.itertuples():
    M.at[r.id, 'C_' + r.cod] = 1
M['I_33_regcon'] = M[[c for c in ['C_3.3.REG', 'C_3.3.GOB', 'C_3.3.CON', 'C_3.3.PRO'] if c in M]].max(1)
M['I_33_adop'] = M[[c for c in ['C_3.3.ADO', 'C_3.3.ADA'] if c in M]].max(1)
M['I_22y23'] = ((M['I_2.2'] == 1) & (M['I_2.3'] == 1)).astype(int)
M['I_22solo'] = ((M['I_2.2'] == 1) & (M['I_2.3'] == 0)).astype(int)
M['I_23solo'] = ((M['I_2.2'] == 0) & (M['I_2.3'] == 1)).astype(int)
M['I_ni22ni23'] = ((M['I_2.2'] == 0) & (M['I_2.3'] == 0)).astype(int)
M.to_csv(f'{OUT}/matriz_nota_presencia.csv')

std_w = M.medio.value_counts(normalize=True)          # distribución estándar de medios (todas las notas codificadas)
std_wp = M.periodo.value_counts(normalize=True)       # distribución estándar de períodos

def std_rate_by_period(col):
    """tasa cruda y estandarizada por composición de medios, por período"""
    out = {}
    for p in PER_ORDER:
        d = M[M.periodo == p]
        raw = d[col].mean() * 100
        s = 0.0; wsum = 0.0
        for m, w in std_w.items():
            dm = d[d.medio == m]
            if len(dm) >= 5:
                s += w * dm[col].mean(); wsum += w
        out[p] = (round(raw, 1), round(100 * s / wsum, 1) if wsum else np.nan, len(d))
    return out

def chi_v(col):
    ct = pd.crosstab(M.periodo, M[col])
    if ct.shape[1] < 2:
        return np.nan, np.nan
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    n = ct.values.sum(); k = min(ct.shape) - 1
    return p, np.sqrt(chi2 / (n * k))

def logit_period(col):
    """OR por período (ref P1) ajustado por medio"""
    d = M[[col, 'periodo', 'medio']].copy()
    d['y'] = d[col]
    if d.y.sum() < 20 or d.y.sum() > len(d) - 20:
        return {}
    try:
        mdl = smf.logit('y ~ C(periodo, Treatment("P1_2019-2021")) + C(medio, Treatment("La Tercera"))', data=d).fit(disp=0, maxiter=200)
    except Exception as e:
        return {}
    res = {}
    for p in PER_ORDER[1:]:
        k = f'C(periodo, Treatment("P1_2019-2021"))[T.{p}]'
        if k in mdl.params:
            ci = mdl.conf_int().loc[k]
            res[p] = (round(float(np.exp(mdl.params[k])), 2), round(float(np.exp(ci[0])), 2), round(float(np.exp(ci[1])), 2), float(mdl.pvalues[k]))
    return res

traj_cols = [('I_' + i, 'Indicador ' + i) for i in inds] + \
            [('C_' + c, c + ' ' + NOMBRE.get(c, '')) for c in cods if c in ['1.1.CORP', '1.1.EST', '1.1.CIE', '1.1.DIF', '1.2.ECO', '1.2.GEO', '2.1.HER', '2.1.INN', '2.1.AGE', '2.1.REV', '2.1.MER', '2.1.LIM',
                                                                           '2.2.ECO', '2.2.LAB', '2.2.EDU', '2.2.SAL', '2.3.EMP', '2.3.DEM', '2.3.PRI', '2.3.SEG', '2.3.DES', '2.3.CUL', '2.3.HUM', '2.3.SAL',
                                                                           '2.4.USO', '2.4.REG', '2.5.HYP', '2.5.ALA', '2.5.AMB', '3.1.CON', '3.1.RUP', '3.1.INC', '3.2.INE', '3.2.DEC',
                                                                           '3.3.ADO', '3.3.ADA', '3.3.REG', '3.3.GOB', '3.3.CON', '3.3.PRO', '3.3.LIB', '3.4.EST', '3.4.EMP', '3.4.ACA', '3.4.INT', '3.4.SOC', '3.4.IND', '3.5.REZ']] + \
            [('I_33_regcon', '3.3 regulación y control (REG, GOB, CON, PRO)'), ('I_33_adop', '3.3 adopción y adaptación (ADO, ADA)'), ('I_22y23', 'Oportunidad y riesgo en la misma nota'), ('I_22solo', 'Solo oportunidad'), ('I_23solo', 'Solo riesgo'), ('I_ni22ni23', 'Ni oportunidad ni riesgo')]
traj_rows = []; logit_rows = []
for col, label in traj_cols:
    r = std_rate_by_period(col)
    p, v = chi_v(col)
    row = dict(variable=col, etiqueta=label, notas_total=int(M[col].sum()), pct_total=round(M[col].mean() * 100, 1))
    for pp in PER_ORDER:
        row[pp + '_crudo'] = r[pp][0]; row[pp + '_estand'] = r[pp][1]
    row['dif_P5_P1_estand'] = round(r['P5_2025-2026'][1] - r['P1_2019-2021'][1], 1) if not np.isnan(r['P1_2019-2021'][1]) else np.nan
    row['p_chi2'] = p; row['cramer_v'] = round(v, 3) if not np.isnan(v) else np.nan
    traj_rows.append(row)
    lr = logit_period(col)
    if lr:
        lrow = dict(variable=col, etiqueta=label)
        for pp, (o, lo, hi, pv) in lr.items():
            lrow[pp + '_OR'] = o; lrow[pp + '_IC'] = f'{lo}–{hi}'; lrow[pp + '_p'] = pv
        logit_rows.append(lrow)
traj = pd.DataFrame(traj_rows); traj.to_csv(f'{OUT}/T5_trayectorias_periodo.csv', index=False)
logit = pd.DataFrame(logit_rows); logit.to_csv(f'{OUT}/T5b_logit_periodo_ajustado_medio.csv', index=False)
# por año (crudo) para figuras
yr_cols = ['I_2.2', 'I_2.3', 'I_22y23', 'I_2.5', 'I_33_regcon', 'I_33_adop', 'C_2.1.INN', 'C_2.1.LIM', 'C_2.1.AGE', 'C_2.1.HER', 'C_2.1.MER', 'I_1.1', 'I_3.3', 'I_3.1', 'C_3.5.REZ']
ty = M.groupby('anio')[yr_cols].mean().mul(100).round(1); ty['n'] = M.groupby('anio').size()
ty.to_csv(f'{OUT}/T5c_indicadores_por_anio.csv')

# ---------------------------------------------------------------- 5. perfiles por medio (estandarizados por período)
def std_rate_by_medio(col):
    out = {}
    for m in MED_ORDER:
        d = M[M.medio == m]
        raw = d[col].mean() * 100
        s = 0.0; wsum = 0.0
        for p, w in std_wp.items():
            dp = d[d.periodo == p]
            if len(dp) >= 5:
                s += w * dp[col].mean(); wsum += w
        out[m] = (round(raw, 1), round(100 * s / wsum, 1) if wsum else np.nan, len(d))
    return out
med_rows = []
for col, label in traj_cols:
    r = std_rate_by_medio(col)
    row = dict(variable=col, etiqueta=label)
    for m in MED_ORDER:
        row[m + '_crudo'] = r[m][0]; row[m + '_estand'] = r[m][1]
    ct = pd.crosstab(M.medio, M[col])
    if ct.shape[1] == 2:
        chi2, p, dof, _ = stats.chi2_contingency(ct); row['p_chi2'] = p; row['cramer_v'] = round(np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1))), 3)
    med_rows.append(row)
pd.DataFrame(med_rows).to_csv(f'{OUT}/T6_perfiles_por_medio.csv', index=False)

# ---------------------------------------------------------------- 6. c1, modificadores, densidad
t7 = pd.crosstab(notes.periodo, notes.c1).reindex(index=PER_ORDER); t7['pct_central'] = (t7.central / t7.sum(1) * 100).round(1)
t7.to_csv(f'{OUT}/T7_centralidad_periodo.csv')
dens = notes.groupby('periodo').n_cod.agg(['mean', 'median']).reindex(PER_ORDER).round(2); dens.to_csv(f'{OUT}/T7b_codigos_por_nota_periodo.csv')
mods = []
for r in sub.itertuples():
    try:
        d = json.loads(r.mod) if r.mod else {}
    except Exception:
        d = {}
    for k, v in d.items():
        mods.append(dict(cod=r.cod, ind=r.ind, periodo=r.periodo, medio=r.medio, mod=k, valor=str(v)))
mods = pd.DataFrame(mods)
mods.to_csv(f'{OUT}/modificadores_largo.csv', index=False)
msum = mods.groupby(['mod', 'valor']).size().sort_values(ascending=False)
msum.to_csv(f'{OUT}/T8_modificadores_frecuencia.csv')
# escala en 1.1 por período y resp en 2.3 por período
esc = mods[(mods['mod'] == 'escala') & (mods.ind == '1.1')]
pd.crosstab(esc.periodo, esc.valor).reindex(index=PER_ORDER).to_csv(f'{OUT}/T8b_escala_11_periodo.csv')
pd.crosstab(esc.cod, esc.valor).to_csv(f'{OUT}/T8c_escala_11_codigo.csv')
resp = mods[(mods['mod'] == 'resp') & (mods.ind == '2.3')]
pd.crosstab(resp.periodo, resp.valor).reindex(index=PER_ORDER).to_csv(f'{OUT}/T8d_resp_23_periodo.csv')
g = mods[(mods['mod'] == 'g') & (mods.ind == '2.3')]
pd.crosstab(g.periodo, g.valor).reindex(index=PER_ORDER).to_csv(f'{OUT}/T8e_intensidad_23_periodo.csv')

# ---------------------------------------------------------------- 7. resumen json
summary = dict(corpus=len(corpus), corpus_por_medio=corpus.medio.value_counts().to_dict(), corpus_por_periodo=corpus.periodo.value_counts().reindex(PER_ORDER).to_dict(),
               notas_codificadas=N, entradas=len(sub), notas_por_periodo=notes.periodo.value_counts().reindex(PER_ORDER).to_dict(), notas_por_medio=notes.medio.value_counts().reindex(MED_ORDER).to_dict(),
               c1=notes.c1.value_counts().to_dict(), voz=t4.entradas.to_dict(), v=sub.v.value_counts().to_dict(), dims=t2d.notas.to_dict(), inds=t2i.notas.to_dict(),
               std_w=std_w.round(4).to_dict(), palabras_media=round(float(corpus.palabras.mean()), 1), palabras_mediana=float(corpus.palabras.median()))
json.dump(summary, open(f'{OUT}/resumen.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
print(traj[['etiqueta', 'pct_total'] + [p + '_estand' for p in PER_ORDER] + ['dif_P5_P1_estand', 'cramer_v']].to_string())
