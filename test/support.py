import sys

def forcibly_utf8(string):
    if string is None:
        return None
    if sys.version_info[0] == 3:
        return bytes(ord(x) for x in string).decode('utf8')
    if type(string) is not unicode:
        return unicode(string, 'utf8')
    return string
