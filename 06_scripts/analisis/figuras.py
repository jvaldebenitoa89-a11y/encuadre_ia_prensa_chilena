import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

OUT = '/mnt/user-data/outputs/resultados'
C = {'blue': '#2a78d6', 'orange': '#eb6834', 'aqua': '#1baf7a', 'yellow': '#eda100', 'magenta': '#e87ba4', 'violet': '#4a3aa7', 'green': '#008300', 'red': '#e34948'}
INK, INK2, MUTED, GRID, AXIS, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#ffffff'
rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': AXIS, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.axisbelow': True,
                 'figure.facecolor': SURF, 'axes.facecolor': SURF, 'legend.frameon': False})
PER = ['P1_2019-2021', 'P2_2022', 'P3_2023', 'P4_2024', 'P5_2025-2026']
PL = ['2019–2021', '2022', '2023', '2024', '2025–2026']

# ---------------- Figura 1: oportunidad, riesgo, ambas, prescripción por año
ty = pd.read_csv(f'{OUT}/T5c_indicadores_por_anio.csv')
fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=300)
series = [('I_2.2', 'Oportunidad (2.2)', C['blue']), ('I_2.3', 'Riesgo o amenaza (2.3)', C['orange']), ('I_3.3', 'Acción prescrita (3.3)', C['violet']), ('I_22y23', 'Oportunidad y riesgo en la misma nota', C['aqua'])]
for col, lab, color in series:
    ax.plot(ty.anio, ty[col], color=color, lw=2, marker='o', ms=5, label=lab, zorder=3)
    ax.annotate(f'{ty[col].iloc[-1]:.0f} %', (ty.anio.iloc[-1], ty[col].iloc[-1]), xytext=(6, 0), textcoords='offset points', va='center', fontsize=8, color=INK)
ax.set_xticks(ty.anio); ax.set_xticklabels([f'{a}\n(n = {n})' for a, n in zip(ty.anio, ty.n)], fontsize=8)
ax.set_ylim(0, 70); ax.set_ylabel('% de notas con codificación sustantiva')
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f} %'))
ax.grid(axis='x', visible=False)
ax.legend(loc='upper left', fontsize=8, ncol=2)
ax.set_xlim(2018.7, 2026.9)
fig.tight_layout()
fig.savefig(f'{OUT}/figura1_oportunidad_riesgo_prescripcion_anio.png'); plt.close(fig)

# ---------------- Figura 2: voces por período (100 % apiladas)
t4 = pd.read_csv(f'{OUT}/T4b_voz_periodo_pct.csv').set_index('periodo').reindex(PER)
n4 = pd.read_csv(f'{OUT}/T4b_voz_periodo_n.csv').set_index('periodo').reindex(PER).sum(axis=1)
voces = [('P', 'Medio (periodista)', C['blue']), ('FE', 'Fuente experta', C['orange']), ('FC', 'Fuente corporativa', C['aqua']), ('FG', 'Gobierno y política', C['yellow']), ('FS', 'Sociedad civil', C['magenta']), ('FI', 'Organismos internacionales', C['violet'])]
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=300)
left = np.zeros(len(PER))
for code, lab, color in voces:
    vals = t4[code].values
    ax.barh(range(len(PER)), vals, left=left, color=color, label=lab, height=0.62, edgecolor=SURF, linewidth=1.5)
    for i, (v, l) in enumerate(zip(vals, left)):
        if v >= 5:
            ax.text(l + v / 2, i, f'{v:.0f}', ha='center', va='center', fontsize=7.5, color='white' if code in ('P', 'FE', 'FC', 'FI', 'FG') else INK)
    left = left + vals
ax.set_yticks(range(len(PER))); ax.set_yticklabels([f'{p}\n(n = {int(n):,})'.replace(',', '.') for p, n in zip(PL, n4)], fontsize=8)
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel('% de las entradas codificadas del período')
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f} %'))
ax.grid(axis='y', visible=False)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=3, fontsize=8)
fig.tight_layout()
fig.savefig(f'{OUT}/figura2_voces_periodo.png'); plt.close(fig)

