from sqlalchemy import create_engine, String, Integer, DateTime, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from dotenv import dotenv_values
import atexit

# Загрузка конфигурации из .env файла
config = dotenv_values('.env')

# Формирование строки подключения
DSN = (f"mysql+mysqlconnector://{config.get('USER')}:{config.get('PASSWORD')}@"
       f"{config.get('HOST')}/{config.get('DATABASE')}")

engine = create_engine(DSN)

class Base(DeclarativeBase):
    pass

# Модель для таблицы 'territories'
class Territory(Base):

    __tablename__ = 'territories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # Name должно быть уникальным
    group: Mapped[str] = mapped_column(String(255))
    maingroup: Mapped[str] = mapped_column(String(255))
    department: Mapped[str] = mapped_column(String(255), nullable=True)


# Модель для таблицы 'settings'
class Setting(Base):

    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # Name должно быть уникальным
    params: Mapped[str] = mapped_column(String(255), nullable=True)
    prop: Mapped[str] = mapped_column(String(255), nullable=True)
    variable1: Mapped[str] = mapped_column(String(255), nullable=True)
    variable2: Mapped[str] = mapped_column(String(255), nullable=True)
    variable3: Mapped[str] = mapped_column(String(255), nullable=True)
    variable4: Mapped[str] = mapped_column(String(255), nullable=True)
    variable5: Mapped[str] = mapped_column(String(255), nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)  # Тип не может быть NULL


# Модель для таблицы 'indicators'
class Indicator(Base):
    __tablename__ = 'indicators'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(8), nullable=False)  # Дата в формате YYYYMMDD
    prop: Mapped[str] = mapped_column(String(255), nullable=True)  # Prop не должно быть NULL
    value: Mapped[int] = mapped_column(Integer, nullable=True)  # Value не должно быть NULL
    variable1: Mapped[str] = mapped_column(String(255), nullable=True)
    variable2: Mapped[str] = mapped_column(String(255), nullable=True)
    variable3: Mapped[str] = mapped_column(String(255), nullable=True)
    variable4: Mapped[str] = mapped_column(String(255), nullable=True)
    variable5: Mapped[str] = mapped_column(String(255), nullable=True)

# Создание таблиц
try:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Ошибка при создании таблицы:", e)

# Создание класса Session для работы с базой данных
try:
    Session = sessionmaker(bind=engine)
except Exception as e:
    print("Ошибка при создании сессии:", e)
    Session = None

# Автоматическое закрытие соединения при завершении программы
atexit.register(engine.dispose)
