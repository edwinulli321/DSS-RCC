# DSS-RCC v15 EXECUTIVE · ANTES / DESPUÉS / REDUCCIÓN · UI MEJORADA
# Sistema de Apoyo a Decisiones para la Gestión Integrada del Riesgo de Contaminación Cruzada
# Streamlit | SIPOC/VSM + Diagnóstico + Pre-FMEA + DMAIC + Ishikawa + Lean + SPC + Validación + Decisiones + PDF

import io
import math
import re
import unicodedata
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
        KeepTogether, HRFlowable
    )
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

# ----------------------------- CONFIG -----------------------------
st.set_page_config(
    page_title="DSS-RCC Executive",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

NAVY = "#07192D"
NAVY2 = "#0B223D"
CARD = "#0E2947"
CYAN = "#20B8F2"
TEAL = "#20D3C2"
GREEN = "#18C77A"
AMBER = "#FFB020"
ORANGE = "#FF7A3D"
RED = "#FF4D5A"
PURPLE = "#8B5CF6"
TEXT = "#F5F8FC"
MUTED = "#A9B8C9"
GRID = "rgba(255,255,255,0.10)"

st.markdown(f"""
<style>
.stApp {{ background: {NAVY}; color:{TEXT}; }}
.block-container {{ padding-top: 1.1rem; padding-bottom: 2.5rem; max-width: 1550px; }}
[data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
.hero {{
 background: linear-gradient(135deg,#0A2440 0%,#0B1E35 55%,#07192D 100%);
 border:1px solid #2D5D86; border-radius:20px; padding:25px 28px; margin-bottom:12px;
 box-shadow:0 12px 35px rgba(0,0,0,.22);
}}
.hero h1 {{margin:0;color:white;font-size:2.05rem;}}
.hero p {{color:#7FD5FF;margin:10px 0 12px 0;font-size:.98rem;}}
.badge {{display:inline-block;border:1px solid {GREEN};color:#4EF2A7;background:rgba(24,199,122,.08);padding:6px 12px;border-radius:999px;font-weight:800;font-size:.78rem;}}
.kpi {{background:linear-gradient(145deg,#102B49,#0B223D);border:1px solid #315B7D;border-radius:16px;padding:17px 18px;min-height:118px;box-shadow:0 7px 22px rgba(0,0,0,.18);}}
.kpi .label {{color:{MUTED};font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;}}
.kpi .value {{color:white;font-size:1.85rem;font-weight:800;margin-top:7px;}}
.kpi .sub {{color:#6FCFFF;font-size:.74rem;margin-top:4px;}}
.section-card {{background:{NAVY2};border:1px solid #284E70;border-radius:16px;padding:16px 18px;margin:8px 0 16px 0;}}
.callout {{background:#0D2B4A;border-left:4px solid {CYAN};border-radius:10px;padding:12px 14px;margin:10px 0;color:#EAF6FF;}}
.warnbox {{background:rgba(255,176,32,.11);border-left:4px solid {AMBER};border-radius:10px;padding:12px 14px;color:#FFE0A1;}}
.goodbox {{background:rgba(24,199,122,.11);border-left:4px solid {GREEN};border-radius:10px;padding:12px 14px;color:#A7F3D0;}}
.redbox {{background:rgba(255,77,90,.10);border-left:4px solid {RED};border-radius:10px;padding:12px 14px;color:#FFD1D5;}}
.smallnote {{color:{MUTED};font-size:.78rem;}}
.flowbox {{background:#0D2743;border:1px solid #3C6688;border-radius:12px;padding:14px;text-align:center;min-height:88px;}}
.flowtitle {{font-weight:800;color:white;font-size:.9rem;}}
.flowsub {{color:#9EDCFF;font-size:.72rem;margin-top:6px;}}
.footer {{color:#7E93A9;font-size:.72rem;margin-top:24px;}}
div[data-testid="stMetric"] {{background:{CARD};border:1px solid #315B7D;padding:14px;border-radius:14px;}}
.stTabs [data-baseweb="tab-list"] {{gap:4px; flex-wrap:wrap;}}
.stTabs [data-baseweb="tab"] {{background:#0B223D;border-radius:8px 8px 0 0;padding:8px 12px;color:#B8C8D8;}}
.stTabs [aria-selected="true"] {{color:white!important;border-bottom:3px solid {CYAN}!important;}}
/* v15: legibilidad global */
.stApp, .stApp p, .stApp label, .stApp span {{ color:{TEXT}; }}
h1,h2,h3,h4 {{color:#FFFFFF!important; font-weight:800!important;}}
[data-testid="stWidgetLabel"] p {{color:#EAF3FC!important;font-size:.94rem!important;font-weight:750!important;}}
[data-baseweb="select"] > div {{background:#F7FAFC!important;border:2px solid #7DB5DB!important;border-radius:10px!important;min-height:48px!important;}}
[data-baseweb="select"] span, [data-baseweb="select"] input {{color:#10233A!important;font-weight:700!important;font-size:.95rem!important;}}
[data-baseweb="popover"] {{color:#10233A!important;}}
[data-baseweb="menu"] {{background:#FFFFFF!important;}}
[data-baseweb="menu"] * {{color:#10233A!important;}}
[data-testid="stFileUploader"] {{background:#0C2743;border:1px solid #3E6C91;border-radius:14px;padding:10px;}}
[data-testid="stFileUploader"] small {{color:#C8D8E7!important;}}
[data-testid="stButton"] button {{min-height:46px;font-weight:800!important;font-size:.92rem!important;}}
.kpi {{min-height:142px!important;padding:20px 20px!important;border:2px solid #3E6C91!important;}}
.kpi .label {{color:#D7E5F2!important;font-size:.86rem!important;font-weight:800!important;}}
.kpi .value {{color:#FFFFFF!important;font-size:2.35rem!important;font-weight:900!important;line-height:1.05!important;text-shadow:0 2px 8px rgba(0,0,0,.3);}}
.kpi .sub {{color:#9EDCFF!important;font-size:.82rem!important;font-weight:650!important;}}
[data-testid="stDataFrame"] {{border:1px solid #4B7292;border-radius:10px;overflow:hidden;}}
</style>
""", unsafe_allow_html=True)

# ----------------------------- HELPERS -----------------------------
def norm(s):
    s = str(s).strip()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

ALIASES = {
    'fecha':['fecha','date'], 'producto':['producto','product'], 'lote':['lote','lot'], 'proceso':['proceso','process'],
    'inspeccionadas':['inspeccionadas','inspeccionados','unidades_inspeccionadas','cantidad_inspeccionada'],
    'no_conformes':['no_conformes','no_conforme','nc','unidades_no_conformes'],
    'retrabajo':['retrabajo','retrabajos','rework'],
    'defecto_sellado':['defecto_sellado','defectos_sellado','sellado','defecto_de_sellado'],
    'incid_higiene':['incid_higiene','incidencia_higiene','incidencias_higiene'],
    'incid_limpieza':['incid_limpieza','incidencia_limpieza','incidencias_limpieza'],
    'incid_manipulacion':['incid_manipulacion','incidencia_manipulacion','incidencias_manipulacion'],
    'temperatura_c':['temperatura_c','temperatura','temp_c'],
    'resultado_laboratorio':['resultado_laboratorio','laboratorio','resultado_lab'],
    'tiempo_ciclo_min':['tiempo_ciclo_min','tiempo_ciclo','cycle_time_min'],
    'tiempo_espera_min':['tiempo_espera_min','tiempo_espera','wait_time_min'],
    'tiempo_va_min':['tiempo_va_min','tiempo_va','value_added_min'],
    'periodo':['periodo','period','etapa'],
    'lsl':['lsl','limite_inferior_especificacion'], 'usl':['usl','limite_superior_especificacion'],
}

def canonicalize(df):
    cols = {norm(c): c for c in df.columns}
    ren = {}
    for target, aliases in ALIASES.items():
        for a in aliases:
            if norm(a) in cols:
                ren[cols[norm(a)]] = target
                break
    return df.rename(columns=ren)

def load_excel(upload):
    xls = pd.ExcelFile(upload)
    preferred = None
    for s in xls.sheet_names:
        if norm(s) in ('datos','data','operaciones','operacional'):
            preferred = s; break
    return pd.read_excel(upload, sheet_name=preferred or xls.sheet_names[0])

def clean(df):
    d = canonicalize(df.copy())
    if 'fecha' in d: d['fecha'] = pd.to_datetime(d['fecha'], errors='coerce')
    nums = ['inspeccionadas','no_conformes','retrabajo','defecto_sellado','incid_higiene','incid_limpieza','incid_manipulacion',
            'temperatura_c','tiempo_ciclo_min','tiempo_espera_min','tiempo_va_min','lsl','usl']
    for c in nums:
        if c in d: d[c] = pd.to_numeric(d[c], errors='coerce')
    for c in ['producto','lote','proceso','resultado_laboratorio','periodo']:
        if c in d: d[c] = d[c].fillna('No especificado').astype(str).str.strip()
    return d

def validate(d):
    req = ['fecha','producto','lote','proceso','inspeccionadas','no_conformes']
    missing = [x for x in req if x not in d.columns]
    issues=[]
    if missing: return missing, issues
    if (d['inspeccionadas'].fillna(0)<0).any() or (d['no_conformes'].fillna(0)<0).any(): issues.append('Existen cantidades negativas.')
    if (d['no_conformes'].fillna(0)>d['inspeccionadas'].fillna(0)).any(): issues.append('Hay registros con No conformes > Inspeccionadas.')
    if 'retrabajo' in d and (d['retrabajo'].fillna(0)>d['inspeccionadas'].fillna(0)).any(): issues.append('Hay Retrabajo > Inspeccionadas.')
    return missing, issues

def pct(a,b): return (100*a/b) if b and not pd.isna(b) else 0.0

def fmt_int(v):
    try: return f"{int(round(v)):,}"
    except: return "0"

def filter_data(d, p='Todos', l='Todos', pr='Todos'):
    f=d.copy()
    if p!='Todos': f=f[f.producto==p]
    if l!='Todos': f=f[f.lote==l]
    if pr!='Todos': f=f[f.proceso==pr]
    return f

def filters(d, key):
    c1,c2,c3=st.columns(3)
    prods=['Todos']+sorted(d.producto.dropna().astype(str).unique().tolist())
    p=c1.selectbox('Producto',prods,key=f'p_{key}')
    temp=d if p=='Todos' else d[d.producto==p]
    lots=['Todos']+sorted(temp.lote.dropna().astype(str).unique().tolist())
    l=c2.selectbox('Lote',lots,key=f'l_{key}')
    temp2=temp if l=='Todos' else temp[temp.lote==l]
    procs=['Todos']+sorted(temp2.proceso.dropna().astype(str).unique().tolist())
    pr=c3.selectbox('Proceso',procs,key=f'pr_{key}')
    return filter_data(d,p,l,pr)

def process_summary(f):
    if f.empty: return pd.DataFrame()
    g=f.groupby('proceso',as_index=False).agg(Inspeccionadas=('inspeccionadas','sum'),No_conformes=('no_conformes','sum'))
    g['Porcentaje_NC']=np.where(g.Inspeccionadas>0,100*g.No_conformes/g.Inspeccionadas,0)
    return g.sort_values('Porcentaje_NC',ascending=False)

def signals(f):
    mapping=[
        ('Retrabajo','retrabajo','Variabilidad del método, defecto previo o condición operacional por verificar','Eliminar causa recurrente, estandarizar método y verificar reducción antes/después.'),
        ('Defectos de sellado','defecto_sellado','Condición de sellado, ajuste, material o método por verificar','Verificar sellado; estandarizar parámetros y mantenimiento si la causa se confirma.'),
        ('Incidencias de manipulación','incid_manipulacion','Manipulación o secuencia operacional por verificar','Reducir manipulación innecesaria, estandarizar secuencia y capacitar.'),
        ('Incidencias de higiene','incid_higiene','Práctica de higiene por verificar','Reforzar higiene, capacitación y verificación documentada.'),
        ('Incidencias de limpieza','incid_limpieza','Limpieza o cambio de condición por verificar','Estandarizar limpieza y verificar eficacia antes de liberar el proceso.'),
    ]
    rows=[]
    total=0
    for name,col,cause,action in mapping:
        if col in f:
            q=float(f[col].fillna(0).sum()); total+=q
            rows.append([name,q,cause,action])
    if not rows:
        return pd.DataFrame(columns=['Señal','Cantidad','Frecuencia_relativa_%','Causa potencial a verificar','Acción sugerida'])
    for r in rows: r.insert(2,pct(r[1],total))
    out=pd.DataFrame(rows,columns=['Señal','Cantidad','Frecuencia_relativa_%','Causa potencial a verificar','Acción sugerida'])
    out=out[out.Cantidad>0].sort_values('Cantidad',ascending=False).reset_index(drop=True)
    out.insert(0,'Prioridad',range(1,len(out)+1))
    return out

def critical(f):
    g=process_summary(f)
    return None if g.empty else g.iloc[0]

def lab_counts(f):
    if 'resultado_laboratorio' not in f: return pd.DataFrame()
    x=f['resultado_laboratorio'].fillna('No evaluado').astype(str).str.strip().replace('', 'No evaluado')
    return x.value_counts().rename_axis('Resultado').reset_index(name='Cantidad')

def plot_layout(fig, height=420, title=None):
    fig.update_layout(
        height=height, paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
        font=dict(color='#F4F8FC', size=14),
        margin=dict(l=55,r=35,t=70 if title else 35,b=55),
        title=dict(text=title, font=dict(color='#FFFFFF',size=19)) if title else None,
        legend=dict(bgcolor='rgba(7,25,45,.88)',bordercolor='#52789A',borderwidth=1,font=dict(color='#FFFFFF',size=13),title_font=dict(color='#FFFFFF',size=13)),
        hoverlabel=dict(bgcolor='#102B49',font_color='white',font_size=13),
    )
    fig.update_xaxes(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color='#E7F0F8',size=13),title_font=dict(color='#FFFFFF',size=14))
    fig.update_yaxes(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color='#E7F0F8',size=13),title_font=dict(color='#FFFFFF',size=14))
    return fig

