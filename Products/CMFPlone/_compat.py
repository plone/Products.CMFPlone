from json import dumps


def dump_json_to_text(obj):
    ''' Encode an obj into a text
    '''
    text = dumps(obj, indent=4)
    if not isinstance(text, str):
        text = text.decode('utf8')
    return text
