import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

#Sidebar
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione a página:", ["Página 1 - Resumo Geral", "Página 2 - Análise Comparativa"])

st.sidebar.title("Upload de Arquivos")
uploaded_file_2023 = st.sidebar.file_uploader("Carregar dados de terremotos de 2023", type=["csv"])
uploaded_file_2024 = st.sidebar.file_uploader("Carregar dados de terremotos de 2024", type=["csv"])

# Dados
earthquakes_2023 = None
earthquakes_2024 = None

if uploaded_file_2023 is not None:
    earthquakes_2023 = pd.read_csv(uploaded_file_2023)
if uploaded_file_2024 is not None:
    earthquakes_2024 = pd.read_csv(uploaded_file_2024)

#Funções
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
    m = folium.Map(location=[0, 0], zoom_start=2)
    heat_data = [[row['latitude'], row['longitude']] for index, row in data.iterrows()]
    HeatMap(heat_data).add_to(m)
    st_folium(m, width=700)

def plot_monthly_average_magnitude(data):
    data['month'] = pd.to_datetime(data['date']).dt.month
    monthly_avg_magnitude = data.groupby('month')['magnitude'].mean()
    fig, ax = plt.subplots()
    monthly_avg_magnitude.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Média de Magnitude dos Terremotos por Mês')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Magnitude Média')
    ax.set_xticks(range(12))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
    st.pyplot(fig)

# Página 1: Resumo Geral dos Terremotos
if page == "Página 1 - Resumo Geral":
    st.title("Resumo Geral dos Terremotos")

    # Combinação dos dados de 2023 e 2024
    combined_data = pd.DataFrame()

    if earthquakes_2023 is not None:
        earthquakes_2023['year'] = 2023  # Adiciona coluna do ano
        combined_data = pd.concat([combined_data, earthquakes_2023], ignore_index=True)

    if earthquakes_2024 is not None:
        earthquakes_2024['year'] = 2024  # Adiciona coluna do ano
        combined_data = pd.concat([combined_data, earthquakes_2024], ignore_index=True)

    # Filtros dos dados
    if not combined_data.empty:

        combined_data['date'] = pd.to_datetime(combined_data.get('date', combined_data.get('time')), errors='coerce', utc=True)

        combined_data = combined_data.dropna(subset=['date'])

        start_date = st.date_input("Data de Início", value=pd.to_datetime("2023-01-01").date())
        end_date = st.date_input("Data de Fim", value=pd.to_datetime("2024-12-31").date())
        min_magnitude = st.slider("Magnitude Mínima:", min_value=0.0, max_value=10.0, value=0.0)
        max_magnitude = st.slider("Magnitude Máxima:", min_value=0.0, max_value=10.0, value=10.0)

        start_date = pd.to_datetime(start_date).tz_localize('UTC')
        end_date = pd.to_datetime(end_date).tz_localize('UTC')

        filtered_data = combined_data[
            (combined_data['date'] >= start_date) &
            (combined_data['date'] <= end_date) &
            (combined_data['magnitude'] >= min_magnitude) &
            (combined_data['magnitude'] <= max_magnitude)
            ]

        # Tabela de detalhes
        st.subheader("Tabela de Detalhes dos Terremotos")
        st.dataframe(filtered_data[['date', 'magnitude', 'latitude', 'longitude', 'depth', 'place', 'tsunami', 'alert', 'year']])

        #Total
        total_filtered_earthquakes = len(filtered_data)
        st.markdown(f"<h2>Total de Terremotos Filtrados: {total_filtered_earthquakes}</h2>", unsafe_allow_html=True)

        #Gráfico 1
        plot_monthly_average_magnitude(filtered_data)

        #Gráfico 2
        st.subheader("Histograma de Magnitude")
        plot_histogram(filtered_data)

        #Gráfico 3
        st.subheader("Gráfico de Dispersão (Magnitude vs Profundidade)")
        plot_scatter(filtered_data)

        #Mapa
        st.subheader("Mapa de Calor de Localização de Terremotos")
        plot_heatmap(filtered_data)

