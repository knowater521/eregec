import sys, random, time
from eregec import PlatformClient

def main():
    id = 'mxb-platform'
    name = 'Ubuntu 18.04'
    host = '39.108.3.243'
    port = 51435

    platform_cilent = PlatformClient(id, name, host, port)
    if not platform_cilent.connect_server():
        sys.exit(1)
    print('服务器链接成功！')

    try:
        while platform_cilent.is_connected():
            platform_cilent.set_temperature(37 + random.randint(1, 10) / 10)
            platform_cilent.upload_data()
            time.sleep(1)
        print("服务器已断开！")
    except KeyboardInterrupt:
        platform_cilent.close()
        print('Ctrl-C')

     
if __name__ == "__main__":
    main()