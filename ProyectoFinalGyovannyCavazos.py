import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import plotly.express as px

@st.cache_data
def cargar_datos():
    return pd.read_csv('Datos/bank-full.csv')

df = cargar_datos()

# Plotly no acepta tamaños menores a 0. Creamos columna auxiliar para los tamaños de las gráficas.
df['balance_size'] = df['balance'].clip(lower=0)

# --- Obtener las metricas ------------

df_suscritos = df[df['y'] == 'yes']
media_balance_suscritos = df_suscritos['balance'].mean()

df_no_suscritos = df[df['y'] == 'no']
media_balance_no_suscritos = df_no_suscritos['balance'].mean()

conteo_suscripciones = df['y'].value_counts()
num_no_suscritos = conteo_suscripciones.iloc[0]
num_si_suscritos = conteo_suscripciones.iloc[1]


# --- Funcion de apoyo para crear la grafica de intervalos ---------

def intervalos(var):
    import math
    n = len(var)
    x_max = var.max()
    x_min = var.min()
    recorrido = x_max - x_min
    intervalos = round(1 + 3.3 * (math.log10(n)))
    amplitud = recorrido / intervalos

    return x_min, x_max, amplitud

def actualiza_layout(grafica,x_title,y_title):
    grafica.update_layout(xaxis_title=x_title,
                        yaxis_title=y_title,
                        paper_bgcolor='white',
                          plot_bgcolor='white',
                          title_pad_l = 20,
                          title_font_family = 'verdana',
                          title_font_color='black',
                          title_font_size = 16,
                          font_size = 15,
                          height = 400,
                          font_color='black'
                        )

def sct(varX, varY, co, cocs, x_titulo, y_titulo, tam, titulo,
        marg_x= None, marg_y= None, facetCol=None):
    grafica_sc = px.scatter(df, x=varX, y=varY,
                            color=co,
                            color_continuous_scale=cocs,
                            size= tam,
                            marginal_x=marg_x,
                            marginal_y=marg_y,
                            facet_col=facetCol,
                            title=titulo)
    actualiza_layout(grafica_sc, x_titulo, y_titulo)

    return grafica_sc

# --- Grafica de histograma ----------
def histograma(var, tit, subtit, col, cods, textoA, x_titulo, y_titulo,
               agrupados, x_min=0, x_max=0, amplitud=0,
               varY=None, pshape=None):
    if agrupados == True:
        grafica_hist = px.histogram(df, x=var,
                                    title=tit,
                                    subtitle=subtit,
                                    text_auto=textoA)

        grafica_hist.update_traces(marker_line_width=1,
                                   xbins=dict(start=x_min,
                                              end=x_max,
                                              size=amplitud))

    elif agrupados == False:
        grafica_hist = px.histogram(df, x=var, y=varY,
                                    pattern_shape=pshape,
                                    title=tit,
                                    subtitle=subtit,
                                    color=col,
                                    color_discrete_sequence=cods,
                                    text_auto=textoA)

    actualiza_layout(grafica_hist, x_titulo, y_titulo)
    return grafica_hist


# Gráfica de Histograma con función de densidad
import plotly.figure_factory as ff

def grafica_densidad(var, etiqueta, color):
    _, _, amplitudA = intervalos(var)
    amplitud = amplitudA

    graf_dens = ff.create_distplot([var.dropna()], [etiqueta],
                                   show_hist='True',
                                   show_curve='True',
                                   curve_type='kde',
                                   show_rug=False,
                                   bin_size=amplitud,
                                   colors=[color]
                                   )

    graf_dens.update_traces(marker_line_width=1)

    graf_dens.update_layout(
        title='Gráfica de densidad: ' + etiqueta,
        xaxis_title='Rango de ' + etiqueta,
        yaxis_title='Frecuencia - Densidad',
        paper_bgcolor='white',
        plot_bgcolor='white',
        title_pad_l=20,
        title_font_family='verdana',
        title_font_color='black',
        title_font_size=16,
        font_size=15,
        height=400,
        font_color='black'
    )

    return graf_dens

def boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
            col=None, xvar =None, puntos=None):

    grafica_box = px.box(df, x = xvar, y = yvar,
                        points = puntos,
                        color = col,
                        color_discrete_sequence=cds,
                        title = titulo
                        )

    actualiza_layout(grafica_box, x_titulo, y_titulo)

    return grafica_box


