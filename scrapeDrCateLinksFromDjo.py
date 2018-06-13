#########################################
#
# 드조위키에서 카테고리별(연도별) 드라마 리스트 요청 url scraping 해오기
# 2017. 12. 05  by ecp
#
#########################################

from urllib.request import urlopen
from urllib.request import HTTPError
from lxml import html
import pandas as pd
# from bs4 import BeautifulSoup


try:
    # 드조위키의 한국드라마 페이지
    url = 'https://www.djowiki.com/w/%EB%B6%84%EB%A5%98:%ED%95%9C%EA%B5%AD_%EB%93%9C%EB%9D%BC%EB%A7%88'
    res = urlopen(url).read().decode('utf-8')
    page = html.fromstring(res)
    # 연도별 페이지 링크 포함된 요소 가져오기
    category_links = page.xpath('//*[@id="mw-content-text"]/table//a')  # tbody 때문인지 full xpath나 full selector 경로?가 안됨
    # 카테고리, 페이지 링크 가져오기
    categories = list()
    page_links = list()
    for link in category_links:
        # 연도(그 외 카테고리명)
        categories.append(link.text)
        # 페이지 링크
        page_links.append(link.get('href'))

    # data frame으로 변환
    category_link_data = pd.DataFrame({'category': categories, 'page_link': page_links})
    # csv로 저장
    category_link_data.to_csv('drCategoryLinks.csv', encoding='utf-8')

except HTTPError as e:
    print('HTTPError >>>>>>>>> ' + str(e))
    # null 반환, break문 실행, or 기타 다른 방법

except AttributeError as e:
    print('AttributeError >>>>>>>>> ' + str(e))

# else:
#     # 프로그램 계속 실행. except절에서 return이나 break 실행 했다면 else절은 필요없음
