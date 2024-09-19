import requests
from datetime import datetime, timedelta
from models import Session, Indicator, Setting, Territory
from sqlalchemy import text
from dotenv import dotenv_values
from calendar import monthrange


config = dotenv_values('.env')

# Получаем вчерашнюю дату
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')


# Функция для вычисления последнего дня месяца
def get_last_day_of_month(year, month):
    return monthrange(year, month)[1]

# Функция для запроса данных из 1С
def fetch_data_from_1c(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from {url}")

# Очистка таблицы перед загрузкой новых данных
def clear_table(session, model_class):
    table_name = model_class.__tablename__
    session.query(model_class).delete()
    session.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"))
    session.commit()

# Загрузка territories
def load_territories(session):
    clear_table(session, Territory)
    data = fetch_data_from_1c('http://server1c.freedom1.ru/UNF_CRM_WS/hs/Grafana/anydata?query=territories')
    
    for row in data:
        # Используем .get() для извлечения данных, если какого-то поля нет, вернется None
        territory = Territory(
            name=row.get('name'),                    
            group=row.get('group1'),
            maingroup=row.get('maingroup'),       
            department=row.get('department')
        )
        session.add(territory)

# Загрузка settings
def load_settings(session):
    clear_table(session, Setting)
    data = fetch_data_from_1c('http://server1c.freedom1.ru/UNF_CRM_WS/hs/Grafana/anydata?query=settings')

    for row in data:
        # Проверяем, существует ли запись с таким же именем
        existing_setting = session.query(Setting).filter_by(name=row.get('name')).first()

        if not existing_setting:
            # Если записи нет, добавляем новую
            setting = Setting(
                name=row.get('name'),
                params=row.get('params'),
                prop=row.get('prop'),
                variable1=row.get('pick1'),
                variable2=row.get('pick2'),
                variable3=row.get('pick3'),
                variable4=row.get('pick4'),
                variable5=row.get('pick5'),
                type=row.get('type')
            )
            session.add(setting)
    
    session.commit()  

# Формирование URL для показателей на основе настроек
def get_query_url(setting_name, params, yesterday):
    param_str = f"&{params}={yesterday}"  # Подставляем дату
    return f"http://server1c.freedom1.ru/UNF_CRM_WS/hs/Grafana/anydata?query={setting_name}&{param_str}"

# Обработка показателей indicators
def load_indicators(session):
    settings = session.query(Setting).group_by(Setting.name, Setting.params, Setting.type).all()

    for setting in settings:
        name, params, setting_type = setting.name, setting.params, setting.type
        url = get_query_url(name, params, yesterday)
        data = fetch_data_from_1c(url)

        # Получаем дату из строки вчерашнего дня
        request_date = datetime.strptime(yesterday, '%Y%m%d')
        last_day_of_month = get_last_day_of_month(request_date.year, request_date.month)

        if setting_type == 1 or setting_type == 3:
            continue
            for row in data:
                indicator_date = datetime.strptime(row.get('date'), '%Y-%m-%d')
                # Проверяем, чтобы дата не была больше последнего дня месяца
                if indicator_date.day > last_day_of_month:
                    continue  # Пропускаем записи с датами после конца месяца

                indicator = Indicator(
                    date=yesterday,
                    prop=row.get('prop'),
                    value=row.get('value'),
                    variable1=row.get('pick1'),
                    variable2=row.get('pick2'),
                    variable3=row.get('pick3'),
                    variable4=row.get('pick4'),
                    variable5=row.get('pick5')
                )
                session.add(indicator)
        
        elif setting_type == 2:
            # Удаляем старые записи и добавляем новые
            session.query(Indicator).filter(Indicator.date > yesterday).delete()
            for row in data:
                indicator_date = datetime.strptime(row.get('date'), '%Y-%m-%d')
                # Проверяем, чтобы дата не была больше последнего дня месяца
                if indicator_date.day > last_day_of_month:
                    continue  # Пропускаем записи с датами после конца месяца

                indicator = Indicator(
                    date=yesterday,
                    prop=row.get('prop'),
                    value=row.get('value'),
                    variable1=row.get('pick1'),
                    variable2=row.get('pick2'),
                    variable3=row.get('pick3'),
                    variable4=row.get('pick4'),
                    variable5=row.get('pick5')
                )
                session.add(indicator)


def main():
    # Создаем сессию
    session = Session()

    try:
        # Загружаем данные
        load_territories(session)
        load_settings(session)
        load_indicators(session)

        # Коммитим изменения
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()  # Откат транзакции в случае ошибки
    finally:
        session.close()

if __name__ == "__main__":
    main()
