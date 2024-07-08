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


class MassBreakVer2Strategy(CtaTemplate):
    """"""

    average_price_day = 5
    buy_price_ratio = 0.04
    volume_break = 0.3
    sell_price_base_day = 2
    volume_range_day = 15
    stop_ratio = 0.03
    fixed_size = 100

    base_average_price = 0
    average_volume = 0
    sell_base_price = 0
    current_buy_price = 0
    has_key_bar = False
    current_key_bar = None
    current_key_volume = 0
    current_continue_day = 0
    current_key_bar_index = 0

    author = "ws"
    # 基本上可以理解为parameters是输入的参数
    # variables是中间产生的变量
    parameters = [
        "average_price_day",
        "buy_price_ratio",
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

    def is_key_bar(self, bars: list[BarData]):
        bar = bars[-1]

        last_5_bars = bars[-6: -1]
        close_price_list = [ele.close_price for ele in last_5_bars]
        base_average_price = np.average(close_price_list)

        last_15_bars = bars[-16: -1]
        volume_list = [ele.volume for ele in last_15_bars]
        average_volume = np.average(volume_list)

        if (
                bar.close_price > (1 + self.buy_price_ratio) * base_average_price
                and bar.volume / average_volume >= (1.0 + self.volume_break)
        ):
            self.has_key_bar = True
            self.current_key_bar = bar
            self.current_key_volume = average_volume
            self.current_key_bar_index = len(bars)
        return

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

        if not self.has_key_bar:
            self.is_key_bar(self.bars)

        else:
            # 3天内维持成交量和成交价格稳定
            # bar.datetime - self.current_key_bar.datetime).days <= 3, 涉及到交易日的问题
            if len(self.bars) - self.current_key_bar_index <= 3:
                if (bar.volume > self.current_key_volume
                        and bar.close_price >= self.current_key_bar.low_price):
                    self.current_continue_day += 1
                    print('量能持续，key date{}, bar date {}'.format(self.current_key_bar.datetime, bar.datetime))
                if self.current_continue_day >= 2:
                    if self.pos == 0:
                        self.buy(bar.close_price * 1.01, self.fixed_size)
                        self.current_buy_price = bar.close_price * 1.01
                        print(
                            "买入, time is {}, len(self.bars) is {}, key bar {}, "
                            "bar.close_price{},current vol is {}".format(
                                bar.datetime,
                                len(self.bars),
                                self.current_key_bar,
                                bar.close_price,
                                bar.volume,
                            )
                        )
            else:
                if self.pos == 0:
                    print('超过三天，关键点失效,重新寻找关键点 {}'.format(self.current_key_bar.datetime))
                    self.has_key_bar = False
                    self.current_continue_day = 0
                else:
                    print('持续持有, {}'.format(bar.datetime))

        if self.pos > 0:
            last_3_bars = self.bars[-1 - self.sell_price_base_day: -1]
            close_price_list = [ele.close_price for ele in last_3_bars]

            self.sell_base_price = np.min(close_price_list)

            if (
                    bar.close_price < (1 - self.stop_ratio) * self.sell_base_price
                    # bar.close_price < self.sell_base_price
                    or bar.close_price < 0.93 * self.current_buy_price
                    # or bar.close_price < average_close_5_price
            ):
                self.sell(bar.close_price, self.fixed_size)
                print('卖出 {}'.format(bar.datetime))

                self.has_key_bar = False
                self.current_continue_day = 0

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
