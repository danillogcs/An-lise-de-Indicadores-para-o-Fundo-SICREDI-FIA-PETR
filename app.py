# import das bibliotecas
import pandas as pd
import plotly.express as px
import yfinance as yf
import pandas_datareader.data as pdr 
from datetime import datetime
import numpy as np
import streamlit as st

# Leitura dos Dados

dados_bruto_diario = pd.read_csv('Dados_Inicio_Fim_Dia_SICREDIPETR.csv') # Dados do Fundo 

dados_selic = pd.read_csv("Dados_Selic_CSV.csv", decimal=',') # Dados da Selic

dados_ibov = pd.read_csv('Dados_Ibov_CSV.csv') # Dados do Ibovespa (Benchmark)

# Tratamento inicial dos dados do Fundo

dados_sicredi_cru = dados_bruto_diario[['DT_COMPTC', 'VL_QUOTA']]

    ## Datas para o formato DateTime

#dados_sicredi_cru['DT_COMPTC'] = pd.to_datetime(dados_sicredi_cru['DT_COMPTC'])

dados_sicredi_cru['DT_COMPTC'] = pd.to_datetime(dados_sicredi_cru['DT_COMPTC'])

    ## Novo DF para os Cálculos

dados_sicredi = dados_sicredi_cru[['DT_COMPTC', 'VL_QUOTA']]

    ## Datas como índice

dados_sicredi.set_index('DT_COMPTC', inplace=True)

# Tratamento inicial dos dados da Selic

    ## Tratar dados - Data e Valor de str para datetime e numeric 

dados_selic['selic_ao_dia'] = pd.to_numeric(dados_selic['selic_ao_dia']) # 'selic_ao_dia' informa qual o retorno diário da taxa selic em %

dados_selic.columns = ['Data'] + list(dados_selic.columns[1:])

dados_selic['Data'] = dados_sicredi_cru['DT_COMPTC']

# Tratamento inicial dos dados do Ibovespa

    ## Renomear colunas para facilitar o acesso

dados_ibov = dados_ibov.rename(columns={'Adj Close':'Adj_Close'}) 

dados_ibov = dados_ibov.rename(columns={'Date':'Data'})

    ## Filtrar dados úteis

dados_ibov = dados_ibov[['Data', 'Adj_Close']]

    ## Conversão da data para datetime format e das cotações para numeric format

dados_ibov['Data'] = pd.to_datetime(dados_ibov['Data'])

dados_ibov['Adj_Close'] = pd.to_numeric(dados_ibov['Adj_Close'])

    ## Datas como índice

dados_ibov.set_index('Data', inplace=True)

# Combinação dos DataFrames em um

dados_combinados1 = pd.merge(dados_sicredi,dados_selic,how='outer',left_index=True,right_on='Data')

dados_combinados1.set_index('Data',inplace=True)

dados_combinados1 = pd.merge(dados_combinados1,dados_ibov,how='outer',left_index=True, right_index=True)

# Cálculo dos Indicadores Técnicos

    ## Retornos e LogRetornos do Ibov

dados_ibov['Retorno_Diario_Ibov(%)'] = dados_ibov['Adj_Close'].pct_change()*100

dados_ibov['Log_Return_Ibov(%)'] = np.log(dados_ibov['Adj_Close']/dados_ibov['Adj_Close'].shift(1))*100

    ## Retorno Diário do Fundo

dados_combinados1['Retornos_Diarios'] = dados_combinados1['VL_QUOTA'].pct_change()

dados_combinados1['Retornos_Diarios(%)'] = dados_combinados1['Retornos_Diarios']*100

    ## LogRetorno do Fundo

dados_combinados1['Log_Return(%)'] = np.log(dados_combinados1['VL_QUOTA']/dados_combinados1['VL_QUOTA'].shift(1))*100

    ## Volatilidade diária anualizada

dados_combinados1['Volatilidade_Dia'] = ((dados_combinados1['Retornos_Diarios'].rolling(window=22)).std())*np.sqrt(252)