def kpi(label,value,sub=''):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>',unsafe_allow_html=True)

def footer():
    st.markdown('<div class="footer">DSS-RCC v15 EXECUTIVE · Prototipo de investigación · Gestión integrada, explicable, trazable y con validación humana</div>',unsafe_allow_html=True)


def reduction_pct(before, after):
    """Reducción relativa %. Positivo=reducción; negativo=incremento. N/D si base=0."""
    try:
        b=float(before); a=float(after)
        if not np.isfinite(b) or not np.isfinite(a) or b==0: return np.nan
        return 100.0*(b-a)/b
    except Exception:
        return np.nan

def compare_process(before, after):
    gb=process_summary(before).rename(columns={'Porcentaje_NC':'Antes'})[['proceso','Antes']] if before is not None and not before.empty else pd.DataFrame(columns=['proceso','Antes'])
    ga=process_summary(after).rename(columns={'Porcentaje_NC':'Después'})[['proceso','Después']] if after is not None and not after.empty else pd.DataFrame(columns=['proceso','Después'])
    c=pd.merge(gb,ga,on='proceso',how='outer')
    if 'Antes' not in c:c['Antes']=np.nan
    if 'Después' not in c:c['Después']=np.nan
    c['Reducción_%']=c.apply(lambda r: reduction_pct(r['Antes'],r['Después']),axis=1)
    return c

def compare_signals(before, after):
    sb=signals(before)[['Señal','Cantidad']].rename(columns={'Cantidad':'Antes'}) if before is not None and not before.empty and not signals(before).empty else pd.DataFrame(columns=['Señal','Antes'])
    sa=signals(after)[['Señal','Cantidad']].rename(columns={'Cantidad':'Después'}) if after is not None and not after.empty and not signals(after).empty else pd.DataFrame(columns=['Señal','Después'])
    c=pd.merge(sb,sa,on='Señal',how='outer').fillna(0)
    c['Reducción_%']=c.apply(lambda r: reduction_pct(r['Antes'],r['Después']),axis=1)
    return c

def metric_pack(q):
    I=float(q.inspeccionadas.sum()) if q is not None and not q.empty else 0
    N=float(q.no_conformes.sum()) if q is not None and not q.empty else 0
    R=float(q.retrabajo.sum()) if q is not None and not q.empty and 'retrabajo' in q else 0
    S=float(q.defecto_sellado.sum()) if q is not None and not q.empty and 'defecto_sellado' in q else 0
    H=float(q.incid_higiene.sum()) if q is not None and not q.empty and 'incid_higiene' in q else 0
    L=float(q.incid_limpieza.sum()) if q is not None and not q.empty and 'incid_limpieza' in q else 0
    M=float(q.incid_manipulacion.sum()) if q is not None and not q.empty and 'incid_manipulacion' in q else 0
    return {'Registros':0 if q is None else len(q),'Inspeccionadas':I,'% NC':pct(N,I),'% Retrabajo':pct(R,I),'Defecto sellado':S,'Incid. higiene':H,'Incid. limpieza':L,'Incid. manipulación':M}

def comparison_long(before, after):
    b=metric_pack(before); a=metric_pack(after)
    rows=[]
    for k in b:
        rows.append({'Indicador':k,'Antes':b[k],'Después':a[k],'Reducción_%':reduction_pct(b[k],a[k])})
    return pd.DataFrame(rows)

def filters_pair(before, after, key):
    pool=pd.concat([before, after],ignore_index=True) if after is not None and not after.empty else before.copy()
    st.markdown('<div style="font-weight:850;color:#FFFFFF;font-size:1.02rem;margin:.15rem 0 .35rem 0">🔎 Filtros de análisis</div>',unsafe_allow_html=True)
    st.caption('Los filtros se aplican simultáneamente a ANTES y DESPUÉS para mantener una comparación equivalente.')
    c1,c2,c3=st.columns(3)
    prods=['Todos']+sorted(pool.producto.dropna().astype(str).unique().tolist())
    p=c1.selectbox('Producto',prods,key=f'p_{key}')
    temp=pool if p=='Todos' else pool[pool.producto==p]
    lots=['Todos']+sorted(temp.lote.dropna().astype(str).unique().tolist())
    l=c2.selectbox('Lote',lots,key=f'l_{key}')
    temp2=temp if l=='Todos' else temp[temp.lote==l]
    procs=['Todos']+sorted(temp2.proceso.dropna().astype(str).unique().tolist())
    pr=c3.selectbox('Proceso',procs,key=f'pr_{key}')
    fb=filter_data(before,p,l,pr)
    fa=filter_data(after,p,l,pr) if after is not None else None
    return fb,fa

# ----------------------------- VISUAL DIAGRAMS -----------------------------
def sipoc_figure(f):
    fig=go.Figure()
    labels=[('PROVEEDOR','Proveedor aprobado',GREEN),('ENTRADA','Materia prima / envases / registros',CYAN),('PROCESO','Recepción → Selección → Empaque → Encajado → Paletizado',PURPLE),('SALIDA','Producto acondicionado / registros',AMBER),('CLIENTE','Cliente / exportación',RED)]
    xs=[0.10,0.30,0.52,0.74,0.92]
    widths=[.14,.16,.23,.16,.14]
    for i,(title,sub,color) in enumerate(labels):
        x=xs[i]; w=widths[i]
        fig.add_shape(type='rect',x0=x-w/2,x1=x+w/2,y0=.36,y1=.68,line=dict(color=color,width=2),fillcolor='rgba(12,38,65,.85)')
        fig.add_annotation(x=x,y=.57,text=f'<b>{title}</b>',showarrow=False,font=dict(color=color,size=12))
        fig.add_annotation(x=x,y=.45,text=sub,showarrow=False,font=dict(color='white',size=9))
        if i<len(labels)-1:
            fig.add_annotation(x=(xs[i]+xs[i+1])/2,y=.52,text='➜',showarrow=False,font=dict(color='#9EDCFF',size=22))
    fig.update_xaxes(visible=False,range=[0,1]); fig.update_yaxes(visible=False,range=[0,1])
    return plot_layout(fig,270)

