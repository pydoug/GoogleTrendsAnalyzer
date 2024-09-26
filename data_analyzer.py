import os
import glob
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import time

# Diretório onde os arquivos estão
directory = r'C:\Users\Douglas\Desktop\10M\date'

# Função para extrair timestamp do nome do arquivo
def get_timestamp(file_path):
    filename = os.path.basename(file_path)
    date_str = filename.split('_')[-1].split('.')[0]
    return datetime.strptime(date_str, '%Y%m%d-%H%M%S')

# Função para calcular o tempo decorrido
def compute_time_ago(df, current_time):
    df['Delta'] = current_time - df['Iniciado']
    df['Minutes_Atras'] = df['Delta'].dt.total_seconds() / 60
    df['Minutes_Atras'] = df['Minutes_Atras'].apply(lambda x: int(x) if not pd.isnull(x) else None)
    df['Tempo_Atras'] = df['Minutes_Atras'].apply(lambda x: f"{x} minutos atrás" if x is not None and x >= 0 else ('N/A' if x is None else f"Em {-x} minutos"))
    # Criar coluna 'Data' baseada em 'Iniciado'
    df['Data'] = df['Iniciado'].dt.strftime('%d/%m/%Y %H:%M:%S').fillna('N/A')
    return df

console = Console()

