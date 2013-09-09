from quick_orm.core import Database
from sqlalchemy import Column, String, Text

__metaclass__ = Database.DefaultMeta

class Question:
    title = Column(String(70))
    content = Column(Text)

@Database.many_to_one(Question, ref_name = 'question', backref_name = 'answers')
class Answer:
    content = Column(Text)

Database.register()

if __name__ == '__main__':
    db = Database('sqlite://')
    db.create_tables()

    question = Question(title = 'What is quick_orm?', content = 'What is quick_orm?')
    answer = Answer(question = question, content = 'quick_orm is a Python ORM framework which enables you to get started in less than a minute!')
    db.session.add_then_commit(answer)

    question = db.session.query(Question).get(1)
    print('The question is:', question.title)
    print('The answer is:', question.answers.first().content)