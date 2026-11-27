import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R='/mnt/user-data/outputs/resultados'; O='/mnt/user-data/outputs/resultados_v2'
PAL={'BioBioChile':'#2a78d6','CNN Chile':'#eb6834','Cooperativa':'#1baf7a','Emol':'#eda100','La Tercera':'#e87ba4','T13':'#4a3aa7'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
# Figura 1: notas por año y medio (absolutas)
t=pd.read_csv(f'{R}/T1d_corpus_medio_anio.csv').set_index('medio')
years=[int(c) for c in t.columns]
fig,ax=plt.subplots(figsize=(7.2,3.9),dpi=300)
for m in ['Cooperativa','La Tercera','Emol','CNN Chile','BioBioChile','T13']:
    ax.plot(years,t.loc[m].values,marker='o',ms=3.5,lw=1.6,color=PAL[m],label=m)
ax.plot(years,t.loc['Total'].values,marker='s',ms=3.5,lw=2.2,color='#333333',ls='--',label='Total')
for x,y in zip(years,t.loc['Total'].values): ax.annotate(f'{y:,}'.replace(',','.'),(x,y),textcoords='offset points',xytext=((-16,2) if x==2022 else (0,7)),ha='center',fontsize=7.5,color='#333333')
ax.set_xticks(years); ax.set_xticklabels([str(y) if y<2026 else '2026*' for y in years])
ax.set_ylabel('Notas con "inteligencia artificial"'); ax.set_ylim(0,1500)
ax.legend(ncol=4,fontsize=7.5,frameon=False,loc='upper left')
ax.grid(axis='y',lw=0.4,alpha=0.5)
plt.tight_layout(); plt.savefig(f'{O}/figura1_notas_anio_medio.png'); plt.close()
# Figura 2: barras de indicadores
ind=pd.read_csv(f'{R}/T2b_frecuencia_indicadores.csv',dtype={'ind':str})
names={'1.1':'1.1 Agente impulsor','1.2':'1.2 Motor atribuido','1.3':'1.3 Narrativa temporal del origen','2.1':'2.1 Naturaleza atribuida','2.2':'2.2 Oportunidad','2.3':'2.3 Riesgo o amenaza','2.4':'2.4 Condicionalidad','2.5':'2.5 Relativización','2.6':'2.6 Caracterizaciones emergentes','3.1':'3.1 Futuro proyectado','3.2':'3.2 Modalidad del futuro','3.3':'3.3 Acción prescrita','3.4':'3.4 Actor responsable de actuar','3.5':'3.5 Imperativo de adopción'}
DIMC={'1':'#eb6834','2':'#2a78d6','3':'#1baf7a'}
ind=ind.sort_values('pct_notas')
fig,ax=plt.subplots(figsize=(7.2,4.4),dpi=300)
cols=[DIMC[i[0]] for i in ind.ind]
ax.barh([names[i] for i in ind.ind],ind.pct_notas,color=cols,height=0.7)
for y,(p,n) in enumerate(zip(ind.pct_notas,ind.notas)): ax.text(p+0.8,y,f'{p:.1f} % ({n:,})'.replace(',','.'),va='center',fontsize=7.5)
ax.set_xlim(0,80); ax.set_xlabel('Porcentaje de las 3.762 notas con codificación sustantiva')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=DIMC['1'],label='D1 Origen'),Patch(color=DIMC['2'],label='D2 Carácter'),Patch(color=DIMC['3'],label='D3 Horizonte')],loc='lower right',frameon=False,fontsize=8)
ax.grid(axis='x',lw=0.4,alpha=0.5)
plt.tight_layout(); plt.savefig(f'{O}/figura2_indicadores_barras.png'); plt.close()
# Figura 3: trayectorias por año (crudas) de oportunidad, riesgo, prescripción, ambas
y=pd.read_csv(f'{R}/T5c_indicadores_por_anio.csv')
fig,ax=plt.subplots(figsize=(7.2,3.6),dpi=300)
series=[('I_2.2','2.2 Oportunidad','#1baf7a'),('I_2.3','2.3 Riesgo o amenaza','#eb6834'),('I_3.3','3.3 Acción prescrita','#2a78d6'),('I_33_regcon','3.3 Regulación y control','#4a3aa7'),('I_22y23','Oportunidad y riesgo en la misma nota','#eda100')]
for c,l,col in series:
    ax.plot(y.anio,y[c],marker='o',ms=3.5,lw=1.8,color=col,label=l)
ax.set_xticks(y.anio); ax.set_xticklabels([str(a) if a<2026 else '2026*' for a in y.anio])
ax.set_ylabel('% de las notas codificadas del año'); ax.set_ylim(0,70)
for a,n in zip(y.anio,y.n): ax.text(a,1.5,f'n={n}',ha='center',fontsize=6.5,color='#555555')
ax.legend(fontsize=7.5,frameon=False,ncol=2,loc='upper left'); ax.grid(axis='y',lw=0.4,alpha=0.5)
plt.tight_layout(); plt.savefig(f'{O}/figura3_trayectorias_anio.png'); plt.close()
print('ok')
