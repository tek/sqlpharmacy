# coding=utf-8
"""
    quick_orm.testsuite.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    database models to be tested against
"""
from quick_orm.core import Database
from sqlalchemy import Column, String, Text, DateTime, func


@Database.many_to_many('Group')
class User(metaclass=Database.DefaultMeta):
    name = Column(String(36), nullable = False, unique = True)


class Group(metaclass=Database.DefaultMeta):
    name = Column(String(36), nullable = False, unique = True)


@Database.many_to_one(User, backref_name = 'blog_entries')
class BlogEntry(metaclass=Database.DefaultMeta):
    title = Column(String(64), nullable = False)
    content = Column(Text)


class Topic(metaclass=Database.DefaultMeta):
    name = Column(String(64), nullable = False)


@Database.many_to_one(User)
class Post(metaclass=Database.DefaultMeta):
    content = Column(Text)


@Database.many_to_many(Topic)
class Question(Post):
    title = Column(String(64), nullable = False)

class Answer(Post):
    pass


Database.register()