def process_flow_figure(f):
    g=process_summary(f)
    if g.empty:return go.Figure()
    order=['Recepción','Seleccion','Selección','Clasificación','Empaque','Encajado','Paletizado','Despacho']
    existing=g.proceso.astype(str).tolist()
    ordered=[]
    for o in order:
        for p in existing:
            if norm(p)==norm(o) and p not in ordered: ordered.append(p)
    ordered += [p for p in existing if p not in ordered]
    g=g.set_index('proceso').loc[ordered].reset_index()
    fig=go.Figure(); n=len(g); xs=np.linspace(.08,.92,max(n,2))[:n]
    vals=g.Porcentaje_NC.tolist(); vmin=min(vals) if vals else 0; vmax=max(vals) if vals else 1
    def col(v):
        if vmax==vmin:return CYAN
        t=(v-vmin)/(vmax-vmin)
        return GREEN if t<.34 else AMBER if t<.67 else RED
    for i,row in g.iterrows():
        x=xs[i]; c=col(row.Porcentaje_NC)
        fig.add_shape(type='rect',x0=x-.07,x1=x+.07,y0=.35,y1=.68,line=dict(color=c,width=2),fillcolor='rgba(12,38,65,.9)')
        fig.add_annotation(x=x,y=.56,text=f'<b>{row.proceso}</b>',showarrow=False,font=dict(color='white',size=11))
        fig.add_annotation(x=x,y=.44,text=f'{row.Porcentaje_NC:.2f}% NC',showarrow=False,font=dict(color=c,size=10))
        if i<n-1: fig.add_annotation(x=(xs[i]+xs[i+1])/2,y=.515,text='➜',showarrow=False,font=dict(color=CYAN,size=20))
    fig.update_xaxes(visible=False,range=[0,1]);fig.update_yaxes(visible=False,range=[0,1])
    return plot_layout(fig,280)

def dmaic_figure(f):
    crit=critical(f); sig=signals(f)
    cp='Proceso observado' if crit is None else str(crit.proceso)
    nc=0 if crit is None else float(crit.Porcentaje_NC)
    s='Señal a investigar' if sig.empty else str(sig.iloc[0].Señal)
    items=[('DEFINIR',f'Priorizar {cp}',CYAN),('MEDIR',f'{fmt_int(f.inspeccionadas.sum())} inspeccionadas · {pct(f.no_conformes.sum(),f.inspeccionadas.sum()):.2f}% NC',TEAL),('ANALIZAR',f'Investigar: {s}',PURPLE),('MEJORAR','Acción sobre causa confirmada',AMBER),('CONTROLAR','SPC + seguimiento + reevaluación',RED)]
    fig=go.Figure(); xs=np.linspace(.1,.9,5)
    for x,(a,b,c) in zip(xs,items):
        fig.add_shape(type='rect',x0=x-.085,x1=x+.085,y0=.33,y1=.70,line=dict(color=c,width=2),fillcolor='rgba(12,38,65,.9)')
        fig.add_annotation(x=x,y=.58,text=f'<b>{a}</b>',showarrow=False,font=dict(color=c,size=12))
        fig.add_annotation(x=x,y=.45,text=b,showarrow=False,font=dict(color='white',size=9))
    fig.update_xaxes(visible=False,range=[0,1]);fig.update_yaxes(visible=False,range=[0,1])
    return plot_layout(fig,280)

def ishikawa_figure(f):
    """Ishikawa 6M fijo y legible. Sin zoom, paneo ni desplazamiento visual."""
    sig = signals(f)
    effect = 'No conformidad / riesgo operacional'
    if not sig.empty:
        effect = f"Señal prioritaria:<br>{sig.iloc[0].Señal}"

    fig = go.Figure()

    # Espina principal y punta de flecha
    fig.add_shape(type='line', x0=0.12, x1=0.80, y0=0.50, y1=0.50,
                  line=dict(color='#D9E7F5', width=4))
    fig.add_annotation(x=0.815, y=0.50, ax=0.775, ay=0.50,
                       xref='x', yref='y', axref='x', ayref='y',
                       text='', showarrow=True,
                       arrowhead=3, arrowsize=1.3, arrowwidth=3,
                       arrowcolor='#D9E7F5')

    # Posiciones fijas: tres ramas superiores y tres inferiores
    branches = [
        ('MANO DE OBRA', 'Capacitación · fatiga<br>prácticas', GREEN, 0.27, 0.82, True),
        ('MÉTODO', 'Estandarización · secuencia<br>manipulación', AMBER, 0.48, 0.82, True),
        ('MAQUINARIA', 'Sellado · mantenimiento<br>condición', RED, 0.69, 0.82, True),
        ('MATERIALES', 'Envases · embalaje<br>contacto', CYAN, 0.27, 0.18, False),
        ('MEDIO AMBIENTE', 'Limpieza · temperatura<br>flujo', PURPLE, 0.48, 0.18, False),
        ('MEDICIÓN', 'Registros · inspección<br>trazabilidad', '#E83E8C', 0.69, 0.18, False),
    ]

    for cat, txt, color, x, y, upper in branches:
        # Unión de cada causa con la espina central
        x_joint = x + 0.075
        fig.add_shape(
            type='line',
            x0=x, y0=(y - 0.075 if upper else y + 0.075),
            x1=x_joint, y1=0.50,
            line=dict(color=color, width=3)
        )
        # Caja de categoría
        fig.add_shape(
            type='rect', x0=x-0.105, x1=x+0.105, y0=y-0.075, y1=y+0.075,
            line=dict(color=color, width=2),
            fillcolor='rgba(11,34,61,0.98)'
        )
        fig.add_annotation(
            x=x, y=y+0.025, text=f'<b>{cat}</b>', showarrow=False,
            font=dict(color=color, size=12), align='center'
        )
        fig.add_annotation(
            x=x, y=y-0.025, text=txt, showarrow=False,
            font=dict(color='#F5F8FC', size=9), align='center'
        )

    # Efecto a la derecha, separado de las ramas
    fig.add_shape(
        type='rect', x0=0.82, x1=0.98, y0=0.40, y1=0.60,
        line=dict(color=RED, width=2.5),
        fillcolor='rgba(255,77,90,0.14)'
    )
    fig.add_annotation(x=0.90, y=0.555, text='<b>EFECTO</b>', showarrow=False,
                       font=dict(color=RED, size=12))
    fig.add_annotation(x=0.90, y=0.475, text=effect, showarrow=False,
                       font=dict(color='white', size=9), align='center')

    # Ejes totalmente fijos para impedir que el diagrama se mueva
    fig.update_xaxes(visible=False, range=[0, 1], fixedrange=True)
    fig.update_yaxes(visible=False, range=[0, 1], fixedrange=True)
    fig.update_layout(
        height=500,
        paper_bgcolor=NAVY2,
        plot_bgcolor=NAVY2,
        margin=dict(l=20, r=20, t=20, b=20),
        dragmode=False,
        hovermode=False,
        showlegend=False,
        uirevision='ishikawa_fijo'
    )
    return fig

def decision_chain_figure(f):
    sig=signals(f); crit=critical(f)
    proc='Proceso' if crit is None else str(crit.proceso)
    signal='Señal' if sig.empty else str(sig.iloc[0].Señal)
    action='Verificar y controlar' if sig.empty else str(sig.iloc[0]['Acción sugerida'])
    nodes=['DETECTAR','PRIORIZAR','EXPLICAR','VALIDAR','ACTUAR','CONTROLAR','REEVALUAR']
    subs=[signal,proc,'Hipótesis 6M','Evidencia','Acción','SPC/KPI','Resultado']
    colors_=[CYAN,ORANGE,PURPLE,TEAL,AMBER,RED,GREEN]
    fig=go.Figure(); xs=np.linspace(.07,.93,7)
    for i,(x,n,s,c) in enumerate(zip(xs,nodes,subs,colors_)):
        fig.add_shape(type='rect',x0=x-.055,x1=x+.055,y0=.38,y1=.67,line=dict(color=c,width=2),fillcolor='rgba(12,38,65,.95)')
        fig.add_annotation(x=x,y=.57,text=f'<b>{n}</b>',showarrow=False,font=dict(color=c,size=10))
        fig.add_annotation(x=x,y=.46,text=s,showarrow=False,font=dict(color='white',size=8))
        if i<6: fig.add_annotation(x=(xs[i]+xs[i+1])/2,y=.525,text='➜',showarrow=False,font=dict(color='#9EDCFF',size=18))
    fig.update_xaxes(visible=False,range=[0,1]);fig.update_yaxes(visible=False,range=[0,1])
    return plot_layout(fig,240)

