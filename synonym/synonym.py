# -*- coding: utf-8 -*-
#!/usr/bin/env python

########################################################
#
# synonym - instant synonym answers via command line
# written by Shanyun Gao (shanyungau@gmail.com)
# inspired by howdoi (http://github.com/gleitz/howdoi )
#
########################################################


import argparse
import random
import os
import requests
import sys

import crayons
from pyquery import PyQuery as pq
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError

# Handle imports from Python 2 and 3
if sys.version < '3':
    import codecs
    from urllib import quote as url_quote
    from urllib import getproxies

    # Handle Unicode
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    from urllib.request import getproxies
    from urllib.parse import quote as url_quote

    def u(x):
        return x


SEARCH_URL = 'http://www.thesaurus.com/browse/{0}?s=t'
VERIFY_SSL_CERTIFICATE = False
URL = 'www.thesaurus.com'
USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                'Safari/536.5'), )


def get_proxies():
    proxies = getproxies()
    filtered_proxies = {}
    for key, value in proxies.items():
        if key.startswith('http'):
            if not value.startswith('http'):
                filtered_proxies[key] = 'http://%s' % value
            else:
                filtered_proxies[key] = value
    return filtered_proxies


def _get_result(url):
    return requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)}, proxies=get_proxies(),
                            verify=VERIFY_SSL_CERTIFICATE).text


def _get_link(query):
    return SEARCH_URL.format(query)


def _get_answer(args, link):
    page = _get_result(link)
    html = pq(page)
    all_answers = html('.filters')

    if len(all_answers) == 0:
        syn_answers = crayons.red(
            '\nCannot find synonym for "{}".\n'.format(args['query'][0])
                )
        return syn_answers

    if len(all_answers) == 1:
        answer = all_answers.eq(0)
        prop = answer('.synonym-description').find('.txt').text()
        defn = answer('.synonym-description').find('.ttl').text()
        if not (prop or defn):
            guess = answer('.heading-row').find('a')
            guess_word = guess.text()
            syn_answers = crayons.red(
                '\nCannot find synonym for "{}". Try "{}"?\n'.format(args['query'][0], guess_word)
                    )
            return syn_answers

    import ast
    syn_answers = []
    index = 0
    for answer in all_answers.items():
        prop = answer('.synonym-description').find('.txt').text()
        defn = answer('.synonym-description').find('.ttl').text()

        syn_answers.append((prop, defn, {}))
        syn_list = answer('a')
        for syn in syn_list.items():
            relevancy_str = syn.attr['data-category']
            relevancy_dict = ast.literal_eval(relevancy_str)
            relevancy_lv = relevancy_dict['name']

            if relevancy_lv not in syn_answers[index][2]:
                syn_answers[index][2][relevancy_lv] = [syn('.text').text()]
            else:
                syn_answers[index][2][relevancy_lv].append(syn('.text').text())
        index += 1

    return syn_answers


def _filter_answer(args):
    answer_url = _get_link(args['query'][0])
    all_answers = _get_answer(args, answer_url)

    if type(all_answers) in [str, crayons.ColoredString]:
        return all_answers

    if not args['property']:
        return all_answers

    filter_answer = []
    if args['property'] == 'n':
        for answer in all_answers:
            if answer[0] == 'noun':
                filter_answer.append(answer)
    if args['property'] == 'v':
        for answer in all_answers:
            if answer[0] == 'verb':
                filter_answer.append(answer)
    if args['property'] == 'adj':
        for answer in all_answers:
            if answer[0] == 'adj':
                filter_answer.append(answer)
    if args['property'] == 'adv':
        for answer in all_answers:
            if answer[0] == 'adv':
                filter_answer.append(answer)

    if not filter_answer:
        return crayons.magenta(
            '\nIt seems, "{}" has no such property.\n'.format(args['query'][0])
                )

    return filter_answer


def _display_answer(args):
    answer_url = _get_link(args['query'][0])
    answers = _filter_answer(args)

    if type(answers) in [str, crayons.ColoredString]:
        return answers

    texts = ''
    texts += crayons.green(
            '--- Synonyms for "{}" ---\n\n'.format(args['query'][0])
                )
    for answer in answers:
        texts += crayons.red('=== {}. {} ===\n\n'.format(answer[0], answer[1]))
        if len(answer[2]) == 0:
            texts += crayons.magenta(
                'Whoops-a-daisy, no synonyms for {} found.'.format(args['query'][0])
                    )
        elif len(answer[2]) == 1:
            (k, v), = answer[2].items()
            texts += ',  '.join(v)
            texts += '\n\n'
        else:
            if 'relevant-3' in answer[2]:
                texts += crayons.green('Most relevant synonyms:\n')
                texts += ',  '.join(answer[2]['relevant-3'])
                texts += crayons.green('\n\nLess relevant synonyms:\n')
                if 'relevant-2' in answer[2]:
                    texts += ',  '.join(answer[2]['relevant-2'])
                else:
                    texts += ',  '.join(answer[2]['relevant-1'])
                texts += '\n\n'
            else:
                texts += ',  '.join(answer[2]['relevant-2'])
                texts += '\n\n'

    texts += crayons.green('---\nAnswer from {}'.format(answer_url))
    return texts


def get_parser():
    parser = argparse.ArgumentParser(description='instant synonym answers via command line')
    parser.add_argument('query', metavar='Word of Interest', type=str, nargs=1, help='The word of interest')
    parser.add_argument('-p', '--property', help='The property of interest (type n / v / adj / adv)',
                        type=str, choices=['n', 'v', 'adj', 'adv'])
    return parser


def synonym(args):
    try:
        return _display_answer(args)
    except (ConnectionError, SSLError):
        return crayons.red(
            '\nFailed to establish network connection.\n'
        )


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if not args['query']:
        parser.print_help()
        return

    if sys.version < '3':
        print(synonym(args).encode('utf-8', 'ignore'))
    else:
        print(synonym(args))


if __name__ == '__main__':
    command_line_runner()