# --- grafica Sunburst ----------
grafica_sunburst = px.sunburst(df, path=['job', 'y', 'marital'],
                               values='balance_size', color='balance',
                               color_continuous_scale=px.colors.cyclical.IceFire)

grafica_sunburst.update_traces(marker=dict(line=dict(color='purple', width=1)))

grafica_sunburst.update_layout(title='Balance por trabajo',
                               font=dict(family='Courier New, monospace',
                                         size=14,
                                         color='purple'),
                               paper_bgcolor='white',
                               height=400,
                               font_color='black'
                               )

def tablaFrecuencia(tabla, col, nomCol):
    tabla1 = pd.DataFrame(tabla)
    lista = []

    for reg in tabla:
        cont = 0
        for i in col:
            if reg == i:
                cont = cont +1

        lista.append(cont)

    tabla2 = pd.DataFrame(lista)
    total = tabla2.sum()
    tabla3 = pd.concat([tabla1, tabla2], axis=1)
    tabla3.columns = [nomCol, 'frecAbs']

    def calcula(frecAbs):
        fRel = frecAbs/total
        return fRel

    tabla3['frecRel'] = tabla3['frecAbs'].apply(calcula)
    tabla3['frecAcum'] = tabla3['frecRel'].cumsum()

    return tabla3


# --- funcion para table de frecuencias ---------

def tabla_Hist(varCol, nomCol):
    global intervvalos
    print('Variable: ' + nomCol + '\n')
    n = len(varCol)
    print('Paso 1 tamano de la mustra: ', n,'\n')

    x_max = varCol.max()
    x_min = varCol.min()
    print('Paso 2# Maximo y Minimo: ')
    print('Maximo: ', x_max)
    print('Minimo: ', x_min, '\n')

    recorrido = x_max - x_min
    print('Paso 3: Recorrido ' , recorrido, '\n')

    intervalos = round(1 + (3.3 *(math.log10(n))))
    print('Paso 4: Intervalos: ', intervalos, '\n')

    amplitud = recorrido / intervalos
    print('Paso 5: Amplitud ', '%0.2f', amplitud , '\n')

    df_tf = pd.DataFrame()
    df_tf['Clase'] = list(range(1, intervalos+1))
    df_tf['limInf'] = np.full(shape= intervalos, fill_value= np.nan)

    for i in range(intervalos):
        df_tf.loc[i, 'limInf'] = round(x_min + (i * amplitud), 3)

    df_tf['limSup'] = round(df_tf['limInf'] + amplitud, 3)
    df_tf['x'] = (df_tf['limSup'] + df_tf['limInf']) / 2
    df_tf['f'] = np.full(shape=intervalos, fill_value= np.nan)

    for i in range(intervalos):
        k = 0
        if i ==0:
            for j in range(n):
                if varCol[j] <= df_tf['limSup'][i]:
                    k=k+1
                df_tf.loc[i,'f'] = k

        else :
            for j in range(n):
                if (varCol[j] > df_tf['limInf'][i]) and (varCol[j] <= df_tf['limSup'][i]):
                    k=k+1
                df_tf.loc[i,'f'] = k

    df_tf['Fa'] = df_tf['f'].cumsum()
    df_tf['fr'] = round(df_tf['f']/n, 4)
    df_tf['Fra'] = df_tf['fr'].cumsum()

    return df_tf

st.set_page_config(page_title='Tablero de control',
                   layout='wide', page_icon= 'Imagenes/imagenIco.ico')
st.markdown(
    """
    <style>
    .block-container{
    padding-top: 1rem;
    padding-bottom: 0rem;
    padding-left: 5rem;
    padding-right: 5rem;
    }
    </style>
""", unsafe_allow_html=True
)


#Titulo principal---------------------------------------------
st.title('TABLERO DE VISUALIZACION DE VARIABLES')
st.text('Indicadores generales para el Dataset de Marketing Bancario')
st.text('Gyovanny Cavazos Marquez')

# --- Visualizacion metricas generales ----------

colm1, colm2, colm3, colm4 = st.columns(4, vertical_alignment='center',
                                        border=True)

with colm1:
    st.metric('Balance promedio suscritos (Yes)',
              '$ %0.2f' %media_balance_suscritos,
                    delta = '9382 mediana',
                    delta_color=' inverse')

