import configparser

import requests

from constant.consts import *
from exception.null_exception import NullException


class YomiaoUtil:
    def __init__(self, config_file):
        if config_file is None or config_file == '':
            raise NullException("配置文件不能为空.")

        self.config_file = config_file
        cf = configparser.ConfigParser()
        cf.read(config_file, 'utf-8')
        yomiao = cf[YO_MIAO]
        self.scheme = yomiao[SCHEME]
        self.host = yomiao[HOST]
        self.url = self.scheme + "://" + self.host
        headers = cf.items(YO_MIAO_HEADERS)
        self.headers = {}
        for header in headers:
            self.headers[header[0]] = header[1]

        self.cookies = {}
        cookies = cf.items(YO_MIAO_COOKIES)
        for cookie in cookies:
            self.cookies[cookie[0]] = cookie[1]

        # 可能有多个
        self.customIds = cf.get(YO_MIAO_PARAMS, YO_MIAO_CUSTOM_IDS).split(",")
        params = cf.get(YO_MIAO_PARAMS, YO_MIAO_URI_GETDEPARTMENTS_DO)
        # 查询部门接口
        self.getDepartments_uri = cf.get(YO_MIAO_URI, YO_MIAO_URI_GETDEPARTMENTS_DO) + params

    def get_departments(self):
        push_list = []
        for customId in self.customIds:
            request_url = self.url + self.getDepartments_uri
            request_url = request_url.format(customId)
            r = requests.post(request_url, self.headers, self.cookies)
            status_code = r.status_code
            if status_code == requests.codes.ok:
                json = r.json()
                code = json['code']
                if code == '0000':
                    data = self.processor_data(json)
                    push = {'customDesc': CUSTOM_DIR[customId], 'data': data}
                    push_list.append(push)
                else:
                    exception_msg = "Exception 接口请求异常. 请求地址: [{}], code码: [{}]".format(request_url, code)
                    print(exception_msg)
                    return {'code': -1, "msg": exception_msg}
            else:
                error_msg = "Error 请求失败. 请求地址: [{}], 状态码: [{}]".format(request_url, status_code)
                print(error_msg)
                return {'code': -1, "msg": error_msg}

        # 组装通知数据
        return self.push(push_list)

    def processor_data(self, json):
        data = json['data']
        # print("数据total: [{}]".format(data['total']))
        rows = data['rows']
        # 可预约的数量
        allow_count = 0
        allow_list = []
        for row in rows:
            if row['total'] > 0:
                allow_count += 1
                allow_doctor = {
                    'name': row['name'],
                    'address': row['address'],
                    'tel': row['tel'],
                    'worktimeDesc': row['worktimeDesc'],
                    'vaccineName': row['vaccineName'],
                    'total': row['total'],
                    'price': row['price'],
                    'isNoticedUserAllowed': row['isNoticedUserAllowed']
                }
                allow_list.append(allow_doctor)

        # print("可预约的数量为: [{}], 可约的医院列表为: ".format(allow_count), allow_list)
        return {'allow_count': allow_count, 'allow_list': allow_list}

    def push(self, push_list):
        # print("push: ", push_list)
        title = "约苗通知"
        contents = ""
        content_head_template = "疫苗种类: {} \n" \
                                "可约门诊数量: {} \n" \
                                "可约列表: \n"
        content_template = "门诊: {} \n" \
                           "地址: {} \n" \
                           "电话: {} \n" \
                           "工作时间: {} \n" \
                           "名称: {} \n" \
                           "数量: {} \n" \
                           "价格: {} \n"
        for push in push_list:
            data = push['data']
            content_head = content_head_template.format(push['customDesc'], data['allow_count'])
            temp_content = ""
            for allow in data['allow_list']:
                content = content_template.format(allow['name'], allow['address'], allow['tel'],
                                                  allow['worktimeDesc'], allow['vaccineName'], allow['total'],
                                                  allow['price'] / 100)
                temp_content += content + "\n"
            if temp_content == "":
                temp_content = "无\n"
            contents += content_head + temp_content + "\n"

        # print(contents)
        return {'title': title, 'content': contents, 'code': 0}
