from strategy import Strategy

class MovingAverageStrategy(Strategy):
    def __init__(self, stock_data, short_window=50, long_window=200):
        """
        단순 이동 평균 전략 초기화
        stock_data: 주식 데이터
        short_window: 단기 이동 평균 기간
        long_window: 장기 이동 평균 기간
        """
        super().__init__(stock_data)
        self.short_window = short_window
        self.long_window = long_window
        self.stock_data['Short_MA'] = self.stock_data['Close'].rolling(window=short_window).mean()
        self.stock_data['Long_MA'] = self.stock_data['Close'].rolling(window=long_window).mean()

    def apply_strategy(self):
        """
        단순 이동 평균 전략 적용
        """
        for index, row in self.stock_data.iterrows():
            if row['Short_MA'] > row['Long_MA'] and self.position == 0:
                # 매수 조건: 단기 이동 평균이 장기 이동 평균보다 높을 때
                buy_quantity = self.cash / row['Close']
                self.buy(index, row['Close'], buy_quantity)  # 현재 살수 있는 만큼 최대한으로 매수
            elif row['Short_MA'] < row['Long_MA'] and self.position > 0:
                # 매도 조건: 단기 이동 평균이 장기 이동 평균보다 낮을 때
                self.sell(index, row['Close'], self.position)  # 전량 매도
