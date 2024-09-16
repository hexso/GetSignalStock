import schedule

from strategy.closing_str import ClosingPriceStrategy
from strategy.rsi_str import RSIStrategy
from simulation import Simulation
from stock_data_scraper import StockScraper
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from telegram_handler import telegtram_main
from multiprocessing import Process

OUTPUT_PATH = 'output/'

def main_download_stock():
    #주식리스트에 있는 모든 데이터값을 stocks/ 폴더에 저장
    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_codes.txt')
    stock_datas = stock_scraper.get_stock_data(stock_codes_list)
    stock_scraper.download_stock_data(stock_datas) # 데이터를 csv파일로 저장

def test_simulation(code=None):
    """
    :param code: 주식코드
    :return:
    """
    #주식 데이터를 받아서 시뮬레이션을 돌려본다.
    money = 10000000
    stock_scraper = StockScraper()
    selected_code_list = []
    if code == None:
        stock_codes_list = stock_scraper.read_stock_codes('stock_codes.txt')
    else:
        stock_codes_list = [str(code)]
    for code in stock_codes_list:
        stock_datas = stock_scraper.get_stock_data([code])
        for stock_code, stock_data in stock_datas.items():
            # DataFrame 생성
            stock_data.index.name = 'Date'

            # 시뮬레이션 클래스 생성
            sim = Simulation(stock_data)

            closing_volume_strategy = ClosingPriceStrategy(stock_data, money)
            sim.add_strategy(closing_volume_strategy)
            sim.run()
            results = sim.get_results()
            for strategy_name, final_value in results.items():
                print(strategy_name, final_value)
                if final_value[0] > money: #현재 가치금액이 초기금액보다 높은 경우
                    selected_code_list.append(stock_code)
            #closing_volume_strategy.plot_stock_data_with_signals() # 해당 주식을 그리기
    return selected_code_list

def test_catch_signal():
    strategy_function_list = [ClosingPriceStrategy, RSIStrategy]
    def process_stock(code, stock_scraper, catched_stock):
        """
        :param code: 주식코드
        :param stock_scraper:
        :param catched_stock: {} 형식으로 받아서 {'함수이름':[주식코드,주식코드],'함수이름':['주식코드','주식코드']} 형식으로 전달됨
        """
        stock_datas = stock_scraper.get_stock_data([code])
        for stock_code, stock_data in stock_datas.items():
            # DataFrame 생성
            stock_data.index.name = 'Date'
            for strategy_function in strategy_function_list:
                str_func = strategy_function(stock_data)
                if str_func.catch_signal():
                    catched_stock[strategy_function.__name__].append(stock_code)
                    print(f"전략 {strategy_function.__name__}에서 주식:{stock_code}를 캐치했습니다.")

    import datetime
    # 오늘 날짜 가져오기
    today = datetime.date.today()
    # 날짜를 문자열 형식으로 변환 (예: 2023-09-12)
    formatted_date = today.strftime('%Y-%m-%d')

    stock_scraper = StockScraper()
    stock_codes_list = stock_scraper.read_stock_codes('stock_codes.txt')
    catched_stock = {}
    catched_stock.update({strategy_function.__name__: [] for strategy_function in strategy_function_list})
    # ThreadPoolExecutor를 사용하여 스레드 생성 및 관리
    with ThreadPoolExecutor(max_workers=8) as executor:  # 스레드 개수 설정 (8개로 설정)
        futures = [executor.submit(process_stock, code, stock_scraper, catched_stock) for code in stock_codes_list]

    # 모든 스레드가 완료될 때까지 대기
    for future in futures:
        future.result()

    print(f"선택된 주식들은 {catched_stock}입니다.")

    # 파일을 쓰기 모드로 열기
    with open(OUTPUT_PATH+formatted_date+'_catched_output.txt', 'w') as file:
        for key, value in catched_stock.items():
            file.write(f"{key}\n")
            file.write(f"{value}\n")
    return catched_stock

def test_filter():
    """
    1.제일먼저 전략을 통해(현재는 closing_str) 오늘 날짜로 주식데이터들을 다운받은 후
    주식들을 선택한다.
    2.closing str의 경우 simulation을 통해 해당 전략을 돌렸을때 이익이 나오는 주식들만을 filter해서 filter_output에 저장한다.
    :return: filter_output 딕셔너리
    """
    import datetime
    # 오늘 날짜 가져오기
    today = datetime.date.today()
    # 날짜를 문자열 형식으로 변환 (예: 2023-09-12)
    formatted_date = today.strftime('%Y-%m-%d')
    catched_list = test_catch_signal()
    filter_list = catched_list
    for stock_code in catched_list[ClosingPriceStrategy.__name__]:
        result = test_simulation(stock_code)
        if len(result) != 0:
            filter_list[ClosingPriceStrategy.__name__].remove(stock_code)
    print(filter_list)

    #filter된 리스트를 따로 아웃풋으로 저장
    with open(OUTPUT_PATH+formatted_date+'_filter_output.txt', 'w') as file:
        for key, value in filter_list.items():
            file.write(f"{key}\n")
            file.write(f"{value}\n")
    return filter_list

def test_auto_filter():
    schedule.every().day.at("15:00").do(test_filter)
    while True:
        schedule.run_pending()
        time.sleep(1)

def test_main():
    p1 = Process(target=test_auto_filter)
    p2 = Process(target=telegtram_main)

    p1.start()
    p2.start()
    p1.join()
    p2.join()

if __name__ == '__main__':
    # 시작 시간 기록
    start_time = time.time()
    #main_download_stock()
    test_simulation('900280')
    #test_catch_signal()
    #test_filter()

    #이 함수를 통해 텔레그램 봇, 특정시간에 주식을 catch하는 함수를 동시에 실행한다
    #test_main()
    # 실행 시간 계산 및 출력
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")