with colm2:
    st.metric('Balance promedio no suscritos (No)',
              '$ %0.2f' %media_balance_no_suscritos,
                    delta = '9382 mediana')

with colm3:
    porcentajeSi = ('%0.0f' % ((num_si_suscritos/len(df))* 100))
    st.metric('Numero de suscritos (Yes)',
              num_si_suscritos,
              delta=f'{porcentajeSi}%',
              delta_color=' inverse')

with colm4:
    porcentajeNo = ('%0.0f' % ((num_no_suscritos/len(df))* 100))
    st.metric('Numero de no suscritos (No)',
              num_no_suscritos,
              delta=f'{porcentajeNo}%')

st.markdown('---')

# --- Seccion logo de la empresa ---------
st.sidebar.header('Logo Empresa')
st.sidebar.image('Imagenes/imagenG.png')

# --- Selector de variables ----------
st.markdown('---')
st.sidebar.header("Analisis exploratorio de Dataset")
op = st.sidebar.radio('Selecciona: ', ['Estadistica', 'Visualizacion'])

if op == 'Visualizacion':
    st.sidebar.markdown('---')

    st.sidebar.header("Visualizacion exploratoria")
    opcion = st.sidebar.radio('Selecciona: ', ['Una variable', 'Dos variables'])

    if opcion == 'Una variable':
        opcionUni = st.sidebar.selectbox('Selecciona: Una variable',['Campaign', 'Job', 'Duration', 'Balance', 'Suscripcion'])
        col1, col2 = st.columns([0.98, 0.02])
        if opcionUni == 'Campaign':
            with col1:
                var='campaign'
                tit='Frecuencia numero de contactos'
                subtit = 'Por campana'
                col = 'campaign'
                cods = [['Red'], ['Olive'], ['Yellow'], ['Purple'], ['Blue'], ['Green']]
                textoA = True
                x_titulo = 'Numero de contactos (campaign)'
                y_titulo = 'Frecuencia'
                agrupados:bool = False
                hist_campana = histograma(var, tit, subtit, col, cods, textoA,
                                        x_titulo, y_titulo, agrupados)

                st.plotly_chart(hist_campana, width='stretch')
                st.markdown('---')

        elif opcionUni == 'Job':
            with col1:
                col1_1, col1_2 = st.columns(2)
            with col1_1:
                var='job'
                tit='Frecuencia de variable trabajo'
                subtit = 'Cantidad por trabajo'
                col = 'job'
                cods = [['Red'], ['Olive'], ['Yellow'], ['Purple'], ['Blue'], ['Green']]
                textoA = True
                x_titulo = 'Trabajos'
                y_titulo = 'Frecuencia'
                agrupados:bool = False
                hist_trabajo = histograma(var, tit, subtit, col, cods, textoA,
                                        x_titulo, y_titulo, agrupados)

                st.plotly_chart(hist_trabajo, width='stretch')
                with col1_2:
                    st.plotly_chart(grafica_sunburst, width='stretch')
                st.markdown('---')

        elif opcionUni == 'Duration':
            with col1:
                col1_1, col1_2 = st.columns(2)
                col_duracion = df['duration']
            with col1_1:
                x_min, x_max, amplitudA = intervalos(col_duracion)
                amplitud = '%0.2f' %amplitudA
                var='duration'
                tit='Frecuencia duracion'
                subtit = 'Duration'
                col = 'duration'
                cods = ['Olive']
                textoA = True
                x_titulo = 'Rango de Duration'
                y_titulo = 'Frecuencia'
                agrupados:bool = True
                hist_duracion = histograma(var, tit, subtit, col, cods, textoA,
                                        x_titulo, y_titulo, agrupados,
                                        x_min, x_max, amplitud)

                st.plotly_chart(hist_duracion, width='stretch')

        elif opcionUni == 'Balance':
            with col1:
                col1_1, col1_2, col1_3 = st.columns(3)
                col_balance = df['balance']
            with col1_1:
                x_min, x_max, amplitudA = intervalos(col_balance)
                amplitud = '%0.2f' %amplitudA
                var='balance'
                tit='Frecuencia de variable balance'
                subtit = 'Balance'
                col = 'balance'
                cods = ['Olive']
                textoA = True
                x_titulo = 'Rango de balance'
                y_titulo = 'Frecuencia'
                agrupados:bool = True
                hist_balance = histograma(var, tit, subtit, col, cods,
                                        textoA, x_titulo, y_titulo,
                                        agrupados, x_min, x_max, amplitud)

                st.plotly_chart(hist_balance, width='stretch')

            with col1_2:
                etiq = 'balance'
                color = 'red'
                densidad_balance = grafica_densidad(col_balance,etiq, color)
                st.plotly_chart(densidad_balance, width='stretch')
                st.markdown('---')

            with col1_3:
                yvar = 'balance'
                cds = ['Olive']
                titulo = 'Balance del cliente'
                x_titulo = 'Variable balance'
                y_titulo = 'Balance'
                box_balance = boxplt1(yvar, cds, titulo, x_titulo, y_titulo)
                st.plotly_chart(box_balance, width='stretch')

        elif opcionUni == 'Suscripcion':
            with col1:
                col1_1, col1_2 = st.columns(2)
            with col1_1:
                var='y'
                tit='Frecuencia de variable suscripcion (y)'
                subtit = 'clasificado por yes y no'
                col = 'y'
                cods = [['Magenta'],['Olive']]
                textoA = True
                x_titulo = 'Suscripcion (y)'
                y_titulo = 'Cantidad'
                agrupados:bool = False
                hist_suscripcion_1 = histograma(var, tit, subtit, col, cods,
                                        textoA, x_titulo, y_titulo,
                                        agrupados)

                st.plotly_chart(hist_suscripcion_1, width='stretch')

            with col1_2:
                var = 'y'
                tit = 'Frecuencia de variable suscripcion'
                subtit = 'clasificado por suscripcion y estado civil'
                col = 'marital'
                cods = [['Magenta','Magenta','Magenta'], ['Olive','Olive','Olive']]
                textoA = True
                x_titulo = 'Suscripcion (y)'
                y_titulo = 'Cantidad'
                agrupados: bool = False
                hist_suscripcion_2 = histograma(var, tit, subtit, col, cods,
                                        textoA, x_titulo, y_titulo,
                                        agrupados)

                st.plotly_chart(hist_suscripcion_2, width='stretch')

    elif opcion == 'Dos variables':
        opcionBi = st.sidebar.multiselect('Selecciona dos variables',
                                          ['Edad', 'Balance', 'Suscripcion'])
        lista1 = ['Edad', 'Balance']
        lista2 = ['Balance','Suscripcion']
        if set(opcionBi) == set(lista1):
            varX = df['age']
            varY = df['balance']
            col1, col2 = st.columns(2)

            with col1:
                col = 'age'
                cocs = 'delta'
                x_title = 'Edad'
                y_title = 'Balance'
                tamano = 'age'
                titulo = 'Edad-balance'
                scatter_edad_bal_1 = sct(varX, varY, col, cocs, x_title, y_title,
                               tamano, titulo)
                st.plotly_chart(scatter_edad_bal_1, width='stretch')

            with col2:
                col = 'y'
                cocs = 'delta'
                tamano = 'balance_size'
                x_title = 'Edad'
                y_title = 'Balance'
                titulo = 'Edad-balance por suscripcion'
                scatter_edad_bal_2 = sct(varX, varY, col, cocs, x_title, y_title,
                               tamano, titulo)
                st.plotly_chart(scatter_edad_bal_2, width='stretch')

            col3, col4 = st.columns(2)
            with col3:
                col = 'y'
                cocs = 'Jet'
                x_title = 'Edad'
                y_title = 'Balance'
                tamano = 'balance_size'
                titulo = 'Edad-balance con graficas al margen'
                marg_x = 'histogram'
                marg_y = 'box'
                scatter_edad_bal_3 = sct(varX, varY, col, cocs, x_title, y_title,
                               tamano, titulo, marg_x, marg_y)
                st.plotly_chart(scatter_edad_bal_3, width='stretch')

            with col4:
                col = 'y'
                cocs = 'Darkmint'
                x_title = 'Edad'
                y_title = 'Balance'
                titulo = 'Edad-balance por suscripcion y estado civil'
                tamano = 'balance_size'
                marg_x = None
                marg_y = None
                faceCol = 'marital'
                scatter_edad_bal_4 = sct(varX, varY, col, cocs, x_title, y_title,
                               tamano, titulo, marg_x, marg_y, faceCol)
                st.plotly_chart(scatter_edad_bal_4, width='stretch')

        elif set(opcionBi) == set(lista2):
            col1, col2 = st.columns(2)

            with col1:
                varX = df['y']
                varY = df['balance']
                col = 'balance'
                cocs = 'Darkmint'
                x_title = 'Suscripcion'
                y_title = 'Balance'
                titulo = 'Suscripcion-balance'
                tamano = 'balance_size'
                marg_x = None
                marg_y = None
                faceCol = 'marital'
                scatter_suscripcion_bal_1 = sct(varX, varY, col, cocs, x_title, y_title,
                               tamano, titulo, marg_x, marg_y, faceCol)
                st.plotly_chart(scatter_suscripcion_bal_1, width='stretch')


            with col2:
                varX = 'marital'
                varY = 'balance'
                col = 'marital'
                pshape = 'y'
                tit = 'Variable Suscripcion - Balance - Estado Civil'
                subtit = 'por balance acumulado'
                cods =['Magenta', 'Olive', 'Blue']
                textoA = True
                x_titulo = 'Suscripcion'
                y_titulo = 'Balance'
                agrupados = False
                x_min = 0
                x_max = 0
                amplitud =0
                hist_suscripcion_bal_2 = histograma(varX, tit, subtit, col, cods,
                                       textoA, x_titulo, y_titulo,
                                       agrupados, x_min, x_max,
                                       amplitud, varY, pshape
                                       )
                st.plotly_chart(hist_suscripcion_bal_2, width='stretch')

            col3, col4, col5 = st.columns(3)
            xvar = 'y'
            yvar = 'balance'

            with col3:
                col = 'y'
                cds = ['Olive', 'red']
                titulo = 'Balance del cliente'
                x_titulo = 'Suscripcion'
                y_titulo = 'Balance'
                box_suscripcion_bal_1 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                               col, xvar)
                st.plotly_chart(box_suscripcion_bal_1, width='stretch')

            with col4:
                col = 'y'
                puntos = 'all'
                cds = ['Olive', 'Magenta']
                titulo = 'Balance del cliente -todos los puntos'
                x_titulo = 'Suscripcion'
                y_titulo = 'Balance'
                box_suscripcion_bal_2 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                               col, xvar, puntos)
                st.plotly_chart(box_suscripcion_bal_2, width='stretch')

            with col5:
                col = 'marital'
                puntos = 'outliers'
                cds = ['Yellow', 'Green', 'Blue']
                titulo = 'Balance del cliente -Suscripcion por estado civil'
                x_titulo = 'Suscripcion'
                y_titulo = 'Balance'
                box_suscripcion_bal_3 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                               col, xvar, puntos)
                st.plotly_chart(box_suscripcion_bal_3, width='stretch')

            col6, col7 = st.columns(2)
            with col6:
                col = 'job'
                puntos = 'outliers'
                cds = ['Yellow', 'Green', 'Blue', 'Magenta', 'Red', 'Cyan']
                titulo = 'Balance del cliente -Suscripcion por trabajos'
                x_titulo = 'Suscripcion'
                y_titulo = 'Balance'
                box_suscripcion_bal_4 = boxplt1(yvar, cds, titulo, x_titulo, y_titulo,
                               col, xvar, puntos)
                st.plotly_chart(box_suscripcion_bal_4, width='stretch')

