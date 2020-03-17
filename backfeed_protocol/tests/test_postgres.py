import sqlalchemy
import logging

from .test_contract_base import BaseContractTestCase
from ..models import DBSession
from ..models.user import User
from ..models.contribution import Contribution
from ..models.evaluation import Evaluation


class TestWithPostgres(BaseContractTestCase):
    """All the other tests run in memory - here we test with files"""

    settings = {
        'sqlalchemy.url': 'postgresql://backfeed_test:backfeed@localhost:5432/backfeed_test',
    }

    def setUp(self):

        try:
            super(TestWithPostgres, self).setUp()
            self.db_ok = True
        except sqlalchemy.exc.OperationalError as error:
            msg = ['*' * 80, "WARNING: There was an error connecting to the postgres server.",
                   "For this test to work, you need to set up a test database", self.settings['sqlalchemy.url'],
                   'psql -c "create database backfeed_test"',
                   'psql -c "create user backfeed_test password \'backfeed\'"',
                   'psql -c "grant all on database backfeed_test to backfeed_test"', str(error), '*' * 80]
            msg = '\n'.join(msg)
            self.db_ok = False
            logging.error(msg)

    def test_sanity(self):
        # the connection is made and defined in self.setUp
        if self.db_ok:
            self.assertTrue(self.contract.create_user())

    def test_persistence(self):
        """test if data is really really saved in the database"""
        if self.db_ok:
            user = self.contract.create_user()
            contribution = self.contract.create_contribution(user=user)
            self.contract.create_evaluation(
                user=user, contribution=contribution, value=1)
            self.assertEqual(DBSession.query(User).count(), 1)
            self.assertEqual(DBSession.query(Contribution).count(), 1)
            self.assertEqual(DBSession.query(Evaluation).count(), 1)
            DBSession.close()
            self.assertEqual(DBSession.query(User).count(), 1)
            self.assertEqual(DBSession.query(Contribution).count(), 1)
            self.assertEqual(DBSession.query(Evaluation).count(), 1)
