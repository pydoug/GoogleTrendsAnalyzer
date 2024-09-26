import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import shutil
import locale

# Opcional: Definir o locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'ptb')

def processar_volume_de_pesquisa(df):
    """
    Função para processar a coluna 'Volume de pesquisa' e substituir 'mil' por *1000, 'mi' por *1.000.000,
    e remover o '+' no final dos números.
    """
    def ajustar_volume(volume):
        volume = volume.replace('\u00a0', ' ').replace(' ', ' ')  # Substituir espaços não separáveis por espaços normais

        # Substituir 'mil' e 'mi'
        if 'mil' in volume:
            volume = volume.replace(' mil+', '').strip()
            volume = str(int(volume) * 1000)
        elif 'mi' in volume:
            volume = volume.replace(' mi+', '').strip()
            volume = str(int(volume) * 1000000)
        else:
            volume = volume.replace('+', '').strip()

        return volume

    df['Volume de pesquisa'] = df['Volume de pesquisa'].apply(ajustar_volume)
    # Converter a coluna para inteiro
    df['Volume de pesquisa'] = pd.to_numeric(df['Volume de pesquisa'], errors='coerce').fillna(0).astype(int)
    return df

def converter_para_timestamp(data_iniciado):
    """
    Converte a string de data 'Iniciado' para timestamp, lidando com espaços extras e o fuso horário 'UTC-3'.
    """
    try:
        data_iniciado = data_iniciado.replace('às', '').replace('  ', ' ').strip()  # Remover espaços extras

        if "UTC-3" in data_iniciado:
            data_iniciado = data_iniciado.replace(' UTC-3', '')  # Remover o fuso horário

        # Mapear nomes de meses em português para números
        meses = {
            'janeiro': '01',
            'fevereiro': '02',
            'março': '03',
            'abril': '04',
            'maio': '05',
            'junho': '06',
            'julho': '07',
            'agosto': '08',
            'setembro': '09',
            'outubro': '10',
            'novembro': '11',
            'dezembro': '12'
        }

        # Substituir o nome do mês pelo número correspondente
        for mes_pt, mes_num in meses.items():
            if mes_pt in data_iniciado:
                data_iniciado = data_iniciado.replace(f' de {mes_pt} de ', f'/{mes_num}/')
                break  # Encontrou o mês, pode sair do loop

        # Parsear a data usando strptime
        dt = datetime.strptime(data_iniciado, "%d/%m/%Y %H:%M:%S")

        # Se necessário, ajustar para UTC (opcional)
        # dt = dt + pd.Timedelta(hours=3)  # Ajuste se precisar converter para UTC

        return dt.timestamp()

    except Exception as e:
        print(f"Erro ao converter data: {data_iniciado} - {e}")
        return None

def converter_iniciado_para_timestamp(df):
    """
    Converte a coluna 'Iniciado' em timestamps.
    """
    df['Iniciado'] = df['Iniciado'].apply(converter_para_timestamp)
    return df

def calcular_indice_trends(df):
    """
    Calcula o Indice_Trends para cada linha do DataFrame.
    """
    # Obter o timestamp atual
    timestamp_atual = datetime.now().timestamp()

    # Calcular a diferença de tempo em minutos
    df['Dif_tempo_minutos'] = (timestamp_atual - df['Iniciado']) / 60

    # Evitar divisão por zero
    df['Dif_tempo_minutos'] = df['Dif_tempo_minutos'].replace(0, 1e-6)  # Substituir 0 por um número muito pequeno

    # Calcular o Indice_Trends
    df['Indice_Trends'] = df['Volume de pesquisa'] / df['Dif_tempo_minutos']

    # Arredondar o Indice_Trends para duas casas decimais
    df['Indice_Trends'] = df['Indice_Trends'].round(2)

    return df

def baixar_csv_periodicamente(download_temp_dir, final_dir, chrome_driver_path, intervalo=60):
    """
    Função para baixar arquivos CSV do Google Trends a cada 'intervalo' de segundos.
    """
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    service = Service(chrome_driver_path)
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_temp_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://trends.google.com.br/trending?geo=BR&hl=pt-BR&hours=48&sort=recency"
    driver.get(url)

    def baixar_csv():
        try:
            export_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[span[contains(text(),"Exportar")]]'))
            )
            export_button.click()
            time.sleep(5)

            driver.execute_script("""
                let csvButton = document.querySelector('li[aria-label="Fazer download como CSV"]');
                if (csvButton) {
                    csvButton.click();
                }
            """)

            time.sleep(10)
            files = os.listdir(download_temp_dir)
            csv_files = [f for f in files if f.endswith(".csv")]

            if csv_files:
                latest_file = max([os.path.join(download_temp_dir, f) for f in csv_files], key=os.path.getctime)
                df = pd.read_csv(latest_file)

                df = processar_volume_de_pesquisa(df)
                df = converter_iniciado_para_timestamp(df)
                df = calcular_indice_trends(df)

                # Reordenar as colunas para posicionar 'Indice_Trends' após 'Volume de pesquisa'
                colunas_ordenadas = ['Tendências', 'Volume de pesquisa', 'Indice_Trends'] + \
                                    [col for col in df.columns if col not in ['Tendências', 'Volume de pesquisa', 'Indice_Trends']]
                df = df[colunas_ordenadas]

                # Remover colunas temporárias
                df = df.drop(columns=['Dif_tempo_minutos'])

                df.to_csv(latest_file, index=False)

                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                novo_nome = f'trending_{timestamp}.csv'
                novo_caminho = os.path.join(final_dir, novo_nome)
                shutil.move(latest_file, novo_caminho)

                # Exibir a mensagem solicitada
                print(f"Trends saved in path: {novo_caminho} at time {timestamp}")
            else:
                pass  # Nenhum arquivo CSV encontrado

        except Exception as e:
            print(f"Erro ao tentar baixar CSV: {e}")

    while True:
        baixar_csv()
        driver.refresh()
        time.sleep(intervalo)

    driver.quit()