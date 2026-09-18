import io, re, unicodedata
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='DSS-RCC | Gestión de Riesgos', page_icon='🛡️', layout='wide', initial_sidebar_state='collapsed')

# ============================ ESTILO ============================
st.markdown('''
<style>
.stApp{background:linear-gradient(135deg,#07111f 0%,#0a1626 55%,#07111f 100%);color:#f8fafc}
#MainMenu,footer{visibility:hidden} header{background:transparent}.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1600px}
.hero{background:linear-gradient(90deg,#10223b,#0b182a);border:1px solid #28415f;border-radius:18px;padding:24px 28px;margin-bottom:15px}
.hero-title{font-size:30px;font-weight:850;color:#fff}.hero-sub{color:#9cc4ef;font-size:14px;margin-top:7px}.status{display:inline-block;margin-top:12px;padding:5px 12px;border-radius:20px;border:1px solid #22c55e;color:#4ade80;background:#083727;font-size:12px;font-weight:800}
.card{background:#0f1e33;border:1px solid #29415f;border-radius:15px;padding:17px;margin:8px 0}.kpi{background:#101f35;border:1px solid #29415f;border-radius:15px;padding:16px;min-height:110px}.kpi-label{color:#8fb1d6;font-size:11px;font-weight:800;text-transform:uppercase}.kpi-value{color:#fff;font-size:28px;font-weight:850;margin-top:7px}.kpi-info{color:#7e9bbc;font-size:11px;margin-top:4px}
.good{border-left:5px solid #22c55e}.warn{border-left:5px solid #f59e0b}.bad{border-left:5px solid #ef4444}.info{border-left:5px solid #38bdf8}.small{color:#9aaabd;font-size:12px}.section-note{background:#0d243d;border:1px solid #244e72;border-radius:12px;padding:13px 16px;color:#c9e3ff}
h1,h2,h3{color:#f8fafc!important}p{color:#cbd5e1}[data-testid='stMetricValue']{color:#eaf2ff}
.dmaic{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:15px 0}.dmaic>div{border-radius:16px;padding:18px 10px;text-align:center;color:white;font-weight:800;min-height:92px}.dmaic small{display:block;color:#eaf6ff;margin-top:5px;font-weight:500}
</style>''', unsafe_allow_html=True)

PLOT_CFG={'displayModeBar':False,'staticPlot':True,'responsive':True}
COLORS=['#22c55e','#f59e0b','#ef4444','#38bdf8','#8b5cf6','#ec4899','#14b8a6','#f97316']

# ============================ DATOS ============================
if 'datos' not in st.session_state: st.session_state.datos=None
if 'archivo' not in st.session_state: st.session_state.archivo=''

def norm(x):
    x=unicodedata.normalize('NFKD',str(x)).encode('ascii','ignore').decode('ascii').lower().strip()
    return re.sub(r'[^a-z0-9]+','_',x).strip('_')

ALIASES={
'fecha':'Fecha','producto':'Producto','lote':'Lote','proceso':'Proceso','inspeccionadas':'Inspeccionadas','inspeccionados':'Inspeccionadas','no_conformes':'No_conformes','no_conforme':'No_conformes',
'fecha_produccion':'Fecha_produccion','fecha_de_produccion':'Fecha_produccion','fecha_vencimiento':'Fecha_vencimiento','fecha_de_vencimiento':'Fecha_vencimiento',
'defecto_sellado':'Defecto_sellado','defectos_sellado':'Defecto_sellado','defectos_de_sellado':'Defecto_sellado','retrabajo':'Retrabajo','incidencia_higiene':'Incid_higiene','incid_higiene':'Incid_higiene','incidencia_limpieza':'Incid_limpieza','incid_limpieza':'Incid_limpieza','incidencia_manipulacion':'Incid_manipulacion','incid_manipulacion':'Incid_manipulacion','temperatura':'Temperatura_C','temperatura_c':'Temperatura_C','resultado_laboratorio':'Resultado_laboratorio','laboratorio':'Resultado_laboratorio','tiempo_proceso_min':'Tiempo_Proceso_min'}
REQ=['Fecha','Producto','Lote','Proceso','Inspeccionadas','No_conformes']
NUM=['Inspeccionadas','No_conformes','Defecto_sellado','Retrabajo','Incid_higiene','Incid_limpieza','Incid_manipulacion','Temperatura_C','Tiempo_Proceso_min']

