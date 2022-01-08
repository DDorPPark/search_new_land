
import logging
import openpyxl
import pandas as pd
import re
import requests
import time
from bs4 import BeautifulSoup
from bs4 import CData

#logging.basicConfig(level=logging.INFO)

raw_data = {
        '사업명',
        '분양단계',
        '물건종류',
        '분양종류',
        '분양가',
        '평당가',
        '분양주소',
        '동수',
        '총세대수',
        '분양세대수',
        '최저/최고층',
        '공고시기',
        '입주시기',
        '난방방식',
        '주차대수',
        '분양문의',
        '건설사',
        '전매여부'
}

data_frame = pd.DataFrame()

logging.info(data_frame)
'''
bclass: IA01:IA02:IC01
    IA01 아파트
    IA02 오피스텔
    IC01 빌라도시형
    IC03 상가 업무
supp_sclass: RNT:PRV:PUB:RCN:RDV
    PUB 공공분양
    PRV 민간
    RNT 임대
    RDV 재건축
    RCN 재개발
'''

URL = "https://isale.land.naver.com/NewiSaleMobile/AjaxContent/"

#sample
'''
data_thumbnail = {
    'sy_ajax_content': 'SYHomeComplexList',
    'bclass': 'IA01:IA02:IC01:IC03',
    'supp_proc_step': 'C11',
    'supp_sclass': 'RNT:PRV:RCN:RDV',
    'sy_now_count': '0',
}
'''

data_thumbnail = {
    'sy_ajax_content': 'SYHomeComplexList',
    'bclass': 'IA01:IA02',
    'supp_proc_step': 'C11',
    'supp_sclass': 'PRV',
    'sy_now_count': '0',
}

data_detail = {
    'sy_ajax_content': 'SYDetailContent',
    'supp_cd': '',
    'build_dtl_cd': '',
}

header = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
    'Host':'isale.land.naver.com',
    'Origin':'https://isale.land.naver.com',
    'Referer':'https://isale.land.naver.com/',
    'Connection':'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'sec-ch-ua-mobile': '?0',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
}


result_supp_pattern = {}
result_build_detail_pattern = {}

#for test
#for entry_thumbnail in range(1):

#range당 20개 물건, 총 물건 개수 보고 정할것
for entry_thumbnail in range(20):
    logging.warning('----------thumbnail-----------')
    time.sleep(0.1)
    data_thumbnail['sy_now_count'] = 20 * entry_thumbnail
    logging.warning(entry_thumbnail)
    logging.info(data_thumbnail['sy_now_count'])

    crawl_data = requests.post(URL, data=data_thumbnail, headers=header)

    logging.info(type(crawl_data))

    logging.info(crawl_data.text)


    soup_data = BeautifulSoup(crawl_data.content, 'html.parser')
#    try:
    soup_data_text = soup_data.select('SYViewContent')[0].getText()
#    except IndexError as e:
#        logging.info(data_thumbnail['sy_now_count'])
#        break
    if(len(soup_data_text) == 1):
        break
    logging.info(len(soup_data_text))
    logging.info(soup_data_text)

    logging.info(soup_data_text)
    logging.info(type(soup_data_text))
    logging.info('------------------------------')
    # 태그/클래스 기반으로 잘라내기 위해 다시 BS로 파싱
    soup_data2 = BeautifulSoup(soup_data_text, 'html.parser')
    logging.info(soup_data2)
    logging.info(type(soup_data2))

    detail_pattern = soup_data2.select('a.ItemLink')
    logging.info(detail_pattern)
    logging.info(len(detail_pattern))
####### supp_cd, build_dtl_cd 추출 #############
    for entry_detail_pattern in detail_pattern:
        time.sleep(0.1)
        logging.info('------------pattern-----------')
        logging.info(entry_detail_pattern)
        logging.info(str(entry_detail_pattern))
        supp_pattern = re.findall(r'supp_cd=.[0-9]+', str(entry_detail_pattern))
        build_detail_pattern = re.findall(r'build_dtl_cd=.[0-9]+', str(entry_detail_pattern))
        logging.info(supp_pattern)
        logging.info(build_detail_pattern)

        Str_supp = ",".join(supp_pattern)
        Str_build_detail = ",".join(build_detail_pattern)

        logging.info(Str_supp)
        logging.info(Str_build_detail)

        if len(result_supp_pattern) == 0:
            result_supp_pattern = re.findall('[0-9]+', Str_supp)
            result_build_detail_pattern = re.findall('[0-9]+', Str_build_detail)
        else:
            result_supp_pattern.extend(re.findall('[0-9]+', Str_supp))
            result_build_detail_pattern.extend(re.findall('[0-9]+', Str_build_detail))

        logging.info(result_supp_pattern)
        logging.info(result_build_detail_pattern)

############### 위에서 추출한 pattern으로 detail 검색 ##########################
#이거 테스트
#for entry_detail in range(1):

