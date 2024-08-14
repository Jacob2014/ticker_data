import asyncio
import json
import ssl
import uuid
from websockets import connect, ConnectionClosed
from stomp.utils import Frame, convert_frame, parse_frame
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получаем значения переменных окружения для первой базы данных
ticker = os.getenv('TICKER')
db_config1 = {
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'host': os.getenv('DATABASE_HOST'),
    'database': os.getenv('DATABASE_NAME'),
}

# Получаем значения переменных окружения для второй базы данных
db_config2 = {
    'user': os.getenv('SECOND_DATABASE_USER'),
    'password': os.getenv('SECOND_DATABASE_PASSWORD'),
    'host': os.getenv('SECOND_DATABASE_HOST'),
    'database': os.getenv('SECOND_DATABASE_NAME'),
}

domain = os.getenv('DOMAIN')
login = os.getenv('LOGIN')
passcode = os.getenv('PASSCODE')


def insert_into_db(ticker, date, time, open_price, high_price, low_price, close_price, volume=None):
    """Функция для вставки данных в таблицы двух баз данных MySQL"""

    # Вставка в первую базу данных
    connection1 = mysql.connector.connect(**db_config1)
    cursor1 = connection1.cursor()
    table_name1 = f"{ticker.upper()}_m1"
    insert_query = f"""
    INSERT INTO {table_name1} (date, time, open, high, low, close, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    data_tuple = (date, time, open_price, high_price, low_price, close_price, volume if volume is not None else None)

    try:
        cursor1.execute(insert_query, data_tuple)
        connection1.commit()
        print(f"Успешная отправка данных в первую базу данных для {ticker}")
    except mysql.connector.Error as err:
        print(f"Ошибка при вставке данных в первую базу данных для {ticker}: {err}")
    finally:
        cursor1.close()
        connection1.close()

    # Вставка во вторую базу данных
    connection2 = mysql.connector.connect(**db_config2)
    cursor2 = connection2.cursor()
    table_name2 = f"{ticker.upper()}_m1"
    insert_query = f"""
    INSERT INTO {table_name2} (date, time, open, high, low, close, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor2.execute(insert_query, data_tuple)
        connection2.commit()
        print(f"Успешная отправка данных во вторую базу данных для {ticker}")
    except mysql.connector.Error as err:
        print(f"Ошибка при вставке данных во вторую базу данных для {ticker}: {err}")
    finally:
        cursor2.close()
        connection2.close()


async def send_frame(websocket, cmd, headers):
    frame = Frame(cmd, headers=headers)
    await websocket.send(b''.join(convert_frame(frame)))


async def receive_message(websocket):
    message = await websocket.recv()
    return parse_frame(message)


async def connect_stomp(websocket, domain, login, passcode):
    await send_frame(websocket, 'CONNECT', {'domain': domain, 'login': login, 'passcode': passcode})
    frame = await receive_message(websocket)
    if frame.cmd != 'CONNECTED':
        raise ConnectionRefusedError(f"STOMP authentication failed; {frame.headers.get('message', 'No error message')}")
    return frame.headers


async def subscribe_to_topic(websocket, destination, selector):
    subscribe_header = {
        'id': str(uuid.uuid4()),
        'destination': destination,
        'selector': selector,
    }
    await send_frame(websocket, 'SUBSCRIBE', subscribe_header)


async def main(url):
    ssl_context = ssl._create_unverified_context()

    async with connect(url, subprotocols=['STOMP'], ssl=ssl_context) as websocket:
        try:
            metadata = await connect_stomp(websocket, domain, login, passcode)
            print("Connected with metadata:", metadata)

            await subscribe_to_topic(websocket, 'MXSE.securities', f'TICKER="{ticker}" and LANGUAGE="en"')
            print("Subscription successful")

            while True:
                frame = await receive_message(websocket)
                if frame.cmd == 'MESSAGE':
                    body = json.loads(frame.body.decode('utf8').strip('\0'))
                    columns = body.get('columns', [])
                    data = body.get('data', [])

                    # Проверяем, что пришли данные, и в них есть необходимые столбцы
                    if 'LAST' in columns and 'TIME' in columns and 'TICKER' in columns:
                        last_index = columns.index('LAST')
                        time_index = columns.index('TIME')
                        ticker_index = columns.index('TICKER')

                        last_price = data[0][last_index][0]
                        time_value = data[0][time_index]
                        ticker_value = data[0][ticker_index].split('.')[2]  # Извлекаем тикер

                        # Преобразуем дату и время
                        date_value = datetime.now().strftime('%Y-%m-%d')  # Используем текущую дату

                        # Показываем дату, время, цену и тикер в консоли
                        print(f"Тикер: {ticker_value}, Дата: {date_value}, Время: {time_value}, Цена: {last_price}")

                        # Вставляем данные в обе базы данных
                        insert_into_db(ticker_value, date_value, time_value, last_price, last_price, last_price,
                                       last_price)

        except ConnectionClosed:
            print("Connection closed unexpectedly!")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            return


if __name__ == '__main__':
    url = 'wss://iss.moex.com/infocx/v3/websocket'
    asyncio.run(main(url))
