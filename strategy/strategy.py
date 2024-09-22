import logging
import matplotlib.pyplot as plt

CASH = 10000000 # 천만원

class Strategy:
    def __init__(self, stock_data, cash=CASH):
        """
        기본 전략 초기화
        stock_data: pandas DataFrame (날짜, 종가, 거래량 등)
        """
        self.stock_data = stock_data
        self.position = 0  # 현재 보유 주식 수
        self.cash = cash
        self.portfolio_value = 0  # 포트폴리오 가치
        self.transactions = []  # 거래 기록

        # 매수 관련 정보
        self.aver_price = 0  # 총 매수 금액
        self.total_shares = 0

        #익절인지 손절인지 체크
        self.profit_cnt = 0
        self.loss_cnt = 0

        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)
        # 파일 핸들러 생성 및 로그 포맷 설정
        file_handler = logging.FileHandler('../my_log.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def buy(self, date, price, quantity):
        """
        매수 함수
        date: 매수 날짜
        price: 매수 가격
        quantity: 매수 수량
        """
        if self.cash >= price * quantity:
            self.position += quantity
            self.cash -= price * quantity
            self.transactions.append((date, "BUY", price, quantity))

            # 매수할 때 총 매수 금액과 총 주식 수량 업데이트
            self.aver_price = (self.aver_price * self.total_shares) + (quantity * price) / (self.total_shares + quantity)
            self.total_shares += quantity
        else:
            self.logger.debug("잔액이 부족합니다.")

    def sell(self, date, price, quantity):
        """
        매도 함수
        date: 매도 날짜
        price: 매도 가격
        quantity: 매도 수량
        """
        if self.position >= quantity:
            self.position -= quantity
            self.cash += price * quantity
            self.transactions.append((date, "SELL", price, quantity))
            if price < self.aver_price:
                self.loss_cnt += 1
            elif price > self.aver_price:
                self.profit_cnt += 1

            # 매수할 때 총 매수 금액과 총 주식 수량 업데이트
            self.total_shares -= quantity

        else:
            self.logger.debug("보유한 주식이 부족합니다.")

    def evaluate(self, current_price=None):
        """
        현재 포트폴리오 가치를 평가하는 함수
        current_price: 현재 주가
        """
        if current_price == None:
            current_price = self.stock_data['Close'].iloc[-1]
        self.portfolio_value = self.cash + (self.position * current_price)
        if self.profit_cnt + self.loss_cnt > 0:
            self.win_rate = (self.profit_cnt)/(self.profit_cnt + self.loss_cnt) * 100
        else :
            self.win_rate = 0
        return [self.portfolio_value, self.win_rate]

    # 주식 데이터를 시각화하는 함수
    def plot_stock_data_with_signals(self):
        # 날짜를 인덱스에서 컬럼으로 변환 (그래프용)
        stock_data = self.stock_data.reset_index()

        # 그래프 생성
        plt.figure(figsize=(12, 8))
        plt.plot(stock_data['Date'], stock_data['Close'], label='Close Price', color='blue')

        # 매수/매도 신호 추가
        for trade in self.transactions:
            trade_date, action, _, _ = trade

            # 거래 날짜에 해당하는 주가 데이터를 찾기
            trade_idx = stock_data[stock_data['Date'] == trade_date].index

            if not trade_idx.empty:  # 해당 날짜가 데이터에 있는 경우에만 실행
                price_at_trade = stock_data.loc[trade_idx[0], 'Close']

                if action == 'BUY':
                    # 매수 신호를 초록색 화살표로 표시
                    plt.annotate(f'Buy: {price_at_trade}',
                                 xy=(stock_data.loc[trade_idx[0], 'Date'], price_at_trade),
                                 xytext=(stock_data.loc[trade_idx[0], 'Date'], price_at_trade + 200),
                                 arrowprops=dict(facecolor='green', shrink=0.05))

                elif action == 'SELL':
                    # 매도 신호를 빨간색 화살표로 표시
                    plt.annotate(f'Sell: {price_at_trade}',
                                 xy=(stock_data.loc[trade_idx[0], 'Date'], price_at_trade),
                                 xytext=(stock_data.loc[trade_idx[0], 'Date'], price_at_trade - 200),
                                 arrowprops=dict(facecolor='red', shrink=0.05))
        # 그래프 설정
        plt.title('Stock Price with Buy/Sell Signals')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.show()