# ----------------------------- PDF -----------------------------
def pdf_report(f, fa=None, responsable=""):
    if not REPORTLAB_OK:return None
    buff=io.BytesIO(); doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=14*mm,bottomMargin=14*mm)
    styles=getSampleStyleSheet()
    title=ParagraphStyle('title',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=18,leading=22,textColor=colors.HexColor('#123A5A'),alignment=TA_CENTER,spaceAfter=10)
    h1=ParagraphStyle('h1',parent=styles['Heading1'],fontName='Helvetica-Bold',fontSize=13,textColor=colors.HexColor('#123A5A'),spaceBefore=8,spaceAfter=6)
    body=ParagraphStyle('body',parent=styles['BodyText'],fontSize=9.2,leading=13,textColor=colors.HexColor('#263746'))
    note=ParagraphStyle('note',parent=body,fontSize=8.2,textColor=colors.HexColor('#5E6D78'))
    story=[]
    story += [Paragraph('REPORTE EJECUTIVO – GESTIÓN INTEGRADA DEL RIESGO DE CONTAMINACIÓN CRUZADA',title),Paragraph('DSS-RCC · Sistema de Apoyo a Decisiones',h1),Paragraph(f'Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}',body),Spacer(1,6)]
    insp=float(f.inspeccionadas.sum()); nc=float(f.no_conformes.sum()); ret=float(f.retrabajo.sum()) if 'retrabajo' in f else 0
    crit=critical(f); sig=signals(f)
    kdata=[['Indicador','Resultado'],['Registros analizados',fmt_int(len(f))],['Unidades inspeccionadas',fmt_int(insp)],['No conformes',f'{fmt_int(nc)} ({pct(nc,insp):.2f}%)'],['Retrabajo',f'{fmt_int(ret)} ({pct(ret,insp):.2f}%)']]
    t=Table(kdata,colWidths=[82*mm,80*mm]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#123A5A')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#AAB7C2')),('FONTSIZE',(0,0),(-1,-1),8.5),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7FA')]),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story += [t,Spacer(1,8),Paragraph('1. Resumen ejecutivo',h1)]
    if crit is not None:
        story.append(Paragraph(f"El proceso con mayor proporción observada de no conformidad es <b>{crit.proceso}</b> ({crit.Porcentaje_NC:.2f}%). Esta priorización identifica dónde concentrar la investigación; no demuestra por sí sola contaminación cruzada ni causalidad.",body))
    if not sig.empty:
        story.append(Paragraph(f"La señal operacional dominante es <b>{sig.iloc[0].Señal}</b>. El DSS la utiliza como evidencia de priorización y propone una hipótesis a verificar antes de cerrar acciones correctivas.",body))
    story += [Paragraph('2. Diagnóstico por proceso',h1)]
    g=process_summary(f)
    pdata=[['Proceso','Inspeccionadas','No conformes','% NC']]+[[r.proceso,fmt_int(r.Inspeccionadas),fmt_int(r.No_conformes),f'{r.Porcentaje_NC:.2f}%'] for _,r in g.iterrows()]
    pt=Table(pdata,colWidths=[55*mm,38*mm,38*mm,28*mm]);pt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2563EB')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B7C2CC')),('FONTSIZE',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8FA')])]))
    story += [pt,Spacer(1,7),Paragraph('3. Señales priorizadas y acciones sugeridas',h1)]
    if sig.empty: story.append(Paragraph('No se encontraron señales operacionales cuantificables en las columnas opcionales disponibles.',body))
    else:
        sdata=[['Prior.','Señal','Cant.','Frecuencia relativa','Acción sugerida']]
        for _,r in sig.head(6).iterrows(): sdata.append([str(r.Prioridad),r.Señal,fmt_int(r.Cantidad),f"{r['Frecuencia_relativa_%']:.1f}%",Paragraph(str(r['Acción sugerida']),note)])
        stbl=Table(sdata,colWidths=[13*mm,37*mm,18*mm,30*mm,67*mm]);stbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0E7490')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#B7C2CC')),('FONTSIZE',(0,0),(-1,-1),7.5),('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.append(stbl)
    story += [PageBreak(),Paragraph('4. Arquitectura metodológica integrada',h1),Paragraph('<b>Datos → SIPOC/VSM → diagnóstico → preevaluación FMEA → DMAIC/Ishikawa → Lean/SPC → decisión → validación → reevaluación.</b>',body),Spacer(1,5)]
    story.append(Paragraph('El DSS integra herramientas de Ingeniería Industrial en una secuencia trazable. Las señales observadas orientan la investigación; las causas raíz, la inocuidad, los criterios FMEA S/O/D y los límites de especificación requieren validación metodológica y/o técnica.',body))
    story += [Paragraph('5. DMAIC ejecutivo',h1)]
    cp='proceso observado' if crit is None else str(crit.proceso); sn='señal prioritaria' if sig.empty else str(sig.iloc[0].Señal)
    dma=[['Fase','Salida automática'],['Definir',f'Priorizar {cp}.'],['Medir',f'{fmt_int(insp)} inspeccionadas; {pct(nc,insp):.2f}% NC.'],['Analizar',f'Investigar {sn} mediante hipótesis 6M y evidencia del proceso.'],['Mejorar','Implementar acción sobre causa confirmada; estandarizar y reducir desperdicio/manipulación cuando corresponda.'],['Controlar','Seguimiento por lote/proceso, SPC cuando aplique y comparación antes/después con diseño válido.']]
    dt=Table(dma,colWidths=[30*mm,135*mm]);dt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#6D28D9')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#B7C2CC')),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story += [dt,Paragraph('6. Ishikawa 6M – hipótesis a verificar',h1)]
    ish=[['6M','Hipótesis'],['Mano de obra','Capacitación, fatiga, prácticas'],['Método','Estandarización, secuencia, manipulación'],['Maquinaria','Sellado, mantenimiento, condición'],['Materiales','Envases, embalaje, contacto'],['Medio ambiente','Limpieza, temperatura, flujo'],['Medición','Registros, inspección, trazabilidad']]
    it=Table(ish,colWidths=[42*mm,123*mm]);it.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#123A5A')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#B7C2CC')),('FONTSIZE',(0,0),(-1,-1),8)]));story.append(it)
    story += [Paragraph('7. Matriz de evidencia, nivel de soporte y decisión',h1)]
    # La matriz separa disponibilidad de evidencia, alcance y uso en la decisión.
    lab_col='resultado_laboratorio' in f
    lab_nc=0
    if lab_col:
        lab_txt=f['resultado_laboratorio'].fillna('').astype(str).str.strip().str.lower()
        lab_nc=int(lab_txt.str.contains('no conforme',regex=False).sum())
    vsm_ok=all(c in f for c in ['tiempo_ciclo_min','tiempo_espera_min','tiempo_va_min'])
    spc_cols=[c for c in ['temperatura_c','tiempo_ciclo_min'] if c in f and pd.to_numeric(f[c],errors='coerce').notna().sum()>=2]
    periodo_ok='periodo' in f and f['periodo'].fillna('').astype(str).str.strip().ne('').any()
    ev=[
        ['Evidencia / herramienta','Estado','Resultado verificable','Uso en la decisión'],
        ['Datos operacionales','DISPONIBLE',f'{len(f)} registros; {fmt_int(insp)} unidades inspeccionadas; {pct(nc,insp):.2f}% NC','Base cuantitativa para priorizar proceso y señales'],
        ['Laboratorio','DISPONIBLE' if lab_col else 'NO DISPONIBLE',f'{lab_nc} resultado(s) No conforme registrado(s)' if lab_col else 'No se incluyó resultado de laboratorio','Complementa la verificación analítica; interpretar según ensayo y criterio aplicable'],
        ['SIPOC / flujo','GENERADO','Secuencia del proceso contextualizada','Ubica etapas, entradas/salidas y puntos donde investigar'],
        ['VSM cuantitativo','DISPONIBLE' if vsm_ok else 'PARCIAL','Tiempos VA, espera y ciclo disponibles' if vsm_ok else 'Faltan una o más columnas de tiempo','Cuantifica flujo y desperdicio solo cuando existen tiempos suficientes'],
        ['FMEA S/O/D','PENDIENTE','Escala S/O/D no validada en el archivo','No calcula NPR hasta contar con criterios de puntuación validados'],
        ['SPC','DISPONIBLE' if spc_cols else 'NO DISPONIBLE',('Variable(s): '+', '.join(spc_cols)) if spc_cols else 'No hay serie continua suficiente','Monitorea estabilidad estadística; límites de control no son límites de especificación'],
        ['Validación antes/después','DISPONIBLE' if periodo_ok else 'PENDIENTE','Periodo Antes/Después identificado' if periodo_ok else 'Falta columna Periodo con Antes/Después','Evalúa cambio observado sin atribuir causalidad automáticamente']
    ]
    # Paragraphs permiten ajuste de texto y evitan que la tabla se desborde.
    evp=[[Paragraph(str(x), note if r>0 else ParagraphStyle('th',parent=note,textColor=colors.white,fontName='Helvetica-Bold',fontSize=7.2,leading=8.5)) for x in row] for r,row in enumerate(ev)]
    et=Table(evp,colWidths=[37*mm,27*mm,54*mm,47*mm],repeatRows=1)
    et.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0F766E')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B7C2CC')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('BACKGROUND',(0,1),(-1,-1),colors.HexColor('#F8FAFC')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F8FAFC'),colors.white])
    ]))
    story += [et,Spacer(1,8),Paragraph('<b>Lectura para la decisión:</b> el DSS distingue entre evidencia disponible, evidencia parcial y elementos pendientes de validación. Una señal operacional permite priorizar la investigación, pero no confirma por sí sola contaminación cruzada ni una causa raíz.',note),Spacer(1,6),Paragraph('<b>Criterio de cierre:</b> la acción correctiva debe aprobarse con revisión del responsable de Calidad/Inocuidad y reevaluarse con datos posteriores a la intervención.',note),Spacer(1,18),HRFlowable(width='70%',thickness=.6,color=colors.grey),Paragraph(f'Responsable de Calidad / Inocuidad: {responsable.strip() if responsable.strip() else "_______________________________"}',body),Paragraph('Fecha de revisión: ____ / ____ / ______',body)]
    # 8. COMPARACIÓN ANTES / DESPUÉS Y DECISIÓN GERENCIAL
    story += [PageBreak(), Paragraph('8. Resultado Antes / Después y decisión gerencial', h1)]
    if fa is not None and not fa.empty:
        mb=metric_pack(f); ma=metric_pack(fa)
        comp_rows=[['Indicador','Antes','Después','Reducción relativa']]
        for indicador in ['% NC','% Retrabajo','Defecto sellado','Incid. higiene','Incid. limpieza','Incid. manipulación']:
            b=float(mb.get(indicador,0) or 0); a=float(ma.get(indicador,0) or 0); rr=reduction_pct(b,a)
            comp_rows.append([indicador,f'{b:.2f}',f'{a:.2f}','N/D' if pd.isna(rr) else f'{rr:.2f}%'])
        ct=Table(comp_rows,colWidths=[48*mm,32*mm,32*mm,48*mm],repeatRows=1)
        ct.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2563EB')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B7C2CC')),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8FA')])]))
        story += [ct,Spacer(1,8)]

        bnc=float(mb.get('% NC',0) or 0); anc=float(ma.get('% NC',0) or 0); rnc=reduction_pct(bnc,anc)
        crit_after=critical(fa); sig_after=signals(fa)
        proc_after='No determinado' if crit_after is None else str(crit_after.proceso)
        proc_after_nc=np.nan if crit_after is None else float(crit_after.Porcentaje_NC)
        signal_after='Sin señal cuantificable' if sig_after.empty else str(sig_after.iloc[0].Señal)
        action_after='Mantener vigilancia de los indicadores y documentar la revisión.' if sig_after.empty else str(sig_after.iloc[0]['Acción sugerida'])

        if pd.isna(rnc):
            estado='EVIDENCIA INSUFICIENTE PARA CALCULAR REDUCCIÓN RELATIVA'
            decision='No cerrar la intervención. Verificar la línea base y recopilar datos comparables antes de aprobar una decisión definitiva.'
        elif rnc >= 50:
            estado='MEJORA IMPORTANTE OBSERVADA'
            decision='Mantener y estandarizar las mejoras implementadas, reforzando el control del proceso crítico residual y verificando que el resultado se sostenga en el periodo de seguimiento.'
        elif rnc > 0:
            estado='MEJORA OBSERVADA, AÚN REQUIERE SEGUIMIENTO'
            decision='Continuar la intervención y reforzar las acciones sobre el proceso y la señal prioritaria hasta demostrar estabilidad y cumplimiento del objetivo definido.'
        elif rnc == 0:
            estado='SIN CAMBIO OBSERVADO'
            decision='Revisar la intervención, volver a la fase Analizar de DMAIC y verificar las hipótesis de causa antes de mantener o modificar las acciones.'
        else:
            estado='DETERIORO DEL INDICADOR'
            decision='Priorizar acción correctiva. Revisar inmediatamente la intervención y las condiciones del proceso, verificar causas y establecer seguimiento reforzado antes del cierre.'

        story += [Paragraph('9. Recomendación automática para la toma de decisiones',h1),
                  Paragraph(f'<b>Estado:</b> {estado}',body),
                  Paragraph(f'<b>Resultado principal:</b> la no conformidad pasó de {bnc:.2f}% a {anc:.2f}%'+(' (reducción relativa no calculable).' if pd.isna(rnc) else f', equivalente a una reducción relativa de {rnc:.2f}%.'),body),
                  Paragraph(f'<b>Proceso crítico residual:</b> {proc_after}'+('' if pd.isna(proc_after_nc) else f' ({proc_after_nc:.2f}% NC).'),body),
                  Paragraph(f'<b>Señal prioritaria después de la intervención:</b> {signal_after}.',body),
                  Paragraph(f'<b>DECISIÓN RECOMENDADA POR EL DSS-RCC:</b> {decision}',body),
                  Paragraph(f'<b>Acción prioritaria sugerida:</b> {action_after}',body)]

        acciones=[['Prioridad','Acción','Responsable sugerido','Indicador de control','Criterio de seguimiento'],
                  ['1',action_after,'Calidad / Inocuidad','% NC y señal prioritaria','Verificar tendencia en el siguiente periodo'],
                  ['2',f'Investigar la causa de {signal_after} mediante evidencia e Ishikawa 6M','Calidad + Operaciones','Evidencia de causa / recurrencia','No cerrar causa raíz sin verificación'],
                  ['3',f'Reforzar control en {proc_after}','Operaciones','% NC por proceso','Comparar con línea base y meta'],
                  ['4','Aplicar SPC cuando exista variable continua y límites válidos','Calidad / Proceso','Puntos fuera de control / estabilidad','Reaccionar ante señales especiales']]
        ap=[[Paragraph(str(x), note if i>0 else ParagraphStyle('th2',parent=note,textColor=colors.white,fontName='Helvetica-Bold',fontSize=7,leading=8)) for x in row] for i,row in enumerate(acciones)]
        at=Table(ap,colWidths=[15*mm,55*mm,32*mm,31*mm,32*mm],repeatRows=1)
        at.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0F766E')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#B7C2CC')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F8FAFC'),colors.white])]))
        story += [Paragraph('10. Plan de acción para ejecución y seguimiento',h1),at,Spacer(1,8),
                  Paragraph('<b>Criterio gerencial:</b> una mejora descriptiva Antes/Después respalda la continuidad o ajuste de la intervención, pero no demuestra por sí sola causalidad. La causa raíz y el cierre de la acción deben ser validados por el responsable de Calidad/Inocuidad.',note),
                  Paragraph('<b>Regla de reevaluación:</b> si el indicador vuelve a aumentar, aparecen nuevas señales críticas o el proceso pierde estabilidad, reabrir la fase Analizar de DMAIC y revisar el plan de mejora.',note)]
    else:
        story += [Paragraph('No se ha ejecutado un conjunto de datos DESPUÉS. El DSS puede priorizar riesgos y proponer acciones con la línea base, pero no debe concluir que existió una mejora hasta contar con datos posteriores comparables.',body),
                  Paragraph('<b>Decisión provisional:</b> ejecutar las acciones priorizadas, definir responsables e indicadores y recopilar el periodo DESPUÉS para evaluar el resultado.',body)]

    story += [Spacer(1,14),HRFlowable(width='70%',thickness=.6,color=colors.grey),
              Paragraph(f'Aprobación / revisión final: {responsable.strip() if responsable.strip() else "_______________________________"}',body),
              Paragraph('Decisión humana final:  ☐ Aprobar  ☐ Ajustar  ☐ Rechazar  ☐ Requiere más evidencia',body),
              Paragraph('Fecha: ____ / ____ / ______',body)]

    doc.build(story);buff.seek(0);return buff.getvalue()

