from emoji import UNICODE_EMOJI


def is_emoji(s):
    for c in s:
        if c in UNICODE_EMOJI['en'].keys():
            return True
    return False
