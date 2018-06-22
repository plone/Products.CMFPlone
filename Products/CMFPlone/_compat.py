# coding=utf-8
from json import dumps
from six import text_type


def dump_json_to_text(obj):
    ''' Encode an obj into a text
    '''
    text = dumps(obj, indent=4)
    if not isinstance(text, text_type):
        text = text.decode('utf8')
    return text
