#########################################
#
# Daum에서 tvProgramId로 드라마 summary 정보 scraping 해오기
# 2017. 12. 06  by ecp
# 참고 : 인물 정보는 별도로 scraping 할 것
#       최근 시청률은 못가져옴. 필요하다면 아래 url을 이용해야 할 듯
#       'http://movie.daum.net/tv/main/recentRating.json?tvProgramId='
#
#########################################

import pandas as pd
import math
import re
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup


def duplicate_key_found(new_dict_keys, origin_dict):

    if sum([key in origin_dict for key in new_dict_keys]) == 0:
        result = False
    else:
        result = True
    return result


def no_comma_whitespace_filter(text):

    # no_whitespace = re.compile('\s+') # 공백까지 처리해버려서 곤란
    no_comma = re.compile(',+')
    no_tap_enter = re.compile('[\t\n]+')
    after_filter = re.compile('-SEP-[ ]*')

    # 대체 문자는 데이터 전처리 하기 좋을만한 임의의 문자
    after = no_tap_enter.sub('-SEP-', no_comma.sub('-AND-', text.strip()))
    result = after_filter.sub('-SEP-', after.strip()).strip()
    return result


# 데이터 불러오기
filename = ''
# 실행하기 전에 파일 경로 확인해야 해서 일단 지워놓음, 예) filename = 'drDaumTvProgramId_final.csv'
df = pd.read_csv(filename)
drama_id_list = list(df['drama_id'])

# drama_id_list = [49640, 48074, 63768] ## 테스트 코드 1
# drama_id_list = [75301, 52345, 79023, 48074, 55829] ## 테스트 코드 2

print('Start with scraping')

drama_infos = list()
scrap_fail_infos = list()
# id 개수만큼 반복
for i in range(len(drama_id_list)):

    # 100개 할 때마다 console에 알림
    if i % 100 == 0:
        print(str(i) + ' 번째 scraping 완료')

    try:
        i_scrap_fail_info = dict()

        # id값이 없으면 다음 반복문
        if math.isnan(drama_id_list[i]):
            continue

        # id값이 있으면 아래 실행
        i_id = int(drama_id_list[i])
        # 해당 id의 드라마 페이지 url
        url = 'http://movie.daum.net/tv/main?tvProgramId=' + str(i_id)
        res = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(res, 'lxml')

        # 해당 웹페이지에서 드라마 요약 정보 div 가져오기
        summary_div = soup.find_all('div', {'class': 'movie_summary'})  # find_all은 해당 요소가 없을 경우 None이 아닌 빈 list 반환
        # 드라마 요약 정보 div가 1 개 이상일 때. 지금까지 확인한 바로는 첫번째 div 쓰면 됨
        i_drama_info = dict()
        if len(summary_div) > 0:
            # drama_id
            i_drama_info['drama_id'] = i_id

            # 제목
            i_drama_info['title'] = summary_div[0].find(
                'div', {'class': 'subject_movie'}
            ).find(
                'strong', {'class': 'tit_movie'}
            ).get_text()

            # 기타 요약 정보
            detail_keys = [dts.get_text() for dts in summary_div[0].find_all('dt')]
            detail_values = [dds.get_text() for dds in summary_div[0].find_all('dd')]
            # no_comma_whitespace_filter 호출
            detail_values_filtered = [no_comma_whitespace_filter(value) for value in detail_values]
            if len(detail_keys) != len(detail_values_filtered):
                raise Exception('기타 요약 정보의 dd와 dt 개수가 다름')
            elif len(detail_keys) != len(list(set(detail_keys))):
                raise Exception('기타 요약 정보의 dt간 중복')
            elif duplicate_key_found(detail_keys, i_drama_info):
                raise Exception('기타 요약 정보의 dt와 기존 key 중복')

            # 이상의 문제 없을 경우 i_drama_info dict에 추가
            i_drama_info.update(dict(zip(detail_keys, detail_values_filtered)))

            # 여태까지 모은 데이터에 추가
            drama_infos.append(i_drama_info)

        # 드라마 요약 정보 div가 0개 이하일 때
        else:
            raise Exception('movie_summary div가 없음')

    except HTTPError as e:
        print('HTTPError >>>>>>>>> ' + str(e))
        i_scrap_fail_info['drama_id'] = i_id
        i_scrap_fail_info['describe'] = str(e)
        scrap_fail_infos.append(i_scrap_fail_info)
        continue

    except AttributeError as e:
        print('AttributeError >>>>>>>>> ' + str(e))
        i_scrap_fail_info['drama_id'] = i_id
        i_scrap_fail_info['describe'] = str(e)
        scrap_fail_infos.append(i_scrap_fail_info)
        continue

    except Exception as e:
        print('Exception >>>>>>>>> ' + str(e))
        i_scrap_fail_info['drama_id'] = i_id
        i_scrap_fail_info['describe'] = str(e)
        scrap_fail_infos.append(i_scrap_fail_info)
        continue

print('Done with scraping')

# data frame으로 변환
# 수집한 데이터
dramaSummaries = pd.DataFrame(drama_infos)
# 실패 로그
scrapFailInfo = pd.DataFrame(scrap_fail_infos)

# csv로 저장
# 수집한 데이터
dramaSummaries.to_csv('dramaSummaryInfo.csv', encoding='utf-8')
# 실패 로그
scrapFailInfo.to_csv('failedSumScrapInfo.csv', encoding='utf-8')
