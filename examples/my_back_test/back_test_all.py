import sys
from datetime import datetime
import akshare as ak
from tqdm import tqdm
import pandas as pd
tqdm.pandas(desc="progress status")

from vnpy.trader.object import TradeData, OrderData
from vnpy.trader.constant import Exchange
from vnpy.trader.optimize import OptimizationSetting
from vnpy.app.vnpy_ctastrategy.backtesting import BacktestingEngine
# from vnpy.app.vnpy_ctastrategy.strategies.mass_break_strategy import MassBreakStrategy
from vnpy.app.vnpy_ctastrategy.strategies.mass_break_ver_2_strategy import MassBreakVer2Strategy


def get_stock_basic_info_ak(stock_code: str):
    try:
        stock_individual_info_em_df = ak.stock_individual_info_em(symbol=stock_code)
        # print(stock_individual_info_em_df)
        market_value = (
            0.0
            if isinstance(stock_individual_info_em_df.loc[0, "value"], str)
            else stock_individual_info_em_df.loc[0, "value"] / 100000000
        )
        flow_market_value = (
            0.0
            if isinstance(stock_individual_info_em_df.loc[1, "value"], str)
            else stock_individual_info_em_df.loc[1, "value"] / 100000000
        )
        capitalization = (
            0.0
            if isinstance(stock_individual_info_em_df.loc[6, "value"], str)
            else stock_individual_info_em_df.loc[6, "value"] / 100000000
        )
        flow_capitalization = (
            0.0
            if isinstance(stock_individual_info_em_df.loc[7, "value"], str)
            else stock_individual_info_em_df.loc[7, "value"] / 100000000
        )
        stock_name = stock_individual_info_em_df.loc[5, "value"]
        current_price = market_value / capitalization
        return (
            stock_name,
            current_price,
            market_value,
            flow_market_value,
            capitalization,
            flow_capitalization,
        )
    except Exception as e:
        return '', 0.0, 0.0, 0.0, 0.0, 0.0


def get_code_list(m_type):
    if "sh" == m_type:
        stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
        exc = "SSE"
    else:
        stock_sh_a_spot_em_df = ak.stock_sz_a_spot_em()
        exc = "SZSE"

    # print(stock_sh_a_spot_em_df[0:10])
    codes_list = stock_sh_a_spot_em_df["代码"].values.tolist()
    print("len {}".format(len(codes_list)))
    print(codes_list)
    return codes_list, exc


def test_single_code(engine, ts_code, _market_type):
    _t_code = "{}.{}".format(ts_code, _market_type)
    print(_t_code)
    engine.set_parameters(
        vt_symbol=_t_code,
        interval="d",
        start=datetime(2024, 1, 1),
        # end=datetime(2024, 5, 22),
        rate=2.5 / 10000,
        slippage=0.1,
        size=200,
        pricetick=0.01,
        capital=1_000_000,
    )
    engine.add_strategy(
        MassBreakVer2Strategy,
        {"average_price_day": 5, "sell_price_base_day": 2, "volume_break": 0.3, "stop_ratio": 0},
    )
    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    # print(df)
    trades: list[OrderData] = engine.get_all_orders()
    last_trade_time = ""
    last_trade_type = ""
    if len(trades) > 0:
        last_trade = trades[-1]
        last_trade_time = last_trade.datetime.strftime("%Y-%m-%d")
        last_trade_type = last_trade.direction

    result = engine.calculate_statistics()
    engine.clear_data()

    return result, last_trade_time, last_trade_type


if __name__ == "__main__":
    market = sys.argv[1]
    vnpy_engine = BacktestingEngine()
    result_list = []
    stock_list, market_type = get_code_list(market)
    for t_stock in stock_list:
        try:
            res, _trade_time, _trade_type = test_single_code(
                vnpy_engine, t_stock, market_type
            )
            print(type(res))
            res_df = pd.DataFrame(res, index=[0])
            res_df["code"] = t_stock
            res_df["last_trade_time"] = _trade_time
            res_df["last_trade_type"] = _trade_type
            result_list.append(res_df)
            # print(res_df)
        except Exception as e:
            print(e)
    result_df = pd.concat(result_list, axis=0, ignore_index=True)
    result_df['basic_info'] = result_df.progress_apply(lambda row: get_stock_basic_info_ak(row["code"]), axis=1)
    result_df['market_value'] = result_df.progress_apply(lambda row: row["basic_info"][2], axis=1)
    result_df['ch_name'] = result_df.progress_apply(lambda row: row["basic_info"][0], axis=1)
    print(result_df[:10])
    result_df.to_csv("res_{}_{}.csv".format(market, datetime.now().strftime('%Y-%m-%d')))
