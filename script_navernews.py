import requests
from bs4 import BeautifulSoup
import sqlite3
from konlpy.tag import Okt
import time
from datetime import datetime
import hashlib
from collections import Counter

# SQLite 데이터베이스 연결
conn = sqlite3.connect('news.db')
c = conn.cursor()

# 테이블 생성 (뉴스 제목, 내용, 키워드, 날짜, 카테고리, 제목 해시)
c.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        keywords TEXT,
        date TEXT,
        category TEXT,
        title_hash TEXT UNIQUE  -- 뉴스 제목의 해시값을 고유 값으로 설정
    )
''')
conn.commit()

# 키워드 추출을 위한 Okt 형태소 분석기
okt = Okt()


# SQLite에서 키워드 데이터를 가져오는 함수 (특정 날짜 또는 전체 데이터)
def fetch_keywords(date=None):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    if date:
        # 특정 날짜의 뉴스를 가져옴
        c.execute("SELECT keywords FROM news WHERE date LIKE ?", (f'{date}%',))
    else:
        # 전체 뉴스를 가져옴
        c.execute('SELECT keywords FROM news')

    rows = c.fetchall()
    conn.close()

    # 모든 키워드 문자열을 결합하여 하나의 리스트로 만듦
    all_keywords = []
    for row in rows:
        keywords = row[0].split(', ')  # 쉼표로 구분된 키워드
        all_keywords.extend(keywords)

    return all_keywords

# 뉴스 제목을 해시로 변환하는 함수 (SHA-256 사용)
def hash_title(title):
    return hashlib.sha256(title.encode('utf-8')).hexdigest()

#저장할 필요없는 단어는 필터링 한다.
def load_exclude_keywords(file_path='exclude_keywords.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            exclude_keywords = [line.strip() for line in f.readlines()]
        return exclude_keywords
    except FileNotFoundError:
        print(f"{file_path} 파일을 찾을 수 없습니다.")
        return []


# 키워드 추출 함수 (중복 키워드 제거 + 특정 키워드 제외 + 길이 필터링)
def extract_keywords(text):
    okt = Okt()
    # 형태소 분석을 통해 명사(N)만 추출
    words = okt.pos(text)

    # 제외할 키워드 목록 로드
    #exclude_keywords = load_exclude_keywords()
    exclude_keywords = words
    # 명사(Noun)만 필터링하고, 단어 길이가 1 이상이며 제외할 키워드가 아닌 경우만 유지
    nouns = [word for word, pos in words if pos == 'Noun' and len(word) > 1 and word not in exclude_keywords]

    # 중복 제거
    unique_keywords = list(set(nouns))

    return ', '.join(unique_keywords)


# 뉴스 크롤링 함수 (네이버 뉴스, 카테고리별로)
def crawl_naver_news(category, sid1):
    url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={sid1}"
    headers = {"User-Agent": "Mozilla/5.0"}

    # 요청 및 파싱
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 목록 파싱
    articles = soup.select('ul.type06_headline li dl')

    for article in articles:
        title_tag = article.select_one('dt:not(.photo) a')
        content_tag = article.select_one('dd')
        date_tag = article.select_one('span.date')  # 날짜 정보

        if title_tag and content_tag:
            title = title_tag.get_text(strip=True)
            content = content_tag.get_text(strip=True)

            # 날짜가 없을 경우 현재 날짜로 대체
            if date_tag:
                date = date_tag.get_text(strip=True)
            else:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 뉴스 제목 해시값 생성
            title_hash = hash_title(title)

            # 키워드 추출
            keywords = extract_keywords(content)

            # 데이터베이스에 저장 (중복 방지)
            save_to_db(title, content, keywords, date, category, title_hash)

# 데이터베이스에 저장 함수 (중복된 기사는 저장하지 않음)
def save_to_db(title, content, keywords, date, category, title_hash):
    try:
        c.execute('INSERT INTO news (title, content, keywords, date, category, title_hash) VALUES (?, ?, ?, ?, ?, ?)',
                  (title, content, keywords, date, category, title_hash))
        conn.commit()
        print(f"저장 완료: {title} (카테고리: {category}, 날짜: {date})")
    except sqlite3.IntegrityError:
        print(f"중복 기사로 저장되지 않음: {title}")

# 키워드 빈도수를 계산하는 함수
def calculate_keyword_frequency(date=None):
    keywords = fetch_keywords(date)
    # 제외할 키워드 목록 불러오기
    exclude_keywords = load_exclude_keywords()
    # 제외할 키워드를 스킵하고 카운트
    filtered_keywords = [keyword for keyword in keywords if keyword not in exclude_keywords]

    keyword_count = Counter(filtered_keywords)  # 키워드 빈도수 계산
    return keyword_count

# 각 카테고리별로 뉴스를 크롤링
def run_news_crawler():
    categories = {
        '정치': '100',
        '경제': '101',
        '사회': '102',
        'IT/과학': '105'
    }

    while True:
        for category, sid1 in categories.items():
            crawl_naver_news(category, sid1)
        time.sleep(60)  # 1분마다 갱신


# 텍스트 파일로 상위 키워드 저장 함수
def save_to_txt_by_date(top_keywords, date=None, file_path='top_keywords_by_date.txt'):
    if date:
        title = f"Top Keywords for {date} (Most Frequent):\n"
    else:
        title = "Top Keywords for All Data (Most Frequent):\n"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(title)
        for keyword, count in top_keywords:
            f.write(f"{keyword}: {count}회\n")

    print(f"상위 키워드가 {file_path}에 저장되었습니다.")


# 키워드 빈도수 상위 N개 출력 (특정 날짜 또는 전체 데이터)
def print_top_keywords_by_date(date=None, n=10):
    keyword_count = calculate_keyword_frequency(date)
    top_keywords = keyword_count.most_common(n)

    if date:
        print(f"Top Keywords for {date} (Most Frequent):")
    else:
        print(f"Top Keywords for All Data (Most Frequent):")

    for keyword, count in top_keywords:
        print(f"{keyword}: {count}회")

    # 텍스트 파일로 저장
    save_to_txt_by_date(top_keywords, date)

# 메인 실행
if __name__ == '__main__':
    #네이버뉴스에서 뉴스정보를 긁어온다.
    #run_news_crawler()

    #디비에 있는 키워드를 뽑아내서 언급된 빈도수로 출력 및 txt파일로 저장한다
    print_top_keywords_by_date(n=10)

