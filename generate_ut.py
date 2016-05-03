# -*- coding: utf-8 -*-
__author__ = 'schiavoni'

import unittest

import generate
from generate import text_split, Poem_generator


class tests(unittest.TestCase):
    def test_text_split(self):
        self.assertEqual(text_split(u'Андрей, сказал: Привет!'),
                         [u'андрей', u',', u'сказал', u':', u'привет', u'!'])
        self.assertEqual(text_split(u'Пора, друзья: - здесь, ура.'),
                         [u'пора', u',', u'друзья', u':', u'-', u'здесь', u',', u'ура', u'.'])

    def test_is_rythm(self):
        my_generator = Poem_generator("learning_text.txt", 20, 3)
        self.assertTrue(my_generator.is_rythm(u'соль', u'боль'))
        self.assertFalse(my_generator.is_rythm(u'соль', u'баранина'))
        self.assertFalse(my_generator.is_rythm(u'я', u'солнце'))
        self.assertTrue(my_generator.is_rythm(u'и', u'ботинки'))

if __name__ == "__main__":
    unittest.main()