import sys, random, time
from eregec import PlatformClient

def main():
    name = 'eregec'
    password = '123456'
    host = '39.108.3.243'
    port = 51435

    platform_cilent = PlatformClient(name, password, host, port)
    if not platform_cilent.connect():
        sys.exit(1)
    print('服务器链接成功！')

    try:
        while platform_cilent.is_connected():
            platform_cilent.set_float_data("temperature", 37 + random.randint(1, 10) / 10)
            platform_cilent.set_float_data("humidity", 18 + random.randint(1, 100) / 100)
            platform_cilent.upload_data()
            time.sleep(1)
        print("服务器已断开！")
    except KeyboardInterrupt:
        platform_cilent.disconnect()
        print('Ctrl-C')

     
if __name__ == "__main__":
    main()