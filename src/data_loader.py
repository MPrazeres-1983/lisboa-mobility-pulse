import pandas as pd
import os

def load_gira_excel(file_name):
    """
    Passo 1: Carrega o ficheiro Excel e faz o diagnóstico inicial.
    Usamos caminhos relativos para garantir que o código funciona em qualquer computador.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_path, '..', 'data', 'raw', file_name)
    
    print(f"📂 A carregar: {file_name}...")
    
    try:
        # Lemos o Excel usando o motor openpyxl (necessário para .xlsx)
        df = pd.read_excel(raw_path, engine='openpyxl')
        
        print("✅ Dados carregados com sucesso!")
        print(f"📊 Dimensões: {df.shape[0]} linhas e {df.shape[1]} colunas.")
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar o ficheiro: {e}")
        return None

def clean_gira_data(df):
    """
    Passo 2: Limpa e padroniza o DataFrame bruto da GIRA.
    Inclui extração geoespacial de alta performance via Regex.
    """
    print("\n🛠️ A iniciar a limpeza de dados (Data Cleaning)...")
    
    # 1. Renomear e separar colunas (como antes)
    df = df.rename(columns={
        'desigcomercial': 'station_name_raw',
        'numbicicletas': 'num_bikes',
        'numdocas': 'num_docks',
        'entity_ts': 'timestamp',
        'estado': 'status'
    })
    
    split_col = df['station_name_raw'].str.split(' - ', n=1, expand=True)
    df['station_id'] = split_col[0]
    df['station_name'] = split_col[1]
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['occupancy_rate'] = (df['num_bikes'] / df['num_docks']).fillna(0)
    df = df.drop(columns=['station_name_raw'])
    
    # ---------------------------------------------------------
    # NOVIDADE: EXTRAÇÃO DE COORDENADAS (NÍVEL SÉNIOR)
    # ---------------------------------------------------------
    print("🌍 A extrair Latitude e Longitude (via Regex para alta performance)...")
    
    # A Regex procura números dentro de parêntesis retos: [lon, lat]
    coords = df['position'].str.extract(r'\[([-\d.]+),\s*([-\d.]+)\]')
    
    # Atribuir às novas colunas e converter texto para número (float)
    df['lon'] = coords[0].astype(float)
    df['lat'] = coords[1].astype(float)
    
    # Já não precisamos da coluna original 'position'
    df = df.drop(columns=['position'])
    
    print(f"✅ Limpeza concluída! Dimensão final: {df.shape}")
    return df

# ==========================================
# BLOCO DE EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    nome_do_arquivo = "estacoes-gira-1-trimestre-2023.xlsx"
    df_raw = load_gira_excel(nome_do_arquivo)
    
    if df_raw is not None:
        df_clean = clean_gira_data(df_raw)
        
        # ---------------------------------------------------------
        # NOVIDADE: GUARDAR OS DADOS LIMPOS EM PARQUET
        # ---------------------------------------------------------
        # Construir caminho para a pasta data/processed/
        base_path = os.path.dirname(os.path.abspath(__file__))
        processed_path = os.path.join(base_path, '..', 'data', 'processed', 'gira_clean.parquet')
        
        print(f"\n💾 A guardar dados limpos em formato Parquet...")
        df_clean.to_parquet(processed_path, index=False)
        print(f"✅ Dados guardados com sucesso em: {processed_path}")
        
        # Prova de que as coordenadas funcionaram
        print("\n👀 Amostra das Coordenadas:")
        print(df_clean[['station_name', 'lat', 'lon']].head(3))