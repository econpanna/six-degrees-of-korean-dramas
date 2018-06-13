#########################################
#
# Daum에서 40000 ~ 90000 사이의 tvProgramId scraping 해오기
# 2017. 12. 09  by ecp
#
# running time: 5000개 당 tvProgramId가 많으면 20~30분 / 적으면 5분 내외 (주말 낮, 55000부터 측정 결과)
#
#########################################

import pandas as pd
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup
import time


max_id_range = list(range(40000, 90000))[45000:50000]
# 한번에 끝까지 실행시켜놓고 기다리면 중간에 멈추는 경우가 많아서
# max_id_range = list(range(40000, 90000))[0:5000] 부터 시작해서 5000개씩 끊어서 실행.

print('Start with scraping')
start_time = time.time()

id_list = list()
genre_list = list()
scrap_fail_ids = list()
scrap_fail_desc = list()
# max_id_range 개수만큼 반복
for i in range(len(max_id_range)):

    # 500개 할 때마다 console에 알림
    if i % 500 == 0:
        print(str(i) + ' 번째 scraping 완료')

    try:
        i_id = int(max_id_range[i])
        # 해당 id의 드라마 페이지 url
        url = 'http://movie.daum.net/tv/main?tvProgramId=' + str(i_id)
        res = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(res, 'lxml')

        # 해당 웹페이지에서 드라마 요약 정보 div 가져오기
        summary_div = soup.find_all('div', {'class': 'movie_summary'})  # find_all은 해당 요소가 없을 경우 None이 아닌 빈 list 반환
        # 드라마 요약 정보 div가 1 개 이상일 때. 지금까지 확인한 바로는 첫번째 div 쓰면 됨
        if len(summary_div) > 0:
            # drama_id
            id_list.append(i_id)
            # 장르
            genre_list.append(summary_div[0].find_all('dd')[1].get_text())

        # 드라마 요약 정보 div가 0개 이하일 때
        else:
            # drama_id
            id_list.append(i_id)
            # 장르
            genre_list.append('div없음')

    except HTTPError as e:
        print('HTTPError >>>>>>>>> ' + str(e))
        scrap_fail_ids.append(i_id)
        scrap_fail_desc.append(str(e))
        continue

    except AttributeError as e:
        print('AttributeError >>>>>>>>> ' + str(e))
        scrap_fail_ids.append(i_id)
        scrap_fail_desc.append(str(e))
        continue

    except Exception as e:
        print('Exception >>>>>>>>> ' + str(e))
        scrap_fail_ids.append(i_id)
        scrap_fail_desc.append(str(e))
        continue

print('Done with scraping')
print('Running Time : ' + str(time.time() - start_time))


# data frame으로 변환
# 수집한 데이터
id_genre = pd.DataFrame({'id': id_list, 'genre': genre_list})
# 실패 로그
scrapFailInfo = pd.DataFrame({'fail_id': scrap_fail_ids, 'fail_desc': scrap_fail_desc})


# csv로 저장할 파일명
# 수집한 데이터
filename_to_export = 'allDaumTvProgramId' + str(int((max_id_range[0]-40000)/5000) + 1) + '.csv'
# 실패 로그
fail_filename_to_export = 'failedIdScrapInfo' + str(int((max_id_range[0]-40000)/5000) + 1) + '.csv'

# csv로 저장
# 수집한 데이터
id_genre.to_csv(filename_to_export, encoding='utf-8')
# 실패 로그
scrapFailInfo.to_csv(fail_filename_to_export, encoding='utf-8')
