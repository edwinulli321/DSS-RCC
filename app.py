# DSS-RCC v18 UNIVERSAL · FMEA + LEAN + SPC + REPORTE GERENCIAL PROFESIONAL
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
/* v18: tipografía y tablas más legibles */
.stApp {{font-family: Inter, Arial, sans-serif;}}
.block-container {{max-width: 1650px;}}
p, li, .stMarkdown {{font-size:1rem; line-height:1.55;}}
[data-testid="stDataFrame"] * {{font-size:.92rem!important;}}
[data-testid="stCaptionContainer"] {{color:#C8D6E5!important;font-size:.88rem!important;}}
hr {{border-color:#315B7D!important;}}
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
    'retrabajo':['retrabajo','retrabajos','rework','numero_retrabajos'],
    'numero_retrabajos':['numero_retrabajos','retrabajos_num','cantidad_retrabajos'],
    'numero_manipulaciones':['numero_manipulaciones','manipulaciones','cantidad_manipulaciones'],
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
    'empresa':['empresa'], 'hora':['hora'], 'area':['area'], 'turno':['turno'],
    'eventos_riesgo':['eventos_riesgo','eventos_de_riesgo'], 'tipo_manipulacion':['tipo_manipulacion'],
    'tipo_peligro':['tipo_peligro'], 'producto_expuesto':['producto_expuesto'],
    'contacto_directo_producto':['contacto_directo_producto'], 'alcance_exposicion':['alcance_exposicion'],
    'barrera_posterior':['barrera_posterior'], 'producto_liberado':['producto_liberado'],
    'fuente_riesgo':['fuente_riesgo'], 'mecanismo_contaminacion':['mecanismo_contaminacion'],
    'evento_observado':['evento_observado'], 'higiene_manos':['higiene_manos'], 'epp_guantes':['epp_guantes'],
    'limpieza_superficie':['limpieza_superficie'], 'sanitizacion':['sanitizacion'], 'segregacion':['segregacion'],
    'integridad_empaque':['integridad_empaque'], 'control_alergenos':['control_alergenos'],
    'tipo_control_deteccion':['tipo_control_deteccion'], 'cobertura_control':['cobertura_control'],
    'momento_control':['momento_control'], 'registro_control':['registro_control'],
    'tiempo_exposicion_min':['tiempo_exposicion_min'], 'accion_inmediata':['accion_inmediata'],
    'responsable':['responsable'], 'estado':['estado'],
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
            'temperatura_c','tiempo_exposicion_min','eventos_riesgo','tiempo_ciclo_min','tiempo_espera_min','tiempo_va_min','numero_retrabajos','numero_manipulaciones','lsl','usl']
    for c in nums:
        if c in d: d[c] = pd.to_numeric(d[c], errors='coerce')
    for c in ['empresa','producto','lote','proceso','area','turno','tipo_manipulacion','tipo_peligro','producto_expuesto','contacto_directo_producto','alcance_exposicion','barrera_posterior','producto_liberado','fuente_riesgo','mecanismo_contaminacion','evento_observado','higiene_manos','epp_guantes','limpieza_superficie','sanitizacion','segregacion','integridad_empaque','control_alergenos','tipo_control_deteccion','cobertura_control','momento_control','registro_control','accion_inmediata','responsable','estado','resultado_laboratorio','periodo']:
        if c in d: d[c] = d[c].fillna('No especificado').astype(str).str.strip()
    return d

def validate(d):
    req = ['fecha','producto','lote','proceso','inspeccionadas','no_conformes','eventos_riesgo']
    missing = [x for x in req if x not in d.columns]
    issues=[]
    if missing: return missing, issues
    if (d['inspeccionadas'].fillna(0)<0).any() or (d['no_conformes'].fillna(0)<0).any(): issues.append('Existen cantidades negativas.')
    if (d['no_conformes'].fillna(0)>d['inspeccionadas'].fillna(0)).any(): issues.append('Hay registros con No conformes > Inspeccionadas.')
    if (d['eventos_riesgo'].fillna(0)<0).any(): issues.append('Existen eventos de riesgo negativos.')
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

def _txt(v):
    return norm('' if pd.isna(v) else v)

def occurrence_score(inspeccionadas, eventos):
    try:
        i=float(inspeccionadas); e=float(eventos)
        if i <= 0: return np.nan
        rate=100.0*e/i
        if rate <= 1: return 1
        if rate <= 3: return 2
        if rate <= 5: return 3
        if rate <= 10: return 4
        return 5
    except Exception: return np.nan

def severity_score(row):
    peligro=_txt(row.get('tipo_peligro','')); exp=_txt(row.get('producto_expuesto',''))=='si'
    contacto=_txt(row.get('contacto_directo_producto',''))=='si'; alcance=_txt(row.get('alcance_exposicion',''))
    barrera=_txt(row.get('barrera_posterior','')); liberado=_txt(row.get('producto_liberado',''))=='si'
    score=1 if (not exp and not contacto) else (2 if exp and not contacto else 3)
    if alcance in ('varias_unidades','lote','indeterminado'): score += 1
    if peligro in ('biologico','quimico','alergeno') and contacto: score += 1
    if barrera=='si': score -= 1
    elif barrera in ('no','no_se_conoce') and contacto: score += 1
    if liberado and contacto: score += 1
    return int(max(1,min(5,score)))

def detection_score(row):
    tipo=_txt(row.get('tipo_control_deteccion','')); cobertura=_txt(row.get('cobertura_control',''))
    momento=_txt(row.get('momento_control','')); registro=_txt(row.get('registro_control',''))
    base={'automatico_instrumentado':1,'inspeccion_100':2,'inspeccion_visual_100':2,'inspeccion_por_muestreo':3,'observacion_ocasional':4,'sin_control':5}.get(tipo,3)
    if cobertura=='ninguna': base=5
    elif cobertura=='ocasional': base=max(base,4)
    elif cobertura=='muestreo': base=max(base,3)
    elif cobertura=='100': base=min(base,2)
    if momento in ('despues_de_liberar','no_existe'): base=5
    elif momento in ('antes_de_liberar','durante_el_proceso'): base=max(1,base-1)
    if registro=='no': base=min(5,base+1)
    return int(max(1,min(5,base)))

def risk_level(npr):
    if pd.isna(npr): return 'N/D'
    if npr <= 20: return 'Bajo'
    if npr <= 40: return 'Moderado'
    if npr <= 70: return 'Alto'
    return 'Crítico'

def fmea_rows(f):
    if f is None or f.empty or not all(c in f for c in ['inspeccionadas','eventos_riesgo']): return pd.DataFrame()
    d=f.copy(); d['Frecuencia_eventos_100']=np.where(d.inspeccionadas>0,100*d.eventos_riesgo/d.inspeccionadas,np.nan)
    d['S']=d.apply(severity_score,axis=1); d['O']=d.apply(lambda r: occurrence_score(r.get('inspeccionadas'),r.get('eventos_riesgo')),axis=1)
    d['D']=d.apply(detection_score,axis=1); d['NPR']=d.S*d.O*d.D; d['Nivel_riesgo']=d.NPR.apply(risk_level)
    return d

def fmea_summary(f):
    x=fmea_rows(f)
    if x.empty: return pd.DataFrame()
    keys=[c for c in ['proceso','fuente_riesgo','mecanismo_contaminacion','tipo_peligro'] if c in x]
    g=x.groupby(keys,dropna=False,as_index=False).agg(Registros=('NPR','size'),Inspeccionadas=('inspeccionadas','sum'),Eventos=('eventos_riesgo','sum'),S=('S','max'),D=('D','max'))
    g['Eventos_100']=np.where(g.Inspeccionadas>0,100*g.Eventos/g.Inspeccionadas,0); g['O']=g.apply(lambda r: occurrence_score(r.Inspeccionadas,r.Eventos),axis=1)
    g['NPR']=g.S*g.O*g.D; g['Nivel']=g.NPR.apply(risk_level)
    return g.sort_values(['NPR','Eventos'],ascending=False).reset_index(drop=True)

def compare_fmea(before, after):
    b=fmea_summary(before); a=fmea_summary(after); key='proceso'
    def byproc(x,prefix):
        if x.empty:return pd.DataFrame(columns=[key,f'NPR_{prefix}',f'Eventos100_{prefix}'])
        return x.groupby(key,as_index=False).agg(**{f'NPR_{prefix}':('NPR','max'),f'Eventos100_{prefix}':('Eventos_100','mean')})
    c=pd.merge(byproc(b,'Antes'),byproc(a,'Después'),on=key,how='outer')
    c['Reducción_NPR_%']=c.apply(lambda r: reduction_pct(r.get('NPR_Antes'),r.get('NPR_Después')),axis=1)
    c['Reducción_eventos_%']=c.apply(lambda r: reduction_pct(r.get('Eventos100_Antes'),r.get('Eventos100_Después')),axis=1)
    return c

def signals(f):
    rows=[]
    if f is None or f.empty: return pd.DataFrame(columns=['Prioridad','Señal','Cantidad','Frecuencia_relativa_%','Causa potencial a verificar','Acción sugerida'])
    if 'eventos_riesgo' in f: rows.append(['Eventos de riesgo',float(f.eventos_riesgo.fillna(0).sum()),'Fuentes y mecanismos de transferencia observados','Priorizar mecanismos con mayor frecuencia/NPR y verificar controles.'])
    controls=[('Higiene de manos','higiene_manos'),('EPP / guantes','epp_guantes'),('Limpieza de superficie','limpieza_superficie'),('Sanitización','sanitizacion'),('Segregación','segregacion'),('Integridad de empaque','integridad_empaque'),('Control de alérgenos','control_alergenos')]
    for name,col in controls:
        if col in f:
            q=float(f[col].map(lambda v: 1 if _txt(v)=='no_conforme' else 0).sum()); rows.append([f'NC · {name}',q,f'Control {name.lower()} no conforme','Corregir el control, documentar acción y verificar eficacia.'])
    rows=[r for r in rows if r[1]>0]
    if not rows:return pd.DataFrame(columns=['Prioridad','Señal','Cantidad','Frecuencia_relativa_%','Causa potencial a verificar','Acción sugerida'])
    total=sum(r[1] for r in rows); out=pd.DataFrame([[r[0],r[1],pct(r[1],total),r[2],r[3]] for r in rows],columns=['Señal','Cantidad','Frecuencia_relativa_%','Causa potencial a verificar','Acción sugerida'])
    out=out.sort_values('Cantidad',ascending=False).reset_index(drop=True); out.insert(0,'Prioridad',range(1,len(out)+1)); return out

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
    st.markdown('<div class="footer">DSS-RCC v18 UNIVERSAL · Prototipo de investigación · Gestión integrada, explicable, trazable y con validación humana</div>',unsafe_allow_html=True)


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
    """KPIs universales. Retrabajos se expresa como conteo, no como % de inspeccionadas."""
    if q is None or q.empty:
        return {'Registros':0,'Inspeccionadas':0.0,'No conformes':0.0,'% NC':0.0,'Retrabajos':0.0,'Eventos de riesgo':0.0,'Eventos / 100':0.0}
    I=float(pd.to_numeric(q.get('inspeccionadas',0),errors='coerce').fillna(0).sum())
    N=float(pd.to_numeric(q.get('no_conformes',0),errors='coerce').fillna(0).sum())
    R=float(pd.to_numeric(q.get('numero_retrabajos',q.get('retrabajo',0)),errors='coerce').fillna(0).sum()) if ('numero_retrabajos' in q or 'retrabajo' in q) else 0.0
    E=float(pd.to_numeric(q.get('eventos_riesgo',0),errors='coerce').fillna(0).sum()) if 'eventos_riesgo' in q else 0.0
    return {'Registros':len(q),'Inspeccionadas':I,'No conformes':N,'% NC':pct(N,I),'Retrabajos':R,'Eventos de riesgo':E,'Eventos / 100':pct(E,I)}

def comparison_long(before, after):
    b=metric_pack(before); a=metric_pack(after)
    rows=[]
    for k in b:
        # Registros e inspeccionadas son contexto; su "reducción" no se interpreta como mejora.
        red=np.nan if k in ('Registros','Inspeccionadas') else reduction_pct(b[k],a[k])
        rows.append({'Indicador':k,'Antes':b[k],'Después':a[k],'Reducción_%':red})
    return pd.DataFrame(rows)

def filters_pair(before, after, key):
    """Filtros comparables para ANTES/DESPUÉS. El lote no se usa porque normalmente cambia entre periodos."""
    pool=pd.concat([before, after],ignore_index=True) if after is not None and not after.empty else before.copy()
    st.markdown('<div style="font-weight:850;color:#FFFFFF;font-size:1.05rem;margin:.15rem 0 .35rem 0">🔎 Filtros comparables</div>',unsafe_allow_html=True)
    st.caption('Producto, proceso, área y turno se aplican a ambos periodos. El lote se excluye de la comparación porque ANTES y DESPUÉS suelen corresponder a lotes distintos.')
    c1,c2,c3,c4=st.columns(4)
    prods=['Todos']+sorted(pool.producto.dropna().astype(str).unique().tolist())
    p=c1.selectbox('Producto',prods,key=f'p_{key}')
    t1=pool if p=='Todos' else pool[pool.producto==p]
    procs=['Todos']+sorted(t1.proceso.dropna().astype(str).unique().tolist())
    pr=c2.selectbox('Proceso',procs,key=f'pr_{key}')
    t2=t1 if pr=='Todos' else t1[t1.proceso==pr]
    areas=['Todos']+sorted(t2.area.dropna().astype(str).unique().tolist()) if 'area' in t2 else ['Todos']
    ar=c3.selectbox('Área',areas,key=f'ar_{key}')
    t3=t2 if ar=='Todos' or 'area' not in t2 else t2[t2.area==ar]
    turns=['Todos']+sorted(t3.turno.dropna().astype(str).unique().tolist()) if 'turno' in t3 else ['Todos']
    tu=c4.selectbox('Turno',turns,key=f'tu_{key}')
    def apply(q):
        if q is None:return None
        x=q.copy()
        if p!='Todos':x=x[x.producto==p]
        if pr!='Todos':x=x[x.proceso==pr]
        if ar!='Todos' and 'area' in x:x=x[x.area==ar]
        if tu!='Todos' and 'turno' in x:x=x[x.turno==tu]
        return x
    return apply(before),apply(after)

def filters_pair_lean(before, after, key):
    """Filtros comparables Lean: no usa lote porque ANTES y DESPUÉS suelen ser lotes distintos."""
    pool=pd.concat([before, after],ignore_index=True) if after is not None and not after.empty else before.copy()
    st.markdown('<div style="font-weight:850;color:#FFFFFF;font-size:1.02rem;margin:.15rem 0 .35rem 0">🔎 Filtros Lean comparables</div>',unsafe_allow_html=True)
    st.caption('Para comparar ANTES y DESPUÉS no se usa Lote como filtro obligatorio, porque los lotes de ambos periodos normalmente son diferentes.')
    c1,c2,c3,c4=st.columns(4)
    prods=['Todos']+sorted(pool.producto.dropna().astype(str).unique().tolist())
    p=c1.selectbox('Producto',prods,key=f'p_{key}')
    temp=pool if p=='Todos' else pool[pool.producto==p]
    procs=['Todos']+sorted(temp.proceso.dropna().astype(str).unique().tolist())
    pr=c2.selectbox('Proceso',procs,key=f'pr_{key}')
    temp2=temp if pr=='Todos' else temp[temp.proceso==pr]
    areas=['Todos']+sorted(temp2.area.dropna().astype(str).unique().tolist()) if 'area' in temp2 else ['Todos']
    ar=c3.selectbox('Área',areas,key=f'ar_{key}')
    temp3=temp2 if ar=='Todos' or 'area' not in temp2 else temp2[temp2.area==ar]
    turns=['Todos']+sorted(temp3.turno.dropna().astype(str).unique().tolist()) if 'turno' in temp3 else ['Todos']
    tu=c4.selectbox('Turno',turns,key=f'tu_{key}')
    def apply(q):
        if q is None: return None
        x=q.copy()
        if p!='Todos': x=x[x.producto==p]
        if pr!='Todos': x=x[x.proceso==pr]
        if ar!='Todos' and 'area' in x: x=x[x.area==ar]
        if tu!='Todos' and 'turno' in x: x=x[x.turno==tu]
        return x
    return apply(before),apply(after)

def lean_summary(before, after=None):
    specs=[
        ('Tiempo de exposición (min)','tiempo_exposicion_min','sum'),
        ('Tiempo de ciclo (min)','tiempo_ciclo_min','mean'),
        ('Tiempo de espera (min)','tiempo_espera_min','sum'),
        ('Manipulaciones','numero_manipulaciones','sum'),
        ('Retrabajos','numero_retrabajos','sum'),
        ('Eventos de riesgo','eventos_riesgo','sum'),
        ('Unidades no conformes','no_conformes','sum'),
    ]
    rows=[]
    for label,col,agg in specs:
        if col not in before.columns: continue
        bser=pd.to_numeric(before[col],errors='coerce')
        b=float(bser.mean() if agg=='mean' else bser.sum())
        a=np.nan
        if after is not None and col in after.columns:
            aser=pd.to_numeric(after[col],errors='coerce')
            a=float(aser.mean() if agg=='mean' else aser.sum())
        rows.append([label,b,a,reduction_pct(b,a) if after is not None and not pd.isna(a) else np.nan])
    # tasa NC comparable por denominador
    bi=float(before.inspeccionadas.sum()) if 'inspeccionadas' in before else 0
    bn=float(before.no_conformes.sum()) if 'no_conformes' in before else 0
    bnc=pct(bn,bi)
    anc=np.nan
    if after is not None and 'inspeccionadas' in after and 'no_conformes' in after:
        ai=float(after.inspeccionadas.sum()); an=float(after.no_conformes.sum()); anc=pct(an,ai)
    rows.append(['No conformidad (%)',bnc,anc,reduction_pct(bnc,anc) if after is not None and not pd.isna(anc) else np.nan])
    return pd.DataFrame(rows,columns=['Indicador Lean','Antes','Después','Reducción_%'])

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
def pdf_report(before, after=None, responsable=""):
    """Reporte gerencial comparativo, orientado a decisión y mejora."""
    if not REPORTLAB_OK:return None
    buff=io.BytesIO()
    doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=14*mm,leftMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm)
    styles=getSampleStyleSheet()
    title=ParagraphStyle('rtitle',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=17,leading=21,textColor=colors.HexColor('#0B2948'),alignment=TA_CENTER,spaceAfter=8)
    h1=ParagraphStyle('rh1',parent=styles['Heading1'],fontName='Helvetica-Bold',fontSize=12.5,leading=15,textColor=colors.HexColor('#0B5D7A'),spaceBefore=9,spaceAfter=5)
    body=ParagraphStyle('rbody',parent=styles['BodyText'],fontSize=9,leading=12.5,textColor=colors.HexColor('#263746'))
    note=ParagraphStyle('rnote',parent=body,fontSize=8,textColor=colors.HexColor('#5D6B78'))
    good=ParagraphStyle('rgood',parent=body,textColor=colors.HexColor('#0F6B46'))
    warn=ParagraphStyle('rwarn',parent=body,textColor=colors.HexColor('#9A5B00'))
    story=[Paragraph('REPORTE GERENCIAL DSS-RCC',title),Paragraph('Gestión Integrada del Riesgo de Contaminación Cruzada',ParagraphStyle('sub',parent=title,fontSize=12,textColor=colors.HexColor('#365B78'))),Paragraph(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',note),Spacer(1,5)]
    mb=metric_pack(before); ma=metric_pack(after) if after is not None else None
    crit=critical(before); sig=signals(before); lean=lean_summary(before,after) if after is not None else lean_summary(before,None)
    fb=fmea_summary(before); fa=fmea_summary(after) if after is not None else pd.DataFrame()
    npr_b=float(fb.NPR.max()) if not fb.empty else np.nan; npr_a=float(fa.NPR.max()) if not fa.empty else np.nan
    # Executive table
    k=[['Indicador','ANTES','DESPUÉS','Mejora / cambio']]
    items=[('% No conformidad',mb['% NC'], ma['% NC'] if ma else np.nan, '%'),('Retrabajos',mb['Retrabajos'],ma['Retrabajos'] if ma else np.nan,'n'),('Eventos de riesgo',mb['Eventos de riesgo'],ma['Eventos de riesgo'] if ma else np.nan,'n'),('Eventos / 100',mb['Eventos / 100'],ma['Eventos / 100'] if ma else np.nan,'%'),('NPR máximo',npr_b,npr_a,'npr')]
    for lab,b,a,typ in items:
        if pd.isna(a): av='N/D'; rv='N/D'
        else:
            av=f'{a:.2f}' if typ=='%' else fmt_int(a)
            r=reduction_pct(b,a); rv='N/D' if pd.isna(r) else f'{r:.2f}%'
        bv=f'{b:.2f}' if typ=='%' else fmt_int(b)
        k.append([lab,bv,av,rv])
    kt=Table(k,colWidths=[58*mm,34*mm,34*mm,42*mm],repeatRows=1)
    kt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B2948')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#C7D2DC')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F7FA')]),('FONTSIZE',(0,0),(-1,-1),8.3),('ALIGN',(1,1),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story += [Paragraph('1. Resumen ejecutivo',h1),kt,Spacer(1,7)]
    if after is not None:
        rnc=reduction_pct(mb['% NC'],ma['% NC']); rev=reduction_pct(mb['Eventos / 100'],ma['Eventos / 100']); rret=reduction_pct(mb['Retrabajos'],ma['Retrabajos'])
        txt=f"La no conformidad pasó de <b>{mb['% NC']:.2f}%</b> a <b>{ma['% NC']:.2f}%</b>"
        txt += (f", equivalente a una reducción relativa de <b>{rnc:.2f}%</b>." if not pd.isna(rnc) else '.')
        txt += f" Los eventos de riesgo cambiaron de <b>{mb['Eventos de riesgo']:.0f}</b> a <b>{ma['Eventos de riesgo']:.0f}</b>"
        txt += (f" ({rev:.2f}% de reducción en eventos por 100 unidades)." if not pd.isna(rev) else '.')
        txt += f" Los retrabajos pasaron de <b>{mb['Retrabajos']:.0f}</b> a <b>{ma['Retrabajos']:.0f}</b>"
        txt += (f" ({rret:.2f}% de reducción)." if not pd.isna(rret) else '.')
        story.append(Paragraph(txt,good if (not pd.isna(rnc) and rnc>0) else body))
    else: story.append(Paragraph('El reporte corresponde únicamente a la línea base ANTES. Cargue y ejecute DESPUÉS para cuantificar la mejora.',warn))
    if crit is not None: story.append(Paragraph(f"El proceso prioritario de la línea base es <b>{crit.proceso}</b>, con <b>{crit.Porcentaje_NC:.2f}%</b> de no conformidad. Debe concentrar la verificación de causas y controles.",body))
    # Process comparison
    story.append(Paragraph('2. Resultados por proceso',h1))
    if after is not None:
        cp=compare_process(before,after).sort_values('Antes',ascending=False)
        pdata=[['Proceso','% NC Antes','% NC Después','Reducción %']]+[[str(r.proceso),f'{r.Antes:.2f}',f'{r.Después:.2f}' if pd.notna(r.Después) else 'N/D',f'{r["Reducción_%"]:.2f}' if pd.notna(r['Reducción_%']) else 'N/D'] for _,r in cp.iterrows()]
    else:
        g=process_summary(before); pdata=[['Proceso','Inspeccionadas','No conformes','% NC']]+[[str(r.proceso),fmt_int(r.Inspeccionadas),fmt_int(r.No_conformes),f'{r.Porcentaje_NC:.2f}'] for _,r in g.iterrows()]
    pt=Table(pdata,colWidths=[55*mm,36*mm,36*mm,38*mm],repeatRows=1);pt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1677A8')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5DF')),('FONTSIZE',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F9FB')])]))
    story.append(pt)
    # FMEA
    story += [Paragraph('3. Riesgo FMEA automático',h1)]
    if not fb.empty:
        story.append(Paragraph(f"NPR máximo ANTES: <b>{npr_b:.0f}</b> ({risk_level(npr_b)})." + (f" NPR máximo DESPUÉS: <b>{npr_a:.0f}</b> ({risk_level(npr_a)}), reducción relativa <b>{reduction_pct(npr_b,npr_a):.2f}%</b>." if after is not None and not pd.isna(npr_a) and not pd.isna(reduction_pct(npr_b,npr_a)) else ''),body))
        top=fb.head(5)
        fd=[['Proceso','Fuente','Peligro','S','O','D','NPR']]+[[str(r.get('proceso','')),str(r.get('fuente_riesgo','')),str(r.get('tipo_peligro','')),str(int(r.S)),str(int(r.O)),str(int(r.D)),str(int(r.NPR))] for _,r in top.iterrows()]
        ft=Table(fd,colWidths=[35*mm,34*mm,28*mm,12*mm,12*mm,12*mm,18*mm],repeatRows=1);ft.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#7C3AED')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5DF')),('FONTSIZE',(0,0),(-1,-1),7.5),('ALIGN',(3,1),(-1,-1),'CENTER')]))
        story.append(ft)
    story.append(Paragraph('La escala S/O/D es algorítmica y debe quedar documentada y validada metodológicamente. El NPR prioriza riesgos; no confirma contaminación por sí solo.',note))
    # Lean
    story += [Paragraph('4. Desempeño Lean y reducción de desperdicios',h1)]
    ld=[['Indicador','Antes','Después','Reducción %']]
    for _,r in lean.iterrows():
        ld.append([str(r['Indicador Lean']),f"{r['Antes']:.2f}",('N/D' if pd.isna(r['Después']) else f"{r['Después']:.2f}"),('N/D' if pd.isna(r['Reducción_%']) else f"{r['Reducción_%']:.2f}")])
    lt=Table(ld,colWidths=[68*mm,32*mm,32*mm,36*mm],repeatRows=1);lt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0F766E')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5DF')),('FONTSIZE',(0,0),(-1,-1),7.8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F2FAF8')])]))
    story.append(lt)
    # What to improve / how
    story += [Paragraph('5. Qué mejorar y cómo actuar',h1)]
    recommendations=[]
    if crit is not None: recommendations.append(f"<b>Prioridad 1 – {crit.proceso}:</b> revisar el mecanismo de contaminación y los controles asociados al proceso con mayor % de no conformidad de la línea base ({crit.Porcentaje_NC:.2f}%).")
    if not sig.empty:
        top=sig.iloc[0]; recommendations.append(f"<b>Prioridad 2 – {top.Señal}:</b> {top['Acción sugerida']} Verificar la hipótesis: {top['Causa potencial a verificar']}")
    if after is not None:
        cp=compare_process(before,after)
        weak=cp.dropna(subset=['Reducción_%']).sort_values('Reducción_%').head(1)
        if not weak.empty:
            r=weak.iloc[0]; recommendations.append(f"<b>Prioridad 3 – sostener/mejorar {r.proceso}:</b> presenta la menor reducción relativa de % NC ({r['Reducción_%']:.2f}%). Revisar estandarización, cumplimiento de controles y seguimiento.")
        lr=lean.dropna(subset=['Reducción_%']).sort_values('Reducción_%')
        if not lr.empty:
            r=lr.iloc[0]; recommendations.append(f"<b>Prioridad Lean:</b> el indicador con menor mejora es {r['Indicador Lean']} ({r['Reducción_%']:.2f}%). Definir meta, responsable, fecha y verificación posterior.")
    for i,x in enumerate(recommendations,1): story.append(Paragraph(f'{i}. {x}',body))
    story.append(Paragraph('Acciones sugeridas: estandarizar el método, reforzar controles de higiene/limpieza/segregación según la señal observada, reducir manipulaciones y esperas innecesarias, registrar evidencia de ejecución y reevaluar con el mismo criterio de medición.',body))
    # Validation and limitations
    story += [Paragraph('6. Interpretación y validación',h1)]
    story.append(Paragraph('Las reducciones mostradas son comparaciones descriptivas ANTES/DESPUÉS. Para atribuir causalidad a la intervención se requiere un diseño de validación adecuado, consistencia de muestreo, comparabilidad de condiciones y revisión por Calidad/Inocuidad.',note))
    story.append(Paragraph('Los eventos de riesgo y las no conformidades observadas no equivalen automáticamente a contaminación microbiológica confirmada. Cuando corresponda, la confirmación requiere evidencia analítica o técnica.',note))
    story += [Spacer(1,12),HRFlowable(width='75%',thickness=.6,color=colors.grey),Paragraph(f'Responsable de Calidad / Inocuidad: {responsable.strip() if responsable.strip() else "_______________________________"}',body),Paragraph('Fecha de revisión: ____ / ____ / ______',body)]
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
        with c[2]:kpi('RETRABAJOS',fmt_int(mb['Retrabajos']),'Cantidad observada · ANTES')
        with c[3]:kpi('Proceso prioritario',str(crit.proceso) if crit is not None else 'N/D',f'{crit.Porcentaje_NC:.2f}% NC' if crit is not None else '')
        with c[4]:kpi('Registros',fmt_int(len(f)),'ANTES')
        st.info('Cuando ejecute el Excel DESPUÉS, estos mismos gráficos incorporarán DESPUÉS y REDUCCIÓN automáticamente.')
    else:
        red_nc=reduction_pct(mb['% NC'],ma['% NC']); red_ret=reduction_pct(mb['Retrabajos'],ma['Retrabajos'])
        c=st.columns(6)
        with c[0]:kpi('NC · ANTES',f"{mb['% NC']:.2f}%",'% de inspeccionadas')
        with c[1]:kpi('NC · DESPUÉS',f"{ma['% NC']:.2f}%",'% de inspeccionadas')
        with c[2]:kpi('REDUCCIÓN NC',('N/D' if pd.isna(red_nc) else f'{red_nc:.2f}%'),'Cambio relativo')
        with c[3]:kpi('RETRABAJOS · ANTES',fmt_int(mb['Retrabajos']),'Cantidad observada')
        with c[4]:kpi('RETRABAJOS · DESPUÉS',fmt_int(ma['Retrabajos']),'Cantidad observada')
        with c[5]:kpi('REDUCCIÓN RETRABAJO',('N/D' if pd.isna(red_ret) else f'{red_ret:.2f}%'),'Cambio relativo')
        st.caption(f'Registros filtrados: ANTES {len(f)} · DESPUÉS {len(fa)}')

    cp=compare_process(f,fa) if fa is not None else None
    if fa is None:
        g=process_summary(f)
        if not g.empty:
            fig=px.bar(g,x='proceso',y='Porcentaje_NC',text=g.Porcentaje_NC.map(lambda x:f'{x:.2f}%'),color='Porcentaje_NC',color_continuous_scale=['#22C55E','#FBBF24','#FF4D5A'])
            fig.update_traces(textposition='outside');st.plotly_chart(plot_layout(fig,430,'No conformidad por proceso · ANTES'),width='stretch')
    elif cp is not None and not cp.empty:
        long=cp.melt(id_vars='proceso',value_vars=['Antes','Después'],var_name='Escenario',value_name='% NC')
        fig=px.bar(long,x='proceso',y='% NC',color='Escenario',barmode='group',text_auto='.2f',color_discrete_map={'Antes':CYAN,'Después':GREEN})
        st.plotly_chart(plot_layout(fig,440,'No conformidad por proceso · Antes vs. Después'),width='stretch')
        red=cp.dropna(subset=['Reducción_%']).copy()
        if not red.empty:
            fig2=px.bar(red,x='proceso',y='Reducción_%',text_auto='.1f',color='Reducción_%',color_continuous_scale=['#F97316','#FBBF24','#22C55E'])
            fig2.update_traces(texttemplate='%{y:.1f}%',textposition='outside')
            st.plotly_chart(plot_layout(fig2,360,'Reducción relativa de no conformidad por proceso (%)'),width='stretch')

    sb=signals(f)
    if fa is None:
        if not sb.empty:
            p=sb.copy();p['Acumulado_%']=100*p.Cantidad.cumsum()/p.Cantidad.sum();fig=go.Figure();fig.add_bar(x=p.Señal,y=p.Cantidad,name='ANTES',marker_color=CYAN);fig.add_scatter(x=p.Señal,y=p['Acumulado_%'],name='% acumulado',yaxis='y2',line=dict(color=AMBER,width=3),mode='lines+markers');fig.update_layout(yaxis2=dict(overlaying='y',side='right',range=[0,105],title='% acumulado'));st.plotly_chart(plot_layout(fig,420,'Pareto de señales · ANTES'),width='stretch')
    else:
        cs=compare_signals(f,fa)
        if not cs.empty:
            lg=cs.melt(id_vars='Señal',value_vars=['Antes','Después'],var_name='Escenario',value_name='Cantidad')
            fig=px.bar(lg,x='Señal',y='Cantidad',color='Escenario',barmode='group',text_auto='.0f',color_discrete_map={'Antes':CYAN,'Después':GREEN});st.plotly_chart(plot_layout(fig,430,'Señales operacionales · Antes vs. Después'),width='stretch')
            rr=cs.dropna(subset=['Reducción_%']).copy()
            if not rr.empty:
                fig2=px.bar(rr,x='Señal',y='Reducción_%',text_auto='.1f',color='Reducción_%',color_continuous_scale=['#F97316','#FBBF24','#22C55E']);fig2.update_traces(texttemplate='%{y:.1f}%',textposition='outside');st.plotly_chart(plot_layout(fig2,360,'Reducción relativa de señales operacionales (%)'),width='stretch')

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
    vcols=['tiempo_ciclo_min','tiempo_espera_min']
    if all(c in f for c in vcols):
        vg=f.groupby('proceso',as_index=False)[vcols].mean();
        fig=go.Figure();fig.add_bar(x=vg.proceso,y=vg.tiempo_espera_min,name='Espera · Antes',marker_color=AMBER);fig.add_bar(x=vg.proceso,y=vg.tiempo_ciclo_min,name='Ciclo · Antes',marker_color=CYAN);
        if fa is not None and all(c in fa for c in vcols):
            va=fa.groupby('proceso',as_index=False)[vcols].mean();fig.add_bar(x=va.proceso,y=va.tiempo_espera_min,name='Espera · Después',marker_color=ORANGE);fig.add_bar(x=va.proceso,y=va.tiempo_ciclo_min,name='Ciclo · Después',marker_color=GREEN)
        fig.update_layout(barmode='group');st.plotly_chart(plot_layout(fig,410,'VSM cuantitativo · Antes / Después'),width='stretch')
    else: st.info('Para cuantificar VSM se requieren Tiempo_Ciclo_min y Tiempo_Espera_min. El flujo SIPOC/VSM visual ya se genera con los datos disponibles.')
    footer()

# FMEA
with tabs[2]:
    st.header('Riesgos y FMEA automático · S/O/D calculados por el DSS')
    f,fa=filters_pair(d,d_after,'fmea')
    st.markdown('<div class="callout"><b>FMEA automatizado:</b> el inspector registra hechos observables. El DSS calcula S, O y D mediante reglas explícitas. O usa eventos por 100 unidades; S usa peligro/exposición/contacto/alcance/barrera; D usa tipo/cobertura/momento/registro del control.</div>',unsafe_allow_html=True)
    st.caption('Escala algorítmica DSS-RCC v18 (1–5). Debe documentarse y validarse metodológicamente antes de declarar el NPR como escala definitiva de la investigación.')
    fb=fmea_summary(f)
    if fb.empty:
        st.error('No fue posible calcular FMEA. Verifique que el Excel corresponda a la plantilla universal nueva.')
    else:
        a=st.columns(4)
        with a[0]: kpi('NPR máximo · Antes',fmt_int(fb.NPR.max()),risk_level(fb.NPR.max()))
        with a[1]: kpi('Eventos · Antes',fmt_int(fb.Eventos.sum()),'Situaciones observadas')
        with a[2]: kpi('Eventos / 100',f'{100*fb.Eventos.sum()/fb.Inspeccionadas.sum():.2f}' if fb.Inspeccionadas.sum()>0 else '0','Frecuencia global')
        with a[3]: kpi('Procesos evaluados',fmt_int(fb.proceso.nunique()),'Cobertura FMEA')
        st.subheader('FMEA calculado · ANTES'); st.dataframe(fb.round(2),width='stretch',hide_index=True)
        fig=px.bar(fb.head(15).sort_values('NPR'),x='NPR',y='proceso',orientation='h',color='Nivel',text='NPR',hover_data=['S','O','D','Eventos_100'])
        st.plotly_chart(plot_layout(fig,440,'Priorización FMEA automática · ANTES'),width='stretch')
        if fa is not None:
            fba=fmea_summary(fa); st.subheader('FMEA calculado · DESPUÉS'); st.dataframe(fba.round(2),width='stretch',hide_index=True)
            cmp=compare_fmea(f,fa); st.subheader('Comparación por proceso · ANTES / DESPUÉS'); st.dataframe(cmp.round(2),width='stretch',hide_index=True)
            if not cmp.empty:
                lg=cmp.melt(id_vars='proceso',value_vars=['NPR_Antes','NPR_Después'],var_name='Escenario',value_name='NPR'); lg['Escenario']=lg['Escenario'].replace({'NPR_Antes':'Antes','NPR_Después':'Después'})
                fig=px.bar(lg,x='proceso',y='NPR',color='Escenario',barmode='group',text_auto='.0f',color_discrete_map={'Antes':CYAN,'Después':GREEN}); st.plotly_chart(plot_layout(fig,450,'NPR por proceso · Antes vs Después'),width='stretch')
    with st.expander('Ver reglas automáticas S / O / D'):
        st.markdown('**Ocurrencia (O):** <=1 evento/100 = 1; >1-3 = 2; >3-5 = 3; >5-10 = 4; >10 = 5.\n\n**Severidad (S):** usa exposición, contacto, alcance, peligro, barrera posterior y liberación; resultado 1-5.\n\n**Detección (D):** usa tipo de control, cobertura, momento y registro; 1 = fácil de detectar y 5 = difícil de detectar.')
    footer()

# DMAIC ISHIKAWA
with tabs[3]:
    st.header('DMAIC + Ishikawa ejecutivo')
    f,fa=filters_pair(d,d_after,'dmaic');st.plotly_chart(dmaic_figure(f),width='stretch')
    if fa is not None:
        cc=comparison_long(f,fa);st.dataframe(cc[cc.Indicador.isin(['% NC','Retrabajos','Eventos de riesgo','Eventos / 100'])].round(2),width='stretch',hide_index=True)
    st.subheader('Ishikawa 6M · hipótesis a verificar, no causas confirmadas')
    st.plotly_chart(ishikawa_figure(f), width='stretch', config={'staticPlot': True, 'displayModeBar': False})
    st.caption('La señal prioritaria orienta la investigación. La causa raíz debe confirmarse con evidencia del proceso.')
    footer()

# LEAN
with tabs[4]:
    st.header('Lean · reducción de desperdicio y exposición operacional')
    f,fa=filters_pair_lean(d,d_after,'lean')
    st.markdown('<div class="callout"><b>Objetivo Lean:</b> medir y reducir exposición, esperas, manipulaciones, retrabajos y no conformidades sin confundir estos indicadores con el NPR del FMEA.</div>',unsafe_allow_html=True)

    required_lean=['tiempo_ciclo_min','numero_manipulaciones','numero_retrabajos','tiempo_espera_min']
    present=[c for c in required_lean if c in f.columns]
    missing=[c for c in required_lean if c not in f.columns]

    w=lean_summary(f,fa)
    if not w.empty:
        st.subheader('Indicadores Lean · ANTES vs. DESPUÉS')
        st.dataframe(w.round(2),width='stretch',hide_index=True)
        if fa is not None:
            plot=w.dropna(subset=['Después']).copy()
            if not plot.empty:
                lg=plot.melt(id_vars='Indicador Lean',value_vars=['Antes','Después'],var_name='Escenario',value_name='Valor')
                fig=px.bar(lg,x='Valor',y='Indicador Lean',orientation='h',color='Escenario',barmode='group',text_auto='.2f',color_discrete_map={'Antes':CYAN,'Después':GREEN})
                st.plotly_chart(plot_layout(fig,430,'Indicadores Lean · Antes / Después'),width='stretch')
                red=plot[['Indicador Lean','Reducción_%']].dropna()
                if not red.empty:
                    fig2=px.bar(red,x='Reducción_%',y='Indicador Lean',orientation='h',text_auto='.1f')
                    fig2.add_vline(x=0,line_dash='dash',line_color='#9FB3C8')
                    st.plotly_chart(plot_layout(fig2,380,'Reducción Lean (%) · positivo = mejora'),width='stretch')

    if missing:
        st.warning('Para completar el análisis Lean cuantitativo agregue en ANTES y DESPUÉS estas columnas: ' + ' · '.join(missing))
    else:
        st.success('Las 4 variables Lean cuantitativas están disponibles: tiempo de ciclo, manipulaciones, retrabajos y tiempo de espera.')

    # Lectura ejecutiva automática
    if fa is not None and not w.empty:
        valid=w.dropna(subset=['Reducción_%'])
        improved=valid[valid['Reducción_%']>0]
        worsened=valid[valid['Reducción_%']<0]
        if not improved.empty:
            best=improved.sort_values('Reducción_%',ascending=False).iloc[0]
            st.markdown(f'<div class="goodbox"><b>Lectura Lean:</b> la mayor reducción observada es <b>{best["Indicador Lean"]}</b> con <b>{best["Reducción_%"]:.1f}%</b>. Es una comparación descriptiva y debe interpretarse junto con el diseño de validación.</div>',unsafe_allow_html=True)
        if not worsened.empty:
            bad=worsened.sort_values('Reducción_%').iloc[0]
            st.warning(f'Atención: {bad["Indicador Lean"]} aumentó respecto a ANTES ({bad["Reducción_%"]:.1f}% de reducción, valor negativo). Revise el proceso.')
    st.caption('Comparabilidad: esta pestaña filtra por Producto, Proceso, Área y Turno. El lote no se usa para emparejar ANTES/DESPUÉS porque normalmente cambia entre periodos.')
    st.markdown('<div class="goodbox"><b>Principio de decisión:</b> una reducción positiva indica mejora descriptiva. La causalidad de la intervención debe validarse con el diseño del estudio.</div>',unsafe_allow_html=True)
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
        chart=base[base.Indicador.isin(['% NC','Retrabajos','Eventos / 100'])].melt(id_vars='Indicador',value_vars=['Antes'],var_name='Escenario',value_name='Valor');fig=px.bar(chart,x='Indicador',y='Valor',color='Escenario',text_auto='.2f',color_discrete_map={'Antes':CYAN});st.plotly_chart(plot_layout(fig,390,'Indicadores de línea base · ANTES'),width='stretch')
    else:
        comp=comparison_long(f,fa);st.dataframe(comp.round(2),width='stretch',hide_index=True)
        chart=comp[comp.Indicador.isin(['% NC','Retrabajos','Eventos de riesgo','Eventos / 100'])].melt(id_vars='Indicador',value_vars=['Antes','Después'],var_name='Escenario',value_name='Valor')
        fig=px.bar(chart,x='Indicador',y='Valor',color='Escenario',barmode='group',text_auto='.2f',color_discrete_map={'Antes':CYAN,'Después':GREEN});st.plotly_chart(plot_layout(fig,430,'Validación integrada · Antes vs. Después'),width='stretch')
        redv=comp[comp.Indicador.isin(['% NC','Retrabajos','Eventos de riesgo','Eventos / 100'])].dropna(subset=['Reducción_%'])
        if not redv.empty:
            fig2=px.bar(redv,x='Indicador',y='Reducción_%',text_auto='.1f',color='Reducción_%',color_continuous_scale=['#F97316','#FBBF24','#22C55E']);fig2.update_traces(texttemplate='%{y:.1f}%',textposition='outside');st.plotly_chart(plot_layout(fig2,350,'Reducción relativa por indicador (%)'),width='stretch')
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
            'Herramienta':'SIPOC/VSM + DMAIC + Ishikawa + Lean/SPC','Indicador de control':'% NC / retrabajos / eventos por 100 / NPR','Estado':'Pendiente de validación humana'}])
        st.dataframe(plan,width='stretch',hide_index=True)
        st.markdown(f'<div class="section-card"><b>Justificación automática</b><br><br>El DSS prioriza <b>{crit.proceso}</b> por presentar el mayor % de no conformidad observado ({crit.Porcentaje_NC:.2f}%). La señal dominante es <b>{top.Señal}</b>. La causa presentada es una hipótesis que debe verificarse antes de cerrar una acción correctiva.</div>',unsafe_allow_html=True)
    if fa is not None:
        st.subheader('Resultado comparativo de la intervención')
        st.dataframe(comparison_long(f,fa).round(2),width='stretch',hide_index=True)
    st.subheader('Matriz de evidencia y explicabilidad')
    ev=[['Datos operacionales','Sí',f'{len(f)} registros'],['Laboratorio','Sí' if 'resultado_laboratorio' in f else 'No','Evidencia analítica registrada' if 'resultado_laboratorio' in f else 'No incluida'],['SIPOC / flujo','Sí','Generado automáticamente'],['VSM cuantitativo','Sí' if all(c in f for c in ['tiempo_ciclo_min','tiempo_espera_min']) else 'Parcial','Depende de columnas de tiempo'],['FMEA S/O/D','Automático','Calculado desde variables observables; validar escala DSS-RCC v18'],['SPC','Sí' if any(c in f for c in ['temperatura_c','tiempo_ciclo_min']) else 'No','Control estadístico exploratorio']]
    st.dataframe(pd.DataFrame(ev,columns=['Fuente','Disponible','Detalle']),width='stretch',hide_index=True)
    footer()

# REPORT
with tabs[8]:
    st.header('Reporte gerencial automático')
    f,fa=filters_pair(d,d_after,'rep')
    st.markdown('<div class="callout"><b>Contenido:</b> resumen ejecutivo, comparación ANTES/DESPUÉS, mejora porcentual, FMEA, Lean, procesos prioritarios, recomendaciones de qué mejorar y cómo actuar, limitaciones metodológicas y espacio de revisión.</div>',unsafe_allow_html=True)
    if fa is not None:
        st.subheader('Resumen Antes / Después / Reducción')
        st.dataframe(comparison_long(f,fa).round(2),width='stretch',hide_index=True)
    responsable=st.text_input('👤 Nombre del responsable de Calidad / Inocuidad',placeholder='Ej.: Rosa Pérez',key='responsable_reporte')
    st.caption('El nombre ingresado aparecerá en el reporte gerencial PDF como responsable de la revisión.')
    pdf=pdf_report(f,fa,responsable)
    if pdf:
        st.download_button('⬇️ Descargar reporte gerencial PDF',pdf,'Reporte_Gerencial_DSS_RCC_v18.pdf','application/pdf',width='stretch')
    else:st.error('Para generar el PDF instale ReportLab: python3 -m pip install reportlab')
    footer()