# ----------------------------- HEADER -----------------------------
st.markdown('''<div class="hero"><h1>🛡️ DSS-RCC · Gestión Integrada del Riesgo de Contaminación Cruzada</h1><p>SIPOC/VSM + diagnóstico + FMEA asistido + DMAIC + Ishikawa + Lean/SPC + decisiones trazables + validación + reporte ejecutivo</p><span class="badge">● SISTEMA EJECUTIVO · ANTES / DESPUÉS / REDUCCIÓN</span></div>''',unsafe_allow_html=True)

st.markdown('<div class="section-card"><b>Arquitectura de validación:</b> cargue primero la línea base (ANTES). El segundo archivo (DESPUÉS) es opcional. Cada archivo se procesa únicamente al pulsar su propio botón Ejecutar.</div>',unsafe_allow_html=True)

if 'd_before' not in st.session_state: st.session_state.d_before=None
if 'd_after' not in st.session_state: st.session_state.d_after=None
if 'before_name' not in st.session_state: st.session_state.before_name=''
if 'after_name' not in st.session_state: st.session_state.after_name=''
if 'before_upload_sig' not in st.session_state: st.session_state.before_upload_sig=None
if 'after_upload_sig' not in st.session_state: st.session_state.after_upload_sig=None

u1,u2=st.columns(2)
with u1:
    st.markdown('### 1️⃣ Línea base · ANTES')
    upload_before=st.file_uploader('📥 Cargar Excel ANTES',type=['xlsx','xls'],key='upload_before')
    run_before=st.button('▶ EJECUTAR ANÁLISIS ANTES',type='primary',use_container_width=True,key='run_before')
    if run_before:
        if upload_before is None:
            st.error('Seleccione primero el Excel ANTES.')
        else:
            try:
                tmp=clean(load_excel(upload_before)); missing,issues=validate(tmp)
                if missing: st.error('Faltan columnas obligatorias: '+', '.join(missing))
                else:
                    st.session_state.d_before=tmp;st.session_state.before_name=upload_before.name;st.session_state.before_upload_sig=(upload_before.name,getattr(upload_before,'size',None))
                    for x in issues: st.warning(x)
                    st.success(f'ANTES ejecutado: {len(tmp)} registros.')
            except Exception as e: st.error(f'No se pudo leer el Excel ANTES: {e}')
with u2:
    st.markdown('### 2️⃣ Seguimiento · DESPUÉS')
    upload_after=st.file_uploader('📥 Cargar Excel DESPUÉS',type=['xlsx','xls'],key='upload_after')
    run_after=st.button('▶ EJECUTAR ANÁLISIS DESPUÉS',type='primary',use_container_width=True,key='run_after')
    if run_after:
        if upload_after is None:
            st.error('Seleccione primero el Excel DESPUÉS.')
        else:
            try:
                tmp=clean(load_excel(upload_after)); missing,issues=validate(tmp)
                if missing: st.error('Faltan columnas obligatorias: '+', '.join(missing))
                else:
                    st.session_state.d_after=tmp;st.session_state.after_name=upload_after.name;st.session_state.after_upload_sig=(upload_after.name,getattr(upload_after,'size',None))
                    for x in issues: st.warning(x)
                    st.success(f'DESPUÉS ejecutado: {len(tmp)} registros. Comparación activada.')
            except Exception as e: st.error(f'No se pudo leer el Excel DESPUÉS: {e}')

