""" test """

def valid_xml_char_ordinal(character):
    """ test 1 """
    codepoint = ord(character)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )


def clear_str_for_xml(dirty_str):
    """ test2 """
    clear_str = ''.join(c for c in dirty_str if valid_xml_char_ordinal(c))
    return clear_str


def clear_str_or_none(dirty_str):
    """ Очистить строку от символов unicode """
    # if dirty_str is None:
    #     return None
    if type(dirty_str) is str:
        return clear_str_for_xml(dirty_str)
    return dirty_str


if __name__ == '__main__':
    ch = None
    CHAR_1 = clear_str_or_none(ch)
    print(CHAR_1)

