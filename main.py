import os

from util.pushplus_util import PushPlusUtil
from util.yomiao_util import YomiaoUtil

CONFIG_FILE = os.path.dirname(__file__) + os.sep + "config.ini"


def main():
    plus_util = PushPlusUtil(CONFIG_FILE)
    yomiao_util = YomiaoUtil(CONFIG_FILE)
    push_data = yomiao_util.get_departments()
    if push_data['code'] == 0:
        plus_util.send(push_data['title'], push_data['content'])
    else:
        for i in range(3):
            plus_util.send('约苗异常通知.', push_data['msg'])


if __name__ == '__main__':
    # 可配置系统定时任务crontab -e
    print("约苗通知启动... 配置文件所在路径: %s" % CONFIG_FILE)
    main()
    print("约苗发送通知完毕...")