# Sincronización inmediata con los cargadores: si un archivo se elimina, sus resultados también se eliminan.
# Si se reemplaza por otro archivo, se invalida el análisis anterior hasta pulsar Ejecutar nuevamente.
def upload_signature(u):
    if u is None: return None
    return (u.name, getattr(u, 'size', None))

sig_b=upload_signature(upload_before); sig_a=upload_signature(upload_after)
if upload_before is None and st.session_state.d_before is not None:
    st.session_state.d_before=None; st.session_state.before_name=''; st.session_state.before_upload_sig=None
    st.info('Excel ANTES retirado: se limpiaron sus resultados. Cargue y ejecute un archivo para continuar.')
    st.stop()
elif upload_before is not None and st.session_state.before_upload_sig is not None and sig_b != st.session_state.before_upload_sig and not run_before:
    st.session_state.d_before=None; st.session_state.before_name=''
    st.warning('El Excel ANTES cambió. Pulse ▶ EJECUTAR ANÁLISIS ANTES para generar los nuevos resultados.')
    st.stop()

if upload_after is None and st.session_state.d_after is not None:
    st.session_state.d_after=None; st.session_state.after_name=''; st.session_state.after_upload_sig=None
    st.success('Excel DESPUÉS retirado. La comparación se desactivó y todos los gráficos vuelven a mostrar solo ANTES.')
elif upload_after is not None and st.session_state.after_upload_sig is not None and sig_a != st.session_state.after_upload_sig and not run_after:
    st.session_state.d_after=None; st.session_state.after_name=''
    st.warning('El Excel DESPUÉS cambió. La comparación quedó en pausa hasta pulsar ▶ EJECUTAR ANÁLISIS DESPUÉS.')

if st.session_state.d_before is None:
    st.markdown('<div class="callout"><b>Para iniciar:</b> cargue el Excel ANTES y pulse ▶ EJECUTAR ANÁLISIS ANTES. El Excel mínimo contiene Fecha · Producto · Lote · Proceso · Inspeccionadas · No conformes.</div>',unsafe_allow_html=True)
    st.stop()

d=st.session_state.d_before
d_after=st.session_state.d_after
status_cols=st.columns(3)
status_cols[0].success(f'ANTES activo · {len(d)} registros')
if d_after is not None:
    status_cols[1].success(f'DESPUÉS activo · {len(d_after)} registros')
    status_cols[2].info('Comparación + reducción activadas')
else:
    status_cols[1].info('DESPUÉS aún no ejecutado')
    status_cols[2].info('Los gráficos muestran solo ANTES')

# ----------------------------- TABS -----------------------------
tabs=st.tabs(['📊 Dashboard','🗺️ Flujo / SIPOC-VSM','⚠️ Riesgos/FMEA','🔄 DMAIC/Ishikawa','♻️ Lean','📈 SPC','🧪 Validación','🎯 Decisiones','📄 Reporte'])

# DASHBOARD
with tabs[0]:
    st.header('Dashboard ejecutivo · Antes / Después / Reducción')
    f,fa=filters_pair(d,d_after,'dash')
    mb=metric_pack(f); ma=metric_pack(fa) if fa is not None else None
    crit=critical(f)
    if fa is None:
        c=st.columns(5)
        with c[0]:kpi('INSPECCIONADAS',fmt_int(mb['Inspeccionadas']),'Unidades · ANTES')
        with c[1]:kpi('NO CONFORMIDAD',f"{mb['% NC']:.2f}%",'% de inspeccionadas · ANTES')
        with c[2]:kpi('RETRABAJO',f"{mb['% Retrabajo']:.2f}%",'% de inspeccionadas · ANTES')
        with c[3]:kpi('Proceso prioritario',str(crit.proceso) if crit is not None else 'N/D',f'{crit.Porcentaje_NC:.2f}% NC' if crit is not None else '')
        with c[4]:kpi('Registros',fmt_int(len(f)),'ANTES')
        st.info('Cuando ejecute el Excel DESPUÉS, estos mismos gráficos incorporarán DESPUÉS y REDUCCIÓN automáticamente.')
    else:
        red_nc=reduction_pct(mb['% NC'],ma['% NC']); red_ret=reduction_pct(mb['% Retrabajo'],ma['% Retrabajo'])
        c=st.columns(6)
        with c[0]:kpi('NC · ANTES',f"{mb['% NC']:.2f}%",'% de inspeccionadas')
        with c[1]:kpi('NC · DESPUÉS',f"{ma['% NC']:.2f}%",'% de inspeccionadas')
        with c[2]:kpi('REDUCCIÓN NC',('N/D' if pd.isna(red_nc) else f'{red_nc:.2f}%'),'Cambio relativo')
        with c[3]:kpi('RETRABAJO · ANTES',f"{mb['% Retrabajo']:.2f}%",'% de inspeccionadas')
        with c[4]:kpi('RETRABAJO · DESPUÉS',f"{ma['% Retrabajo']:.2f}%",'% de inspeccionadas')
        with c[5]:kpi('REDUCCIÓN RETRABAJO',('N/D' if pd.isna(red_ret) else f'{red_ret:.2f}%'),'Cambio relativo')
        st.caption(f'Registros filtrados: ANTES {len(f)} · DESPUÉS {len(fa)}')

    cp=compare_process(f,fa) if fa is not None else None
    if fa is None:
        g=process_summary(f)
        if not g.empty:
            fig=px.bar(g,x='proceso',y='Porcentaje_NC',text=g.Porcentaje_NC.map(lambda x:f'{x:.2f}%'),color='Porcentaje_NC',color_continuous_scale=['#22C55E','#FBBF24','#FF4D5A'])
            fig.update_traces(textposition='outside');st.plotly_chart(plot_layout(fig,430,'No conformidad por proceso · ANTES'),width='stretch')
    elif cp is not None and not cp.empty:
        long=cp.melt(id_vars='proceso',value_vars=['Antes','Después','Reducción_%'],var_name='Escenario',value_name='Valor')
        fig=px.bar(long,x='proceso',y='Valor',color='Escenario',barmode='group',text_auto='.2f',color_discrete_map={'Antes':CYAN,'Después':GREEN,'Reducción %':AMBER,'Reducción_%':AMBER})
        st.plotly_chart(plot_layout(fig,440,'No conformidad por proceso · Antes / Después / Reducción %'),width='stretch')

    sb=signals(f)
    if fa is None:
        if not sb.empty:
            p=sb.copy();p['Acumulado_%']=100*p.Cantidad.cumsum()/p.Cantidad.sum();fig=go.Figure();fig.add_bar(x=p.Señal,y=p.Cantidad,name='ANTES',marker_color=CYAN);fig.add_scatter(x=p.Señal,y=p['Acumulado_%'],name='% acumulado',yaxis='y2',line=dict(color=AMBER,width=3),mode='lines+markers');fig.update_layout(yaxis2=dict(overlaying='y',side='right',range=[0,105],title='% acumulado'));st.plotly_chart(plot_layout(fig,420,'Pareto de señales · ANTES'),width='stretch')
    else:
        cs=compare_signals(f,fa)
        if not cs.empty:
            lg=cs.melt(id_vars='Señal',value_vars=['Antes','Después','Reducción_%'],var_name='Escenario',value_name='Valor');lg['Escenario']=lg['Escenario'].replace({'Reducción_%':'Reducción %'})
            fig=px.bar(lg,x='Señal',y='Valor',color='Escenario',barmode='group',text_auto='.1f',color_discrete_map={'Antes':CYAN,'Después':GREEN,'Reducción %':AMBER,'Reducción_%':AMBER});st.plotly_chart(plot_layout(fig,430,'Señales operacionales · Antes / Después / Reducción %'),width='stretch')

    if 'fecha' in f and f.fecha.notna().any():
        tb=f.dropna(subset=['fecha']).groupby('fecha',as_index=False).agg(I=('inspeccionadas','sum'),N=('no_conformes','sum'));tb['NC']=np.where(tb.I>0,100*tb.N/tb.I,0);tb['Serie']='Antes'
        fig=go.Figure();fig.add_scatter(x=tb.fecha,y=tb.NC,mode='lines+markers',name='Antes',line=dict(color=CYAN,width=3))
        if fa is not None and 'fecha' in fa and fa.fecha.notna().any():
            ta=fa.dropna(subset=['fecha']).groupby('fecha',as_index=False).agg(I=('inspeccionadas','sum'),N=('no_conformes','sum'));ta['NC']=np.where(ta.I>0,100*ta.N/ta.I,0)
            fig.add_scatter(x=ta.fecha,y=ta.NC,mode='lines+markers',name='Después',line=dict(color=GREEN,width=3))
            r=reduction_pct(mb['% NC'],ma['% NC']); fig.add_annotation(xref='paper',yref='paper',x=.99,y=.98,text=('Reducción global: N/D' if pd.isna(r) else f'Reducción global: {r:.2f}%'),showarrow=False,bgcolor='#5A4300',font=dict(color='white'))
        st.plotly_chart(plot_layout(fig,350,'Tendencia temporal de no conformidad'),width='stretch')
    footer()

