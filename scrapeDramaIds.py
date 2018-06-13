#########################################
#
# Daum에서 드라마 제목으로 tvProgramId scraping 해오기
# 2017. 12. 05  by ecp
#
#########################################

import urllib
import json
import pandas as pd
from urllib.request import urlopen, HTTPError


# 데이터 불러오기
filename = 'drListByYear.csv'
df = pd.read_csv(filename)

wiki_years = list()
wiki_titles = list()
drama_titles = list()
drama_ids = list()
genre = list()
# title 개수만큼 반복
for i in range(len(df['title'])):
    try:
        d_title = df['title'][i]
        # 검색을 위해 title에 있는 괄호 정보 삭제
        srch_title = df['title'][i].split('(')[0].strip()
        # year 에 있는 년 삭제
        d_year = int(df['year'][i].split('년')[0].strip())

        # 다음 드라마 검색 결과 json url (추정)
        url = 'http://movie.daum.net/data/movie/search/v2/tv.json?size=20&searchText='\
              + urllib.parse.quote(srch_title) + '&start=1&sortType=acc'
        res = urlopen(url).read().decode('utf-8')
        json_data = json.loads(res)

        # 검색 결과 json에서 tvProgramId 가져오기
        # 검색 결과가 1개이면서 연도가 같으면
        if json_data['count'] == 1 and json_data['data'][0]['prodYear'] == d_year:
            drama_ids.append(json_data['data'][0]['tvProgramId'])
            drama_titles.append(json_data['data'][0]['titleKo'])
            genre.append(json_data['data'][0]['genres'][0]['genreName'])
            wiki_titles.append(d_title)
            wiki_years.append(d_year)
        # 검색 결과가 1개 초과일 경우
        elif json_data['count'] > 1:
            # 내가 찾는 드라마일 가능성이 높은 데이터 추려내기(연도로)
            possible_list = list()
            for d_cnt in range(json_data['count']):
                if json_data['data'][d_cnt]['prodYear'] == d_year:
                        possible_list.append(d_cnt)
            # 추려낸 결과가 1개이면
            if len(possible_list) == 1:
                new_idx = possible_list[0]
                drama_ids.append(json_data['data'][new_idx]['tvProgramId'])
                drama_titles.append(json_data['data'][new_idx]['titleKo'])
                genre.append(json_data['data'][new_idx]['genres'][0]['genreName'])
                wiki_titles.append(d_title)
                wiki_years.append(d_year)
            # 추려낸 결과가 1개가 아니면
            else:
                raise Exception('오류!')

        # 검색결과가 0이나 음수? 혹은 1개인데 연도가 다른 경우
        else:
            raise Exception('오류!')

    except HTTPError as e:
        print('HTTPError >>>>>>>>> ' + str(e))
        drama_ids.append('')
        drama_titles.append('')
        genre.append('')
        wiki_titles.append(d_title)
        wiki_years.append(d_year)
        continue

    except Exception as e:
        print('Exception >>>>>>>>> ' + str(e))
        # 안 나온 데이터 검색어에 '드라마' 붙여서 한번만 더 해보기
        try:
            # 다음 드라마 검색 결과 json url (추정)
            url = 'http://movie.daum.net/data/movie/search/v2/tv.json?size=20&searchText=' \
                  + urllib.parse.quote('드라마 ' + srch_title) + '&start=1&sortType=acc'
            res = urlopen(url).read().decode('utf-8')
            json_data = json.loads(res)

            # 검색 결과 json에서 tvProgramId 가져오기
            # 검색 결과가 1개이면서 연도가 같으면
            if json_data['count'] == 1 and json_data['data'][0]['prodYear'] == d_year:
                drama_ids.append(json_data['data'][0]['tvProgramId'])
                drama_titles.append(json_data['data'][0]['titleKo'])
                genre.append(json_data['data'][0]['genres'][0]['genreName'])
                wiki_titles.append(d_title)
                wiki_years.append(d_year)
            # 검색 결과가 1개 초과일 경우
            elif json_data['count'] > 1:
                # 내가 찾는 드라마일 가능성이 높은 데이터 추려내기(연도로)
                possible_list = list()
                for d_cnt in range(json_data['count']):
                    if json_data['data'][d_cnt]['prodYear'] == d_year:
                        possible_list.append(d_cnt)
                # 추려낸 결과가 1개이면
                if len(possible_list) == 1:
                    new_idx = possible_list[0]
                    drama_ids.append(json_data['data'][new_idx]['tvProgramId'])
                    drama_titles.append(json_data['data'][new_idx]['titleKo'])
                    genre.append(json_data['data'][new_idx]['genres'][0]['genreName'])
                    wiki_titles.append(d_title)
                    wiki_years.append(d_year)
                # 추려낸 결과가 1개가 아니면
                else:
                    raise Exception('여전히 오류!!')
            # 검색결과가 0이나 음수?
            else:
                raise Exception('여전히 오류!!')
        # 여전히 검색 결과가 안나올 때
        except Exception as e:
            print('Exception >>>>>>>>> ' + str(e))
            drama_ids.append('')
            drama_titles.append('')
            genre.append('')
            wiki_titles.append(d_title)
            wiki_years.append(d_year)
            continue

        # 검색 결과가 나왔을 때
        else:
            continue

# data frame으로 변환
title_id_data = pd.DataFrame(
    {'wiki_year': wiki_years, 'wiki_title': wiki_titles, 'drama_id': drama_ids, 'drama_title': drama_titles, 'genre': genre}
)
# csv로 저장
title_id_data.to_csv('drDaumTvProgramId.csv', encoding='utf-8')



# tvProgramId 가져오지 못한 데이터 확인
# import pandas as pd
# import math
# filename = 'drDaumTvProgramId.csv'
# temp = pd.read_csv(filename)
# print([row for i, row in temp.iterrows() if math.isnan(row['drama_id'])])
# print(len([row for i, row in temp.iterrows() if math.isnan(row['drama_id'])]))
# # 확인 결과 106개 실패
