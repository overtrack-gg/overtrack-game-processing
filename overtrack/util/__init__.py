import datetime


def humansize(nbytes, suffixes=('B', 'KB', 'MB', 'GB', 'TB', 'PB')):
    # http://stackoverflow.com/a/14996816
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def ms2ts(ms):
    sign = ''
    if ms < 0:
        sign = '-'
        ms = -ms
    s = ms / 1000
    m = s / 60
    h = m / 60
    return '%s%02d:%02d:%02d' % (sign, h, m % 60, s % 60)


def ts2ms(ts):
    h, m, s = ts.split(':')
    h, m, s = int(h), int(m), int(s)
    m = m + 60 * h
    s = m * 60 + s
    return s * 1000


def dhms2timedelta(s):
    td = datetime.timedelta()
    current = ''
    for c in s:
        if c.isdigit():
            current += c
        else:
            if c == 'd':
                td += datetime.timedelta(days=int(current))
            elif c == 'h':
                td += datetime.timedelta(hours=int(current))
            elif c == 'm':
                td += datetime.timedelta(minutes=int(current))
            elif c == 's':
                td += datetime.timedelta(seconds=int(current))
            else:
                raise ValueError('Unknown timedelta specifier "%s"', c)
            current = ''
    return td