# FLOW
with tabs[1]:
    st.header('Flujo gerencial · SIPOC + VSM')
    f,fa=filters_pair(d,d_after,'flow')
    st.subheader('SIPOC visual');st.plotly_chart(sipoc_figure(f),width='stretch')
    st.subheader('Flujo del proceso con criticidad observada');st.plotly_chart(process_flow_figure(f),width='stretch')
    vcols=['tiempo_ciclo_min','tiempo_espera_min','tiempo_va_min']
    if all(c in f for c in vcols):
        vg=f.groupby('proceso',as_index=False)[vcols].mean();
        fig=go.Figure();fig.add_bar(x=vg.proceso,y=vg.tiempo_va_min,name='VA · Antes',marker_color=CYAN);fig.add_bar(x=vg.proceso,y=vg.tiempo_espera_min,name='Espera · Antes',marker_color=AMBER);fig.add_bar(x=vg.proceso,y=vg.tiempo_ciclo_min,name='Ciclo · Antes',marker_color=PURPLE);
        if fa is not None and all(c in fa for c in vcols):
            va=fa.groupby('proceso',as_index=False)[vcols].mean();fig.add_bar(x=va.proceso,y=va.tiempo_va_min,name='VA · Después',marker_color=GREEN);fig.add_bar(x=va.proceso,y=va.tiempo_espera_min,name='Espera · Después',marker_color=ORANGE);fig.add_bar(x=va.proceso,y=va.tiempo_ciclo_min,name='Ciclo · Después',marker_color=RED)
        fig.update_layout(barmode='group');st.plotly_chart(plot_layout(fig,410,'VSM cuantitativo · Antes / Después'),width='stretch')
    else: st.info('Para cuantificar VSM agregue opcionalmente Tiempo_Ciclo_min, Tiempo_Espera_min y Tiempo_VA_min. El flujo SIPOC/VSM visual ya se genera con los datos disponibles.')
    footer()

# FMEA
with tabs[2]:
    st.header('Riesgos y preevaluación FMEA')
    f,fa=filters_pair(d,d_after,'fmea');sig=signals(f)
    st.markdown('<div class="callout"><b>Separación metodológica:</b> el DSS prioriza señales observadas. S/O/D no se inventan; el NPR se habilita solo con escala validada.</div>',unsafe_allow_html=True)
    if fa is None:
        if sig.empty: st.info('No hay señales opcionales cuantificables para priorizar.')
        else:
            st.dataframe(sig,width='stretch',hide_index=True);fig=px.bar(sig.sort_values('Cantidad'),x='Cantidad',y='Señal',orientation='h',color='Frecuencia_relativa_%',text='Cantidad');st.plotly_chart(plot_layout(fig,390,'Priorización observada · ANTES'),width='stretch')
    else:
        cs=compare_signals(f,fa)
        st.dataframe(cs.round(2),width='stretch',hide_index=True)
        lg=cs.melt(id_vars='Señal',value_vars=['Antes','Después','Reducción_%'],var_name='Escenario',value_name='Valor');lg['Escenario']=lg['Escenario'].replace({'Reducción_%':'Reducción %'});fig=px.bar(lg,x='Valor',y='Señal',orientation='h',color='Escenario',barmode='group',text_auto='.1f',color_discrete_map={'Antes':CYAN,'Después':GREEN,'Reducción %':AMBER});fig.update_traces(textfont=dict(color='white',size=13));st.plotly_chart(plot_layout(fig,470,'Señales FMEA asistidas · Antes / Después / Reducción %'),width='stretch')
    st.markdown('<div class="warnbox"><b>FMEA definitivo:</b> S × O × D requiere criterios aprobados. La comparación observada no sustituye el NPR.</div>',unsafe_allow_html=True)
    footer()

# DMAIC ISHIKAWA
with tabs[3]:
    st.header('DMAIC + Ishikawa ejecutivo')
    f,fa=filters_pair(d,d_after,'dmaic');st.plotly_chart(dmaic_figure(f),width='stretch')
    if fa is not None:
        cc=comparison_long(f,fa);st.dataframe(cc[cc.Indicador.isin(['% NC','% Retrabajo'])].round(2),width='stretch',hide_index=True)
    st.subheader('Ishikawa 6M · hipótesis a verificar, no causas confirmadas')
    st.plotly_chart(ishikawa_figure(f), width='stretch', config={'staticPlot': True, 'displayModeBar': False})
    st.caption('La señal prioritaria orienta la investigación. La causa raíz debe confirmarse con evidencia del proceso.')
    footer()

# LEAN
with tabs[4]:
    st.header('Lean · reducción de desperdicio y exposición operacional')
    f,fa=filters_pair(d,d_after,'lean')
    st.markdown('<div class="callout"><b>Objetivo Lean:</b> reducir retrabajos, esperas, movimientos, manipulación innecesaria y variabilidad del método.</div>',unsafe_allow_html=True)
    cols=[('Defectos / retrabajo','retrabajo'),('Movimiento / manipulación','incid_manipulacion'),('Limpieza / cambio','incid_limpieza'),('Espera','tiempo_espera_min')]
    rows=[]
    for name,col in cols:
        if col in f:
            b=float(f[col].fillna(0).sum());a=float(fa[col].fillna(0).sum()) if fa is not None and col in fa else np.nan
            rows.append([name,b,a,reduction_pct(b,a) if fa is not None else np.nan])
    if rows:
        w=pd.DataFrame(rows,columns=['Desperdicio / condición','Antes','Después','Reducción_%']);st.dataframe(w.round(2),width='stretch',hide_index=True)
        vals=['Antes'] if fa is None else ['Antes','Después','Reducción_%'];lg=w.melt(id_vars='Desperdicio / condición',value_vars=vals,var_name='Escenario',value_name='Valor');fig=px.bar(lg,x='Valor',y='Desperdicio / condición',orientation='h',color='Escenario',barmode='group',text_auto='.1f',color_discrete_map={'Antes':CYAN,'Después':GREEN,'Reducción %':AMBER,'Reducción_%':AMBER});st.plotly_chart(plot_layout(fig,390,'Focos Lean · Antes / Después / Reducción %'),width='stretch')
    else:st.info('Agregue columnas opcionales de retrabajo, manipulación, limpieza o tiempos para ampliar el análisis Lean.')
    st.markdown('<div class="goodbox"><b>Principio de decisión:</b> una reducción positiva es descriptiva. La causa y el efecto de la intervención deben validarse con el diseño del estudio.</div>',unsafe_allow_html=True)
    footer()

# SPC
with tabs[5]:
    st.header('SPC con límites de control ejecutables')
    f,fa=filters_pair(d,d_after,'spc')
    candidates=[c for c in ['temperatura_c','tiempo_ciclo_min','tiempo_espera_min','tiempo_va_min'] if c in f and f[c].notna().sum()>=2]
    if not candidates:
        st.info('No existe una variable continua con suficientes observaciones. Agregue Temperatura o tiempos de proceso para SPC.')
    else:
        var=st.selectbox('Variable continua',candidates,key='spcvar')
        x=f[['fecha',var]].dropna().copy() if 'fecha' in f else f[[var]].dropna().copy()
        vals=x[var].astype(float)
        mean=vals.mean();sd=vals.std(ddof=1)
        ucl_auto=mean+3*sd;lcl_auto=mean-3*sd

        st.subheader('Límites de control')
        modo=st.radio('¿Cómo desea definir LIC y LSC?', ['Ingresar manualmente','Calcular automáticamente (media ± 3σ)'], horizontal=True, key='spc_lim_mode')

        # Cada variable conserva su último análisis ejecutado. Escribir nuevos valores NO modifica la carta hasta pulsar Ejecutar.
        state_key=f'spc_result_{var}'

        if modo=='Ingresar manualmente':
            c1,c2=st.columns(2)
            lic_txt=c1.text_input('LIC · Límite Inferior de Control', value='', placeholder='Ej.: -20', key=f'lic_{var}')
            lsc_txt=c2.text_input('LSC · Límite Superior de Control', value='', placeholder='Ej.: -16', key=f'lsc_{var}')
            ejecutar=st.button('▶ EJECUTAR SPC',type='primary',use_container_width=True,key=f'run_spc_manual_{var}')
            if ejecutar:
                try:
                    lic=float(str(lic_txt).replace(',','.').strip())
                    lsc=float(str(lsc_txt).replace(',','.').strip())
                    if not (np.isfinite(lic) and np.isfinite(lsc)):
                        raise ValueError
                    if lic>=lsc:
                        st.error('LIC debe ser menor que LSC. Revise los valores e intente nuevamente.')
                    else:
                        st.session_state[state_key]={'lic':lic,'lsc':lsc,'modo':'Usuario'}
                        st.success(f'SPC ejecutado con LIC = {lic:.3f} y LSC = {lsc:.3f}.')
                except Exception:
                    st.error('Ingrese valores numéricos válidos para LIC y LSC.')
            if state_key not in st.session_state:
                st.info('Ingrese los límites aprobados y pulse ▶ EJECUTAR SPC. El gráfico no cambiará mientras solo esté escribiendo.')
        else:
            st.caption('Los límites automáticos son exploratorios (media ± 3σ) y no sustituyen límites aprobados del proceso o especificaciones.')
            ejecutar=st.button('▶ EJECUTAR SPC AUTOMÁTICO',type='primary',use_container_width=True,key=f'run_spc_auto_{var}')
            if ejecutar:
                if not np.isfinite(sd) or sd<=0:
                    st.error('No es posible calcular límites automáticos: la serie no presenta una desviación estándar válida.')
                else:
                    st.session_state[state_key]={'lic':float(lcl_auto),'lsc':float(ucl_auto),'modo':'Media ± 3σ'}
                    st.success('SPC automático ejecutado correctamente.')

        result=st.session_state.get(state_key)
        if result:
            lcl=float(result['lic']);ucl=float(result['lsc']);fuente=result['modo']
            out_mask=(vals>ucl)|(vals<lcl)
            out=int(out_mask.sum())

            a=st.columns(4)
            with a[0]:kpi('Variable',var,'Control estadístico')
            with a[1]:kpi('Observaciones',fmt_int(len(vals)),'Serie disponible')
            with a[2]:kpi('Media',f'{mean:.3f}','Centro estadístico')
            with a[3]:kpi('Fuera de límites',fmt_int(out),'Según LIC / LSC ejecutados')

            xx=x.fecha if 'fecha' in x else np.arange(1,len(x)+1)
            fig=go.Figure()
            fig.add_scatter(x=xx,y=vals,mode='lines+markers',name='Antes',line=dict(color=CYAN,width=2),marker=dict(color=AMBER,size=7))
            if fa is not None and var in fa and pd.to_numeric(fa[var],errors='coerce').notna().sum()>=2:
                xa=fa.dropna(subset=[var]).copy();va=pd.to_numeric(xa[var],errors='coerce').dropna();xxa=xa.loc[va.index,'fecha'] if 'fecha' in xa else np.arange(1,len(va)+1);fig.add_scatter(x=xxa,y=va,mode='lines+markers',name='Después',line=dict(color=GREEN,width=2),marker=dict(color=TEAL,size=7));mean_after=float(va.mean());variation=reduction_pct(mean,mean_after);fig.add_hline(y=mean_after,line_dash='dash',line_color=TEAL,annotation_text=f'Media Después {mean_after:.2f}',annotation_position='bottom right');fig.add_annotation(xref='paper',yref='paper',x=.01,y=.98,text=('Variación media: N/D' if pd.isna(variation) else f'Variación relativa media: {variation:.2f}%'),showarrow=False,bgcolor='#123A5A',font=dict(color='white'))
            fig.add_hline(y=mean,line_dash='dash',line_color=GREEN,annotation_text=f'Media {mean:.2f}',annotation_position='top right')
            fig.add_hline(y=ucl,line_dash='dot',line_color=RED,annotation_text=f'LSC {ucl:.2f}',annotation_position='top right')
            fig.add_hline(y=lcl,line_dash='dot',line_color=RED,annotation_text=f'LIC {lcl:.2f}',annotation_position='bottom right')

            if out:
                xo=np.asarray(xx)[out_mask.to_numpy()]
                yo=vals[out_mask]
                fig.add_scatter(x=xo,y=yo,mode='markers',name='Fuera de límites',marker=dict(color=RED,size=12,symbol='x'))

            st.plotly_chart(plot_layout(fig,460,f'Carta de control · {var}'),width='stretch')
            st.markdown(f'<div class="callout"><b>Límites ejecutados:</b> LIC = {lcl:.3f} &nbsp;&nbsp; | &nbsp;&nbsp; Media = {mean:.3f} &nbsp;&nbsp; | &nbsp;&nbsp; LSC = {ucl:.3f} &nbsp;&nbsp; <span style="opacity:.75">({fuente})</span></div>',unsafe_allow_html=True)

            if out:
                st.markdown(f'<div class="redbox">Se identificaron <b>{out}</b> observaciones fuera de los límites ejecutados. El resultado es una señal para investigación del proceso; no confirma por sí solo una causa raíz.</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="goodbox">No se identificaron observaciones fuera de los límites ejecutados.</div>',unsafe_allow_html=True)

            if 'lsl' in f and 'usl' in f and f.lsl.notna().any() and f.usl.notna().any():
                lsl=float(f.lsl.dropna().iloc[0]);usl=float(f.usl.dropna().iloc[0]);cp=(usl-lsl)/(6*sd) if sd>0 else np.nan;cpk=min((usl-mean)/(3*sd),(mean-lsl)/(3*sd)) if sd>0 else np.nan
                st.info(f'Límites de especificación provistos en el Excel: LSL={lsl:g}, USL={usl:g}. Cp={cp:.2f}, Cpk={cpk:.2f}.')
            else:
                st.caption('Cp/Cpk no se calcula sin LSL/USL válidos. LIC/LSC son límites de control y no deben confundirse con límites de especificación.')
        else:
            st.markdown('<div class="warnbox"><b>SPC pendiente de ejecución.</b> Defina LIC/LSC o seleccione el cálculo automático y pulse el botón Ejecutar.</div>',unsafe_allow_html=True)
    footer()

