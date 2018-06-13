#########################################
#
# 드조위키의 연도별 드라마 리스트 url로 드라마 정보 scraping 해오기
# 2017. 12. 05  by ecp
#
#########################################

from urllib.request import urlopen, HTTPError
from lxml import html
import pandas as pd
# from bs4 import BeautifulSoup


# 데이터 불러오기
filename = 'drCategoryLinks.csv'
df = pd.read_csv(filename)

# 2000년 ~ 2017년 링크 가져오기
years = list()
year_links = list()
for idx, row in df.iterrows():
    if row['category'].endswith('년') and 1999 < int(row['category'].split('년')[0]) < 2018:
        years.append(row['category'])
        year_links.append(row['page_link'])


print('Start with scraping')

# 연도 수만큼 반복
drama_years = list()
drama_titles = list()
drama_links = list()
for i in range(len(years)):
    try:
        print('Scraping ' + years[i])
        # 해당 연도의 드라마 리스트 페이지 url
        url = 'https://www.djowiki.com' + year_links[i]
        res = urlopen(url).read().decode('utf-8')
        page = html.fromstring(res)
        # 해당 웹페이지에서 드라마 리스트 포함된 요소 가져오기
        dramas = page.xpath('//*[@id="mw-pages"]/div/div/div/ul/li/a')
        # 연도, 제목, 링크 가져오기
        if dramas:
            for dr in dramas:
                try:
                    # 연도
                    drama_years.append(years[i])
                    # 드라마 제목
                    drama_titles.append(dr.text)
                    # 드라마 링크
                    drama_links.append(dr.get('href'))
                except AttributeError as e:
                    print('AttributeError >>>>>>>>> ' + str(e))
                    drama_years.append(years[i])
                    drama_titles.append("")
                    drama_links.append("")
                    continue
        else:
            raise HTTPError

    except HTTPError as e:
        print('HTTPError >>>>>>>>> ' + str(e))
        drama_years.append(years[i])
        drama_titles.append("")
        drama_links.append("")
        continue

print('Done with scraping')


# 두 해 이상에 걸쳐서 방영해서 드라마가 중복되면 삭제할 인덱스 골라내기
duplicate_idx = list()
already_check = list()
for i in range(len(drama_titles)):
    if i not in already_check:
        cnt = 0
        for j in range(i+1, len(drama_titles)):
                if drama_titles[i] == drama_titles[j] and drama_links[i] == drama_links[j]:
                    cnt += 1
                    dup_i = j
                    already_check.append(dup_i)
        # 혹시 모르니 중복 데이터가 2개 뿐인 것만 뒤에 나오는 데이터 삭제
        if cnt == 1:
            duplicate_idx.append(dup_i)


# data frame으로 변환
title_link_data = pd.DataFrame({'year': drama_years, 'title': drama_titles, 'drama_link': drama_links})

# 중복 데이터 삭제
result = title_link_data.drop(duplicate_idx, 0)


# csv로 저장
result.to_csv('drListByYear.csv', encoding='utf-8')
