from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
import requests
import json
import os


def get_miwifi_ip(password, admin_addr='http://192.168.31.1'):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    driver.get(admin_addr)

    input_password = driver.find_element(By.ID, 'password')
    input_password.send_keys(password)

    btnRtSubmit = driver.find_element(By.ID, 'btnRtSubmit')
    btnRtSubmit.click()

    sleep(1)
    current_url = driver.current_url

    wan_ip_url = current_url.replace('home', 'setting/wan')
    driver.get(wan_ip_url)

    sleep(2)
    element = driver.find_element(By.CLASS_NAME, "wanStatus")

    msg = element.text
    # 获取ip地址
    ip = re.findall(r'IP地址：(.*)', msg)[0]
    return ip


def get_router_ip(type = 'lan', params = {}):
    if type == 'lan':
        if params['brand'] == 'miwifi':
            ip = get_miwifi_ip(params['password'], params['admin_addr'])
        elif params['brand'] == 'huawei':
            pass # TODO
    else: #外网ip
        ip = requests.get('http://ip.42.pl/raw').text
    return ip

    
def get_dnspod_record(domain, token, sub_domain=None):
    # 获取域名解析记录 curl -X POST https://dnsapi.cn/Record.List -d
    # 'login_token=LOGIN_TOKEN&format=json&domain_id=12600793&sub_domain=www&record_type=A&offset=0&length=3'
    params = {
        'login_token': token,
        'format': 'json',
        'domain': domain,
        'sub_domain': sub_domain,
    }
    url = 'https://dnsapi.cn/Record.List'
    r = requests.post(url, data=params)
    return r.json()


def create_dnspod_record(domain, token, sub_domain, value, record_type='A', record_line='默认', mx=1, ttl=600):
    # 创建域名解析记录 curl -X POST https://dnsapi.cn/Record.Create -d
    # 'login_token=LOGIN_TOKEN&format=json&domain_id=2317346&sub_domain=@&record_type=A&record_line_id=10%3D0&value=1
    # .1.1.1'
    params = {
        'login_token': token,
        'format': 'json',
        'domain': domain,
        'sub_domain': sub_domain,
        'record_type': record_type,
        'record_line': record_line,
        'mx': mx,
        'ttl': ttl,
        'value': value,
    }
    url = 'https://dnsapi.cn/Record.Create'
    r = requests.post(url, data=params)
    return r.json()


# curl -X POST https://dnsapi.cn/Record.Modify -d
# 'login_token=LOGIN_TOKEN&format=json&domain_id=2317346&record_id=16894439&sub_domain=www&value=3.2.2.2&record_type
# =A&record_line_id=10%3D0'
def modify_dnspod_record(domain, token, record_id, sub_domain, record_line_id, value, record_type='A', mx=1, ttl=600):
    params = {
        'login_token': token,
        'format': 'json',
        'domain': domain,
        'record_id': record_id,
        'sub_domain': sub_domain,
        'record_line_id': record_line_id,
        'value': value,
        'record_type': record_type,
        'mx': mx,
        'ttl': ttl,
    }
    url = 'https://dnsapi.cn/Record.Modify'
    r = requests.post(url, data=params)
    return r.json()


def dnspod_ddns(domain, token, sub_domain, miwifi_passwd):
    while True:
        miwifi_params = {
            'password': miwifi_passwd,
            'admin_addr': 'http://192.168.31.1',
            'brand': 'miwifi'
        }
        ip = get_router_ip(type='lan',params=miwifi_params)  # 获取小米路由器IP地址
        record = get_dnspod_record(domain, token, sub_domain=sub_domain)  # 获取域名解析记录
        if (record['status']['code'] == '10'):  # 如果没有解析记录，则创建
            print('创建域名解析记录')
            record = create_dnspod_record(domain, token, sub_domain, ip)
        else:
            record_ip = record['records'][0]['value']
            if (ip == record_ip):  # 如果IP地址未变化，则不更新
                print('IP地址未变化，无需更新')
                continue
            record_id = record['records'][0]['id']
            record_line_id = record['records'][0]['line_id']
            print('更新域名解析记录')
            record = modify_dnspod_record(domain, token, record_id, sub_domain, record_line_id, ip)

        sleep(60 * 15)  # 每15分钟更新一次


def get_env_setting():
    domain = os.environ['DOMAIN']
    token = os.environ['TOKEN']
    sub_domain = os.environ['SUB_DOMAIN']
    miwifi_passwd = os.environ['MIWIFI_PASSWD']
    return domain, token, sub_domain, miwifi_passwd


if __name__ == '__main__':
    domain, token, sub_domain, miwifi_passwd = get_env_setting()
    dnspod_ddns(domain, token, sub_domain, miwifi_passwd)
