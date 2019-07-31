from sqlalchemy import Column, Integer, String

from database_connect import Base


class TestTable(Base):

    """
    TestTable class:
        If you want to use sqlalchemy for modeling your database you can create your model classes here.

    """

    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name
