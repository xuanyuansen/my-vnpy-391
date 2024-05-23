import time
import sys
from vnpy.trader.constant import Exchange, Interval

from vnpy.trader.engine import MainEngine
from  datetime import  datetime
from vnpy.event import EventEngine

from vnpy.app.vnpy_datamanager import ManagerEngine
import akshare as ak

if __name__ == "__main__":
    market = sys.argv[1]
    if market == 'sh':
        stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
        exc = Exchange("SSE")
    else:
        stock_sh_a_spot_em_df = ak.stock_sz_a_spot_em()
        exc = Exchange("SZSE")

    print(stock_sh_a_spot_em_df[0:10])
    codes_list = stock_sh_a_spot_em_df['代码'].values.tolist()
    print('len {}'.format(len(codes_list)))
    print(codes_list)
    index = codes_list.index('300736')
    print(index)
    codes_list = codes_list[index:-1]
    # sys.exit(0)

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)
    engine = ManagerEngine(main_engine, event_engine)

    start_date = datetime.strptime("2019-01-01", "%Y-%m-%d")

    for code in codes_list:
        try:
            res = engine.delete_bar_data(
                symbol=code,
               exchange=exc,
               interval=Interval('d')
            )
            print("delete res is {}".format(res))

            #his_cnt = engine.load_bar_data(
            #    symbol=code,
            #    exchange=exc,
            #    interval=Interval('d'),
            #    start=start_date,
            #    end=datetime.strptime("2024-05-23", "%Y-%m-%d")
            #)
            #print("code {} data cnt is {}".format(code, len(his_cnt)))
            #if len(his_cnt) < 10:
                #print("code {} down".format(code))
            res = engine.download_bar_data(symbol=code,
                                       exchange=exc,
                                       interval='d',
                                       start=start_date, output=None)
        except Exception as e:
            print(e)
        # time.sleep(1)

    pass
