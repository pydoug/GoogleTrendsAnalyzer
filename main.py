import os

from data_downloader import baixar_csv_periodicamente
from data_analyzer import analyze_data
import threading

def main():
    download_temp_dir = input("Digite o diretório temporário de download (ex: C:\\Downloads): ").strip()
    final_dir = input("Digite o diretório final para salvar os CSVs (ex: C:\\GoogleTrendsAnalyzer\\data): ").strip()
    chrome_driver_path = input("Digite o caminho para o chromedriver.exe (ex: C:\\chromedriver\\chromedriver.exe): ").strip()

    if not os.path.exists(download_temp_dir):
        os.makedirs(download_temp_dir)
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)
    if not os.path.exists(chrome_driver_path):
        print("Caminho para o chromedriver.exe inválido.")
        return

    downloader_thread = threading.Thread(
        target=baixar_csv_periodicamente,
        args=(download_temp_dir, final_dir, chrome_driver_path, 60)
    )
    downloader_thread.start()

    analyze_data(final_dir)

if __name__ == "__main__":
    main()
