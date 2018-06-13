#########################################
#
# tvProgramId scraping한 데이터와 수작업으로 추가한(scraping에서 누락됐던) 데이터 병합
# 2017. 12. 06  by ecp
#
#########################################

import pandas as pd
import math

# 데이터 불러오기
# original
origin_filename = 'drDaumTvProgramId.csv'
origin_df = pd.read_csv(origin_filename)
origin_drama_id_list = origin_df['drama_id']
# 수작업으로 데이터 추가한 파일
new_filename = 'ManualLabor/dramaTvProgramId_addManually.txt'
new_df = pd.read_table(new_filename)

# original에서 id 못가져왔던 데이터 찾기
origin_df.dtypes
origin_df.describe()
missingIdIdx = [idx for idx, row in origin_df.iterrows() if math.isnan(row['drama_id'])] # 타입이 float64이므로 ''체크는 필요없음
len(missingIdIdx)  # 106 개
missingkeys = list(origin_df['Unnamed: 0'][origin_df.index.isin(missingIdIdx)]) # missing id들의 'Unnamed: 0' 컬럼 값

# new에서 원래 없었는데 추가된 데이터 찾기
new_df.dtypes # drama_id 타입은 float64
# 확인용
newAdded = [idx for idx, row in new_df.iterrows() if math.isnan(row['Unnamed: 0']) and not math.isnan(row['drama_id'])]
len(newAdded)  # 2 개
new_df[new_df.index.isin(newAdded)]  # 안녕 프란체스카 시즌 1, 2
# id만 가져오기
newAddedIds = [row['drama_id'] for idx, row in new_df.iterrows() if math.isnan(row['Unnamed: 0']) and not math.isnan(row['drama_id'])]


# 채워넣기
sum(origin_df['Unnamed: 0'].duplicated())  # 0 중복값 없음
merged_df = origin_df
for m_key in missingkeys:
    id_found = float(new_df.loc[new_df['Unnamed: 0'] == m_key, 'drama_id'])
    if not math.isnan(id_found):
        merged_df.loc[merged_df['Unnamed: 0'] == m_key, 'drama_id'] = id_found
        merged_df.loc[merged_df['Unnamed: 0'] == m_key, 'drama_title'] = '수작업 추가'

for new_id in newAddedIds:
    merged_df_copy = merged_df
    merged_df = merged_df_copy.append(
        {
            'drama_id': new_id, 'drama_title': '수작업 추가',
            'Unnamed: 0': math.nan, 'genre': math.nan, 'wiki_title': math.nan, 'wiki_year': math.nan
        }, ignore_index=True)


# csv로 저장
merged_df.to_csv('drDaumTvProgramId_final.csv', encoding='utf-8')
