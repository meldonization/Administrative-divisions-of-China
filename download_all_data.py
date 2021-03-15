"""
# province
# city
# county
# town
# village
"""
import json
import re
from urllib.parse import urljoin
import random
import time

import requests
from bs4 import BeautifulSoup

base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/index.html'
header = {
    'Cookie': 'SF_cookie_1=37059734',
    'Host': 'www.stats.gov.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': base_url,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
}
province_done = ['北京市', '天津市', '河北省', '山西省']


def load_json_from_file(file):
    with open(file, 'r') as _f:
        _c = json.load(_f)
    return _c


def write_json_to_file(res, file, mode=0):
    if mode == 0:
        with open(file, 'w') as _f:
            json.dump(res, _f)
    else:
        try:
            with open(file, 'w', encoding='utf-8') as _f:
                json.dump(res, _f, ensure_ascii=False)
        except:
            pass


def get_local_json():
    try:
        a = load_json_from_file('backup_a.json')
        b = load_json_from_file('backup_b.json')
        c = load_json_from_file('backup_c.json')
        return [i for i in a if i['name'] in province_done], {i: b[i] for i in b if i in province_done}, c
    except:
        return [], {}, {}


def backup():
    write_json_to_file(result, 'backup_a.json')
    write_json_to_file(result_1, 'backup_b.json')
    write_json_to_file(code_name_map, 'backup_c.json')


def get_html(url, referer=base_url):
    global last_time
    print(url, flush=True)
    header.update({'referer': referer})
    while True:
        try:
            if last_time and time.time() - last_time < 3:
                sleep_time = 2.5 + 3 * random.random()
                print('sleep {}...'.format(sleep_time), flush=True)
                time.sleep(sleep_time)
            last_time = time.time()
            r = requests.get(url, headers=header)
            soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser')
            _ = get_valid_table_row(soup)
            return soup
        except:
            pass


def get_valid_table_row(soup, merge=False):
    target = soup.find('tr', attrs={'class': re.compile('.+head')})
    tr_list = target.find_next_siblings('tr', attrs={'class': re.compile('.+tr')})
    td_list = []
    for each_tr in tr_list:
        if merge:
            td_list.extend(each_tr.find_all('td'))
        else:
            td_list.append(each_tr.find_all('td'))
    return td_list


result, result_1, code_name_map = get_local_json()
last_time = None


def retrieve_content():
    province_soup = get_html(base_url)
    province_td_list = get_valid_table_row(province_soup, merge=True)
    for province_td in province_td_list:
        province_anchor = province_td.find('a')
        if not province_anchor:
            continue
        province = province_anchor.text
        province_code = province_anchor.attrs['href'].split('.')[0]
        if not province:
            continue
        if province in province_done:
            continue
        print('province: ' + province, flush=True)
        result.append({'name': province, 'code': province_code, 'children': []})
        result_1.update({province: {}})
        code_name_map[province_code] = province
        province_result = result[-1]['children']
        city_url = urljoin(base_url, province_anchor.attrs['href'])
        city_soup = get_html(city_url, referer=base_url)
        city_td_list = get_valid_table_row(city_soup)
        for city_td in city_td_list:
            city_code = city_td[0].text
            city = city_td[1].text
            if not city:
                continue
            print(' city: ' + city, flush=True)
            province_result.append({'name': city, 'code': city_code, 'children': []})
            code_name_map[city_code] = city
            result_1[province].update({city: {}})
            city_result = province_result[-1]['children']
            city_anchor = city_td[0].find('a')
            if not city_anchor:
                continue
            county_url = urljoin(city_url, city_anchor.attrs['href'])
            county_soup = get_html(county_url, referer=city_url)
            county_td_list = get_valid_table_row(county_soup)
            for county_td in county_td_list:
                county_code = county_td[0].text
                county = county_td[1].text
                if not county:
                    continue
                print('  county: ' + county, flush=True)
                city_result.append({'name': county, 'code': county_code, 'children': []})
                result_1[province][city].update({county: {}})
                code_name_map[county_code] = county
                county_result = city_result[-1]['children']
                county_anchor = county_td[0].find('a')
                if not county_anchor:
                    continue
                town_url = urljoin(county_url, county_anchor.attrs['href'])
                town_soup = get_html(town_url, referer=county_url)
                town_td_list = get_valid_table_row(town_soup)
                for town_td in town_td_list:
                    town_code = town_td[0].text
                    town = town_td[1].text
                    if not town:
                        continue
                    print('   town: ' + town, flush=True)
                    county_result.append({'name': town, 'code': town_code, 'children': []})
                    result_1[province][city][county].update({town: []})
                    code_name_map[town_code] = town
                    town_result = county_result[-1]['children']
                    town_anchor = town_td[0].find('a')
                    if not town_anchor:
                        continue
                    village_url = urljoin(town_url, town_anchor.attrs['href'])
                    village_soup = get_html(village_url, referer=town_url)
                    village_td_list = get_valid_table_row(village_soup)
                    for village_td in village_td_list:
                        village_code = village_td[0].text
                        village_type = village_td[1].text
                        village = village_td[2].text
                        if not village:
                            continue
                        # print('    village: ' + village, flush=True)
                        town_result.append({'name': village, 'code': village_code, 'type': village_type})
                        result_1[province][city][county][town].append(village)
                        code_name_map[village_code] = village

        backup()


if __name__ == "__main__":
    try:
        retrieve_content()
    except Exception as e:
        print(e, flush=True)
        backup()

    write_json_to_file(result, 'a.json')
    write_json_to_file(result_1, 'b.json')
    write_json_to_file(code_name_map, 'c.json')

    write_json_to_file(result, 'a_1.json', mode=1)
    write_json_to_file(result_1, 'b_1.json', mode=1)
    write_json_to_file(code_name_map, 'c_1.json', mode=1)

    print('done!', flush=True)
