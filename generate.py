# - * - coding: utf - 8 - * -
__author__ = 'schiavoni'

import optparse
import codecs
import numpy as np
import random
import pandas as pd


PUNCTUATIONS_MARKS = ['?', '.', '!', ',', '"', '-', ':', '(', ')', ' ']
END_MARKS = ['.', '!', '?']
UNNECESSARY_MARKS = ['"', '(', ')', ' ']


def text_split(text):
    """split all text by words, punctuations marks are words too"""
    splitted_text = []
    index = 0
    begin = 0
    while index < len(text):
        if text[index] in PUNCTUATIONS_MARKS:
            if begin != index:
                word = text[begin: index]
                word = word.lower()
                splitted_text.append(word)
            if text[index] not in UNNECESSARY_MARKS:
                splitted_text.append(text[index])
            begin = index + 1
            index = begin
            continue
        index += 1
    return splitted_text


def add_dependences(sentence, depth, data_frame_keys, data_frame_values):
    """ on enter sentense without end punctuation """
    if depth == 0:
        for word in sentence:
            data_frame_keys.append(word)
            data_frame_values.append(word)
            return
    for index_of_cur_word, word in enumerate(sentence):
        if index_of_cur_word == 0:
            data_frame_keys.append(word)
            data_frame_values.append(word)
        for dep_index in range(index_of_cur_word + 1,
                               min(index_of_cur_word + depth + 1, len(sentence))):
            data_frame_keys.append(word)
            data_frame_values.append(sentence[dep_index])


def statistics_collector(path, depth, data_frame):
    """calculate statistics"""

    word_dict = {}
    words_in_sentence = []
    data_frame_keys = []
    data_frame_values = []
    # split the text
    with open(path) as fin:
        data_in = fin.readlines()
        data_in = [x.decode("utf-8") for x in data_in]
        text = []
        sentence = []
        words_in_line = []
        words_quantity = 0
        for line in data_in:
            text_line = text_split(line)
            for word in text_line:
                if word in END_MARKS:
                    add_dependences(sentence, depth, data_frame_keys, data_frame_values)
                    text.append(sentence)
                    words_in_sentence.append(len(sentence))
                    sentence = []
                    continue
                words_quantity += 1
                sentence.append(word)
            if words_quantity > 0:
                words_in_line.append(words_quantity)
                words_quantity = 0

        data_frame["key"] = data_frame_keys
        data_frame["val"] = data_frame_values

    # calculate mean of words in sentence quantity and in the line
    mean_words_in_sentence_quantity = np.mean(words_in_sentence)
    print mean_words_in_sentence_quantity
    mean_words_in_line_quantity = np.mean(words_in_line)
    print mean_words_in_line_quantity
    return word_dict, mean_words_in_sentence_quantity, mean_words_in_line_quantity


def choice_rythm():
    """choose the rythm scheme: abab, aabb or abba"""
    possible_rythm = [[0, 1, 0, 1], [0, 0, 2, 2], [0, 1, 1, 0]]
    return random.choice(possible_rythm)


def weighted_random(weights):
    number = random.random() * sum(weights.values())
    for k, v in weights.iteritems():
        if number < v:
            break
        number -= v
    return str(k)


