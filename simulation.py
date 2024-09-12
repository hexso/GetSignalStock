class Simulation:
    def __init__(self, stock_data):
        """
        시뮬레이션 초기화
        stock_data: pandas DataFrame (날짜, 종가, 거래량 등)
        """
        self.stock_data = stock_data
        self.strategies = []
        self.results = {}

    def add_strategy(self, strategy_class):
        """
        시뮬레이션에 전략 추가
        strategy_class: Strategy 클래스 또는 그 하위 클래스
        """
        self.strategies.append(strategy_class)

    def run(self):
        """
        모든 전략을 실행하여 결과 저장
        """
        for strategy in self.strategies:
            strategy.apply_strategy()  # 전략 실행
            final_value = strategy.evaluate(self.stock_data['Close'].iloc[-1])  # 마지막 날 주가로 포트폴리오 평가
            self.results[strategy.__class__.__name__] = final_value

    def get_results(self):
        """
        시뮬레이션 결과 반환
        """
        return self.results
