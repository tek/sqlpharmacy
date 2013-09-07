# coding=utf-8
"""
    quick_orm.testsuite.core
    ~~~~~~~~~~~~~~~~~~~~~~~~
    test the core of quick_orm
"""

import unittest

from quick_orm.core import Database
from quick_orm.testsuite.models import User, Group, BlogEntry, Question
import quick_orm.testsuite.fixtures as fixtures


class CoreTestCase(unittest.TestCase):
    """The default test case"""

    @classmethod
    def setUpClass(self):
        db_name = 'sqlite'
        db_strs = {
            'postgresql': 'postgresql://postgres:123456@localhost/quick_orm',
            'sqlite': 'sqlite:///quick_orm/testsuite/quick_orm.db',
            'mysql': 'mysql://root:123456@localhost/quick_orm?charset=utf8',
        }
        db_str = db_strs[db_name]
        self.db = Database(db_str)
        self.db.drop_tables()
        self.db.create_tables()
        self.db.load_data(fixtures)

    def tearDown(self):
        self.db.session.remove()

    def test_many_to_one(self):
        """Test many_to_one relationship"""
        user = self.db.session.query(User).filter_by(name='simon').first()
        assert user
        assert user.blog_entries.count() > 0
        assert user.blog_entries.first().user.name == 'simon'

    def test_many_to_many(self):
        """Test many_to_many relationship"""
        user = self.db.session.query(User).filter_by(name='simon').first()
        assert user
        assert user.groups.count() > 0
        assert user.groups.first().users.count() > 0
        assert any(u.name == 'simon' for u in user.groups.first().users)

    def test_many_to_one_cascade(self):
        """Test cascade in a many_to_one relationship.
        When record from the one side gets deleted,
        records from the many side are deleted automatically.
        Make sure no ignorant records are deleted.
        """
        user_query = self.db.session.query(User)
        user_count = user_query.count()
        blog_query = self.db.session.query(BlogEntry)
        blog_count = blog_query.count()
        user = self.db.session.query(User).filter_by(name='peter').first()
        assert user
        user_blog_count = user.blog_entries.count()
        blog_entry = user.blog_entries.first()
        assert blog_entry
        self.db.session.delete_then_commit(user)
        blog_entry = self.db.session.query(BlogEntry).get(blog_entry.id)
        assert not blog_entry
        assert user_count - 1 == user_query.count()
        assert blog_count - user_blog_count == blog_query.count()

    def test_many_to_many_cascade(self):
        """Test cascade in a many_to_many relationship.
        when record from either side gets deleted,
        records from the middle table are deleted automatically,
        records from the other side retain.
        make sure no ignorant records are deleted.
        """
        user_query = self.db.session.query(User)
        user_count = user_query.count()
        group_query = self.db.session.query(Group)
        group_count = group_query.count()
        middle_query_str = 'select count(*) from user_group'
        middle_count = self.db.engine.execute(middle_query_str).scalar()

        user = self.db.session.query(User).filter_by(name='tyler').first()
        assert user
        query = 'select count(*) from user_group where user_id={0}'
        query = query.format(user.id)
        user_middle_count = self.db.engine.execute(query).scalar()
        group = self.db.session.query(Group).filter_by(name='editor').first()
        assert group
        query_str = ('select count(*) from user_group where user_id={0} and '
                     'group_id={1}'.format(user.id, group.id))
        assert self.db.engine.execute(query_str).scalar() == 1
        self.db.session.delete_then_commit(user)
        assert self.db.engine.execute(query_str).scalar() == 0
        group = self.db.session.query(Group).filter_by(name='editor').first()
        assert group

        assert user_count - 1 == user_query.count()
        assert group_count == group_query.count()
        assert (middle_count - user_middle_count ==
                self.db.engine.execute(middle_query_str).scalar())

    def test_table_inheritance(self):
        """Test table inheritance"""
        question_query = self.db.session.query(Question)
        question_count = question_query.count()
        assert question_count > 0
        query = self.db.session.query(Question)
        question = query.filter_by(title='question_title_1').first()
        assert question

        assert question.user
        assert any(question.title == q.title for q in question.user.questions)
