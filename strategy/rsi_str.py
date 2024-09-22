import pandas as pd
import talib as ta
from strategy.strategy import Strategy
from datetime import timedelta
"""
RSI가 20이하일 경우에 매수한후 매수가 기준 특정 %만큼 오르면 매도하는 전략
이 전략의 단점은 급격한 하락의 경우에는 대처하지 못한다. (예:035290 골드앤에스. 2023-05-31 급격한 하락후 매수 불가)
2024/09/15 수정 : rsi가 바닥을 찍고 올라갈때 매수하도록 수정. 
"""

# RSI 기반 전략 클래스 정의
class RSIStrategy(Strategy):
    def __init__(self, stock_data, money=10000000, rsi_period=14, buy_rsi_threshold=25, sell_gain=0.05, reset_rsi_threshold=30):
        """
        stock_data: 주식 데이터 (pandas DataFrame)
        rsi_period: RSI 계산 기간 (기본값: 14)
        buy_threshold: RSI 매수 기준 임계값 (기본값: 20 이하)
        sell_threshold: 매수 후 상승률 기준 (기본값: 10%)
        """
        super().__init__(stock_data, money)
        self.rsi_period = rsi_period
        self.buy_rsi_threshold = buy_rsi_threshold
        self.sell_gain = sell_gain
        self.waiting_for_rsi_reset = False  # 매수 후 RSI 리셋 대기 상태 플래그
        self.reset_rsi_threshold=reset_rsi_threshold
        self.buy_date = None  # 매수한 날짜를 저장할 변수
        self.test_start_index = 150

    def calculate_rsi(self):
        """ RSI를 계산하여 데이터프레임에 추가 """
        close_prices = self.stock_data['Close']
        rsi = ta.RSI(close_prices, timeperiod=self.rsi_period)
        return rsi

    def apply_strategy(self):
        """
        매매 전략 적용 함수
        """
        rsi = self.calculate_rsi()  # RSI 값 계산

        for i in range(self.test_start_index, len(self.stock_data)):
            today_rsi = rsi.iloc[i]
            yesterday_rsi = rsi.iloc[i - 1]
            today_open = self.stock_data['Open'].iloc[i]
            today_close = self.stock_data['Close'].iloc[i]
            today_price = today_close if today_close > today_open else today_open
            today_date = self.stock_data.index[i]  # 현재 날짜

            # 매수 조건: RSI가 20 이하로 내려갔다가 다시 올라갈 때, 그리고 매수 후 RSI 리셋이 완료된 상태에서만 매수 가능
            if self.position == 0 and not self.waiting_for_rsi_reset:
                if today_rsi > yesterday_rsi and yesterday_rsi <= self.buy_rsi_threshold and today_rsi < 25:
                    position = self.cash // today_price
                    self.buy(self.stock_data.index[i], today_price, position)
                    self.buy_date = today_date  # 매수한 날짜 기록
                    self.waiting_for_rsi_reset = True  # 매수 후 RSI 리셋 대기 시작
                    print(f"{self.stock_data.index[i]}: RSI {today_rsi:.2f}, 종가 {today_price}에 매수")

            elif self.position > 0:
                #매도 조건: 매수가 대비 10% 이상 상승 시
                if today_price >= self.transactions[-1][2] * (1 + self.sell_gain):
                    self.sell(self.stock_data.index[i], today_price, self.position)  # 전량 매도
                    print(f"{self.stock_data.index[i]}: RSI {today_rsi:.2f}, 종가 {today_price}에 매도")

                # 매도 조건: 7일뒤에는 매도
                elif (today_date - self.buy_date) >= timedelta(days=7):
                    self.sell(self.stock_data.index[i], today_price, self.position)  # 전량 매도
                    print(f"{self.stock_data.index[i]}: 7일이 넘어서 매도, 종가 {today_price}에 매도")

            # 매수 후 RSI 리셋 대기: RSI가 30 이상으로 올라가야 다시 매수 가능
            if self.waiting_for_rsi_reset and today_rsi >= self.reset_rsi_threshold:
                self.waiting_for_rsi_reset = False  # RSI 리셋 완료

    def show_transactions(self):
        """ 거래 내역을 출력 """
        print("거래 내역:")
        for transaction in self.transactions:
            print(transaction)

    def catch_signal(self, index = 0):
        rsi = self.calculate_rsi()  # RSI 값 계산
        today_rsi = rsi.iloc[-1 - index]
        yesterday_rsi = rsi.iloc[-2 - index]

        # 매수 조건: RSI가 20 이하로 내려갔다가 다시 올라갈 때
        if today_rsi > yesterday_rsi and yesterday_rsi <= self.buy_rsi_threshold and today_rsi < 25:
            return True
        return False

# 예시 사용법
if __name__ == '__main__':
    from stock_data_scraper import StockScraper
    stock_scraper = StockScraper()
    code = '000670'
    # 주식 데이터를 로드 (예시 데이터)
    stock_datas = stock_scraper.get_stock_data([code])
    for stock_code, stock_data in stock_datas.items():
        # DataFrame 생성
        stock_data.index.name = 'Date'
        # RSI 기반 전략 생성 및 적용
        for rate in range(2, 10):
            rsi_strategy = RSIStrategy(stock_data, sell_gain=rate*0.01)
            rsi_strategy.apply_strategy()
            print(f"sell rate : {rate}")
            print(rsi_strategy.evaluate())