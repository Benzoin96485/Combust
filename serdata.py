import time
import pandas as pd
import matplotlib.pyplot as plt
import serial
import argparse
import serial.tools.list_ports


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--number',
        type=int,
        default=0,
        help="第几组数据"
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=0.4,
        help="数字越小，数据点越密集" 
    )
    flags, unparsed = parser.parse_known_args()
    return flags


def DOpenPort(portx, bps, timeout):
    ret = False
    try:
        ser = serial.Serial(portx, bps, timeout=timeout)
        if ser.is_open:
            ret = True
    except Exception as e:
        print("---异常---：", e)
    return ser, ret


def DClosePort(ser):
    ser.close()


def trans(s):
    ans = ''
    minus = s[5]
    if minus == '1':
        ans += "1"
    elif minus == 'b':
        ans += "-"
    elif minus == 'c':
        ans += "-1"
    ans += s[7] + '.' + s[9] + s[11] + s[13]
    return ans


if __name__ == "__main__":
    FLAGS = parseArgs()
    port_list = list(serial.tools.list_ports.comports())
    port = ''
    if len(port_list) == 0:
        print('无可用串口')
        exit(0)
    else:
        q = 0
        for portinfo in port_list:
            if "341" in str(portinfo):
                print("已经找到仪器")
                port = str(portinfo).split()[0]
                break
    if not port:
        print("未找到仪器")
        exit(0)
    plt.ion()
    df = pd.DataFrame()
    times = []
    temp = []
    starttime = time.time()
    while True:
        try:
            ser, ret = DOpenPort(port, 1200, None)
            s = str(ser.read(7).hex())
            endtime = time.time()
            loc = s.find("ff")
            if loc:
                ser.read(loc)
            plt.clf()
            s = str(ser.read(7).hex())
            DClosePort(ser)
            try:
                T = float(trans(s))
            except:
                continue
            else:
                times.append(round(endtime - starttime, 2))
                temp.append(T)
            print(str(round(endtime - starttime, 2)) + " s, " + trans(s) + " K")
            plt.plot(times, temp)
            plt.pause(FLAGS.interval)
        except KeyboardInterrupt:
            break
    plt.ioff()
    plt.savefig("./figure{}.png".format(FLAGS.number))
    plt.show() 
    df["t"] = times
    df["T"] = temp
    df.to_csv("./data{}.csv".format(FLAGS.number))