class Poem_generator:
    """Generate poem with fixed size depth dependenced and unfixed rythm"""
    def __init__(self, path, size, depth):
        self.path = path
        self.size = size
        self.depth = depth
        self.lines_quantity = 0
        self.sentences_quantity = 0
        self.generated_word_in_lines = []
        self.lines_per_sentence = 0
        self.rythm = []
        self.data_frame = pd.DataFrame()

    def define_poem_properties(self, mean_words_in_line, mean_words_in_sentence):
        # define lines quantity and words in lines quantity
        print mean_words_in_line
        self.lines_quantity = self.size / int(mean_words_in_line)
        if self.size % int(round(mean_words_in_line) >= int(mean_words_in_line)) / 3:
            # correct size
            self.lines_quantity += 1

        # define words quantity in each line
        self.generated_words_in_lines = []
        generated_words = 0
        for line_index in range(0, self.lines_quantity - 1):
            cur_generated_quantity = int(round(np.random.normal(mean_words_in_line, 0.55)))
            self.generated_words_in_lines.append(cur_generated_quantity)
            generated_words += cur_generated_quantity
        # in the last line:
        self.generated_words_in_lines.append(self.size - generated_words)

        # define sentences quantity
        self.lines_per_sentence = int(round(mean_words_in_sentence / mean_words_in_line))
        self.sentence_quantity = self.lines_quantity / self.lines_per_sentence
        if self.lines_quantity % self.lines_per_sentence > 0:
            self.sentence_quantity += 1

        #define is there a rythm
        self.rythm = choice_rythm()

    def generate_end_punctuation(self):
        # the following values can be any non-negative numbers, no need of sum=100
        weights = {'.': 70,
                   '!': 20,
                   '?': 10.}
        return weighted_random(weights)

    def generate_possibility_list(self, previous_words):
        """generate list of possible words we could generate in depend on fixed previous"""
        possibility_list = []
        for word in previous_words:
            possibility_list += list(self.data_frame[self.data_frame["key"] == word]["val"])
        return possibility_list

    def generate_first_word(self):
        """generate random word not in PUNCTUATIONS_MARKS"""
        word = random.choice(self.data_frame["key"])
        while word in PUNCTUATIONS_MARKS:
            word = random.choice(self.data_frame["key"])
        return word

    def generate_word(self, sentence):
        if self.depth == 0:
            return self.generate_first_word()
        previous_words = sentence[max(0, len(sentence)-self.depth):]
        prev_word = sentence[-1]
        probability_list = self.generate_possibility_list(previous_words)
        if len(probability_list) == 0:
            word = random.choice(self.data_frame["key"])
        else:
            word = random.choice(probability_list)
        # do not generate two punctuations in a row
        while word in PUNCTUATIONS_MARKS and prev_word in PUNCTUATIONS_MARKS:
            if len(probability_list) == 0:
                word = random.choice(self.data_frame["key"])
            else:
                word = random.choice(probability_list)
        return word

    def generate_no_punctuation(self, sentence):
        """generate word not in PUNCTUATION_MARKS"""
        previous_words = sentence[max(0, len(sentence)-self.depth):]
        probability_list = self.generate_possibility_list(previous_words)
        if len(probability_list) == 0:
            word = random.choice(self.data_frame["key"])
        else:
            word = random.choice(probability_list)
        while word in PUNCTUATIONS_MARKS:
            if len(probability_list) == 0:
                word = random.choice(self.data_frame["key"])
            else:
                word = random.choice(probability_list)
        return word

    def is_rythm(self, word_first, word_second):
        """check if two words are rhymed"""
        # if two/one last letters are the same
        min_length = min(len(word_first), len(word_second))
        if min_length >= 2:
            return word_first[len(word_first) - 2:] == word_second[len(word_second) - 2:]
        return word_first[-1] == word_second[-1]

    def generate_rythm(self, sentence, rythm_word):
        """generate rythmed word"""
        if self.depth == 0:
            return self.generate_first_word()
        previous_words = sentence[max(0, len(sentence)-self.depth):]
        probability_list = self.generate_possibility_list(previous_words)
        if len(probability_list) > 0:
            word = random.choice(probability_list)
            probability_list.remove(word)
            while (self.is_rythm(word, rythm_word) == 0) and (len(probability_list) > 0):
                word = random.choice(probability_list)
                probability_list.remove(word)
            if self.is_rythm(word, rythm_word):
                return word
        # if there's no rythm word from possibility, choice it from all
        for possible_rythm in self.data_frame["key"]:
            if self.is_rythm(possible_rythm, word):
                return possible_rythm
        # if there's no rytm everyvere choose random word
        return random.choice(self.data_frame["key"])

    def generate_rythm_word(self, index_in_quatrain, end_words, sentence, word):
        # if we needn't to rythm in rythm scheme
        if index_in_quatrain == self.rythm[index_in_quatrain]:
            return word
        # is rythm already exist
        if self.is_rythm(end_words[self.rythm[index_in_quatrain]], word):
            return word
        # else generate rythm word
        return self.generate_rythm(sentence, end_words[self.rythm[index_in_quatrain]])

    def generate_line(self, sentence, words_quantity, index_in_quatrain,
                      index_in_sentence, end_words, is_end):
        sentence_new = sentence
        string = []

        # generate first word in line
        if index_in_sentence == 0:
            generated_word = self.generate_first_word()
        else:
            generated_word = self.generate_no_punctuation(sentence_new)
        sentence_new.append(generated_word)
        string.append(generated_word)

        # generate another words
        for index in range(1, words_quantity):
            if is_end and (index == words_quantity - 1):
                generated_word = self.generate_no_punctuation(sentence_new)
            else:
                generated_word = self.generate_word(sentence_new)
            sentence_new.append(generated_word)
            string.append(generated_word)
        if (index_in_sentence == self.lines_per_sentence - 1) or is_end:
            generated_word = self.generate_end_punctuation()
            string.append(generated_word)

        # change the last word in string to make a rythm
        if string[-1] in PUNCTUATIONS_MARKS:
            rythm_word = string[-2]
            string[-2] = \
                self.generate_rythm_word(index_in_quatrain, end_words, sentence, rythm_word)
        else:
            rythm_word = string[-1]
            string[-1] = \
                self.generate_rythm_word(index_in_quatrain, end_words, sentence, rythm_word)
        return string

    def text_generator(self):
        """generate the poem"""
        word_dict, mean_words_in_sentence, mean_words_in_line = \
            statistics_collector(self.path, self.depth, self.data_frame)

        self.define_poem_properties(mean_words_in_line, mean_words_in_sentence)

        # now generate poem's strings
        poem = []
        sentence = []
        end_line_words = []
        end_lines_indexes = []

        for index in range(0, self.lines_quantity):
            if index % self.lines_per_sentence == self.lines_per_sentence - 1:
                end_lines_indexes.append(index)
        if end_lines_indexes[-1] != self.lines_quantity - 1:
            end_lines_indexes.append(self.lines_quantity - 1)

        for line_index in range(0, self.lines_quantity):
            index_in_quatrain = line_index % 4
            index_in_sentence = line_index % self.lines_per_sentence
            if index_in_sentence == 0:
                sentence = []
            if index_in_quatrain == 0:
                end_line_words = []
            line = self.generate_line(sentence, self.generated_words_in_lines[line_index],
                                      index_in_quatrain, index_in_sentence, end_line_words,
                                      (line_index in end_lines_indexes))
            if line[-1] in PUNCTUATIONS_MARKS:
                end_line_words.append(line[-2])
            else:
                end_line_words.append(line[-1])
            sentence += line
            poem.append(line)
        return poem


