from datetime import datetime
import sqlalchemy
try:
    import db_settings as dbs
except ImportError:
    from . import db_settings as dbs
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.exc import OperationalError

db_string = dbs.drv + '://' + dbs.login + ':' + dbs.passwd + \
            '@' + dbs.address + '/' + dbs.name.lower()

engine = sqlalchemy.create_engine(db_string)
base = declarative_base()
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()


class Movies(base):
    __tablename__ = 'Movies'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    director = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    _length = sqlalchemy.Column("length", sqlalchemy.Time, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __init__(self, title, year, director, length, rating):
        self.title = title
        self.year = year
        self.director = director
        self._length = datetime.strptime(length, "%H:%M:%S")
        self.rating = rating

    @property
    def length(self):
        return self._length.strftime("%H:%M:%S")

    @length.setter
    def length(self, length):
        self._length = datetime.strptime(length, "%H:%M:%S")

    @validates('title')
    @validates('director')
    def validate_strings(self, key, string):
        assert 0 < len(string) <= 100, str(key) + " length should be less 100 symbols"
        return string

    @validates('year')
    def validate_year(self, key, year):
        assert 1900 <= year < 2100, "Year should be less then 2100 and more 1900"
        return year

    @validates('rating')
    def validate_rating(self, key, rating):
        assert 0 <= rating <= 10, "Rating should be less then 10 and more 0"
        return rating


if __name__ == '__main__':
    # Небольшой костыль для того чтоб создавать струкутуру базы из питона и саму базу
    from sqlalchemy.orm import sessionmaker

    try:
        conntmp = sqlalchemy.create_engine(db_string).connect()
    except OperationalError:
        db_string2 = dbs.drv + '://' + dbs.login + ':' + dbs.passwd + '@' + dbs.address + '/postgres'
        engine2 = sqlalchemy.create_engine(db_string2)
        conn = engine2.connect()
        conn.execute("COMMIT")
        conn.execute("CREATE DATABASE " + dbs.name)
        conn.close()
    Session2 = sessionmaker(bind=engine)
    Session2.configure(bind=engine)
    session2 = Session2()
    base.metadata.create_all(bind=engine)
    # Добавляем пример в базу
    movie = Movies("Example Movies", 2018, "Somebody", "02:30:00", 8)
    session.add(movie)
    movie = Movies("Example Movies 2", 2018, "Somebody 2", "02:25:00", 8)
    session.add(movie)
    session.commit()
