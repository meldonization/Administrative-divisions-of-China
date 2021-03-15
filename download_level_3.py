"""
# province
# city
# county
"""
from download_data import *


def retrieve_level_3():
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
        print('province: ' + province)
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
            print(' city: ' + city)
            province_result.append({'name': city, 'code': city_code, 'children': []})
            code_name_map[city_code] = city
            result_1[province].update({city: []})
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
                # print('  county: ' + county)
                city_result.append({'name': county, 'code': county_code})
                result_1[province][city].append(county)
                code_name_map[county_code] = county
        backup()


if __name__ == "__main__":
    try:
        retrieve_level_3()
    except Exception as e:
        print(e)
        backup()

    write_json_to_file(result, 'a.json')
    write_json_to_file(result_1, 'b.json')
    write_json_to_file(code_name_map, 'c.json')

    write_json_to_file(result, 'a_1.json', mode=1)
    write_json_to_file(result_1, 'b_1.json', mode=1)
    write_json_to_file(code_name_map, 'c_1.json', mode=1)

    print('done!')
