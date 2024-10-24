import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# Sidebar para upload dos arquivos
st.sidebar.title("Upload de Arquivos")
uploaded_file_2023 = st.sidebar.file_uploader("Carregar dados de terremotos de 2023", type=["csv"])
uploaded_file_2024 = st.sidebar.file_uploader("Carregar dados de terremotos de 2024", type=["csv"])

# Inicializa as variáveis de dados
earthquakes_2023 = None
earthquakes_2024 = None

# Carregar os dados quando os arquivos forem enviados
if uploaded_file_2023 is not None:
    earthquakes_2023 = pd.read_csv(uploaded_file_2023)
if uploaded_file_2024 is not None:
    earthquakes_2024 = pd.read_csv(uploaded_file_2024)

# Sidebar para navegação entre páginas
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione a página:", ["Página 1 - Resumo Geral", "Página 2 - Análise Comparativa"])

# Função para exibir gráficos
def plot_histogram(data):
    fig, ax = plt.subplots()
    ax.hist(data['magnitude'], bins=30, alpha=0.7, color='blue')
    ax.set_title('Distribuição da Magnitude dos Terremotos')
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Frequência')
    st.pyplot(fig)

def plot_scatter(data):
    fig, ax = plt.subplots()
    ax.scatter(data['depth'], data['magnitude'], alpha=0.5)
    ax.set_title('Magnitude vs Profundidade')
    ax.set_xlabel('Profundidade (km)')
    ax.set_ylabel('Magnitude')
    st.pyplot(fig)

def plot_heatmap(data):
    # Cria um mapa de calor
    m = folium.Map(location=[0, 0], zoom_start=2)
    heat_data = [[row['latitude'], row['longitude']] for index, row in data.iterrows()]
    HeatMap(heat_data).add_to(m)

    # Use st_folium para renderizar o mapa no Streamlit
    st_folium(m, width=700)  # Ajuste a largura conforme necessário

# Página 1: Resumo Geral dos Terremotos
if page == "Página 1 - Resumo Geral":
    st.title("Resumo Geral dos Terremotos")

    # Combina os dados de 2023 e 2024
    combined_data = pd.DataFrame()

    if earthquakes_2023 is not None:
        earthquakes_2023['year'] = 2023  # Adiciona coluna do ano
        combined_data = pd.concat([combined_data, earthquakes_2023], ignore_index=True)

    if earthquakes_2024 is not None:
        earthquakes_2024['year'] = 2024  # Adiciona coluna do ano
        combined_data = pd.concat([combined_data, earthquakes_2024], ignore_index=True)

    # Filtrando dados com base nos filtros da sidebar
    if not combined_data.empty:
        # Convertendo a coluna 'date' para datetime, permitindo formatos mistos
        combined_data['date'] = pd.to_datetime(combined_data['date'], errors='coerce', utc=True)

        # Remover entradas com data inválida (se houver)
        combined_data = combined_data.dropna(subset=['date'])

        # Adicionando filtros dinâmicos
        start_date = st.date_input("Data de Início", value=pd.to_datetime("2023-01-01").date())
        end_date = st.date_input("Data de Fim", value=pd.to_datetime("2024-12-31").date())
        min_magnitude = st.slider("Magnitude Mínima:", min_value=0.0, max_value=10.0, value=0.0)
        max_magnitude = st.slider("Magnitude Máxima:", min_value=0.0, max_value=10.0, value=10.0)

        # Convertendo start_date e end_date para o mesmo fuso horário UTC
        start_date = pd.to_datetime(start_date).tz_localize('UTC')
        end_date = pd.to_datetime(end_date).tz_localize('UTC')

        # Filtrando os dados
        filtered_data = combined_data[
            (combined_data['date'] >= start_date) &
            (combined_data['date'] <= end_date) &
            (combined_data['magnitude'] >= min_magnitude) &
            (combined_data['magnitude'] <= max_magnitude)
            ]

        # Exibir os gráficos

        # Tabela de detalhes
        st.subheader("Tabela de Detalhes dos Terremotos (obs.: Demora a carregar)")
        st.dataframe(filtered_data[['date', 'magnitude', 'latitude', 'longitude', 'depth', 'place', 'tsunami', 'alert', 'year']])

        st.subheader("Histograma de Magnitude")
        plot_histogram(filtered_data)

        st.subheader("Gráfico de Dispersão (Magnitude vs Profundidade)")
        plot_scatter(filtered_data)

        st.subheader("Mapa de Calor de Localização de Terremotos")
        plot_heatmap(filtered_data)

# Página 2: Análise Comparativa entre 2023 e 2024
if page == "Página 2 - Análise Comparativa":
    st.title("Análise Comparativa entre 2023 e 2024")

    if earthquakes_2023 is not None and earthquakes_2024 is not None:
        # Convertendo 'time' para datetime no dataset de 2023
        earthquakes_2023['month'] = pd.to_datetime(earthquakes_2023['time'], errors='coerce').dt.to_period('M')

        # Convertendo 'date' para datetime no dataset de 2024
        earthquakes_2024['month'] = pd.to_datetime(earthquakes_2024['date'], errors='coerce').dt.to_period('M')

        # Gráficos de contagem de terremotos por mês
        monthly_counts_2023 = earthquakes_2023['month'].value_counts().sort_index()
        monthly_counts_2024 = earthquakes_2024['month'].value_counts().sort_index()

        fig, ax = plt.subplots()
        ax.plot(monthly_counts_2023.index.astype(str), monthly_counts_2023.values, label='2023', marker='o')
        ax.plot(monthly_counts_2024.index.astype(str), monthly_counts_2024.values, label='2024', marker='o')
        ax.set_title('Total de Terremotos por Mês')
        ax.set_xlabel('Mês')
        ax.set_ylabel('Número de Terremotos')
        ax.legend()
        st.pyplot(fig)

        # Gráfico de barras de média de magnitude por ano
        avg_mag_2023 = earthquakes_2023['mag'].mean()  # Verifique se o nome da coluna é 'magnitude'
        avg_mag_2024 = earthquakes_2024['magnitude'].mean()  # Verifique se o nome da coluna é 'magnitude'

        fig, ax = plt.subplots()
        ax.bar(['2023', '2024'], [avg_mag_2023, avg_mag_2024], color=['orange', 'green'])
        ax.set_title('Média de Magnitude por Ano')
        ax.set_ylabel('Magnitude Média')
        st.pyplot(fig)

        # Gráfico de pizza com contagem de terremotos por lugar
        place_counts_2023 = earthquakes_2023['place'].value_counts().head(10)  # Top 10 locais
        place_counts_2024 = earthquakes_2024['place'].value_counts().head(10)  # Top 10 locais

        # Gráfico de pizza para 2023
        fig, ax = plt.subplots()
        ax.pie(place_counts_2023, labels=place_counts_2023.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribuição de Terremotos por Lugar em 2023')
        st.pyplot(fig)

        # Gráfico de pizza para 2024
        fig, ax = plt.subplots()
        ax.pie(place_counts_2024, labels=place_counts_2024.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribuição de Terremotos por Lugar em 2024')
        st.pyplot(fig)

        # Valor total de terremotos registrados
        total_earthquakes = len(earthquakes_2023) + len(earthquakes_2024)
        st.write(f"Total de Terremotos Registrados: {total_earthquakes}")

