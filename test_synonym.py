#!/usr/bin/env python

"""Tests for synonym."""
import unittest

from synonym import synonym


class SynonymTestCase(unittest.TestCase):

    def return_synonym(self, query):
        parser = synonym.get_parser()
        args = vars(parser.parse_args(query.split(' ')))
        return synonym.synonym(args)

    def setUp(self):
        self.queries = ['display', 'make', 'very']
        self.typo_queries = ['halla', 'intesting', 'placs']
        self.bad_queries = ['lksdlkf', 'lksjldkjf']

    def tearDown(self):
        pass

    def test_synonyms(self):
        for query in self.queries:
            self.assertTrue(self.return_synonym(query))
        for query in self.typo_queries:
            self.assertTrue(self.return_synonym(query))
        for query in self.bad_queries:
            self.assertTrue(self.return_synonym(query))

    def test_property(self):
        query = self.queries[0]
        first_answer = self.return_synonym(query)
        second_answer = self.return_synonym(query + ' -pn')
        self.assertNotEqual(first_answer, second_answer)


if __name__ == '__main__':
    unittest.main()
