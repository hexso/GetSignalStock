from strategy.strategy import Strategy

class ClosingPriceStrategy(Strategy):
    def __init__(self, stock_data, money=10000000, threshold=3, stop_loss=0.98, skip_change=0.2):
        """
        종가 매매법 전략 초기화
        stock_data: 주식 데이터
        threshold: 거래량 기준 (예: 최근 30일 평균 거래량 대비 3배 이상일 시 매수)
        stop_loss: 손절매 조건 (사용하지 않음, 하지만 필요할 경우 사용 가능)
        그러나 상승률이 20% 이상인경우는 캐치하지 않는다.(이미 오른 종목)
        """
        super().__init__(stock_data, money)
        self.skip_change = skip_change
        self.threshold = threshold  # 매수 기준 임계치 (거래량 기준)
        self.stop_loss = stop_loss  # 손절매 기준 임계치 (사용하지 않음)

    def apply_strategy(self):
        """
        종가 매매법 전략 적용
        """
        for i in range(30, len(self.stock_data)):  # 30일 이후부터 체크
            today_close = self.stock_data['Close'].iloc[i]
            today_volume = self.stock_data['Volume'].iloc[i]
            today_high = self.stock_data['High'].iloc[i]
            today_open = self.stock_data['Open'].iloc[i]
            avg_volume = self.stock_data['Volume'].iloc[i-30:i].mean()

            # 매수 조건: 오늘 거래량이 최근 30일 평균 거래량의 10배 이상일 경우
            if today_volume >= avg_volume * self.threshold and self.position == 0:
                buy_quantity = self.cash / today_close
                self.buy(self.stock_data.index[i], today_close, buy_quantity)  # 현재 살수 있는 최대한으로 매수
                self.logger.debug(f"{self.stock_data.index[i]}: 종가 {today_close}에 매수 (거래량: {today_volume})")

            # 매도 조건: 매수한 다음 날 매도
            elif self.position > 0 and (self.stock_data.index[i] - self.transactions[-1][0]).days == 1:
                self.sell(self.stock_data.index[i], today_open, self.position)  # 전량 매도
                self.logger.debug(f"{self.stock_data.index[i]}: 종가 {today_open}에 매도")

    def catch_signal(self, index=0):
        """
        :param index: 최신날짜를 기준으로 몇일전의 데이터를 볼것인가. 0이 오늘 1이 어제
        :return: True인 경우 맞다.
        """
        today_data = self.stock_data.iloc[-1-index]
        today_volume = today_data['Volume']
        today_change = today_data['Change']
        avg_volume = self.stock_data['Volume'].iloc[-31-index:-1-index].mean()
        if today_volume >= avg_volume * self.threshold and self.position == 0 and today_change < self.skip_change:
            return True
        return False