def write_out(path_out, poem):
    text = []
    first_word = 1
    new_quatrain = 1
    for line in poem:
        for word in line:
            if first_word:
                word = word.capitalize()
                text.append(word)
                first_word = 0
                continue
            if word in PUNCTUATIONS_MARKS:
                text.append(word)
            else:
                text.append(" ")
                text.append(word)
        text.append("\n")
        first_word = 1
        if new_quatrain % 4 == 0:
            text.append("\n")
        new_quatrain += 1
    text = ''.join(text)
    with codecs.open(path_out, "w", "utf-8") as file_out:
        file_out.write(text)


def main():
    parser = optparse.OptionParser()
    parser.description = __doc__
    parser.add_option('-p', '--path',
                      dest='path',
                      metavar='learning text path',
                      help='Path to file with learning text.')
    parser.add_option('-s', '--size',
                      dest='size',
                      metavar='generated file size',
                      help='Number of the words we will need to generate.')
    parser.add_option('-o', '--out',
                      dest='out',
                      metavar='out text path',
                      help='Path to file to write out generated text.')
    parser.add_option('-d', '--depth',
                      dest='depth',
                      metavar='depending length',
                      help='Number of words on witch current word is depending.')
    options, args = parser.parse_args()

    if options.path is None:
        parser.error("Learning file isn't identified.")
    if options.size is None:
        parser.error("Size isn't fixed.")
    if options.out is None:
        parser.error("Out file isn't identified.")
    if options.depth is None:
        parser.error("Depth isn't fixed.")

    path = options.path
    out = options.out
    size = int(options.size)
    depth = int(options.depth)

    my_generator = Poem_generator(path, size, depth)

    poem = my_generator.text_generator()
    write_out(out, poem)


if __name__ == "__main__":
    main()