while True:
    # Encontrar todos os arquivos CSV no diretório
    csv_files = glob.glob(os.path.join(directory, 'trending_*.csv'))
    
    # Verificar se há arquivos CSV no diretório
    if not csv_files:
        console.print("Nenhum arquivo CSV encontrado no diretório especificado.")
        time.sleep(60)
        continue
    
    # Ordenar os arquivos por timestamp (mais recente primeiro)
    csv_files.sort(key=get_timestamp, reverse=True)
    
    # Obter o arquivo mais recente
    latest_file = csv_files[0]
    latest_timestamp = get_timestamp(latest_file)
    
    # Encontrar o arquivo mais próximo de 15 minutos atrás
    target_time_15 = latest_timestamp - timedelta(minutes=15)
    file_15min = min(csv_files, key=lambda x: abs(get_timestamp(x) - target_time_15))
    timestamp_15min = get_timestamp(file_15min)
    
    # Encontrar o arquivo mais próximo de 60 minutos atrás
    target_time_60 = latest_timestamp - timedelta(minutes=60)
    file_60min = min(csv_files, key=lambda x: abs(get_timestamp(x) - target_time_60))
    timestamp_60min = get_timestamp(file_60min)
    
    # Ler os arquivos necessários
    df_current = pd.read_csv(latest_file)
    df_15min = pd.read_csv(file_15min)
    df_60min = pd.read_csv(file_60min)
    
    # Converter colunas e calcular 'Iniciado'
    for df in [df_current, df_15min, df_60min]:
        # Converter colunas numéricas
        df['Indice_Trends'] = pd.to_numeric(df['Indice_Trends'], errors='coerce')
        df['Volume de pesquisa'] = pd.to_numeric(df['Volume de pesquisa'], errors='coerce')
        # Converter coluna 'Iniciado' para datetime
        df['Iniciado'] = pd.to_datetime(df['Iniciado'], unit='s', errors='coerce')
    
    # Encontrar o tempo atual baseado nos dados
    current_time = max(
        df_current['Iniciado'].max(),
        df_15min['Iniciado'].max(),
        df_60min['Iniciado'].max()
    )
    
    # Calcular 'Tempo Atrás' e 'Minutes_Atras' usando o tempo atual ajustado
    df_current = compute_time_ago(df_current, current_time)
    df_15min = compute_time_ago(df_15min, current_time)
    df_60min = compute_time_ago(df_60min, current_time)
    
    # Renomear colunas 'Indice_Trends' nos DataFrames de 15min e 60min
    df_15min.rename(columns={'Indice_Trends': 'Indice_Trends_15min'}, inplace=True)
    df_60min.rename(columns={'Indice_Trends': 'Indice_Trends_60min'}, inplace=True)
    
    # Preparar df_variation
    df_variation = df_current[['Tendências', 'Indice_Trends']].copy()
    df_variation.rename(columns={'Indice_Trends': 'Indice_Trends_Atual'}, inplace=True)
    
    # Mesclar com df_15min
    df_variation = df_variation.merge(
        df_15min[['Tendências', 'Indice_Trends_15min']],
        on='Tendências',
        how='left'
    )
    
    # Mesclar com df_60min
    df_variation = df_variation.merge(
        df_60min[['Tendências', 'Indice_Trends_60min']],
        on='Tendências',
        how='left'
    )
    
    # Calcular variações
    df_variation['Variação_15min'] = df_variation['Indice_Trends_Atual'] - df_variation['Indice_Trends_15min']
    df_variation['Variação_60min'] = df_variation['Indice_Trends_Atual'] - df_variation['Indice_Trends_60min']
    
    # Mesclar variações com o DataFrame atual
    df_current = df_current.merge(
        df_variation[['Tendências', 'Variação_15min', 'Variação_60min']],
        on='Tendências',
        how='left'
    )
    
    # Criar os painéis
    ## Painel 1: Índice_Trends do maior para o menor (top 25) com variações
    panel1_data = df_current.sort_values(by='Indice_Trends', ascending=False).head(25)
    
    # Criar a tabela
    table1 = Table(title="Top 25 - Índice Trends (Maior para Menor)")
    
    # Adicionar colunas
    table1.add_column("Data", style="cyan")
    table1.add_column("Tempo Atrás", style="magenta")
    table1.add_column("Tendência", style="green")
    table1.add_column("Volume de Pesquisa", justify="right", style="yellow")
    table1.add_column("Índice Trends", justify="right", style="red")
    table1.add_column("Variação 15min", justify="right", style="blue")
    table1.add_column("Variação 60min", justify="right", style="blue")
    
    # Adicionar linhas
    for index, row in panel1_data.iterrows():
        data_formatted = row['Data']
        tempo_atras = row['Tempo_Atras']
        variacao_15 = f"{row['Variação_15min']:.2f}" if not pd.isnull(row['Variação_15min']) else 'N/A'
        variacao_60 = f"{row['Variação_60min']:.2f}" if not pd.isnull(row['Variação_60min']) else 'N/A'
        
        # Verificar a condição para aplicar o estilo
        if row['Minutes_Atras'] is not None and row['Minutes_Atras'] < 120 and row['Indice_Trends'] > 100:
            style = "on yellow"
        else:
            style = None
        
        table1.add_row(
            data_formatted,
            tempo_atras,
            row['Tendências'],
            f"{int(row['Volume de pesquisa'])}",
            f"{row['Indice_Trends']}",
            variacao_15,
            variacao_60,
            style=style  # Aplicar o estilo condicional
        )
    
    # Criar o painel
    panel1 = Panel(table1, title="Painel 1")
    
    ## Painel 2: Iniciado do mais novo para o mais velho (top 25)
    panel2_data = df_current.dropna(subset=['Iniciado']).sort_values(by='Iniciado', ascending=False).head(25)
    
    # Criar a tabela
    table2 = Table(title="Top 25 - Iniciado (Mais Novo para Mais Velho)")
    
    # Adicionar colunas
    table2.add_column("Data", style="cyan")
    table2.add_column("Tempo Atrás", style="magenta")
    table2.add_column("Tendência", style="green")
    table2.add_column("Volume de Pesquisa", justify="right", style="yellow")
    table2.add_column("Índice Trends", justify="right", style="red")
    
    # Adicionar linhas
    for index, row in panel2_data.iterrows():
        data_formatted = row['Data']
        tempo_atras = row['Tempo_Atras']
        table2.add_row(
            data_formatted,
            tempo_atras,
            row['Tendências'],
            f"{int(row['Volume de pesquisa'])}",
            f"{row['Indice_Trends']}"
        )
    
    # Criar o painel
    panel2 = Panel(table2, title="Painel 2")
    
    ## Painel 3: Volume de pesquisa do maior para o menor (top 25)
    panel3_data = df_current.sort_values(by='Volume de pesquisa', ascending=False).head(25)
    
    # Criar a tabela
    table3 = Table(title="Top 25 - Volume de Pesquisa (Maior para Menor)")
    
    # Adicionar colunas
    table3.add_column("Data", style="cyan")
    table3.add_column("Tempo Atrás", style="magenta")
    table3.add_column("Tendência", style="green")
    table3.add_column("Volume de Pesquisa", justify="right", style="yellow")
    table3.add_column("Índice Trends", justify="right", style="red")
    
    # Adicionar linhas
    for index, row in panel3_data.iterrows():
        data_formatted = row['Data']
        tempo_atras = row['Tempo_Atras']
        table3.add_row(
            data_formatted,
            tempo_atras,
            row['Tendências'],
            f"{int(row['Volume de pesquisa'])}",
            f"{row['Indice_Trends']}"
        )
    
    # Criar o painel
    panel3 = Panel(table3, title="Painel 3")
    
    # Criar o layout principal
    layout = Layout()

    # Dividir o layout em duas partes na vertical
    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )

    # Dividir a parte superior em duas colunas para os painéis 1 e 2
    layout["upper"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )

    # Atribuir os painéis às seções do layout
    layout["left"].update(panel1)
    layout["right"].update(panel2)
    layout["lower"].update(panel3)
    
    # Limpar a tela antes de imprimir
    console.clear()
    
    # Exibir o layout
    console.print(layout)
    
    # Aguardar 1 minuto antes da próxima atualização
    time.sleep(60)