from strategy.closing_str import ClosingPriceStrategy
from simulation import Simulation
from stock_data_scraper import StockScraper
import threading
from concurrent.futures import ThreadPoolExecutor

def main_download_stock():
    #주식리스트에 있는 모든 데이터값을 stocks/ 폴더에 저장
    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_codes.txt')
    stock_datas = stock_scraper.get_stock_data(stock_codes_list)
    stock_scraper.download_stock_data(stock_datas) # 데이터를 csv파일로 저장

def test_simulation():
    #주식 데이터를 받아서 시뮬레이션을 돌려본다.
    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_codes.txt')
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

            closing_volume_strategy.plot_stock_data_with_signals()

def test_catch_signal():
    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_codes.txt')
    catched_stock = []
    for code in stock_codes_list:
        stock_datas = stock_scraper.get_stock_data([code])
        for stock_code, stock_data in stock_datas.items():
            # DataFrame 생성
            stock_data.index.name = 'Date'
            closing_volume_strategy = ClosingPriceStrategy(stock_data)
            if closing_volume_strategy.catch_signal() == True:
                print(f"주식 {code}가 catch되었습니다.")
                catched_stock.append(code)
    print(f"선택된 주식들은 {catched_stock}입니다.")
    # 파일을 쓰기 모드로 열기
    with open('catched_output.txt', 'w') as file:
        for item in catched_stock:
            file.write(f"{item}\n")  # 각 요소를 줄바꿈 문자와 함께 쓰기

if __name__ == '__main__':
    #test_simulation()
    #main_download_stock()
    test_catch_signal()