# Página 2: Análise Comparativa entre 2023 e 2024
if page == "Página 2 - Análise Comparativa":
    st.title("Análise Comparativa entre 2023 e 2024")

    #Filtro de profundidade
    if earthquakes_2023 is not None and earthquakes_2024 is not None:

        min_depth = st.slider("Profundidade Mínima (km):", min_value=0.0, max_value=700.0, value=0.0)
        max_depth = st.slider("Profundidade Máxima (km):", min_value=0.0, max_value=700.0, value=700.0)

        filtered_depth_2023 = earthquakes_2023[
            (earthquakes_2023['depth'] >= min_depth) &
            (earthquakes_2023['depth'] <= max_depth)
            ]
        filtered_depth_2024 = earthquakes_2024[
            (earthquakes_2024['depth'] >= min_depth) &
            (earthquakes_2024['depth'] <= max_depth)
            ]

        # Filtro do ano
        filtered_depth_2023 = filtered_depth_2023[pd.to_datetime(filtered_depth_2023['time'], errors='coerce').dt.year == 2023]
        filtered_depth_2024 = filtered_depth_2024[pd.to_datetime(filtered_depth_2024['date'], errors='coerce').dt.year == 2024]

        filtered_depth_2023['month'] = pd.to_datetime(filtered_depth_2023['time'], errors='coerce').dt.to_period('M')
        filtered_depth_2024['month'] = pd.to_datetime(filtered_depth_2024['date'], errors='coerce').dt.to_period('M')

        filtered_depth_2023 = filtered_depth_2023.dropna(subset=['month'])
        filtered_depth_2024 = filtered_depth_2024.dropna(subset=['month'])

        monthly_counts_2023 = filtered_depth_2023['month'].value_counts().sort_index()
        monthly_counts_2024 = filtered_depth_2024['month'].value_counts().sort_index()

        all_months = sorted(set(monthly_counts_2023.index).union(set(monthly_counts_2024.index)))

        counts_2023 = [monthly_counts_2023.get(month, 0) for month in all_months]
        counts_2024 = [monthly_counts_2024.get(month, 0) for month in all_months]

        all_months_str = [str(month) for month in all_months]

        # Tabelas
        st.subheader("Tabela de Detalhes dos Terremotos Filtrados por Profundidade")
        st.write("Dados de 2023:")
        st.dataframe(filtered_depth_2023[['time', 'mag', 'latitude', 'longitude', 'depth', 'place']])

        st.write("Dados de 2024:")
        st.dataframe(filtered_depth_2024[['date', 'magnitude', 'latitude', 'longitude', 'depth', 'place']])

        # Total
        total_earthquakes = len(filtered_depth_2023) + len(filtered_depth_2024)
        st.markdown(f"<h2>Total de Terremotos Registrados (Filtrados por Profundidade): {total_earthquakes}</h2>", unsafe_allow_html=True)

        # Gráfico 1
        fig, ax = plt.subplots()
        ax.plot(all_months_str, counts_2023, label='2023', marker='o', color='orange', linestyle='-', linewidth=2)
        ax.plot(all_months_str, counts_2024, label='2024', marker='o', color='green', linestyle='-', linewidth=2)
        ax.fill_between(all_months_str, counts_2023, color='orange', alpha=0.3)
        ax.fill_between(all_months_str, counts_2024, color='green', alpha=0.3)
        ax.set_title('Total de Terremotos por Mês (Filtrado por Profundidade)')
        ax.set_xlabel('Mês')
        ax.set_ylabel('Número de Terremotos')
        ax.legend()
        ax.set_xticks(all_months_str)
        ax.set_xticklabels(all_months_str, rotation=45)
        st.pyplot(fig)

        # Gráfico 2
        avg_mag_2023 = filtered_depth_2023['mag'].mean()
        avg_mag_2024 = filtered_depth_2024['magnitude'].mean()
        fig, ax = plt.subplots()
        ax.bar(['2023', '2024'], [avg_mag_2023, avg_mag_2024], color=['orange', 'green'])
        ax.set_title('Média de Magnitude por Ano (Filtrado por Profundidade)')
        ax.set_ylabel('Magnitude Média')
        st.pyplot(fig)

        # Gráfico 3
        place_counts_2023 = filtered_depth_2023['place'].value_counts().head(10)  # Top 10 locais
        place_counts_2024 = filtered_depth_2024['place'].value_counts().head(10)  # Top 10 locais

        # Gráfico 4
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(place_counts_2023, labels=place_counts_2023.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribuição de Terremotos por Lugar em 2023 (Filtrado por Profundidade)')
        ax.legend(place_counts_2023.index, title='Top 10 Lugares', loc='center left', bbox_to_anchor=(1.5, 0.5))
        st.pyplot(fig)

        # Gráfico 5
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(place_counts_2024, labels=place_counts_2024.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribuição de Terremotos por Lugar em 2024 (Filtrado por Profundidade)')
        ax.legend(place_counts_2024.index, title='Top 10 Lugares', loc='center left', bbox_to_anchor=(1.5, 0.5))
        st.pyplot(fig)