elif op == 'Estadistica':

    st.sidebar.markdown('---')
    st.sidebar.header('Análisis exploratorio')
    opcion_explora = st.sidebar.selectbox('Selecciona:',
                                          ['Visualizar DataFrame', 'Descripcion por Variable',
                                           'Cuartiles', 'T Frecuencias No Agrupados',
                                           'T Frecuencias Agrupados', 'Medidas Centrales',
                                           'Medidas de Dispersión']
                                          )

    if opcion_explora == 'Visualizar DataFrame':
        with st.expander('Data Set: Banco', expanded=False):
            st.markdown('''
                El Data Set es un conjunto de datos de Marketing Bancario
                Incluye información sobre los clientes, que incluye
                * **age**. Edad del cliente.
                * **job**. Tipo de trabajo.
                * **marital**. Estado civil.
                * **education**. Nivel academico.
                * **y**. Si el cliente suscribio el deposito a plazo (yes / no).
                * **balance**. Saldo promedio.
                * **campaign**. Numero de contactos realizados en la campana.
                * **duration**. Duracion de la llamada en segundos.
                ''')

        df_limpio = df.copy()
        for col in df_limpio.columns:
            if str(df_limpio[col].dtype) in ['Int64', 'Float64', 'boolean']:
                df_limpio[col] = df_limpio[col].astype(object)

        st.dataframe(df_limpio, width= 'stretch')
        col1, col2, col3 = st.columns(3, border=True)

        with col1:
            st.markdown("**Tipos de datos**")
            tipos_df = df.dtypes.astype(str)
            st.dataframe(tipos_df, width= 'stretch')

        with col2:
            st.markdown("**Informacion general**")
            info = io.StringIO()
            df.info(buf=info)
            info_df = info.getvalue()
            st.code(info_df, language=None)

        with col3:
            st.markdown("**Describe df**")
            describ = df.describe(include='all')
            desrib_limpio = describ.astype(str)
            desrib_limpio = desrib_limpio.replace('nan','-')
            st.dataframe(desrib_limpio, width= 'stretch')

    elif opcion_explora == 'Descripcion por Variable':
        col1, col2, col3 = st.columns(3, border=False)

        with col1:
            var_col = list(df.columns)
            opcion_col = st.selectbox('Selecciona la variable (describe()): ', var_col)

        with col2:
            describe_col = df[opcion_col].describe()
            desrib_col_limpio = describe_col.astype(str)
            st.dataframe(desrib_col_limpio, width= 'stretch')

    elif opcion_explora == 'Cuartiles':
        col1, col2, col3 = st.columns([0.3,0.2,0.5], border=False)

        with col1:
            opcion_col = st.selectbox('Selecciona la variable (cuartiles): ',
                                      ['age','duration','campaign','balance'])

        with col2:
            cuartiles = df[opcion_col].quantile([0.25,0.50,0.75])
            st.write(cuartiles)

    elif opcion_explora == 'T Frecuencias No Agrupados':
        col1, col2, col3 = st.columns([0.2, 0.6, 0.2], border=False)

        with col1:
            opcion_col = st.selectbox('Selecciona la variable (Tabla Frecuencias): ',
                                      ['job', 'campaign'])

        with col2:
            tablaF = sorted(df[opcion_col].unique())
            colF = df[opcion_col]
            nomColF = opcion_col
            t_f = tablaFrecuencia(tablaF, colF, nomColF)
            st.write(t_f)

    elif opcion_explora == 'T Frecuencias Agrupados':
        col1, col2, col3 = st.columns([0.2, 0.6, 0.2], border=False)

        with col1:
            opcion_col = st.selectbox('Selecciona la variable (Tabla Frecuencias): ',
                                      ['duration', 'balance'])

        with col2:
            nomCol = opcion_col
            var_col = df[opcion_col]
            t_fA = tabla_Hist(var_col, nomCol)
            st.write(t_fA)

    elif opcion_explora == 'Medidas Centrales':
        col1, col2, col3, col4 = st.columns(4, border=False)
        with col1:
            opcion_col = st.selectbox('Selecciona la variable (Medidas Centrales): ',
                                      ['age', 'duration', 'campaign', 'balance'])

        with col2:
            media_v = df[opcion_col].mean()
            st.metric('Media', '%0.2f' % media_v)
        with col3:
            mediana_v = df[opcion_col].median()
            st.metric('Mediana', '%0.2f' % mediana_v)
        with col4:
            moda_v = df[opcion_col].mode()
            st.metric('Moda', '%0.2f' % moda_v.iloc[0])

    elif opcion_explora == 'Medidas de Dispersión':
        col1, col2, col3, col4, col5, col6 = st.columns(6, border=False)

        with col1:
            opcion_col = st.selectbox('Selecciona la variable (Medidas de dispercion): ',
                                      ['age', 'duration', 'campaign', 'balance'])

        with col2:
            rango_v = df[opcion_col].max() - df[opcion_col].min()
            st.metric('Rango', '%0.2f' % rango_v)

        with col3:
            varianza_v = df[opcion_col].var()
            st.metric('Varianza', '%0.2f' % varianza_v)

        with col4:
            std_v = df[opcion_col].std()
            st.metric('Desviacion estandar', '%0.2f' % std_v)

        with col5:
            asimetria_v = df[opcion_col].skew()
            st.metric('Asimetria', '%0.3f' % asimetria_v)

        with col6:
            curtosis_v = df[opcion_col].kurt()
            st.metric('Curtosis', '%0.3f' % curtosis_v)