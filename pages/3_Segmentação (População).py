import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
import numpy as np

st.title('Segmentação (População)')

# Leitura do CSV
dadosTotal = pd.read_csv('dataset/DADOS_IFOOD_MUNICIPIO.csv', encoding='latin1', delimiter=';')

cutoff_value = 10 # % ideal de resturantes por cidade




########################
def categorize_populacao(pop):
    if pop < 200000:
        return 'a) 0-200.000 habitantes'
    elif pop < 400000:
        return 'b) 200.000-400.000 habitantes'
    elif pop < 600000:
        return 'c) 400.000-600.000 habitantes'
    elif pop < 800000:
        return 'd) 600.000-800.000 habitantes'
    elif pop < 1000000:
        return 'e) 800.000-1.000.000 habitantes'
    else:
        return 'f) 1.000.000+ habitantes'




dadosTotal['FAIXA_POPULACAO'] = dadosTotal['POPULACAO'].apply(categorize_populacao)

#Criando o filtro
opcoes_tipo_municipio = sorted(dadosTotal['FAIXA_POPULACAO'].unique())
option = st.selectbox('Selecione o tipo de cidade', opcoes_tipo_municipio)



#selecionando os dados
dadosTotal_filtered = dadosTotal[dadosTotal['FAIXA_POPULACAO'] == option]

df_grouped = dadosTotal_filtered.groupby(['UF', 'CIDADE']).agg({
    'POPULACAO': 'max',
    'CHS': 'max',
    'RESTAURANTES': 'max',
    'RECEITA_RESTAURANTE_ATIVO': 'max'

}).reset_index()

# Adiciona a nova coluna com o cálculo
df_grouped['REST_COBERTURA'] = (df_grouped['RESTAURANTES'] / df_grouped['RECEITA_RESTAURANTE_ATIVO']) * 100.00
# Ajusta os valores da coluna COBERTURA para que não excedam 100
df_grouped['REST_COBERTURA'] = df_grouped['REST_COBERTURA'].clip(upper=100)

# Adiciona a nova coluna com o cálculo
df_grouped['CHS %'] = (df_grouped['CHS'] / df_grouped['POPULACAO']) * 100.00
# Ajusta os valores da coluna COBERTURA para que não excedam 100
df_grouped['CHS %'] = df_grouped['CHS %'].clip(upper=100)

################################################################
st.subheader('População coberta', divider='rainbow')

# Exemplo de texto com quebras de linha
texto = """
 - O campo ESTRATEGIA considera quais cidades são potenciais candidatas a expansão. O cálculo se baseia
 na média do CHS % (cobertura da população) e na média de REST_COBERTURA(cobertura por restaurantes que existem na cidade mas
que ainda não são clientes)
 - Cidades que estão com valores abaixo das duas médias são marcadas como POTENCIAL e pode indicar pequena
 cobertura da população e grande potencial de novos restaurantes.
 """
st.markdown(texto)

# Obter o maior valor da coluna 'População'
maior_MUB_Perc = df_grouped['CHS %'].max()
media_MUB_Perc = df_grouped['CHS %'].median()

media_Cobertura_Perc = df_grouped['REST_COBERTURA'].median()



df_grouped['ESTRATEGIA'] = 'SEM POTENCIAL'
df_grouped.loc[(df_grouped['CHS %'] < media_Cobertura_Perc) 
               & (df_grouped['REST_COBERTURA'] < media_Cobertura_Perc), 'ESTRATEGIA'] = 'POTENCIAL'



# Supondo que seu dataframe seja df
agrupado = df_grouped.groupby('ESTRATEGIA').agg({
    'CIDADE': 'count',
    'POPULACAO': 'sum',
    'RECEITA_RESTAURANTE_ATIVO': 'sum',
    'RESTAURANTES': 'sum'
}).reset_index()

# Calculando a diferença entre RESTAURANTE_ATIVO e RESTAURANTE
agrupado['RESTAURANTES POTENCIAL EXPANSAO'] = agrupado['RECEITA_RESTAURANTE_ATIVO'] - agrupado['RESTAURANTES']

st.subheader('Resultado para expansão', divider='rainbow')

st.dataframe(agrupado[['ESTRATEGIA','CIDADE', 'RESTAURANTES POTENCIAL EXPANSAO', 'POPULACAO']], hide_index=True,use_container_width=True)



st.subheader('Detalhamento', divider='rainbow')

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Média CHS %", value=f"{media_MUB_Perc:.2f}%")
with col2:
    st.metric(label="Média Cobertura %", value=f"{media_Cobertura_Perc:.2f}%")

st.dataframe(df_grouped,hide_index=True,use_container_width=True)
