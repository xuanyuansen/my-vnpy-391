from datetime import datetime

from vnpy.trader.object import TradeData, OrderData

# import matplotlib.pyplot as plt
from vnpy.trader.optimize import OptimizationSetting
from vnpy.app.vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy.app.vnpy_ctastrategy.strategies.mass_break_strategy import MassBreakStrategy

if __name__ == "__main__":
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="301389.SZSE",
        interval="d",
        start=datetime(2024, 1, 1),
        # end=datetime(2024, 5, 22),
        rate=0.3/10000,
        slippage=0.1,
        size=1000,
        pricetick=0.2,
        capital=1_000_000,
    )
    engine.add_strategy(MassBreakStrategy, {"average_price_day": 5,
                                            "sell_price_base_day": 2,
                                            "volume_break": 0.3})
    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    print(df)
    all_trade: list[OrderData] = engine.get_all_orders()
    for trade in all_trade:
        print(trade.direction)
        print(trade.datetime.strftime("%Y-%m-%d"))
    res = engine.calculate_statistics()
    fig = engine.show_chart(df)
    print(type(fig))
    fig.show()
    print(res)

    #setting = OptimizationSetting()
    #setting.set_target("sharpe_ratio")
    #setting.add_parameter("average_price_day", 5, 5, 1)
    #setting.add_parameter("sell_price_base_day", 2, 2, 1)

    # engine.run_ga_optimization(setting)
    # engine.run_bf_optimization(setting)
    # engine.calculate_statistics(df)
    # engine.show_chart(df)
