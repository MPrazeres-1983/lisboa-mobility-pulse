import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import os

def plot_hourly_occupancy(df):
    """
    Gera um gráfico de linha mostrando a taxa de ocupação média por hora.
    """
    print("📊 A processar análise temporal...")
    
    # 1. Feature Engineering (se não tiver sido feito antes, garantimos a hora)
    # Como o Parquet manteve o tipo datetime, podemos extrair a hora diretamente
    df['hour'] = df['timestamp'].dt.hour
    
    # 2. Agregação de Dados (A magia estatística)
    # Calculamos a média da ocupação para cada hora do dia (0 a 23)
    hourly_trend = df.groupby('hour')['occupancy_rate'].mean().reset_index()
    
    # 3. Configuração Visual (Estilo Sénior)
    plt.style.use('ggplot') # Estilo limpo e profissional
    plt.figure(figsize=(12, 6))
    
    # 4. Criar o gráfico
    sns.lineplot(
        data=hourly_trend, 
        x='hour', 
        y='occupancy_rate', 
        marker='o', 
        color='#2ecc71', # Verde sustentabilidade
        linewidth=2.5
    )
    
    # 5. Formatação do Gráfico
    plt.title('Ritmo Circadiano da Rede GIRA (Ocupação Média por Hora)', fontsize=16, pad=15)
    plt.xlabel('Hora do Dia (0-23h)', fontsize=12)
    plt.ylabel('Taxa de Ocupação Média', fontsize=12)
    plt.xticks(range(0, 24))
    plt.grid(True, alpha=0.3)
    
    # 6. Guardar o ficheiro na pasta outputs
    base_path = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_path, '..', 'outputs', 'figures')
    os.makedirs(output_dir, exist_ok=True) # Cria a pasta se ela não existir
    
    file_path = os.path.join(output_dir, 'hourly_occupancy.png')
    plt.savefig(file_path, dpi=300, bbox_inches='tight') # dpi=300 para alta resolução
    
    print(f"✅ Gráfico guardado com sucesso em: {file_path}")
    
    # Mostrar no ecrã também
    plt.show()

def generate_stockout_heatmap(df):
    """
    Gera um mapa de calor interativo mostrando os pontos críticos de falta de bicicletas.
    """
    print("🗺️ A gerar Mapa de Calor de Stockouts (Estações Vazias)...")
    
    # 1. Filtrar apenas os momentos de falha (0 bikes disponíveis)
    # E removemos linhas que por acaso não tenham coordenadas válidas
    df_stockouts = df[(df['num_bikes'] == 0) & (df['lat'].notna()) & (df['lon'].notna())]
    
    # 2. Iniciar o mapa centrado em Lisboa (Marquês de Pombal)
    # cartodbpositron é um estilo de mapa claro e profissional, excelente para dashboards
    m = folium.Map(location=[38.7253, -9.1500], zoom_start=13, tiles='cartodbpositron')
    
    # 3. Preparar dados para o HeatMap (Lista de [Lat, Lon])
    heat_data = df_stockouts[['lat', 'lon']].values.tolist()
    
    # 4. Adicionar a camada de calor ao mapa
    HeatMap(
        heat_data, 
        radius=15,       # Tamanho da "mancha"
        blur=10,         # Suavidade das bordas
        max_zoom=1, 
        gradient={0.4: 'blue', 0.65: 'yellow', 1.0: 'red'} # Do leve ao crítico
    ).add_to(m)
    
    # 5. Guardar o mapa na pasta outputs
    base_path = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_path, '..', 'outputs', 'maps')
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, 'stockout_heatmap.html')
    m.save(file_path)
    
    print(f"✅ Mapa de Calor guardado com sucesso em: {file_path}")

# ==========================================
# BLOCO DE EXECUÇÃO PRINCIPAL ATUALIZADO
# ==========================================
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(base_path, '..', 'data', 'processed', 'gira_clean.parquet')
    
    print("📂 A carregar dados limpos...")
    try:
        df_clean = pd.read_parquet(parquet_path)
        
        # 1. Gerar o gráfico de linhas (se quiseres podes comentar esta linha para não abrir sempre)
        plot_hourly_occupancy(df_clean)
        
        # 2. Gerar o novo mapa de calor
        generate_stockout_heatmap(df_clean)
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")