# VALIDATION
with tabs[6]:
    st.header('Validación Antes / Después / Reducción')
    f,fa=filters_pair(d,d_after,'val')
    if fa is None:
        st.markdown('<div class="warnbox"><b>Línea base activa.</b> Aún no se ha ejecutado el Excel DESPUÉS. La validación muestra únicamente la información del primer archivo y no inventa resultados posteriores.</div>',unsafe_allow_html=True)
        base=comparison_long(f,None)[['Indicador','Antes']];st.dataframe(base.round(2),width='stretch',hide_index=True)
        chart=base[base.Indicador.isin(['% NC','% Retrabajo'])].melt(id_vars='Indicador',value_vars=['Antes'],var_name='Escenario',value_name='Valor');fig=px.bar(chart,x='Indicador',y='Valor',color='Escenario',text_auto='.2f',color_discrete_map={'Antes':CYAN});st.plotly_chart(plot_layout(fig,390,'Indicadores de línea base · ANTES'),width='stretch')
    else:
        comp=comparison_long(f,fa);st.dataframe(comp.round(2),width='stretch',hide_index=True)
        chart=comp[comp.Indicador.isin(['% NC','% Retrabajo','Defecto sellado','Incid. higiene','Incid. limpieza','Incid. manipulación'])].melt(id_vars='Indicador',value_vars=['Antes','Después','Reducción_%'],var_name='Escenario',value_name='Valor')
        fig=px.bar(chart,x='Indicador',y='Valor',color='Escenario',barmode='group',text_auto='.2f',color_discrete_map={'Antes':CYAN,'Después':GREEN,'Reducción %':AMBER,'Reducción_%':AMBER});st.plotly_chart(plot_layout(fig,450,'Validación integrada · Antes / Después / Reducción %'),width='stretch')
        b=metric_pack(f)['% NC'];a=metric_pack(fa)['% NC'];r=reduction_pct(b,a)
        if pd.isna(r):st.info('No es posible calcular reducción relativa de % NC porque la línea base es cero o no válida.')
        elif r>0:st.markdown(f'<div class="goodbox">La no conformidad pasó de <b>{b:.2f}%</b> a <b>{a:.2f}%</b>: reducción descriptiva relativa de <b>{r:.2f}%</b>. La atribución causal requiere el diseño de validación del estudio.</div>',unsafe_allow_html=True)
        elif r<0:st.markdown(f'<div class="redbox">La no conformidad pasó de <b>{b:.2f}%</b> a <b>{a:.2f}%</b>: incremento descriptivo relativo de <b>{abs(r):.2f}%</b>. Revisar intervención, contexto y causas.</div>',unsafe_allow_html=True)
        else:st.info('No se observó cambio relativo en % de no conformidad.')
    footer()

# DECISIONS
with tabs[7]:
    st.header('Centro de decisiones y trazabilidad')
    f,fa=filters_pair(d,d_after,'dec');sig=signals(f);crit=critical(f)
    st.plotly_chart(decision_chain_figure(f),width='stretch')
    st.subheader('Plan de acción generado por el DSS')
    if crit is not None and not sig.empty:
        top=sig.iloc[0]
        plan=pd.DataFrame([{
            'Prioridad':1,'Proceso crítico':crit.proceso,'Evidencia':f'{crit.Porcentaje_NC:.2f}% NC','Señal':top.Señal,
            'Causa potencial a verificar':top['Causa potencial a verificar'],'Acción sugerida':top['Acción sugerida'],
            'Herramienta':'SIPOC/VSM + DMAIC + Ishikawa + Lean/SPC','Indicador de control':'% NC / % retrabajo / señal específica','Estado':'Pendiente de validación humana'}])
        st.dataframe(plan,width='stretch',hide_index=True)
        st.markdown(f'<div class="section-card"><b>Justificación automática</b><br><br>El DSS prioriza <b>{crit.proceso}</b> por presentar el mayor % de no conformidad observado ({crit.Porcentaje_NC:.2f}%). La señal dominante es <b>{top.Señal}</b>. La causa presentada es una hipótesis que debe verificarse antes de cerrar una acción correctiva.</div>',unsafe_allow_html=True)
    if fa is not None:
        st.subheader('Resultado comparativo de la intervención')
        st.dataframe(comparison_long(f,fa).round(2),width='stretch',hide_index=True)
    st.subheader('Matriz de evidencia y explicabilidad')
    ev=[['Datos operacionales','Sí',f'{len(f)} registros'],['Laboratorio','Sí' if 'resultado_laboratorio' in f else 'No','Evidencia analítica registrada' if 'resultado_laboratorio' in f else 'No incluida'],['SIPOC / flujo','Sí','Generado automáticamente'],['VSM cuantitativo','Sí' if all(c in f for c in ['tiempo_ciclo_min','tiempo_espera_min','tiempo_va_min']) else 'Parcial','Depende de columnas de tiempo'],['FMEA S/O/D','Pendiente','Requiere escala validada'],['SPC','Sí' if any(c in f for c in ['temperatura_c','tiempo_ciclo_min']) else 'No','Control estadístico exploratorio']]
    st.dataframe(pd.DataFrame(ev,columns=['Fuente','Disponible','Detalle']),width='stretch',hide_index=True)
    footer()

# REPORT
with tabs[8]:
    st.header('Reporte gerencial automático')
    f,fa=filters_pair(d,d_after,'rep')
    st.markdown('<div class="callout"><b>Contenido:</b> resumen ejecutivo, KPIs, diagnóstico por proceso, señales y acciones priorizadas, arquitectura metodológica, DMAIC, Ishikawa 6M, matriz de evidencia, nota metodológica y espacio de revisión.</div>',unsafe_allow_html=True)
    if fa is not None:
        st.subheader('Resumen Antes / Después / Reducción')
        st.dataframe(comparison_long(f,fa).round(2),width='stretch',hide_index=True)
    responsable=st.text_input('👤 Nombre del responsable de Calidad / Inocuidad',placeholder='Ej.: Rosa Pérez',key='responsable_reporte')
    st.caption('El nombre ingresado aparecerá en el reporte gerencial PDF como responsable de la revisión.')
    pdf=pdf_report(f,fa,responsable)
    if pdf:
        st.download_button('⬇️ Descargar reporte gerencial PDF',pdf,'Reporte_Gerencial_DSS_RCC_Decisiones_v16.pdf','application/pdf',width='stretch')
    else:st.error('Para generar el PDF instale ReportLab: python3 -m pip install reportlab')
    footer()