dados_combinados1['Volatilidade_Dia(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=22)).std())*np.sqrt(252)

    ## Índice Sharpe no fechamento de cada dia

dados_combinados1['Sharpe/Dia'] = (dados_combinados1['Retornos_Diarios(%)'] - dados_combinados1['selic_ao_dia']) / dados_combinados1['Volatilidade_Dia(%)']

# Visualização dos Dados com Plotly

dados_combinados1['Retorno_Diario_Ibov(%)'] = dados_ibov['Retorno_Diario_Ibov(%)']

dados_combinados1_clean = dados_combinados1.dropna(subset=['Retornos_Diarios(%)', 'selic_ao_dia', 'Retorno_Diario_Ibov(%)'])

    ## Rentabilidade Diária

graph_return = px.line(dados_combinados1_clean, 
                       x=dados_combinados1_clean.index, 
                       y='Retornos_Diarios(%)', 
                       title='Rentabilidade Diária (%)')

graph_return.update_layout(template='plotly_dark', title_font_size=24, title_x=0.5)

graph_return.update_traces(line=dict(width=2))

###graph_return.show()

    ## LogRetorno

graph_LOG_return = px.line(dados_combinados1_clean, 
                           x=dados_combinados1_clean.index, 
                           y='Log_Return(%)', 
                           title='Gráfico com Log Retorno(%) (diário) do Fundo')

graph_LOG_return.update_layout(template='plotly_dark', title_font_size=24, title_x=0.5)

graph_LOG_return.update_traces(line=dict(width=2)) 

###graph_LOG_return.show()

    ## Rentabilidade Diária x Selic x Ibovespa

graph_fundreturn_selic_ibovreturn = px.line(dados_combinados1_clean, 
                                            x=dados_combinados1_clean.index, 
                                            y=['Retornos_Diarios(%)',
                                               'selic_ao_dia',
                                               'Retorno_Diario_Ibov(%)'],
                                            title='Rentabilidade Diária x Selic x Ibovespa')

graph_fundreturn_selic_ibovreturn.update_layout(template='plotly_dark', title_font_size=24, title_x=0.5)

graph_fundreturn_selic_ibovreturn.update_traces(line=dict(width=2))                                                                                             

###graph_fundreturn_selic_ibovreturn.show()

    ## Volatilidade Diária (%)

graph_volatility_daily = px.line(dados_combinados1_clean, 
                                 x=dados_combinados1_clean.index, 
                                 y='Volatilidade_Dia(%)', 
                                 title='Volatilidade Diária do Fundo (%)')

graph_volatility_daily.update_layout(template='plotly_dark', title_font_size=24, title_x=0.5)

graph_volatility_daily.update_traces(line=dict(width=2))

###graph_volatility_daily.show()

# Cálculo dos Indicadores Técnicos em diferentes Janelas Temporais

    ## Retornos

        ### 1 mês

dados_combinados1['Retorno_1M(%)'] = dados_combinados1['VL_QUOTA'].pct_change(periods=21)*100 # 21 dias / mês
        
        ### 3 meses

dados_combinados1['Retorno_3M(%)'] = dados_combinados1['VL_QUOTA'].pct_change(periods=65)*100 # 65 dias / 03 meses
        
        ### 6 meses

dados_combinados1['Retorno_6M(%)'] = dados_combinados1['VL_QUOTA'].pct_change(periods=123)*100 # 123 dias / 06 meses

        ### 12 meses

dados_combinados1['Retorno_12M(%)'] = dados_combinados1['VL_QUOTA'].pct_change(periods=252)*100 # 252 dias / 12 meses

        ### 24 meses

dados_combinados1['Retorno_24M(%)'] = dados_combinados1['VL_QUOTA'].pct_change(periods=503)*100 # 503 dias / 24 meses

        ### 36 meses

dados_combinados1['Retorno_36M(%)'] = dados_combinados1['VL_QUOTA'].pct_change(periods=752)*100 # 752 dias / 36 meses

    ## Volatilidade

        ### 1 mês

dados_combinados1['Volatilidade_Mensal(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=21)).std())*np.sqrt(252)

        ### 3 meses

dados_combinados1['Volatilidade_3M(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=65)).std())*np.sqrt(252)

        ### 6 meses

dados_combinados1['Volatilidade_6M(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=123)).std())*np.sqrt(252)

        ### 12 meses

dados_combinados1['Volatilidade_12M(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=252)).std())*np.sqrt(252)

        ### 24 meses

dados_combinados1['Volatilidade_24M(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=503)).std())*np.sqrt(252)

        ### 36 meses

dados_combinados1['Volatilidade_36M(%)'] = ((dados_combinados1['Retornos_Diarios(%)'].rolling(window=752)).std())*np.sqrt(252)

    ## Selic nas Janelas de Tempo para o Cálculo do Índice Sharpe nas Janelas de Tempo

dados_combinados1['selic_ao_mes'] = dados_combinados1['selic_ao_dia'].rolling(window=21).sum()

dados_combinados1['selic_3M'] = dados_combinados1['selic_ao_dia'].rolling(window=65).sum()

dados_combinados1['selic_6M'] = dados_combinados1['selic_ao_dia'].rolling(window=123).sum()

dados_combinados1['selic_12M'] = dados_combinados1['selic_ao_dia'].rolling(window=252).sum()

dados_combinados1['selic_24M'] = dados_combinados1['selic_ao_dia'].rolling(window=503).sum()

dados_combinados1['selic_36M'] = dados_combinados1['selic_ao_dia'].rolling(window=752).sum()

    ## Sharpe nas Janelas Temporais

dados_combinados1['IS_1M'] = (dados_combinados1['Retorno_1M(%)'] - dados_combinados1['selic_ao_mes']) / dados_combinados1['Volatilidade_Mensal(%)']

dados_combinados1['IS_3M'] = (dados_combinados1['Retorno_3M(%)'] - dados_combinados1['selic_3M']) / dados_combinados1['Volatilidade_3M(%)']

dados_combinados1['IS_6M'] = (dados_combinados1['Retorno_6M(%)'] - dados_combinados1['selic_6M']) / dados_combinados1['Volatilidade_6M(%)']

dados_combinados1['IS_12M'] = (dados_combinados1['Retorno_12M(%)'] - dados_combinados1['selic_12M']) / dados_combinados1['Volatilidade_12M(%)']

dados_combinados1['IS_24M'] = (dados_combinados1['Retorno_24M(%)'] - dados_combinados1['selic_24M']) / dados_combinados1['Volatilidade_24M(%)']

dados_combinados1['IS_36M'] = (dados_combinados1['Retorno_36M(%)'] - dados_combinados1['selic_36M']) / dados_combinados1['Volatilidade_36M(%)']

# Organização do DataFrame com todas as variáveis

dados_combinados1 = dados_combinados1[['Retorno_Diario_Ibov(%)', 'Log_Return_Ibov(%)',
                                       'selic_ao_dia', 'selic_ao_mes', 'selic_3M', 
                                       'selic_6M', 'selic_12M', 'selic_24M', 'selic_36M',
                                       'VL_QUOTA', 'Retornos_Diarios', 'Retornos_Diarios(%)', 'Log_Return(%)',
                                       'Volatilidade_Dia', 'Volatilidade_Dia(%)', 'Sharpe/Dia',
                                       'Retorno_1M(%)', 'Volatilidade_Mensal(%)', 'IS_1M',
                                       'Retorno_3M(%)', 'Volatilidade_3M(%)', 'IS_3M',
                                       'Retorno_6M(%)', 'Volatilidade_6M(%)', 'IS_6M',
                                       'Retorno_12M(%)', 'Volatilidade_12M(%)', 'IS_12M',
                                       'Retorno_24M(%)', 'Volatilidade_24M(%)', 'IS_24M',
                                       'Retorno_36M(%)', 'Volatilidade_36M(%)', 'IS_36M']]

# Cálculo de outros indicadores financeiros

    ## Beta



    ## Tracking Error



    ## Sortino Ratio



    ## Information Ratio



    ## Treynor Index

# Código em Streamlit para Apresentação dos Dados

st.title('DashBoard - SICREDI FIA PETROBRÁS') # Título da página

st.subheader('Tabela com Dados Financeiros Compilados') # Introdução para a tabela geral

st.dataframe(dados_combinados1) # Tabela completa

st.subheader('Dados da Variação Diária (%) dos Índices e do Fundo')

st.markdown('#### Tabela com Retornos (%) da Selic')

selic_janelas_tempo = dados_combinados1[['selic_ao_dia', 'selic_ao_mes', 'selic_3M', 'selic_6M', 
                                        'selic_12M', 'selic_24M', 'selic_36M']] # DataFrame com a Selic nas Janelas de Tempo

st.dataframe(selic_janelas_tempo) # Tabela com dados da Selic 

st.markdown('#### Tabela com Dados do Ibovespa')

dados_ibov = dados_ibov.rename(columns={'Adj_Close':'Cotação_Ibovespa'})

st.dataframe(dados_ibov) # Tabela com dados do Ibovespa

st.markdown('#### Tabela com Dados do Fundo')

dados_diarios_fundo = dados_combinados1[['VL_QUOTA', 'Retornos_Diarios', 'Retornos_Diarios(%)', 'Log_Return(%)',
                                       'Volatilidade_Dia', 'Volatilidade_Dia(%)', 'Sharpe/Dia']]

st.dataframe(dados_diarios_fundo) # Tabela com Dados diários do fundo

st.markdown('#### Tabela com Dados do Fundo nas Janelas de Tempo')

st.write('1 Mês, 3 Meses, 6 Meses, 12 Meses, 24 Meses e 36 Meses')

dados_fundo_janelas_tempo = dados_combinados1[['Retorno_1M(%)', 'Volatilidade_Mensal(%)', 'IS_1M',
                                       'Retorno_3M(%)', 'Volatilidade_3M(%)', 'IS_3M',
                                       'Retorno_6M(%)', 'Volatilidade_6M(%)', 'IS_6M',
                                       'Retorno_12M(%)', 'Volatilidade_12M(%)', 'IS_12M',
                                       'Retorno_24M(%)', 'Volatilidade_24M(%)', 'IS_24M',
                                       'Retorno_36M(%)', 'Volatilidade_36M(%)', 'IS_36M']]

st.dataframe(dados_fundo_janelas_tempo)

st.subheader('Visualização dos dados')

col1, col2 = st.columns(2)

with col1:
    st.markdown('#### Gráfico de Rentabilidade Diária(%)')
    st.plotly_chart(graph_return)

with col2:
    st.markdown('#### Gráfico de Rentabilidade Diária(%) x Ibovespa x Selic')
    st.plotly_chart(graph_fundreturn_selic_ibovreturn)

st.markdown('#### Gráfico de Volatilidade Diária(%)')

st.plotly_chart(graph_volatility_daily)

# Estilizar Página
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    </style>
    """,
    unsafe_allow_html=True
)