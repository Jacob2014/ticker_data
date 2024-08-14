import os
import shutil


def create_folders_and_copy_samples(tickers_file, samples_folder):
    # Открываем файл с тикерами
    with open(tickers_file, 'r') as file:
        tickers = file.read().splitlines()

    # Проходим по каждому тикеру
    for ticker in tickers:
        # Создаем папку с именем тикера
        directory = os.path.join(os.getcwd(), ticker)
        os.makedirs(directory, exist_ok=True)

        # Копируем все файлы из папки samples в папку тикера
        for item in os.listdir(samples_folder):
            s = os.path.join(samples_folder, item)
            d = os.path.join(directory, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        # Путь к файлу .env в новой папке
        env_file_path = os.path.join(directory, '.env')

        # Обновляем файл .env, изменяя только строку с тикером
        with open(env_file_path, 'r') as env_file:
            env_content = env_file.readlines()

        with open(env_file_path, 'w') as env_file:
            for line in env_content:
                if line.startswith("TICKER=MXSE.TQBR."):
                    env_file.write(f"TICKER=MXSE.TQBR.{ticker}\n")
                else:
                    env_file.write(line)

        print(f"Папка и обновленный файл .env для {ticker} созданы.")


# Путь к файлу с тикерами и к папке samples
tickers_file = '12'
samples_folder = 'samples'

# Запуск функции
create_folders_and_copy_samples(tickers_file, samples_folder)