def preparar(df):
    df=df.copy(); df.columns=[ALIASES.get(norm(c),c) for c in df.columns]
    falt=[c for c in REQ if c not in df.columns]
    if falt: raise ValueError('Faltan columnas obligatorias: '+', '.join(falt))
    for c in ['Fecha','Fecha_produccion','Fecha_vencimiento']:
        if c in df: df[c]=pd.to_datetime(df[c],errors='coerce',dayfirst=True)
    for c in NUM:
        if c in df: df[c]=pd.to_numeric(df[c],errors='coerce').fillna(0)
    for c in ['Producto','Lote','Proceso']:
        df[c]=df[c].fillna('Sin dato').astype(str).str.strip()
    if (df['Inspeccionadas']<0).any() or (df['No_conformes']<0).any(): raise ValueError('No se permiten cantidades negativas.')
    if (df['No_conformes']>df['Inspeccionadas']).any(): raise ValueError('Hay filas donde No conformes supera Inspeccionadas.')
    return df

def pct(a,b): return float(a/b*100) if b else 0.0

def lab_estado(s):
    t=norm(s)
    if t in ['conforme','aprobado','cumple']: return 'Conforme'
    if t in ['no_conforme','noconforme','rechazado','no_cumple']: return 'No conforme'
    return 'No evaluado / otro'

def agg_proc(df):
    g=df.groupby('Proceso',as_index=False).agg(Inspeccionadas=('Inspeccionadas','sum'),No_conformes=('No_conformes','sum'))
    g['Porcentaje_NC']=np.where(g.Inspeccionadas>0,g.No_conformes/g.Inspeccionadas*100,0)
    return g.sort_values('Porcentaje_NC',ascending=False)

def risk_signals(df):
    mapping=[('Defecto_sellado','Defectos de sellado'),('Incid_higiene','Incidencias de higiene'),('Incid_limpieza','Incidencias de limpieza'),('Incid_manipulacion','Incidencias de manipulación'),('Retrabajo','Retrabajo')]
    rows=[]
    for c,n in mapping:
        if c in df: rows.append([n,float(df[c].sum())])
    if 'Resultado_laboratorio' in df:
        n=sum(lab_estado(x)=='No conforme' for x in df['Resultado_laboratorio'].fillna(''))
        rows.append(['Laboratorio no conforme',float(n)])
    r=pd.DataFrame(rows,columns=['Señal','Cantidad'])
    if r.empty: return r
    total=r.Cantidad.sum(); r['Prioridad_relativa_%']=np.where(total>0,r.Cantidad/total*100,0)
    return r.sort_values(['Prioridad_relativa_%','Cantidad'],ascending=False)

def action_for(signal):
    d={
    'Laboratorio no conforme':('Revisar informe, ensayo, criterio aplicable y trazabilidad del lote.','Escalar a Calidad/Inocuidad, determinar causa y documentar acción/cierre.','Verificación + AMEF + DMAIC'),
    'Defectos de sellado':('Parámetros de sellado, equipo, método y manipulación.','Estandarizar sellado, corregir causa comprobada y verificar por lote.','AMEF + DMAIC + control'),
    'Incidencias de higiene':('Prácticas del personal, procedimiento y puntos de contacto.','Reforzar higiene, capacitación y verificación documentada.','DMAIC + Lean'),
    'Incidencias de limpieza':('Frecuencia, método, responsables, superficies y registros.','Corregir causa, estandarizar limpieza y verificar recurrencia.','AMEF + DMAIC + control visual'),
    'Incidencias de manipulación':('Método, movimientos y contacto producto-superficie.','Reducir manipulación innecesaria, estandarizar método y capacitar.','VSM + Lean + DMAIC'),
    'Retrabajo':('Motivo del retrabajo y etapa donde se origina.','Eliminar causa recurrente y verificar reducción antes/después.','VSM + DMAIC')}
    return d.get(signal,('Validar la señal y su causa.','Definir acción con Calidad/Inocuidad.','DMAIC'))

def style_fig(fig,title='',height=390):
    fig.update_layout(title=title,height=height,paper_bgcolor='#0f1e33',plot_bgcolor='#0f1e33',font=dict(color='#dbeafe'),margin=dict(l=45,r=25,t=60,b=45),showlegend=True)
    fig.update_xaxes(gridcolor='#29415f',zeroline=False); fig.update_yaxes(gridcolor='#29415f',zeroline=False)
    return fig

