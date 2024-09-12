import pandas as pd
from strategy.closing_str import ClosingPriceStrategy
from simulation import Simulation
from stock_data_scraper import StockScraper
import os
import glob

# stocks 폴더 경로
folder_path = 'stocks/'


# 주식 코드별로 파일을 읽어와서 처리하는 함수
def read_stock_data():
    # stocks 폴더 내의 모든 _data.csv 파일 경로 가져오기
    csv_files = glob.glob(os.path.join(folder_path, '*_data.csv'))

    # 각 파일 읽어서 데이터 처리
    for file in csv_files:
        stock_code = os.path.basename(file).replace('_data.csv', '')  # 주식 코드 추출
        print(f"파일명: {file}, 주식 코드: {stock_code}")

        # CSV 파일 읽기
        stock_data = pd.read_csv(file)

        # 주식 데이터 확인 (상위 5개 행 출력)
        print(stock_data.head())


# 함수 실행
read_stock_data()

if __name__ == '__main__':

    #주식 데이터 받기
    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_code.txt')
    stock_datas = stock_scraper.get_stock_data(stock_codes_list)
    #stock_scraper.download_stock_data(stock_datas)

    top_value = [0,0,0]
    for stock_code, stock_data in stock_datas.items():
        # DataFrame 생성
        stock_data.index.name = 'Date'

        # 시뮬레이션 클래스 생성
        sim = Simulation(stock_data)

        closing_volume_strategy = ClosingPriceStrategy(stock_data)
        sim.add_strategy(closing_volume_strategy)
        sim.run()
        results = sim.get_results()
        for strategy_name, final_value in results.items():
            print(strategy_name, final_value)
        # 전략 추가
        # moving_average_strategy = MovingAverageStrategy(stock_data)
        # sim.add_strategy(moving_average_strategy)
        # for threshold in range(3,11):
        #     closing_volume_strategy = ClosingPriceStrategy(stock_data, threshold)
        #     sim.add_strategy(closing_volume_strategy)
        #
        #     # 시뮬레이션 실행
        #     sim.run()
        #
        #     # 결과 확인
        #     results = sim.get_results()
        #
        #     # 결과 출력
        #     for strategy_name, final_value in results.items():
        #         print(f"{strategy_name}: stock code = {stock_code} 최종 포트폴리오 가치 = {final_value:.2f}  threshold = {threshold}")
        #         if final_value > top_value[0]:
        #             top_value[0] = final_value
        #             top_value[1] = stock_code
        #             top_value[2] = threshold
        #
        # print(f"지금까지의 최고는 {top_value}")