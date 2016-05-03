# -*- coding: utf-8 -*-
__author__ = 'schiavoni'

from urllib2 import urlopen
from HTMLParser import HTMLParser
import optparse
import codecs
from contextlib import closing


class MyHTMLParser(HTMLParser):
    """Find and save poem from html code. Text is a poem, if it's in main div tag
    and input tag with name and id_poem are its attrs"""
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_in_text = False
        self.is_in_div = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        if (tag == "div") and (("class", "main_div") in attrs):
            self.is_in_div = True
        if (tag == "input") and (("name", "id_poem") in attrs) and self.is_in_div:
            self.is_in_text = True

    def handle_data(self, data):
        if self.is_in_text:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self.is_in_text:
            self.is_in_text = False
            self.is_in_div = False
            return


def save_text_from_url(url):
    with closing(urlopen(url)) as conn:
        html = conn.read().decode('windows-1251')

    parser = MyHTMLParser()
    parser.feed(html)
    return parser.text


def main():
    """collect poems =)"""
    parser = optparse.OptionParser()
    parser.description = __doc__
    parser.add_option('-o', '--out',
                      dest='out',
                      metavar='out text path',
                      help='Path to file to write out collected text.')
    options, args = parser.parse_args()
    print options

    if options.out is None:
        parser.error("Out file isn't identified.")

    out = options.out

    text = []
    for index in range(0, 10000):
        try:
            text += save_text_from_url("http://stihidl.ru/poem/" + str(index) + str("/"))
            text += "\n\n\n"
            print index
        except KeyboardInterrupt:
            break
        except:
            pass
    text = ' '.join(text)

    with codecs.open(out, "w", "utf-8") as file_out:
        file_out.write(text)
    pass

if __name__ == "__main__":
    main()
