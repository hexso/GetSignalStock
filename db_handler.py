import sqlite3
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter


# 한글 폰트 설정 함수 (macOS용)
def set_korean_font():
    plt.rc('font', family='AppleGothic')  # macOS의 경우 "AppleGothic" 사용
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 폰트 깨짐 방지


# SQLite에서 키워드 데이터를 가져오는 함수
def fetch_keywords_from_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('SELECT keywords FROM news')
    rows = c.fetchall()
    conn.close()

    # 모든 키워드 문자열을 결합하여 하나의 리스트로 만듦
    all_keywords = []
    for row in rows:
        keywords = row[0].split(', ')  # 쉼표로 구분된 키워드
        all_keywords.extend(keywords)

    return all_keywords


# 키워드 빈도수를 계산하는 함수
def calculate_keyword_frequency():
    keywords = fetch_keywords_from_db()
    keyword_count = Counter(keywords)
    return keyword_count

class DBHandler:
    def __init__(self):
        pass

    # 막대그래프를 그리는 함수
    def plot_keyword_frequency(self):
        # Tkinter GUI 설정
        window = tk.Tk()
        window.title("키워드 빈도수")
        window.geometry("800x600")

        # 그래프 그리기 버튼
        set_korean_font()  # 한글 폰트 설정

        keyword_count = calculate_keyword_frequency()

        # 상위 10개의 키워드만 추출
        top_keywords = keyword_count.most_common(10)
        keywords, counts = zip(*top_keywords)

        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(keywords, counts, color='skyblue')
        ax.set_xlabel('키워드')
        ax.set_ylabel('빈도수')
        ax.set_title('상위 10개 키워드 빈도수')
        plt.xticks(rotation=45)

        # Tkinter 창에 그래프 표시
        canvas = FigureCanvasTkAgg(fig, master=window)  # Tkinter 창에 matplotlib 그래프 붙이기
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        window.mainloop()

if __name__ == '__main__':
    db_handler = DBHandler()
    db_handler.plot_keyword_frequency()