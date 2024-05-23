from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
import numpy as np


class MassBreakStrategy(CtaTemplate):
    """"""

    average_price_day = 5
    volume_break = 0.3
    sell_price_base_day = 2
    volume_range_day = 15
    stop_ratio = 0.05
    fixed_size = 100

    base_average_price = 0
    average_volume = 0
    sell_base_price = 0
    current_buy_price = 0
    # buy_and_sell_list = []

    author = "ws"
    # 基本上可以理解为parameters是输入的参数
    # variables是中间产生的变量
    parameters = [
        "average_price_day",
        "volume_break",
        "sell_price_base_day",
        "stop_ratio",
    ]
    variables = [
        "base_average_price",
        "average_volume",
        "sell_base_price",
        "current_buy_price",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(size=10)
        self.bars = []

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        # 需要过去30天数据
        self.load_bar(20)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    # https://zhuanlan.zhihu.com/p/114631485
    def on_bar(self, bar: BarData):
        # print(bar.datetime)
        """
        Callback of new bar data update.
        """
        self.cancel_all()
        # 调用ArrayManager的方法去执行一些基础计算
        am = self.am
        # 更新K线
        am.update_bar(bar)
        # print(am)
        if not am.inited:
            return

        self.bars.append(bar)
        if len(self.bars) < 16:
            return

        last_5_bars = self.bars[-1 - self.average_price_day : -1]
        close_price_list = [ele.close_price for ele in last_5_bars]
        # print("close_price_list {} ".format(close_price_list))
        self.base_average_price = np.average(close_price_list)
        last_15_bars = self.bars[-1 - self.volume_range_day : -1]
        volume_list = [ele.volume for ele in last_15_bars]
        self.average_volume = np.average(volume_list)

        last_3_bars = self.bars[-1 - self.sell_price_base_day : -1]

        close_price_list = [ele.high_price for ele in last_3_bars]
        # print("close_price_list is {} ".format(close_price_list))
        self.sell_base_price = np.min(close_price_list)
        if self.pos == 0:
            if (
                bar.close_price > 1.04 * self.base_average_price
                and bar.volume / self.average_volume >= (1.0 + self.volume_break)
            ):
                self.buy(bar.close_price * 1.02, self.fixed_size)
                self.current_buy_price = bar.close_price * 1.01
                print(
                    "time is {}, len(self.bars) is {}, self.base_average_price {}, "
                    "bar.close_price{}, average_volume is {},current vol is {}".format(
                        bar.datetime,
                        len(self.bars),
                        self.base_average_price,
                        bar.close_price,
                        self.average_volume,
                        bar.volume,
                    )
                )
                # self.buy_and_sell_list.append(("buy", bar.datetime, self.current_buy_price))

        if self.pos > 0:
            if (
                bar.close_price < (1 - self.stop_ratio) * self.sell_base_price
                or bar.close_price < 0.93 * self.current_buy_price
            ):
                self.sell(bar.close_price * 0.99, self.fixed_size)
                # self.buy_and_sell_list.append(("sell", bar.datetime, bar.close_price*0.99))

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
