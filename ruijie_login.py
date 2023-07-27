import requests
import re
import datetime
import time

check_url = 'http://www.baidu.com'
username = hh
passwd = dd
def check_network():
    try:
        response = requests.get(check_url, timeout=3)
        if response.status_code == 200 and 'http://172.19.1.9:8080/eportal/index.jsp' not in response.text:
            return None
        elif 'http://172.19.1.9:8080/eportal/index.jsp' in response.text:
            re_query = re.compile(r'href=\'(.*?)\'')
            url = re_query.findall(response.text)[0]
            query_string = url.split('?')[1]
            return query_string
    except requests.exceptions.ConnectionError:
        return None

def login(query_string):
    login_url = 'http://172.19.1.9:8080/eportal/InterFace.do?method=login'

    data = {
        'userId': username,
        'password': passwd,
        'queryString': query_string,
        'service': 'Internet',
        'operatorPwd': '',
        'operatorUserId': '',
        'validcode': '',
        'passwordEncrypt': 'false'
    }
    try:
        response = requests.post(login_url, data=data)
        if response.status_code == 200:
            print('登录成功')
            return True
        else:
            print('登录失败')
            return False
    except requests.exceptions.ConnectionError:
        print('登录失败')
        return False

def main():
    while True:
        now = datetime.datetime.now()
        print(now.strftime('%Y-%m-%d %H:%M:%S'), end=' ')
        query_string = check_network()
        if query_string:
            print('网络连接异常，正在尝试登录')
            login(query_string)
        else:
            print('网络连接正常')
        time.sleep(2 * 60)

if __name__ == '__main__':
    main()
