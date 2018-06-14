rm(list=ls())
library(tidyverse) 
library(stringr)

## 데이터 불러오기
list.files()
dat = read.csv('dramaSummaryInfo.csv', stringsAsFactors = F)
View(dat)
summary(dat)
dim(dat) # 1432    9
str(dat)
names(dat)

## 필요한 컬럼만 가져오기
dat_new1 = dat[c('drama_id', 'title', '국가', '방송국.및.방영시간', '연출진', '장르', '현재')] 
head(dat_new1)
names(dat_new1) = c('drama_id', 'title', 'country', 'network_airtime', 'prod_team', 'genre', 'status')
str(dat_new1)
summary(dat_new1)
# 전처리
# trimming
dat_new2 <- dat_new1 %>% 
  lapply(trimws) %>% 
  as.data.frame(stringsAsFactors=F) 
# drama_id에 중복값, na 확인
dat_new2 %>% select(drama_id) %>% duplicated %>% sum() # 0 중복값 없음
dat_new2 %>% select(drama_id) %>% is.na %>% sum() # 0 na 없음
dat_new2 %>% filter(drama_id == '') # ''없음
# title에 중복값, na, 빈값 확인
dat_new2 %>% select(title) %>% is.na() %>% sum() # 0 중복값 없음
dat_new2 %>% select(title) %>% is.na %>% sum() # 0 na 없음
dat_new2 %>% filter(title == '') # ''없음


## 컬럼 나누기
# 나누기 전 status 전처리
dat_new2['status'] <- dat_new2 %>% 
  select(status) %>% 
  lapply(str_replace_all, '-SEP-', '@') %>% 
  lapply(str_replace_all, '@+', 'SEP') %>% 
  as.data.frame(stringsAsFactors=F)
# dat_new1['status']의 class는 데이터프레임
# 대입값도 데이터프레임이어야함
# str_replace_all 만 쓰면 결과값이 vector이기 때문에 안됨. lapply 필요

# network_airtime, status 나누기
dat_new2 <- dat_new2 %>% 
  separate(col= network_airtime, into = c('network', 'airday', 'airtime'), sep='-SEP-') %>% 
  separate(col= status, into = c('period', 'status'), sep='SEP') %>% 
  lapply(trimws) %>% 
  as.data.frame(stringsAsFactors=F) 
# 결과 확인
dat_new2 %>% select(network) %>% unique() # network 이상값 확인
dat_new2 %>% select(airday) %>% unique() # airday 이상값 확인: '낮에도 별은 뜬다' 드라마. 웹페이지 값이 이상
dat_new2 %>% select(airtime) %>% unique() # airtime 이상값 확인
dat_new2 %>% select(status) %>% unique() # status 이상값 확인: 28?
# period 이상값 확인
dat_new2 %>% select(period) %>% unique()
for (i in 1:nrow(dat_new2['period'])) {
  if (nchar(dat_new2['period'][i,]) != 21) {
    print(i)
  }
} # 28, 560, 697, 836, 1147, 1281
dat_new2[c(28, 560, 697, 836, 1147, 1281), ] # 시트콤 세친구, 드라마시티, 강력 1반, 빅히트, 뱀파이어의 꽃, 어울림 
dat_new2[c(28, 560, 697, 836, 1147, 1281), c('period', 'status')]
dat_new2[28, 'period'] <- '2000.02.14~2001.04.09' # 시트콤 세친구, 시트콤이지만 일단 네이버 검색 결과 입력
dat_new2[28, 'status'] <- '방송종료'
dat_new2[560, 'period'] # 드라마시티, 단막극, 기간이 매우 길고 daum에 출연진 정보가 제대로 없어서(위키에 일부 있음) 삭제할 것
dat_new2[697, 'period'] <- '2010.01.21~2010.05.08' # 강력 1반, 네이버 검색 결과 입력
dat_new2[836, 'period'] <- '2011.04.21~2011.07.14' # 빅히트, 네이버 검색 결과 입력
dat_new2[1147, 'period'] # 뱀파이어의 꽃, 웹드라마. 네이버에 정보도 없음. 일단 daum 장르가 드라마인 기준이므로 둠
dat_new2[1281, 'period'] # 어울림, 어린이tv 드라마. 위와 같은 이유로 둠

dat_new3 <- dat_new2[-c(560), ] # 드라마시티 삭제
View(dat_new3)

# period 다시 나누기
dat_new3 <- dat_new3 %>% 
  separate(col = period, into = c('start_date', 'end_date'), sep='~') %>% 
  lapply(trimws) %>% 
  as.data.frame(stringsAsFactors=F)
View(dat_new3)
# as.Date('.', '%Y.%d.%m') 데이터프레임에는 안되는듯...


## 구분자 처리
# airday
dat_new3['airday'] <- dat_new3 %>% 
  select(airday) %>% 
  lapply(str_replace_all, '-AND-', '') %>%
  lapply(str_replace_all, '요일', '') %>% 
  lapply(trimws) %>% 
  as.data.frame(stringsAsFactors=F)
# prod_team
dat_new3['prod_team'] <- dat_new3 %>% 
  select(prod_team) %>% 
  lapply(str_replace_all, '-SEP-', '+') %>%
  lapply(str_replace_all, '-AND-', '') %>% 
  lapply(trimws) %>% 
  as.data.frame(stringsAsFactors=F)
# country
dat_new3['country'] <- dat_new3 %>% 
  select(country) %>% 
  lapply(str_replace_all, '-AND-', '+') %>% 
  lapply(trimws) %>% 
  as.data.frame(stringsAsFactors=F)
View(dat_new3)

# 기타 값 확인
head(dat_new3)
dat_new3 %>% select(country) %>% unique
dat_new3 %>% select(genre) %>% unique
dat_new3 %>% select(country) %>% table
dat_new3 %>% select(genre) %>% table
# country
dat_new4 <- dat_new3 %>% 
  filter(!country %in% c('북한','영국')) # 북한, 영국 방송 삭제
dat_new4 %>% select(country) %>% table
dat_new4[dat_new4['country']=='', 'country'] <- '대한민국'  # '' 값 확인 결과 모두 한국 방송
dat_new4 %>% select(country) %>% table
# genre
dat_new4 <- dat_new4 %>% 
  filter(genre %in% c('드라마','시트콤'))


# 마지막으로, 앞뒤 공백 제거 및 공백값 NA로 변환
dat_final <- dat_new4 %>% 
  lapply(trimws) %>% 
  lapply(function (x) ifelse(x == '', NA, x)) %>% 
  as.data.frame(stringsAsFactors=F)

View(dat_final)
dim(dat_final) # 1419 11
summary(dat_final)
str(dat_final)

# 실행 전 경로확인!
write.csv(dat_final, file='dramaSummaryInfo_filtered.csv', na = '', row.names=F, fileEncoding = 'utf-8')