def excel_bytes(df):
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w: df.to_excel(w,index=False,sheet_name='Trazabilidad')
    return out.getvalue()

def pdf_bytes(df,supervisor='',firma=True):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
        from reportlab.lib.enums import TA_CENTER
    except Exception: return None
    b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=35,leftMargin=35,topMargin=35,bottomMargin=35)
    ss=getSampleStyleSheet(); title=ParagraphStyle('t',parent=ss['Title'],textColor=colors.HexColor('#123b66'),alignment=TA_CENTER)
    story=[Paragraph('REPORTE GERENCIAL – GESTIÓN DE RIESGOS DE CONTAMINACIÓN CRUZADA',title),Spacer(1,10),Paragraph('Modelo Integrado de Gestión de Riesgos – DSS-RCC',ss['Heading2']),Paragraph('Fecha de generación: '+datetime.now().strftime('%d/%m/%Y %H:%M'),ss['BodyText']),Spacer(1,12)]
    ins=df.Inspeccionadas.sum(); nc=df.No_conformes.sum(); ret=df.Retrabajo.sum() if 'Retrabajo' in df else 0
    data=[['Indicador','Resultado'],['Registros analizados',str(len(df))],['Unidades inspeccionadas',f'{ins:,.0f}'],['No conformes',f'{nc:,.0f} ({pct(nc,ins):.2f}%)'],['Retrabajo',f'{ret:,.0f} ({pct(ret,ins):.2f}%)']]
    t=Table(data,colWidths=[240,220]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#123b66')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey),('PADDING',(0,0),(-1,-1),7)])); story += [t,Spacer(1,14)]
    rp=agg_proc(df); story.append(Paragraph('Procesos observados',ss['Heading2'])); td=[['Proceso','Inspeccionadas','No conformes','% NC']]+[[r.Proceso,f'{r.Inspeccionadas:.0f}',f'{r.No_conformes:.0f}',f'{r.Porcentaje_NC:.2f}%'] for _,r in rp.iterrows()]
    tt=Table(td,colWidths=[180,100,100,80]); tt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2563eb')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey),('PADDING',(0,0),(-1,-1),6)])); story += [tt,Spacer(1,14)]
    rs=risk_signals(df); story.append(Paragraph('Acciones priorizadas para revisión',ss['Heading2']))
    if rs.empty or rs.Cantidad.sum()==0: story.append(Paragraph('No se registraron señales cuantificables en los campos opcionales.',ss['BodyText']))
    else:
        for i,(_,r) in enumerate(rs.iterrows(),1):
            if r.Cantidad<=0: continue
            v,a,h=action_for(r.Señal); story += [Paragraph(f'<b>{i}. {r.Señal}</b> – prioridad relativa observada {r["Prioridad_relativa_%"]:.1f}%',ss['BodyText']),Paragraph('Acción sugerida: '+a,ss['BodyText']),Spacer(1,5)]
    story += [Spacer(1,12),Paragraph('Nota metodológica: las señales orientan la evaluación. Una no conformidad no equivale automáticamente a contaminación cruzada confirmada. La validación corresponde a Calidad/Inocuidad.',ss['BodyText'])]
    if firma:
        story += [Spacer(1,55),Paragraph('________________________________________',ParagraphStyle('c',parent=ss['BodyText'],alignment=TA_CENTER)),Paragraph(supervisor.strip() if supervisor.strip() else 'Supervisor(a) de Calidad',ParagraphStyle('c2',parent=ss['BodyText'],alignment=TA_CENTER)),Paragraph('Supervisor(a) de Calidad',ParagraphStyle('c3',parent=ss['BodyText'],alignment=TA_CENTER)),Paragraph('Fecha: ____ / ____ / ______',ParagraphStyle('c4',parent=ss['BodyText'],alignment=TA_CENTER))]
    doc.build(story); return b.getvalue()

# ============================ CABECERA ============================
st.markdown('''<div class="hero"><div class="hero-title">🛡️ Modelo Integrado de Gestión de Riesgos para reducir la contaminación cruzada</div><div class="hero-sub">DSS-RCC · PYMES exportadoras de alimentos del Perú · SIPOC/VSM + AMEF/FMEA asistido + DMAIC + Lean Manufacturing + SPC</div><span class="status">● SISTEMA ACTIVO</span></div>''',unsafe_allow_html=True)

tabs=st.tabs(['📊 Dashboard','🔎 Diagnóstico','⚠️ Riesgos / FMEA','🔄 DMAIC','📈 SPC','🎯 Decisiones'])

# ============================ CARGA ============================
with tabs[1]:
    st.header('🔎 Diagnóstico gerencial y carga de datos')
    st.markdown('<div class="section-note">Cargue la plantilla Excel y presione <b>Ejecutar análisis</b>. El DSS no procesa el archivo hasta que usted lo confirme.</div>',unsafe_allow_html=True)
    up=st.file_uploader('Archivo Excel',type=['xlsx','xls'],key='up')
    if st.button('▶ Ejecutar análisis',type='primary',use_container_width=True):
        if up is None: st.warning('Primero seleccione un archivo Excel.')
        else:
            try:
                d=preparar(pd.read_excel(up)); st.session_state.datos=d; st.session_state.archivo=up.name; st.success(f'Análisis ejecutado: {len(d)} registros cargados.')
            except Exception as e: st.error(str(e))

# Sin datos: aviso en todas las demás pestañas
if st.session_state.datos is None:
    for idx in [0,2,3,4,5]:
        with tabs[idx]: st.info('📁 Cargue el Excel en la pestaña Diagnóstico y presione “Ejecutar análisis”.')
    st.stop()

df=st.session_state.datos.copy()

# ============================ FILTROS GLOBALES ============================
def filtros(df,key):
    c1,c2,c3=st.columns(3)
    prods=['Todos']+sorted(df.Producto.dropna().unique().tolist())
    p=c1.selectbox('Producto',prods,key=f'p_{key}')
    base=df if p=='Todos' else df[df.Producto==p]
    lotes=['Todos']+sorted(base.Lote.dropna().unique().tolist())
    l=c2.selectbox('Lote',lotes,key=f'l_{key}')
    procs=['Todos']+sorted(base.Proceso.dropna().unique().tolist())
    pr=c3.selectbox('Proceso',procs,key=f'pr_{key}')
    out=base.copy()
    if l!='Todos': out=out[out.Lote==l]
    if pr!='Todos': out=out[out.Proceso==pr]
    return out

# ============================ DASHBOARD ============================
with tabs[0]:
    st.header('📊 Dashboard gerencial · Riesgo de contaminación cruzada')
    f=filtros(df,'dash')
    ins=f.Inspeccionadas.sum(); nc=f.No_conformes.sum(); ret=f.Retrabajo.sum() if 'Retrabajo' in f else 0
    lab=[lab_estado(x) for x in f.Resultado_laboratorio] if 'Resultado_laboratorio' in f else []
    conformes=lab.count('Conforme'); no_lab=lab.count('No conforme')
    cs=st.columns(5)
    vals=[('Inspeccionadas',f'{ins:,.0f}','Base analizada'),('No conformidad',f'{pct(nc,ins):.2f}%',f'{nc:,.0f} unidades'),('Retrabajo',f'{pct(ret,ins):.2f}%',f'{ret:,.0f} unidades'),('Laboratorio analizados',str(len(lab)),f'{conformes} conformes'),('Laboratorio no conforme',str(no_lab),'Requiere revisión')]
    for c,(a,b,z) in zip(cs,vals): c.markdown(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div><div class="kpi-info">{z}</div></div>',unsafe_allow_html=True)

    st.subheader('📦 Trazabilidad por producto y lote')
    # cada producto+lote es una fila independiente
    aggs={'Fecha':('Fecha','min'),'Inspeccionadas':('Inspeccionadas','sum'),'No_conformes':('No_conformes','sum')}
    if 'Retrabajo' in f: aggs['Retrabajo']=('Retrabajo','sum')
    if 'Fecha_produccion' in f: aggs['Fecha_produccion']=('Fecha_produccion','min')
    if 'Fecha_vencimiento' in f: aggs['Fecha_vencimiento']=('Fecha_vencimiento','max')
    tr=f.groupby(['Producto','Lote'],as_index=False).agg(**aggs)
    tr['% NC']=np.where(tr.Inspeccionadas>0,tr.No_conformes/tr.Inspeccionadas*100,0).round(2)
    for c in ['Fecha','Fecha_produccion','Fecha_vencimiento']:
        if c in tr: tr[c]=tr[c].dt.strftime('%d/%m/%Y').fillna('')
    st.dataframe(tr,use_container_width=True,height=250,hide_index=True)
    st.download_button('⬇ Descargar trazabilidad filtrada en Excel',excel_bytes(tr),'trazabilidad_DSS_RCC.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)

    st.subheader('📊 Análisis visual por proceso')
    rp=agg_proc(f); rs=risk_signals(f); c1,c2=st.columns(2)
    if not rp.empty:
        fig=px.bar(rp.sort_values('Porcentaje_NC'),x='Porcentaje_NC',y='Proceso',orientation='h',text=rp.sort_values('Porcentaje_NC').Porcentaje_NC.map(lambda x:f'{x:.2f}%'),color='Porcentaje_NC',color_continuous_scale=['#22c55e','#f59e0b','#ef4444'])
        fig.update_coloraxes(showscale=False); fig.update_traces(textposition='inside'); c1.plotly_chart(style_fig(fig,'% de no conformidad por proceso'),use_container_width=True,config=PLOT_CFG)
    if not rs.empty:
        rr=rs[rs.Cantidad>0]
        fig=px.bar(rr,x='Señal',y='Prioridad_relativa_%',text=rr['Prioridad_relativa_%'].map(lambda x:f'{x:.1f}%'),color='Señal',color_discrete_sequence=COLORS)
        fig.update_traces(textposition='outside'); c2.plotly_chart(style_fig(fig,'Distribución relativa de señales de riesgo'),use_container_width=True,config=PLOT_CFG)

    st.subheader('📈 Evolución diaria de la no conformidad')
    name=st.selectbox('Producto para la evolución diaria',['Todos']+sorted(f.Producto.unique().tolist()),key='trend_name')
    ft=f if name=='Todos' else f[f.Producto==name]
    td=ft.dropna(subset=['Fecha']).copy(); td['Día']=td.Fecha.dt.date
    td=td.groupby('Día',as_index=False).agg(Inspeccionadas=('Inspeccionadas','sum'),No_conformes=('No_conformes','sum')); td['% NC']=np.where(td.Inspeccionadas>0,td.No_conformes/td.Inspeccionadas*100,0)
    fig=go.Figure(go.Scatter(x=td['Día'],y=td['% NC'],mode='lines+markers+text',text=[f'{x:.2f}%' for x in td['% NC']],textposition='top center',line=dict(color='#38bdf8',width=4),marker=dict(size=10,color='#f59e0b')))
    fig.update_xaxes(dtick='D1',tickformat='%d/%m/%Y'); st.plotly_chart(style_fig(fig,'Tendencia diaria · % de no conformidad',380),use_container_width=True,config=PLOT_CFG)

    st.subheader('🧪 Análisis de laboratorio')
    if lab:
        lc=pd.Series(lab).value_counts().reindex(['Conforme','No conforme','No evaluado / otro'],fill_value=0).reset_index(); lc.columns=['Resultado','Cantidad']
        fig=px.pie(lc,values='Cantidad',names='Resultado',hole=.48,color='Resultado',color_discrete_map={'Conforme':'#22c55e','No conforme':'#ef4444','No evaluado / otro':'#94a3b8'})
        fig.update_traces(textinfo='label+value+percent'); st.plotly_chart(style_fig(fig,'Resultados de laboratorio registrados',410),use_container_width=True,config=PLOT_CFG)
    else: st.info('No hay resultados de laboratorio en el archivo filtrado.')

    st.subheader('🎯 Prioridad de acciones')
    if not rs.empty and rs.Cantidad.sum()>0:
        ra=rs[rs.Cantidad>0].copy(); fig=px.bar(ra.sort_values('Prioridad_relativa_%'),x='Prioridad_relativa_%',y='Señal',orientation='h',text=ra.sort_values('Prioridad_relativa_%')['Prioridad_relativa_%'].map(lambda x:f'{x:.1f}%'),color='Prioridad_relativa_%',color_continuous_scale=['#38bdf8','#f59e0b','#ef4444']); fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig,'Acciones a revisar · de mayor a menor señal observada',430),use_container_width=True,config=PLOT_CFG)
        for i,(_,r) in enumerate(ra.iterrows(),1):
            v,a,h=action_for(r.Señal); st.markdown(f'<div class="card warn"><b>{i}. {r.Señal} · {r["Prioridad_relativa_%"]:.1f}%</b><br><span class="small"><b>Qué verificar:</b> {v}<br><b>Acción sugerida:</b> {a}<br><b>Herramienta:</b> {h}</span></div>',unsafe_allow_html=True)
    st.caption('La prioridad relativa es una distribución de las señales registradas; no es un NPR de FMEA ni confirma por sí sola contaminación cruzada.')

# ============================ DIAGNÓSTICO COMPLETO ============================
with tabs[1]:
    st.divider(); st.header('📌 Resultado del diagnóstico')
    f=filtros(df,'diag'); rp=agg_proc(f); rs=risk_signals(f)
    if not rp.empty:
        top=rp.iloc[0]; st.markdown(f'<div class="card info"><b>Proceso con mayor % de no conformidad observado: {top.Proceso}</b><br><span class="small">{top.Porcentaje_NC:.2f}% ({top.No_conformes:.0f} no conformes / {top.Inspeccionadas:.0f} inspeccionadas). Es una señal para priorizar revisión, no una confirmación de contaminación cruzada.</span></div>',unsafe_allow_html=True)
        fig=px.bar(rp,x='Proceso',y='Porcentaje_NC',text=rp.Porcentaje_NC.map(lambda x:f'{x:.2f}%'),color='Porcentaje_NC',color_continuous_scale=['#22c55e','#f59e0b','#ef4444']); fig.update_coloraxes(showscale=False); st.plotly_chart(style_fig(fig,'Diagnóstico ejecutivo por proceso',440),use_container_width=True,config=PLOT_CFG)
    c1,c2,c3=st.columns(3); c1.metric('Registros',len(f)); c2.metric('Productos',f.Producto.nunique()); c3.metric('Lotes',f[['Producto','Lote']].drop_duplicates().shape[0])
    st.markdown('<div class="card info"><b>Lectura gerencial</b><br><span class="small">Use el proceso con mayor no conformidad como punto de entrada para SIPOC/VSM. Luego contraste las señales operativas, el resultado de laboratorio y la trazabilidad por lote antes de definir causas y acciones.</span></div>',unsafe_allow_html=True)

# ============================ FMEA ============================
with tabs[2]:
    st.header('⚠️ AMEF / FMEA asistido · priorización visual')
    f=filtros(df,'fmea'); rs=risk_signals(f)
    st.markdown('<div class="section-note"><b>Importante:</b> el gráfico muestra el peso relativo de las señales observadas. No calcula NPR automáticamente porque Severidad, Ocurrencia y Detección requieren una escala FMEA validada para el estudio.</div>',unsafe_allow_html=True)
    if not rs.empty and rs.Cantidad.sum()>0:
        rr=rs[rs.Cantidad>0].copy(); fig=px.bar(rr,x='Señal',y='Prioridad_relativa_%',text=rr['Prioridad_relativa_%'].map(lambda x:f'{x:.1f}%'),color='Prioridad_relativa_%',color_continuous_scale=['#38bdf8','#f59e0b','#ef4444']); fig.update_coloraxes(showscale=False); fig.update_traces(textposition='outside')
        st.plotly_chart(style_fig(fig,'Pre-evaluación AMEF · señales de mayor a menor prioridad relativa',520),use_container_width=True,config=PLOT_CFG)
        st.subheader('Explicación de cada señal')
        for i,(_,r) in enumerate(rr.iterrows(),1):
            v,a,h=action_for(r.Señal); st.markdown(f'<div class="card warn"><b>{i}. {r.Señal} · {r["Prioridad_relativa_%"]:.1f}%</b><br><span class="small"><b>Evidencia observada:</b> {r.Cantidad:.0f}<br><b>Verificar:</b> {v}<br><b>Respuesta sugerida:</b> {a}</span></div>',unsafe_allow_html=True)
    else: st.info('No hay señales opcionales cuantificables para priorizar.')

# ============================ DMAIC ============================
with tabs[3]:
    st.header('🔄 DMAIC · ruta de mejora')
    f=filtros(df,'dmaic'); rp=agg_proc(f); rs=risk_signals(f); top=rp.iloc[0] if not rp.empty else None; sig=rs.iloc[0].Señal if (not rs.empty and rs.Cantidad.sum()>0) else 'No conformidad operacional'
    st.markdown('''<div class="dmaic"><div style="background:#0ea5e9">DEFINIR<small>¿Cuál es el problema?</small></div><div style="background:#14b8a6">MEDIR<small>¿Qué muestran los datos?</small></div><div style="background:#8b5cf6">ANALIZAR<small>¿Qué causas verificar?</small></div><div style="background:#f59e0b">MEJORAR<small>¿Qué acción implementar?</small></div><div style="background:#ef4444">CONTROLAR<small>¿Cómo sostener la mejora?</small></div></div>''',unsafe_allow_html=True)
    if top is not None:
        v,a,h=action_for(sig); st.markdown(f'<div class="card info"><b>Definir:</b> revisar {top.Proceso}, con {top.Porcentaje_NC:.2f}% de no conformidad.<br><b>Medir:</b> {top.No_conformes:.0f} no conformes de {top.Inspeccionadas:.0f} inspeccionadas.<br><b>Analizar:</b> señal prioritaria “{sig}”. {v}<br><b>Mejorar:</b> {a}<br><b>Controlar:</b> comparar antes/después por producto y lote; aplicar SPC cuando exista una serie suficiente.</div>',unsafe_allow_html=True)
    st.subheader('🐟 Diagrama de Ishikawa asistido')
    cats={'MANO DE OBRA':['Capacitación','Fatiga / presión','Prácticas de higiene'],'MÉTODO':['Estandarización','Manipulación','Secuencia de trabajo'],'MAQUINARIA':['Sellado','Mantenimiento','Parámetros del equipo'],'MATERIALES':['Envases / embalaje','Orden / segregación','Condición del material'],'MEDIO AMBIENTE':['Limpieza','Temperatura','Flujo / congestión'],'MEDICIÓN':['Registros','Inspección','Seguimiento por lote']}
    fig=go.Figure(); fig.add_shape(type='line',x0=.12,y0=.5,x1=.9,y1=.5,line=dict(color='#f8fafc',width=5)); fig.add_annotation(x=.93,y=.5,text='<b>EFECTO<br>Riesgo / no conformidad</b>',showarrow=False,bgcolor='#ef4444',font=dict(color='white',size=13),borderpad=12)
    positions=[(.22,.82,.34,.5),(.45,.82,.52,.5),(.68,.82,.70,.5),(.22,.18,.34,.5),(.45,.18,.52,.5),(.68,.18,.70,.5)]
    for (name,items),(x,y,xe,ye),col in zip(cats.items(),positions,COLORS):
        fig.add_shape(type='line',x0=x,y0=y,x1=xe,y1=ye,line=dict(color=col,width=4)); fig.add_annotation(x=x,y=y,text='<b>'+name+'</b><br>'+'<br>'.join(items),showarrow=False,bgcolor='#10243b',bordercolor=col,borderwidth=2,borderpad=8,font=dict(color='white',size=11))
    fig.update_xaxes(visible=False,range=[0,1]); fig.update_yaxes(visible=False,range=[0,1]); fig.update_layout(height=560,paper_bgcolor='#0f1e33',plot_bgcolor='#0f1e33',margin=dict(l=20,r=20,t=30,b=20))
    st.plotly_chart(fig,use_container_width=True,config=PLOT_CFG)
    st.caption('El Ishikawa organiza causas potenciales para verificar. No afirma que todas sean causas reales; deben confirmarse con evidencia del proceso.')

# ============================ SPC ============================
with tabs[4]:
    st.header('📈 Control Estadístico del Proceso (SPC)')
    f=filtros(df,'spc'); variable=None
    for c in ['Temperatura_C','Tiempo_Proceso_min']:
        if c in f and pd.to_numeric(f[c],errors='coerce').notna().sum()>=2: variable=c; break
    if variable:
        x=f[['Fecha',variable]].dropna().sort_values('Fecha'); vals=x[variable].astype(float); mean=vals.mean(); sd=vals.std(ddof=1) if len(vals)>1 else 0; u=mean+3*sd; l=mean-3*sd
        c1,c2,c3,c4=st.columns(4); c1.metric('Variable',variable); c2.metric('Observaciones',len(vals)); c3.metric('Media',f'{mean:.3f}'); c4.metric('Desv. estándar',f'{sd:.3f}')
        fig=go.Figure(); fig.add_trace(go.Scatter(x=x.Fecha,y=vals,mode='lines+markers',name='Observado',line=dict(color='#38bdf8',width=4),marker=dict(color='#f59e0b',size=9))); fig.add_hline(y=mean,line_dash='dash',line_color='#22c55e',annotation_text='Media'); fig.add_hline(y=u,line_dash='dot',line_color='#ef4444',annotation_text='LSC estadístico'); fig.add_hline(y=l,line_dash='dot',line_color='#ef4444',annotation_text='LIC estadístico')
        st.plotly_chart(style_fig(fig,f'Tendencia y límites de control estadístico · {variable}',500),use_container_width=True,config=PLOT_CFG)
        fuera=int(((vals>u)|(vals<l)).sum()) if sd>0 else 0
        st.markdown(f'<div class="card info"><b>¿Cómo leer este gráfico?</b><br><span class="small">La línea azul son los valores observados. La línea verde representa el promedio. Las líneas rojas son límites estadísticos calculados como media ± 3σ. Con los datos actuales se observan <b>{fuera}</b> puntos fuera de esos límites. Estos límites describen el comportamiento observado y <b>no son límites de especificación</b> del producto.</span></div>',unsafe_allow_html=True)
        if len(vals)<20: st.warning(f'Solo hay {len(vals)} observaciones. El gráfico es exploratorio; para un SPC más estable se requiere una serie temporal mayor y un plan de muestreo definido.')
    else: st.info('No existe una variable continua con suficientes observaciones para mostrar SPC.')

# ============================ DECISIONES ============================
with tabs[5]:
    st.header('🎯 Centro de decisiones gerencial')
    f=filtros(df,'dec'); rp=agg_proc(f); rs=risk_signals(f); ins=f.Inspeccionadas.sum(); nc=f.No_conformes.sum(); ret=f.Retrabajo.sum() if 'Retrabajo' in f else 0
    c1,c2,c3=st.columns(3); c1.metric('Proceso prioritario',rp.iloc[0].Proceso if not rp.empty else '—'); c2.metric('% no conformidad',f'{pct(nc,ins):.2f}%'); c3.metric('% retrabajo',f'{pct(ret,ins):.2f}%')
    if not rs.empty and rs.Cantidad.sum()>0:
        rr=rs[rs.Cantidad>0].copy(); fig=px.funnel(rr,x='Prioridad_relativa_%',y='Señal',color='Señal',color_discrete_sequence=COLORS); st.plotly_chart(style_fig(fig,'Embudo de prioridades para la toma de decisiones',470),use_container_width=True,config=PLOT_CFG)
        sig=rr.iloc[0].Señal; v,a,h=action_for(sig); st.markdown(f'<div class="card warn"><b>Primera señal a revisar: {sig}</b><br><span class="small">Representa {rr.iloc[0]['Prioridad_relativa_%']:.1f}% de las señales cuantificadas. <b>Verificar:</b> {v}<br><b>Acción sugerida:</b> {a}</span></div>',unsafe_allow_html=True)
    st.subheader('🧭 Ruta de decisión integrada')
    st.markdown('<div class="card info"><b>Excel → Diagnóstico SIPOC/VSM → Señales de riesgo → AMEF/FMEA asistido → DMAIC → Mejora Lean → Control/SPC → Decisión y seguimiento</b><br><span class="small">El DSS prioriza y orienta. La validación de causas y las decisiones de inocuidad corresponden a los responsables del proceso y de Calidad/Inocuidad.</span></div>',unsafe_allow_html=True)
    st.subheader('📄 Reporte gerencial PDF')
    a,b=st.columns([4,1]); supervisor=a.text_input('Nombre del Supervisor de Calidad (opcional)',key='sup'); firma=b.checkbox('Incluir firma',value=True,key='firma')
    pdf=pdf_bytes(f,supervisor,firma)
    if pdf: st.download_button('⬇ Descargar reporte gerencial en PDF',pdf,'Reporte_Gerencial_DSS_RCC.pdf','application/pdf',use_container_width=True)
    else: st.error('Para generar el PDF instale ReportLab: python3 -m pip install reportlab')

st.markdown('<br>',unsafe_allow_html=True); st.caption('DSS-RCC · Sistema de Soporte a Decisiones | Modelo Integrado de Gestión de Riesgos')
