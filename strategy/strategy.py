import logging

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
        else:
            self.logger.debug("보유한 주식이 부족합니다.")

    def evaluate(self, current_price):
        """
        현재 포트폴리오 가치를 평가하는 함수
        current_price: 현재 주가
        """
        self.portfolio_value = self.cash + (self.position * current_price)
        return self.portfolio_value