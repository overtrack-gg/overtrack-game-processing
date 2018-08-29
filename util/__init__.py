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
