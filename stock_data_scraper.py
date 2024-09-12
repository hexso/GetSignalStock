import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime

START_DATE = '2022-01-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')

class StockScraper:
    def __init__(self):
        self.start_date = START_DATE
        self.end_data = END_DATE

    # 메모장에서 주식 코드를 읽어오는 함수
    def read_stock_codes(self, file_path):
        """
        메모장에서 주식 코드를 읽어오는 함수
        file_path: 메모장 파일 경로 (주식 코드가 한 줄에 하나씩 입력되어 있다고 가정)
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            stock_codes = [line.strip() for line in file.readlines()]
        return stock_codes

    # 주식 데이터를 다운로드하는 함수
    def get_stock_data(self, stock_codes, start_date=None, end_date=None):
        """
        주식 데이터를 다운로드하여 딕셔너리로 반환하는 함수
        stock_codes: 주식 코드 리스트
        start_date: 데이터 시작일 (YYYY-MM-DD 형식)
        end_date: 데이터 종료일 (YYYY-MM-DD 형식)
        """

        #시작일과 종료일의 경우 따로 설정하지 않으면 맨위의 날짜가 삽입된다.
        if start_date == None:
            start_date = self.start_date
        if end_date == None:
            end_date = self.end_data

        stock_data = {}
        for code in stock_codes:
            print(f"{code} 데이터를 다운로드 중...")
            try:
                stock = fdr.DataReader(code, start_date, end_date)
                stock_data[code] = stock
                print(f"{code} 데이터 다운로드 완료.")
            except Exception as e:
                print(f"{code} 데이터 다운로드 중 오류 발생: {e}")

        return stock_data

    def download_stock_data(self, stock_datas):
        """
        딕셔너리로 되어 있는 데이터를 파일로 저장하는 함수
        :param stock_datas: 딕셔너리로 되어 있는 주식데이터
        :return:
        """
        for code, data in stock_datas.items():
            data.to_csv(f"stocks/{code}_data.csv")  # 각 주식 데이터를 CSV 파일로 저장
            print(f"{code} 데이터가 저장되었습니다.")

if __name__ == '__main__':
    # 메모장 파일 경로
    file_path = 'stock_codes.txt'  # 메모장에 있는 주식 코드 파일 경로
    stock_scraper = StockScraper()
    # 주식 코드 읽기
    stock_codes = stock_scraper.read_stock_codes(file_path)

    # 주식 데이터 다운로드
    stock_datas = stock_scraper.get_stock_data(stock_codes)
    stock_scraper.download_stock_data(stock_datas)
