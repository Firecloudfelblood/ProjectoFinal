import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import plotly.express as px

@st.cache_data #cargando al cache los datos para que no se recarguen cada vez que se actualiza la app
def cargar_datos():
    return pd.read_csv('Datos/bank-full.csv')

df = cargar_datos()

# --- Obtener las metricas ------------

#costo medio de la poliza

si_casados = df[df['marital'] == 'married']
si_casados_media = si_casados['balance'].mean()

no_casados = df[df['marital'] == 'single']
no_casados_media = no_casados['balance'].mean()

divorciados = df[df['marital'] == 'divorced']
divorciados = divorciados['balance'].mean()

#Cantidad de maritales

maritales = df['marital'].value_counts()
solteros = maritales.iloc[0]
casados = maritales.iloc[1]
otro = maritales.iloc[2]

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
                        )
    # return grafica

    #--- Grafica de scatter:-----------
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

    graf_dens = ff.create_distplot([var], [etiqueta],
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
        height=400
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
grafica_sunburst = px.sunburst(df, path=['education', 'marital', 'housing'],
                               values='balance', color='balance',
                               color_continuous_scale=px.colors.cyclical.IceFire)

grafica_sunburst.update_traces(marker=dict(line=dict(color='purple', width=1)))

grafica_sunburst.update_layout(title='Saldos bancarios por educación, estado civil y vivienda',
                               font_color='black',
                               font=dict(family='Courier New, monospace',
                                         size=14,
                                         color='purple'),
                               paper_bgcolor='white',
                               height=400
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
    #paso 1 determinar el tamano de la muestra
    print('Variable: ' + nomCol + '\n')
    n = len(varCol)
    print('Paso 1 tamano de la mustra: ', n,'\n')

    #Paso 2 determinar el maximo y el minimo
    x_max = varCol.max()
    x_min = varCol.min()
    print('Paso 2# Maximo y Minimo: ')
    print('Maximo: ', x_max)
    print('Minimo: ', x_min, '\n')

    # Paso 3 calcular el recorrido
    recorrido = x_max - x_min
    print('Paso 3: Recorrido ' , recorrido, '\n')

    #paso 4 calcular intervalos(clases)
    #Formula Sturged(1 + 3.3 log n)
    intervalos = round(1 + (3.3 *(math.log10(n))))
    print('Paso 4: Intervalos: ', intervalos, '\n')

    # Paso 5: calcular  la amplitud de cada intervalo
    amplitud = recorrido / intervalos
    print('Paso 5: Amplitud ', '%0.2f', amplitud , '\n')

    #Paso 6: construidr la tabla de frecuenciass
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
st.text('Indicadore generales para el Dataset Poliza de seguro para gastos medicos')

# --- Visualizacion metricas generales ----------

colm1, colm2, colm3, colm4 = st.columns(4, vertical_alignment='center',
                                        border=True)