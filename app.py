import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sidebar para upload dos arquivos
st.sidebar.title("Upload de Arquivos")
uploaded_file_2023 = st.sidebar.file_uploader("Carregar dados de terremotos de 2023", type=["csv"])
uploaded_file_2024 = st.sidebar.file_uploader("Carregar dados de terremotos de 2024", type=["csv"])

# Inicializa as variáveis de dados
earthquakes_2023 = None
earthquakes_2024 = None

# Carregar dados se os arquivos forem carregados
if uploaded_file_2023 is not None:
    earthquakes_2023 = pd.read_csv(uploaded_file_2023)

if uploaded_file_2024 is not None:
    earthquakes_2024 = pd.read_csv(uploaded_file_2024)

# Sidebar para navegação entre páginas
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione a página:", ["Página 1 - Visão Geral", "Página 2 - Análise Detalhada"])

# Função para exibir gráficos
def plot_graphs(data):
    # Gráfico de Magnitude ao longo do Tempo
    fig, ax = plt.subplots()
    ax.plot(pd.to_datetime(data['time']), data['mag'], marker='o', linestyle='-', markersize=2)
    ax.set_title('Magnitude dos Terremotos ao longo do Tempo')
    ax.set_xlabel('Data')
    ax.set_ylabel('Magnitude')
    st.pyplot(fig)

    # Histograma de Profundidade
    fig, ax = plt.subplots()
    ax.hist(data['depth'], bins=30, alpha=0.7, color='blue')
    ax.set_title('Distribuição da Profundidade dos Terremotos')
    ax.set_xlabel('Profundidade (km)')
    ax.set_ylabel('Frequência')
    st.pyplot(fig)

    # Gráfico de dispersão: Magnitude vs Profundidade
    fig, ax = plt.subplots()
    ax.scatter(data['depth'], data['mag'], alpha=0.5)
    ax.set_title('Magnitude vs Profundidade')
    ax.set_xlabel('Profundidade (km)')
    ax.set_ylabel('Magnitude')
    st.pyplot(fig)

# Página 1: Visão Geral
if page == "Página 1 - Visão Geral":
    st.title("Visão Geral dos Terremotos")

    # Verifica se os dados foram carregados
    if earthquakes_2023 is not None and earthquakes_2024 is not None:
        # Filtro dinâmico para selecionar a profundidade mínima
        min_depth = st.slider("Selecione a profundidade mínima (km):", min_value=0, max_value=700, value=0)
        filtered_data_2023 = earthquakes_2023[earthquakes_2023['depth'] >= min_depth]
        filtered_data_2024 = earthquakes_2024[earthquakes_2024['depth'] >= min_depth]

        st.write(f"Número de terremotos em 2023 com profundidade maior ou igual a {min_depth} km: {len(filtered_data_2023)}")
        st.write(f"Número de terremotos em 2024 com profundidade maior ou igual a {min_depth} km: {len(filtered_data_2024)}")

        # Gráficos
        st.subheader("Gráficos de 2023")
        plot_graphs(filtered_data_2023)

        st.subheader("Gráficos de 2024")
        plot_graphs(filtered_data_2024)
    else:
        st.warning("Por favor, carregue os arquivos de dados para continuar.")

# Página 2: Análise Detalhada
if page == "Página 2 - Análise Detalhada":
    st.title("Análise Detalhada dos Terremotos")

    # Verifica se os dados foram carregados
    if earthquakes_2023 is not None:
        # Filtro para selecionar tipo de evento
        event_type = st.selectbox("Selecione o tipo de evento:", options=earthquakes_2023['type'].unique())
        filtered_data_2023_event = earthquakes_2023[earthquakes_2023['type'] == event_type]
        filtered_data_2024_event = earthquakes_2024[earthquakes_2024['type'] == event_type] if earthquakes_2024 is not None else pd.DataFrame()

        # Tabela de dados filtrados
        st.subheader(f"Tabela de Terremotos - {event_type}")
        st.dataframe(filtered_data_2023_event)

        # Valor total de terremotos do tipo selecionado
        st.write(f"Número total de terremotos do tipo '{event_type}' em 2023: {len(filtered_data_2023_event)}")
        if earthquakes_2024 is not None:
            st.write(f"Número total de terremotos do tipo '{event_type}' em 2024: {len(filtered_data_2024_event)}")

        # Gráfico de Histograma da Magnitude
        fig, ax = plt.subplots()
        ax.hist(filtered_data_2023_event['mag'], bins=20, alpha=0.7, color='orange')
        ax.set_title(f'Distribuição da Magnitude - {event_type} em 2023')
        ax.set_xlabel('Magnitude')
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

        # Gráfico de dispersão: Profundidade vs Magnitude para o tipo selecionado
        fig, ax = plt.subplots()
        ax.scatter(filtered_data_2023_event['depth'], filtered_data_2023_event['mag'], alpha=0.5, color='green')
        ax.set_title(f'Profundidade vs Magnitude - {event_type} em 2023')
        ax.set_xlabel('Profundidade (km)')
        ax.set_ylabel('Magnitude')
        st.pyplot(fig)
    else:
        st.warning("Por favor, carregue os arquivos de dados para continuar.")
