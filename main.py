import pandas as pd
from strategy.closing_str import ClosingPriceStrategy
from simulation import Simulation
from stock_data_scraper import StockScraper
import os
import glob

if __name__ == '__main__':

    #주식 데이터 받기
    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_code.txt')
    #stock_datas = stock_scraper.get_stock_data(stock_codes_list)
    #stock_scraper.download_stock_data(stock_datas) # 데이터를 csv파일로 저장

    #top_value = [0,0,0]
    for code in stock_codes_list:
        stock_datas = stock_scraper.get_stock_data([code])
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




#################################################
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