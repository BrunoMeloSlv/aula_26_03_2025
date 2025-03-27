import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd
import lxml
import plotly.express as px #plotly==5.15.0


#### Tabela Brasileirão

tabela = pd.read_html('https://fbref.com/en/comps/24/Serie-A-Stats')

tabela_brasileirao = tabela[0]
tabela_brasileirao.head()


tabela_brasileirao.rename(
    columns={
        'Rk':'Posição',
        'Squad':'Time',
        'MP':'Jogos',
        'W':'Vitórias',
        'D':'Empates',
        'L':'Derrotas',
        'GF':'Gols Pró',
        'GA':'Gols Contra',
        'GD':'Saldo de Gols',
        'Pts':'Pontos',
        'Pts/MP':'Pontos por partida'
    }, inplace=True
)

tabela_brasileirao= tabela_brasileirao.iloc[:,0:14]

colunas = list(tabela_brasileirao.columns)
colunas.insert(2, colunas.pop(colunas.index('Pontos')))
tabela_brasileirao = tabela_brasileirao[colunas]

tabela_brasileirao['Aproveitamento'] = ((tabela_brasileirao['Pontos'] / (tabela_brasileirao['Jogos'] * 3)) * 100).round(2)

#### Design tabela brasileirao

def aplicar_estilos(df):
    # Definir estilos de cor de fundo e fonte para diferentes posições
    def estilos_linhas(s):
        if s.name < 4:  # Top 4
            return ['background-color: #023047; color: white'] * len(s)
        elif s.name == 4 or s.name == 5:  # 5º e 6º lugar
            return ['background-color: #dad7cd; color: black'] * len(s)
        elif s.name >= len(df) - 4:  # Últimos 4 lugares
            return ['background-color: #c1121f; color: white'] * len(s)
        else:
            return [''] * len(s)
    
    styled_df = df.style.apply(estilos_linhas, axis=1)
    return styled_df


##### Importar tabela

transfermarket = pd.read_excel('transfermarket.xlsx')

hist = pd.read_csv('brasileirao.csv')



#### Dashboard / APP

st.set_page_config(page_title="Dashboard Transfermarkt", layout="wide")

st.title('Dashboard Brasileirão 2025 ⚽')

abas = st.tabs(['Classificação','Valor de Mercado','Probabilidades','Histórico'])


with abas[0]:

    st.subheader("Classificação do Campeonato Brasileiro de Futebol 2025")

    tabela_brasileirao['Pontos por partida'] = tabela_brasileirao['Pontos por partida'].astype(float).map("{:.2f}".format)
    tabela_brasileirao['xG'] = tabela_brasileirao['xG'].astype(float).map("{:.2f}".format)
    tabela_brasileirao['xGA'] = tabela_brasileirao['xGA'].astype(float).map("{:.2f}".format)
    tabela_brasileirao['xGD'] = tabela_brasileirao['xGD'].astype(float).map("{:.2f}".format)
    tabela_brasileirao['Aproveitamento'] = tabela_brasileirao['Aproveitamento'].astype(float).map("{:.2f}".format)
    
    # Exibir tabela de classificação com estilos personalizados e sem índice
    st.markdown(aplicar_estilos(tabela_brasileirao).hide(axis='index').to_html(), unsafe_allow_html=True)

with abas[1]: #valor de mercado
    #Criar filtro de clube
    clubes = transfermarket["Equipe"].unique()
    clube_selecionado = st.selectbox("Selecione um clube:", clubes)

    # Filtrar os dados com base no clube selecionado
    df_filtrado = transfermarket[transfermarket["Equipe"] == clube_selecionado]

    # Cálculo dos KPIs
    valor_total = df_filtrado["Valor em Reais"].sum()   # Convertendo para milhões
    media_valor = df_filtrado["Valor em Reais"].mean()   # Convertendo para milhões
    media_idade = df_filtrado["Idade"].astype(float).mean()
    quantidade_jogadores = df_filtrado.shape[0]

    # Exibir KPIs
    st.markdown("### 📌 Indicadores do Clube")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Valor Total do Elenco", f"R$ {valor_total:,.2f}")
    col2.metric("⚖ Média Valor/Jogador", f"R$ {media_valor:,.2f}")
    col3.metric("📊 Média de Idade", f"{media_idade:.1f} anos")
    col4.metric("🏃‍♂️ Quantidade de Jogadores", quantidade_jogadores)

    # Exibir tabela detalhada
    st.markdown("### 📋 Jogadores da Equipe")
    st.dataframe(df_filtrado[["Jogador", "Posição", "Idade", "Valor em Reais"]])
with abas[2]: # probabilidade      
  ####
  with st.expander("Sobre o Conjunto de Dados"):
        st.write("""
        Este visual ainda não pode ser exibido porque não temos dados do Brasileirão. Dessa forma, a divisão por zero tende ao infinito, resultando em um erro no momento em que rodamos o código. 
        """)
with abas[3]: 
    with st.expander("Sobre o Conjunto de Dados"):
        st.write("""
        Este conjunto de dados utiliza exclusivamente informações do Campeonato Brasileiro de Futebol no período de 2003 a 2023. 
        """)

   # Filtrar os dados onde 'Posição' é igual a 1
    times_campeoes = hist[hist['place'] == 1]

    # Contar a quantidade de vezes que cada time ficou na posição 1
    contagem_times = times_campeoes['team'].value_counts().reset_index()
    contagem_times.columns = ['Time', 'Quantidade']

    # Ordenar os times pelo número de vezes que ficaram na posição 1
    contagem_times = contagem_times.sort_values(by='Quantidade', ascending=False)

    # Criar o gráfico com o Plotly
    fig = px.bar(contagem_times, x='Time', y='Quantidade', text='Quantidade', title='Times Campeões',
                labels={'Time': 'Time', 'Quantidade': 'Quantidade'})

    # Personalizar cores
    fig.update_traces(marker_color='#023047')

    # Adicionar rótulos
    fig.update_layout(yaxis_title='Quantidade', xaxis_title='Time')

    # Criar um filtro para temporada
    temp = st.selectbox("Selecione a Temporada:", hist['season'].unique())

    # Filtrar os dados pela temporada selecionada e remover a coluna 'season'
    hist_filtrado = hist[hist['season'] == temp].drop(columns=['season']).reset_index(drop=True)

    # Função para calcular o percentual
    def calcular_percentual(df):
        total_jogos = df['won'].sum() + df['draw'].sum() + df['loss'].sum()
        df['Percentual_vitórias'] = df['won'] / total_jogos
        df['Percentual_empates'] = df['draw'] / total_jogos
        df['Percentual_derrotas'] = df['loss'] / total_jogos
        return df

    # Exibir os gráficos
    

    # Exibir a tabela completa
    st.table(hist_filtrado)
    st.plotly_chart(fig)