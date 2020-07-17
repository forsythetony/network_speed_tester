#!/usr/bin/env python3

import pyspeedtest

SPEED_TEST_HOST_SERVER = "sp1.mwdata.net:8080"

def convert_to_mbps(bitsPerSecond):

    mbs_per_second = bitsPerSecond / 1000000

    return mbs_per_second


def run_and_print():    
    st = pyspeedtest.SpeedTest(SPEED_TEST_HOST_SERVER)

    ping = st.ping()

    download_speed = st.download()
    download_speed_mbps = convert_to_mbps(download_speed)

    message = """
    Download bits/s: {}
    Download mb/s: {}
    Ping: {}
    """.format(download_speed, download_speed_mbps, ping)

    print(message)


def main():
    run_and_print()


if __name__ == "__main__":
    main()