# ---------------- Figura 3: trayectorias de ocho códigos (estandarizadas por medio)
tr = pd.read_csv(f'{OUT}/T5_trayectorias_periodo.csv').set_index('variable')
panels = [('C_1.1.CIE', '1.1.CIE Comunidad científica\ncomo agente impulsor'), ('C_2.2.SAL', '2.2.SAL Oportunidad\nen salud y ciencia'), ('C_2.1.MER', '2.1.MER IA como\nproducto o negocio'), ('C_2.3.SEG', '2.3.SEG Riesgo\npara la seguridad'),
          ('C_3.3.CON', '3.3.CON Controlar\no limitar'), ('C_3.3.REG', '3.3.REG Regular\n'), ('I_2.5', '2.5 Relativización\n(hype, alarmismo)'), ('C_3.4.EMP', '3.4.EMP Empresas como\nresponsables de actuar')]
fig, axes = plt.subplots(2, 4, figsize=(9.6, 5.0), dpi=300, sharex=True)
for ax, (var, title) in zip(axes.ravel(), panels):
    est = [tr.loc[var, p + '_estand'] for p in PER]; raw = [tr.loc[var, p + '_crudo'] for p in PER]
    ax.plot(range(5), raw, color=MUTED, lw=1.2, ls='--', marker='o', ms=3.5, label='cruda')
    ax.plot(range(5), est, color=C['blue'], lw=2, marker='o', ms=5, label='estandarizada por medio')
    for i, v in enumerate(est):
        if i in (0, 4):
            ax.annotate(f'{v:.0f} %', (i, v), xytext=(0, 6), textcoords='offset points', ha='center', fontsize=7.5, color=INK)
    ax.set_title(title, fontsize=8, loc='left', color=INK)
    ax.set_xticks(range(5)); ax.set_xticklabels(['19–21', '22', '23', '24', '25–26'], fontsize=7.5)
    ymax = max(max(est), max(raw)) * 1.35
    ax.set_ylim(0, ymax); ax.grid(axis='x', visible=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f}'))
    ax.tick_params(axis='y', labelsize=7.5)
axes[0, 0].legend(loc='upper right', fontsize=7)
fig.text(0.005, 0.5, '% de notas con codificación sustantiva', va='center', rotation=90, fontsize=8, color=INK2)
fig.tight_layout(rect=(0.015, 0, 1, 1))
fig.savefig(f'{OUT}/figura3_trayectorias_codigos.png'); plt.close(fig)

# ---------------- Figura 4: valoración positiva entre entradas polares de 2.1 por voz y por período
sub = pd.read_csv('/mnt/user-data/outputs/corregido2/registro_citas_completo.csv', keep_default_na=False, dtype=str)
d = sub[(sub.cod.str.startswith('2.1')) & (sub.v.isin(['+', '-']))]
g = d.groupby(['voz', 'periodo']).v.apply(lambda s: (s == '+').mean() * 100).unstack().reindex(index=['FC', 'P', 'FG', 'FS', 'FE'], columns=PER)
n = d.groupby('voz').size()
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=300)
cols = {'FC': C['aqua'], 'P': C['blue'], 'FG': C['yellow'], 'FS': C['magenta'], 'FE': C['orange']}
labs = {'FC': 'Fuente corporativa', 'P': 'Medio (periodista)', 'FG': 'Gobierno y política', 'FS': 'Sociedad civil', 'FE': 'Fuente experta'}
for v in g.index:
    ax.plot(range(5), g.loc[v].values, color=cols[v], lw=2, marker='o', ms=5, label=f'{labs[v]} (n = {int(n[v])})')
    ax.annotate(f'{g.loc[v].values[-1]:.0f} %', (4, g.loc[v].values[-1]), xytext=(6, 0), textcoords='offset points', va='center', fontsize=8, color=INK)
ax.set_xticks(range(5)); ax.set_xticklabels(PL); ax.set_ylim(30, 100)
ax.set_ylabel('% de valoraciones positivas (códigos 2.1)')
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f} %'))
ax.grid(axis='x', visible=False); ax.set_xlim(-0.2, 4.7)
ax.legend(loc='lower left', fontsize=7.5, ncol=2)
fig.tight_layout(); fig.savefig(f'{OUT}/figura4_valoracion_21_voz_periodo.png'); plt.close(fig)
print('ok')
