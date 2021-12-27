import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import POSTGRES_URI


Base = declarative_base()
engine = sq.create_engine(POSTGRES_URI)
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    id_vk = sq.Column(sq.Integer, unique=True)
    city = sq.Column(sq.String)
    age = sq.Column(sq.Integer)
    sex = sq.Column(sq.Integer)
    relation = sq.Column(sq.Integer)


class Candidates(Base):
    __tablename__ = 'candidates'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    id_vk = sq.Column(sq.Integer, unique=True)
    user_link = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id_vk', ondelete='CASCADE'))


def create_tables():
    Base.metadata.create_all(engine)


def add_candidate(id_vk, first_name, last_name, user_link, id_user):
    session.expire_on_commit = False
    new_candidate = Candidates(id_vk=id_vk, first_name=first_name, last_name=last_name,
                               user_link=user_link, id_user=id_user)
    session.add(new_candidate)
    session.commit()
    return True


def get_user(id_vk):
    session.expire_on_commit = False
    user = session.query(User).filter_by(id_vk=id_vk).first()
    return user


def get_candidate(id_vk):
    session.expire_on_commit = False
    candidate = session.query(Candidates).filter_by(id_vk=id_vk).first()
    return candidate


def register_user(id_vk, first_name, last_name, city, age, sex, relation):
    session.expire_on_commit = False
    new_user = User(id_vk=id_vk, first_name=first_name, last_name=last_name,
                    city=city, age=age, sex=sex, relation=relation)
    session.add(new_user)
    session.commit()
    return True
