#########################################
#
# Daum에서 tvProgramId로 드라마 crew 정보 scraping 해오기
# 2017. 12. 06  by ecp
#
#########################################

import pandas as pd
import math
import re
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup


def no_comma_filter(text):

    no_comma = re.compile(',+')
    # 대체 문자는 데이터 전처리 하기 좋은 임의의 문자
    result = no_comma.sub('+', text.strip()).strip()
    return result


# 데이터 불러오기
filename = ''
# 실행하기 전에 파일 경로 확인해야 해서 일단 지워놓음, 예) filename = 'dramaSummaryInfo_filtered.csv'
# dramaSummaryInfo_filtered.csv : summary 스크래핑 후 R로 필터링한 데이터
df = pd.read_csv(filename)
drama_id_list = list(df['drama_id'])[1000:]
# crew 데이터가 너무 많아서 list(df['drama_id'])[0:500] 부터 시작해서 500개씩 끊어서 실행
# drama_id_list = [49640, 48074, 49643, 49647, 63768] ## 테스트 코드

print('Start with scraping')

drama_ids = list()
crew_types = list()
crew_type_seqs = list()
person_codes = list()
person_names = list()
person_roles = list()
person_pic_urls = list()
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
        # 해당 id의 드라마 출연/제작진 페이지 url
        url = 'http://movie.daum.net/tv/crew?tvProgramId=' + str(i_id)
        res = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(res, 'lxml')

        # 해당 웹페이지에서 출연/제작진 정보 div 가져오기
        summary_div = soup.find_all('div', {'class': 'movie_join movie_staff'})  # find_all은 해당 요소가 없을 경우 None이 아닌 빈 list 반환
        # 출연/제작진 정보 div가 2 개일 때
        i_drama_ids = list()
        i_crew_types = list()
        i_crew_type_seqs = list()
        i_person_codes = list()
        i_person_names = list()
        i_person_roles = list()
        i_person_pic_urls = list()
        if len(summary_div) == 2:
            # 첫번째 div는 배우, 두번째 div는 제작진
            for div_i in range(len(summary_div)):
                # 해당 div의 모든 인물들
                members = summary_div[div_i].find_all('li')
                # 해당 div의 인물들 수만큼 반복
                for member_i in range(len(members)):
                    # drama_id
                    i_drama_ids.append(i_id)
                    # 타입
                    i_crew_types.append('배우' if div_i == 0 else '제작진')
                    # 순서(1부터)
                    i_crew_type_seqs.append(member_i + 1)
                    # 코드
                    i_person_codes.append(
                        members[member_i].find_all('a')[0].get('href').replace("'", '').split('(')[1].split(',')[0]
                    )
                    # 이름
                    i_person_names.append(
                        members[member_i].find_all('strong', {'class': 'tit_join'})[0].get_text()
                    )
                    # 역할
                    i_person_roles.append(
                        members[member_i].find_all('span', {'class': 'txt_join'})[0].get_text())
                    # 사진 url
                    i_person_pic_urls.append(
                        members[member_i].find_all('img')[0].get('src')
                    )
                # no_comma_filter 호출
                i_person_roles_filtered = [no_comma_filter(value) for value in i_person_roles]
                # scraping 해온 변수별 값의 개수 같은지 확인
                if not len(i_drama_ids) == len(i_person_codes) == len(i_person_names) == len(i_person_roles_filtered) == len(i_person_pic_urls):
                    raise Exception('인물 정보의 변수별 값의 개수가 다름')

            drama_ids += i_drama_ids
            crew_types += i_crew_types
            crew_type_seqs += i_crew_type_seqs
            person_codes += i_person_codes
            person_names += i_person_names
            person_roles += i_person_roles_filtered
            person_pic_urls += i_person_pic_urls

        # 출연/제작진 정보 div가 0개일 때
        elif len(summary_div) == 0:
            raise Exception('movie_summary div가 없음')
        # 출연/제작진 정보 div가 0개도, 2개도 아닐 때
        else:
            raise Exception('movie_summary div가 2개가 아님')

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
dramaCrews = pd.DataFrame(
    {'drama_id': drama_ids, 'crew_type': crew_types, 'crew_type_seq': crew_type_seqs,
     'person_code': person_codes, 'person_name': person_names, 'person_role': person_roles,
     'person_pic_url': person_pic_urls}
)
# 실패 로그
scrapFailInfo = pd.DataFrame(scrap_fail_infos)

# csv로 저장
# 수집한 데이터
dramaCrews.to_csv('dramaCrewInfo.csv', encoding='utf-8')
# 실패 로그
scrapFailInfo.to_csv('failedCrewScrapInfo.csv', encoding='utf-8')