#이게 원본
for entry_detail in range(len(result_supp_pattern)):
    time.sleep(0.1)
    logging.info('-----------detail-----------')
    logging.warning(entry_detail)
    logging.info(result_supp_pattern[entry_detail], result_build_detail_pattern[entry_detail])

    data_detail['supp_cd'] = result_supp_pattern[entry_detail]
    data_detail['build_dtl_cd'] = result_build_detail_pattern[entry_detail]
    logging.info(data_detail['supp_cd'], data_detail['build_dtl_cd'])

    crawl_detail_data = requests.post(URL, data=data_detail, headers=header)
    logging.info(crawl_detail_data.text)

    #detail data로 각각의 물건 정보 크롤링
    soup_detail_data = BeautifulSoup(crawl_detail_data.content, 'html.parser')

    #syviewcontent 태그 안의 내용만 가져옴
    soup_detail_data_text = soup_detail_data.select('syviewcontent')[0].getText()
    logging.info(soup_detail_data_text)


    #태그/클래스 기반으로 잘라내기 위해 다시 BS로 파싱
    soup_detail_data2 = BeautifulSoup(soup_detail_data_text, 'html.parser')

    #분양정보 요약탭의 내용 저장. 사업명, 세대수, 분양단계, 물건종류, 분양종류 등 정보 확인
    soup_detail_summary_area = soup_detail_data2.select_one('div.DetailSummaryArea')
    logging.info(soup_detail_summary_area)

    detail_name = soup_detail_summary_area.find('div', class_='Heading').text
    detail_progress = soup_detail_summary_area.find('span', class_='LabelDetail C11').text
    detail_complex = soup_detail_summary_area.find('span', class_='LabelDetail Complex').text
    detail_type = soup_detail_summary_area.find(class_='LabelDetail Type').text
    detail_complexPrice = soup_detail_summary_area.select_one('div > dl.ComplexPrice > dd.Data').getText()
    try:
        detail_scalePrice = soup_detail_summary_area.select_one('div > dl.ScalePrice > dd.Data').getText()
    except AttributeError as e:
        detail_scalePrice = "미정"

    if(detail_name is not None):
        data_frame.loc[entry_detail, '사업명'] = detail_name
        logging.info(detail_name)

    if(detail_progress is not None):
        data_frame.loc[entry_detail, '분양단계'] = detail_progress
        logging.info(detail_progress)

    if(detail_complex is not None):
        data_frame.loc[entry_detail, '물건종류'] = detail_complex
        logging.info(detail_complex)

    if(detail_type is not None):
        data_frame.loc[entry_detail, '분양종류'] = detail_type
        logging.info(detail_type)

    if(detail_complexPrice is not None):
        data_frame.loc[entry_detail, '분양가'] = detail_complexPrice
        logging.info(detail_complexPrice)

    if(detail_scalePrice is not None):
        data_frame.loc[entry_detail, '평당가'] = detail_scalePrice
        logging.info(detail_scalePrice)

    logging.info(data_frame)

    logging.info('------------------------------')

    #분양정보의 기본정보 탭의 내용 저장. 분양주소, 총 세대수, 분양 세대수, 공고 시기, 분양 문의, 건설사, 전매 여부 등
    soup_detail_articlebox_detail = soup_detail_data2.select_one('div.ArticleBox')
    logging.info(soup_detail_articlebox_detail)

    article_detail = soup_detail_articlebox_detail.select('span.Data')

    if (article_detail is not None):
        logging.info(article_detail)
        detail_list = []
        for entry_art_detail in article_detail:
            detail_list.append(entry_art_detail.getText())

        logging.info(detail_list)

    logging.info(len(detail_list))
    logging.info(entry_detail)
    data_frame.loc[entry_detail, '분양주소'] = detail_list[0]
    data_frame.loc[entry_detail, '동수'] = detail_list[1]
    data_frame.loc[entry_detail, '총세대수'] = detail_list[2]
    data_frame.loc[entry_detail, '분양세대수'] = detail_list[3]
    data_frame.loc[entry_detail, '최저/최고층'] = detail_list[4]
    data_frame.loc[entry_detail, '공고시기'] = detail_list[5]
    data_frame.loc[entry_detail, '입주시기'] = detail_list[6]
    data_frame.loc[entry_detail, '난방방식'] = detail_list[7]
    try:
        data_frame.loc[entry_detail, '주차대수'] = detail_list[8]
    except IndexError as e:
        data_frame.loc[entry_detail, '주차대수'] = "-"
    try:
        data_frame.loc[entry_detail, '문양문의'] = detail_list[9]
    except IndexError as e:
        data_frame.loc[entry_detail, '문양문의'] = "-"
    try:
        data_frame.loc[entry_detail, '건설사'] = detail_list[10]
    except IndexError as e:
        data_frame.loc[entry_detail, '건설사'] = "-"
    try:
        data_frame.loc[entry_detail, '전매여부'] = detail_list[11]
    except IndexError as e:
        data_frame.loc[entry_detail, '전매여부'] = "-"
    logging.warning(data_frame.loc[entry_detail])

logging.warning('------------')
logging.warning(data_frame)

try:
    data_frame.to_excel("result_land.xlsx")
except IndexError as e:
    data_frame.to_excel("result_land2.xlsx")