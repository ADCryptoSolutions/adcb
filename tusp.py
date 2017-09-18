#-*-coding:utf-8-*-

import datetime, time

def ts2string(ts, fmt="%Y-%m-%d %H:%M:%S"):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime(fmt)

def string2ts(string, fmt="%Y-%m-%d %H:%M:%S"):
    dt = datetime.datetime.strptime(string, fmt)
    t_tuple = dt.timetuple()
    return int(time.mktime(t_tuple))

def test():
    ts = 1504244643

    string = ts2string(ts)
    print string

    ts = string2ts(string)
    print ts

if __name__ == '__main__':
    test()

