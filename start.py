import multiprocessing
import subprocess
import time
import os

# Путь к файлу с тикерами
tickers_file = '12'

# Функция для запуска процесса
def run_script(ticker):
    try:
        subprocess.run(["python3", f"./{ticker.upper}/main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Процесс {ticker} завершился с ошибкой: {e}. Перезапуск через 5 секунд...")
        time.sleep(5)
        run_script(ticker)

# Основная функция для запуска процессов параллельно
def main():
    if os.path.exists(tickers_file):
        with open(tickers_file, 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
            processes = []

            for ticker in tickers:
                p = multiprocessing.Process(target=run_script, args=(ticker.lower(),))
                p.start()
                processes.append(p)

            # Ожидаем завершения всех процессов
            for p in processes:
                p.join()

    else:
        print(f"Файл {tickers_file} не найден!")

if __name__ == "__main__":
    main()
