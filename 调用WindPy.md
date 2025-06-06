### 2. 调用WindPy

WindPy API接口可用于获取各类高质量的金融数据，在使用时可借助Wind终端的**API代码生成器**生成获取数据的函数代码，而无需记住各类繁杂的参数说明及函数手册。具体使用流程如下：

首先，用户必须加载WindPy，然后执行w.start()启动API接口：

```python
from WindPy import w

w.start() # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒 

w.isconnected() # 判断WindPy是否已经登录成功
```

可以使用如下命令停止WindPy：

```python
w.stop() # 当需要停止WindPy时，可以使用该命令
          # 注： w.start不重复启动，若需要改变参数，如超时时间，用户可以使用w.stop命令先停止后再启动。
          # 退出时，会自动执行w.stop()，一般用户并不需要执行w.stop()，另外重复调用start/stop函数效果同单次调用。
```

需要注意的是，程序退出时会自动执行`w.stop()`，因此**一般用户并不需要执行`w.stop()`**

用户可以用`w.menu()`，显示导航界面，帮助创建命令。

### 3. 获取日时间序列函数WSD

**`w.wsd（codes, fields, beginTime, endTime, options）`**

支持股票、债券、基金、期货、指数等多种证券的基本资料、股东信息、市场行情、证券分析、预测评级、财务数据等各种数据。`wsd`可以支持取 **多品种单指标** 或者 **单品种多指标** 的时间序列数据。

- **参数说明**

| 参数      | 类型          | 可选 | 默认值       | 说明                                                         |
| :-------- | :------------ | :--- | :----------- | :----------------------------------------------------------- |
| codes     | str或list     | 否   | 无           | 证券代码，支持获取单品种或多品种，如“600030.SH”或[“600010.SH”,“000001.SZ”] |
| fields    | str或list     | 否   | 无           | 指标列表,支持获取单指标或多指标，，如“CLOSE,HIGH,LOW,OPEN”   |
| beginTime | str或datetime | 是   | endTime      | 起始日期，为空默认为截止日期，如: "2016-01-01"、“20160101”、“2016/01/01”、"-5D"(当前日期前推5个交易日)、datetime/date类型 |
| endTime   | str或datetime | 是   | 系统当前日期 | 如: "2016-01-05"、“20160105”、“2016/01/05”、"-2D"(当前日期前推2个交易日) 、datetime/date类型 |
| options   | str           | 是   | “”           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数            | 类型 | 可选 | 默认值     | 说明                                                         |
| :-------------- | :--- | :--- | :--------- | :----------------------------------------------------------- |
| Days            | str  | 是   | 'Trading'  | 日期选项，参数值含义如下： Weekdays: 工作日， Alldays: 日历日， Trading: 交易日 |
| Fill            | str  | 是   | 'Blank'    | 空值填充方式。参数值含义如下： Previous：沿用前值， Blank：返回空值  如需选择自设数值填充，在`options`添加“ShowBlank=X", 其中X为自设数。 |
| Order           | str  | 是   | 'A'        | 日期排序，“A”：升序，“D”：降序                               |
| Period          | str  | 是   | 'D'        | 取值周期。参数值含义如下： D：天， W：周， M：月， Q：季度， S：半年， Y：年 |
| TradingCalendar | str  | 是   | 'SSE'      | 交易日对应的交易所。参数值含义如下： SSE ：上海证券交易所， SZSE：深圳证券交易所， CFFE：中金所， TWSE：台湾证券交易所， DCE：大商所， NYSE：纽约证券交易所， CZCE：郑商所， COMEX：纽约金属交易所， SHFE：上期所， NYBOT：纽约期货交易所， HKEX：香港交易所， CME：芝加哥商业交易所， Nasdaq：纳斯达克证券交易所， NYMEX：纽约商品交易所， CBOT：芝加哥商品交易所， LME：伦敦金属交易所， IPE：伦敦国际石油交易所 |
| Currency        | str  | 是   | 'Original' | 输入币种。参数值含义如下： Original：“原始货币”， HKD：“港币”， USD：“美元”， CNY：“人民币” |
| PriceAdj        | str  | 是   | 不复权     | 股票和基金(复权方式)。参数值含义如下： F：前复权， B：后复权， T：定点复权；债券(价格类型) CP：净价， DP：全价， MP：市价， YTM：收益率 |

**注**:

1. Fields和Parameter也可以传入list，比如可以用[“CLOSE”,“HIGH”,“LOW”,“OPEN”]替代“CLOSE,HIGH,LOW,OPEN”;
2. 获取多个证券数据时，Fields只能选择一个。
3. 日期支持相对日期宏表达方式，日期宏具体使用方式参考'日期宏’部分内容
4. options为可选参数，可选参数多个，在参数说明详细罗列。
5. wsd函数支持输出DataFrame数据格式，需要函数添加参数usedf=True，可以使用usedfdt=True来填充DataFrame输出NaT的日期。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，`.ErrorCode =0`表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 返回函数获取的数据，比如读取000592.SZ的close指标从'2017-05-08'到'2017-05-18'区间的数据，返回值为`.Data=[[5.12,5.16,5.02,4.9,4.91,5.13,5.35,5.42,5.32],[5.3,5.12,5.17,4.98,4.94,4.93,5.1,5.4,5.4]]` |
| Codes     | 证券代码列表 | 返回获取数据的证券代码列表`.Codes=[000592.SZ]`               |
| Field     | 指标列表     | 返回获取数据的指标列表`.Fields=[CLOSE]`                      |
| Times     | 时间列表     | 返回获取数据的日期序列`.Times=[20170508,20170509,20170510,20170511,20170512,20170515,20170516, 20170517,20170518]` |

注：以DataFrame 展示数据时，如果取单个标的数据，以指标为维度进行数据展示， 如果取多个标的数据，只能取单个指标，以标的为维度进行数据展示

- **示例说明**

```python
# 任取一只国债010107.SH六月份以来的净值历史行情数据
history_data=w.wsd("010107.SH",
                   "sec_name,ytm_b,volume,duration,convexity,open,high,low,close,vwap", 
                   "2018-06-01", "2018-06-11", "returnType=1;PriceAdj=CP", usedf=True) 
# returnType表示到期收益率计算方法，PriceAdj表示债券价格类型‘
history_data[1].head()
```

### 4.获取日截面数据函数WSS

**`w.wss（codes, fields, options）`**

同样支持股票、债券、基金、期货、指数等多种证券的基本资料、股东信息、市场行情、证券分析、预测评级、财务数据等各种数据。但是WSS支持取**多品种多指标**某个时间点的截面数据。

- **参数说明**

| 参数    | 类型      | 可选 | 默认值 | 说明                                                         |
| :------ | :-------- | :--- | :----- | :----------------------------------------------------------- |
| codes   | str或list | 否   | 无     | 证券代码，支持获取单品种或多品种如'600030.SH'或['600010.SH','000001.SZ'] |
| fields  | str或list | 否   | 无     | 指标列表，支持获取多指标如'CLOSE,HIGH,LOW,OPEN'              |
| options | str       | 是   | ""     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

**注**:

1. wss函数一次只能提取一个交易日或报告期数据，但可以提取多个品种和多个指标；
2. wss函数可选参数有很多，`rptDate`，`currencyType`，`rptType`等可借助代码生成器获取；
3. wss函数支持输出DataFrame数据格式，需要函数添加参数`usedf=True`，可以使用usedfdt=True来填充DataFrame输出NaT的日期。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 返回函数获取的数据，比如读取"600111.SH,600340.SH,600485.SH" 的"eps_basic,profittogr"指标20161231（即2016年的年报）的数据，返回值为.Data=[[0.025,2.22,0.52],[1.5701,11.4605,51.8106]] |
| Codes     | 证券代码列表 | 返回获取数据的证券代码列表.Codes=[600111.SH,600340.SH,600485.SH] |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[EPS_BASIC,PROFITTOGR]         |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20180824]                      |

- **示例说明**

```python
# 取被动指数型基金最新业绩排名
fund=w.wset("sectorconstituent","date=2018-06-11;sectorid=2001010102000000").Data[1]
error_code,returns=w.wss(fund, 
                         "sec_name,return_1w,return_1m,return_3m,return_6m,return_1y,return_ytd,fund_fundmanager",
                         "annualized=0;tradeDate=20180611",usedf=True)
returns.head(10)
```

### 5. 获取分钟序列数据函数WSI

**`w.wsi(codes, fields, beginTime, endTime, options)`**

用来获取国内六大交易所（上海交易所、深圳交易所、郑商所、上金所、上期所、大商所）证券品种的分钟线数据，包含基本行情和部分技术指标的分钟数据，分钟周期为1-60min，技术指标参数可以自定义设置。

- **参数说明**

| 参数      | 类型          | 可选 | 默认值       | 说明                                                         |
| :-------- | :------------ | :--- | :----------- | :----------------------------------------------------------- |
| codes     | str或list     | 否   | 无           | 证券代码，支持获取单品种或多品种，如'600030.SH'或['600010.SH','000001.SZ'] |
| fields    | str或list     | 否   | 无           | 指标列表,支持获取单指标或多指标，，如'CLOSE,HIGH,LOW,OPEN'   |
| beginTime | str或datetime | 是   | endTime      | 分钟数据的起始时间，支持字符串、datetime/date如: "2016-01-01 09:00:00" |
| endTime   | str或datetime | 是   | 当前系统时间 | 分钟数据的截止时间，支持字符串、datetime/date如: "2016-01-01 15:00:00"，缺省默认当前时间 |
| options   | str           | 是   | ""           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数     | 类型 | 可选 | 默认值  | 说明                                                         |
| :------- | :--- | :--- | :------ | :----------------------------------------------------------- |
| BarSize  | str  | 是   | “1”     | BarSize在1-60间选择输入整数数字，代表分钟数                  |
| Fill     | str  | 是   | 'Blank' | 空值填充方式。参数值含义如下： Previous：沿用前值， Blank：返回空值  如需选择自设数值填充，在`options`添加“ShowBlank=X", 其中X为自设数。 |
| PriceAdj | str  | 是   | U       | 股票和基金(复权方式)。参数值含义如下： U：不复权, F：前复权， B：后复权。 |

**注**：

1. `wsi`一次支持提取单品种或多品种，并且品种名带有“.SH”等后缀；
2. `wsi`提取的指标fields和可选参数option可以用list实现；
3. `wsi`支持国内六大交易(上交所、深交所、大商所、中金所、上期所、郑商所)近三年的分钟数据;
4. `wsi`函数支持输出DataFrame数据格式，需要函数添加参数usedf=True，如例2.
5. `wsi`支持多品种多指标,单次提取一个品种支持近三年数据，若单次提多个品种,则品种数*天数≤100。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 读取中国平安"601318.SH"的"open,high"指标2017-06-01 09:30:00至2017-06-01 10:01:00的五分钟数据，返回值为.Data=[[45.4,45.15,45.42,45.34,45.47,45.48],[45.63,45.49,45.56,45.52,45.51,45.72]] |
| Codes     | 证券代码列表 | 返回获取数据的证券代码列表.Codes=[600111.SH,600340.SH,600485.SH] |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[open,high]                    |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20170601 09:35:00,20170601 09:40:00,20170601 09:45:00,20170601 09:50:00,20170601 09:55:00,20170601 10:00:00] |

- **示例说明**

```python
# 取IF00.CFE的分钟数据

from datetime import *
codes="IF00.CFE";
fields="open,high,low,close";
error,data=w.wsi(codes, fields, "2017-06-01 09:30:00", datetime.today(), "",usedf=True)
#其中，datetime.today()是python内置的日期函数，表示当前时刻。
```

### 6. 获取日内tick数据函数WST

**`w.wst(codes, fields, beginTime, endTime, options)`**

用获取国内六大交易所（上海交易所、深圳交易所、郑商所、上金所、上期所、大商所）证券品种的日内盘口买卖五档快照数据和分时成交数据(tick数据).

- **参数说明**

| 参数      | 类型          | 可选 | 默认值       | 说明                                                         |
| :-------- | :------------ | :--- | :----------- | :----------------------------------------------------------- |
| codes     | str或list     | 否   | 无           | 证券代码，支持获取单品种，如'600030.SH'                      |
| fields    | str或list     | 否   | 无           | 指标列表,支持获取单指标或多指标，，如'CLOSE,HIGH,LOW,OPEN'   |
| beginTime | str或datetime | 是   | endTime      | 分钟数据的起始时间，支持字符串、datetime/date如: "2016-01-01 09:00:00" |
| endTime   | str或datetime | 是   | 当前系统时间 | 分钟数据的截止时间，支持字符串、datetime/date如: "2016-01-01 15:00:00"，缺省默认当前时间 |
| options   | str           | 是   | ""           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

**注**：

1. wst只支持提取单品种，并且品种名带有“.SH”等后缀；
2. wst提取的指标fields可以用list实现；
3. wst支持国内六大交易(上交所、深交所、大商所、中金所、上期所、郑商所)近七个交易日的tick数据;
4. wst函数支持输出DataFrame数据格式，需要函数添加参数usedf=True。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 返回函数获取的tick数据，读取中国平安"601318.SH"的"last,bid1"指标2017-06-13 09:30:00至2017-06-13 9:31:00的tick数据，返回值为.Data=[[9.11,9.11,9.11,9.11,9.11,9.11,9.11,9.11,9.11,9.11,...],[9.11,9.11,9.12,9.11,9.11,9.11,9.11,9.11,9.11,9.12,...]] |
| Codes     | 证券代码列表 | 返回获取数据的证券代码列表.Codes=[601318.SH]                 |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[open,high]                    |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20170601 09:35:00,20170601 09:40:00,20170601 09:45:00,20170601 09:50:00,20170601 09:55:00,20170601 10:00:00] |

- **示例说明**

```python
# 提取平安银行（000001.SZ）当天的买卖盘数据。
from datetime import *

# 设置起始时间和截止时间，通过wst接口提取序列数据
begintime=datetime.strftime(datetime.now(),'%Y-%m-%d 09:30:00')
endtime=datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
# last最新价，amt成交额，volume成交量
# bid1 买1价，bsize1 买1量
# ask1 卖1价, asize1 卖1量
codes="000001.SZ"
fields="last,bid1,ask1" 
w.wst(codes,fields,begintime,endtime)
```

### 7.实时行情数据函数 WSQ

**`w.wsq（codes, fields, options, func)`**

用来获取股票、债券、基金、期货、指数等选定证券品种的当天指标实时数据，可以一次性请求实时快照数据，也可以通过订阅的方式获取实时数据。

- **参数说明**

| 参数    | 类型      | 可选 | 默认值 | 说明                                                         |
| :------ | :-------- | :--- | :----- | :----------------------------------------------------------- |
| codes   | str或list | 否   | 无     | 证券代码，支持获取单品种或多品种，如："600030.SH,000001.SZ "、["600030.SH","000001.SZ"]' |
| fields  | str或list | 否   | 无     | 指标列表,支持获取多指标，，如'CLOSE,HIGH,LOW,OPEN'           |
| options | str       | 是   | ”“     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |
| func    | str       | 是   | None   | func默认为None, 此时以一次性快照方式获取数据，func=DemoWSQCallback时, 以订阅的方式实时返回行情数据, DemoWSQCallback的函数定义可参考API帮助中心的案例 |

**注：**

1. `wsq`函数的参数中品种代码、指标和可选参数也可以用list实现；用户可以一次提取或者订阅多个品种数据多个指标；
2. `wsq`函数订阅模式下只返回订阅品种行情有变化的订阅指标, 对没有变化的订阅指标不重复返回实时行情数据；
3. `wsq`订阅时，API发现用户订阅内容发生变化则调用回调函数，并且只把变动的内容传递给回调函数。
4. 用户自己定义的回调函数格式请参考API帮助中心的案例，回调函数中不应处理复杂的操作；
5. `wsq`函数快照模式支持输出DataFrame数据格式，需要函数添加参数usedf=True，可以使用usedfdt=True来填充DataFrame输出NaT的日期。

- **返回说明**

  **快照模式下函数输出字段解释如下：**

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 返回函数获取的快照数据，读取中国平安"601318.SH "的"rt_last,rt_open"指标快照数据.Data=[[54.16],[53.72]] |
| Codes     | 证券代码列表 | 返回获取数据的证券代码列表.Codes=[601318.SH]                 |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[open,high]                    |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20170626 17:50:53]             |

 **订阅模式下函数输出字段解释如下：**

`w.wsq`运行后，会将行情传入回调函数`DemoWSQCallback`, 传入数据为WindData类型，具体数据字段信息如下:

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| StateCode | 状态ID       | 返回订阅时的字段，无实质意义..StateCode=1                    |
| RequestID | 请求ID       | 返回订阅的请求ID.RequestID=4                                 |
| Code      | 证券代码列表 | 返回获取实时数据的品种列表, 只返回行情变动指标对应的品种..Code=[601318.SZ] |
| Fileds    | 字段列表     | 返回获取的实时数据的指标列表, 只返回行情变动的指标列表.Fields=[RT_OPEN,RT_LAST] |
| Times     | 时间列表     | 返回获取数据的本地时间戳.Times=[20170626 17:50:53]           |
| Data      | 数据列表     | 返回函数获取的实时行情数据，获取中国平安"601318.SH" 的"rt_last,rt_open"指标订阅数据.Data=[[54.16],[53.72]] |

#### 取消实时行情订阅函数CancelRequest

**`w.cancelRequest(RequestID)`**

用来根据w.wsq的订阅请求ID来取消订阅

- **参数说明**

| 参数      | 类型 | 可选 | 默认值 | 说明                                                         |
| :-------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| RequestID | int  | 否   | 无     | 输入取消订阅的订阅ID, 支持取消单次订阅和全部订阅.支持格式: 1或0 |

**注**：

1. 可以像w.cancelRequest(3)一样，输入一个id的数字，而取消某订阅；
2. 请求ID为0代表取消全部订阅，即输入w.cancelRequest(0)。

- **示例说明**

```python
data=w.wsq("600000.SH","rt_low,rt_last_vol",func=DemoWSQCallback);
#订阅
#等待回调，用户可以根据实际情况写回调函数
#....
#根据刚才wsq返回的请求ID，取消订阅
w.cancelRequest(data.RequestID)
```

### 8. 获取板块日序列数据函数WSES

**`w.wses(codes, fields, beginTime, endTime, options)`**

用来获取沪深股票、香港股票、全球股票的板块的历史日序列数据，包括依据板块个股数据计算的板块日行情数据、基本面数据以及盈利预测数据等。

- **参数说明**

| 参数      | 类型 | 可选 | 默认值       | 说明                                                         |
| :-------- | :--- | :--- | :----------- | :----------------------------------------------------------- |
| codes     | str  | 否   | 无           | 支持获取单板块或多板块如："a001010100"、["a001010200","a001010200"]、 |
| fields    | str  | 否   | 无           | 仅支持单指标如："sec_close_avg"                              |
| beginTime | str  | 是   | 截止日期     | 为空默认为截止日期如: "2016-01-01"、“20160101”、“2016/01/01”、"-5D"(当前日期前推5个交易日)、datetime/date格式 |
| endTime   | str  | 是   | 当前系统日期 | 如: "2016-01-05"、“20160105”、“2016/01/05”、"-2D"(当前日期前推2个交易日) 、datetime/date格式 |
| options   | str  | 是   | ""           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些经常被用到的参数：

| 参数            | 类型 | 可选 | 默认值    | 说明                                                         |
| :-------------- | :--- | :--- | :-------- | :----------------------------------------------------------- |
| Fill            | str  | 是   | "Blank"   | 空值填充方式。参数值含义如下： Previous：沿用前值， Blank：返回空值  如需选择自设数值填充，在`options`添加“ShowBlank=X", 其中X为自设数。 |
| Period          | str  | 是   | "D"       | 取值周期。参数值含义如下： D：天， W：周， M：月， Q：季度， S：半年， Y：年 |
| Days            | str  | 是   | "Trading" | 日期选项。参数值含义如下： Weekdays：工作日, Alldays： 日历日, Trading：交易日 |
| TradingCalendar | str  | 是   | "SSE"     | 交易日对应的交易所。参数含义如下： SSE : 上海证券交易所, SZSE: 深圳证券交易所, CFFE: 中金所, TWSE: 台湾证券交易所, DCE: 大商所， NYSE: 纽约证券交易所, CZCE: 郑商所, COMEX: 纽约金属交易所, SHFE: 上期所, NYBOT: 纽约期货交易所, HKEX: 香港交易所, CME: 芝加哥商业交易所, Nasdaq: 纳斯达克证券交易所, NYMEX: 纽约商品交易所, CBOT: 芝加哥商品交易所, LME: 伦敦金属交易所, IPE: 伦敦国际石油交易所 |
| DynamicTime     | str  | 是   | "1"       | "0"：使用板块历史成分，"1"：使用板块最新成分                 |

**注**:

1. `wses`函数一次性可选取多个板块一个指标来提取日期序列数据；
2. `wses`函数支持Python中的date或datetime时间格式；
3. `wses`函数支持输出DataFrame数据格式，需要函数添加参数usedf=True. 如例1。可以使用usedfdt=True来填充DataFrame输出NaT的日期。
4. 板块名称或板块ID可通过板块查询工具查找。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 比如读取上证A股和深证A股近两日的平均收盘价"sec_close_avg"指标数据，返回值为.Data=[[13.00764,13.31552],[ 12.88665,13.19833]] |
| Codes     | 证券代码列表 | 返回获取数据的板块ID.Codes=[a001010200000000, a001010300000000] |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[sec_close_avg]                |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20180828]                      |

- **示例说明**

```python
# 提取上证A股和深证A股的当日平均收盘价信息。
errorCode,data=w.wses("a001010200000000,a001010100000000", "sec_close_avg", "2018-08-21", "2018-08-27", "", usedf=True)
```

### 9. 获取板块日截面数据函数WSEE

**`w.wsee(codes, fields, options)`**

获取沪深股票、香港股票、全球股票选定板块的历史日截面数据，比如取全部A股板块的平均行情数据、平均财务数据等。

- **参数说明**

| 参数    | 类型 | 可选 | 默认值 | 说明                                                         |
| :------ | :--- | :--- | :----- | :----------------------------------------------------------- |
| codes   | str  | 否   | 无     | 支持获取单板块或多板块如："a001010100"、["a001010200","a001010200"]、 |
| fields  | str  | 否   | 无     | 仅支持单指标如："sec_close_avg"                              |
| options | str  | 是   | ”“     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数        | 类型 | 可选 | 默认值 | 说明                                     |
| :---------- | :--- | :--- | :----- | :--------------------------------------- |
| DynamicTime | str  | 是   | “1”    | 0：使用板块历史成分，1：使用板块最新成分 |

**注**:

1. `wsee`函数一次只能提取一个交易日数据，但可以提取多个板块和多个指标；
2. `wsee`函数可选参数有很多，unit，currencyType等可借助代码生成器获取；
3. `wsee`函数支持输出DataFrame数据格式，需要函数添加参数usedf=True，如例1。可以使用usedfdt=True来填充DataFrame输出NaT的日期。
4. 板块名称或板块ID可通过板块查询工具查找。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 比如读取上证A股和深证A股近两日的平均收盘价"sec_close_avg"指标数据，返回值为.Data=[[13.00764,13.31552],[ 12.88665,13.19833]] |
| Codes     | 证券代码列表 | 返回获取数据的板块ID.Codes=[a001010200000000, a001010300000000] |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[sec_close_avg]                |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20180828 ]                     |

- **示例说明**

```python
# 提取上证A股和深证A股的当日平均收盘价信息。
errorCode,data=w.wsee("a001010200000000,a001010300000000","sec_close_avg","tradeDate=20180827",usedf=True)
```

### 10.获取报表数据函数WSET

**`w.wset(tableName, options)`**

用来获取数据集信息，包括板块成分、指数成分、ETF申赎成分信息、分级基金明细、融资标的、融券标的、融资融券担保品、回购担保品、停牌股票、复牌股票、分红送转等报表数据。

- **参数说明**

| 参数      | 类型 | 可选 | 默认值 | 说明                                                         |
| :-------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| tableName | str  | 否   | 无     | 输入获取数据的报表名称，可借助代码生成器生成如：" SectorConstituent ", |
| options   | str  | 是   | ”“     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

**注**:

1. 数据集涉及内容较多，并且每个报表名称均不同，建议使用代码生成器生成代码，更方便地获取数据；
2. `wset`函数支持输出DataFrame数据格式，需要函数添加参数`usedf = True`, 如例2。可以使用usedfdt=True来填充DataFrame输出NaT的日期。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 返回函数获取的报表数据，比如读取全部A股2018-08-27的板块成分,返回值为.Data=[[2018-08-27,2018-08-27,…],[ 000001.SZ,000002.SZ,…],[平安银行,万科A,…] |
| Codes     | 证券代码列表 | 返回获取数据的板块ID.Codes=[1,2,3,4,5,6,7,8,9,10,...]        |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[date,wind_code,sec_name]      |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20180828]                      |

- **示例说明**

```python
# 获取申万一级行业的成分股
sw_index=w.wset("sectorconstituent","date=2018-06-12;sectorid=a39901011g000000",usedf=True)
sw_index[1].head(5)
```

### 11. 获取全球宏观经济数据函数EDB

**`w.edb(codes, beginTime, endTime, options)`**

用来获取Wind宏观经济数据库中的数据信息，为用户提供了一个方便查看及导出宏观/行业板块数据的工具。宏观经济数据库现在包括中国宏观经济、全球宏观经济、行业经济数据、商品数据、利率数据这几大类。

- **参数说明**

| 参数      | 类型         | 可选 | 默认值       | 说明                                                         |
| :-------- | :----------- | :--- | :----------- | :----------------------------------------------------------- |
| codes     | String/ List | 否   | 无           | 输入获取数据的指标代码，可借助代码生成器生成格式如"M5567877,M5567878" ,["M5567877","M5567878"] |
| beginTime | str          | 是   | 截止日期     | 为空默认为截止日期如: "2016-01-01"、“20160101”、“2016/01/01”、"-5D"(当前日期前推5个交易日)、datetime/date类型 |
| endTime   | str          | 是   | 系统当前日期 | 如: "2016-01-05"、“20160105”、“2016/01/05”、"-2D"(当前日期前推2个交易日) 、datetime/date类型 |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数 | 类型 | 可选 | 默认值  | 说明                                                         |
| :--- | :--- | :--- | :------ | :----------------------------------------------------------- |
| Fill | str  | 是   | 'Blank' | 空值填充方式。参数值含义如下： Previous：沿用前值， Blank：返回空值  如需选择自设数值填充，在`options`添加“ShowBlank=X", 其中X为自设数。 |

**注**:

1. `edb`函数对接Wind终端宏观经济数据库, 其中的指标一般都可以通过API下载；
2. `edb`函数支持输出DataFrame数据格式，需要函数添加参数`usedf = True`, 如例1。可以使用usedfdt=True来填充DataFrame输出NaT的日期。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释         | 说明                                                         |
| :-------- | :----------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID       | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表     | 返回函数获取的数据，比如读取 M5567878,M5567879从'2017-05-08'到'2017-05-18'的季度数据，返回值为.Data[[82323.0,106982.4]] |
| Codes     | 证券代码列表 | 返回获取数据的证券代码列表.Codes=[M5567878,M5567879]         |
| Field     | 指标列表     | 返回获取数据的指标列表.Fields=[CLOSE]                        |
| Times     | 时间列表     | 返回获取数据的日期序列.Times=[20170630]                      |

- **示例说明**

```python
# 提取我国近十年三大产业的GDP值
from datetime import *
w.edb("M0001395,M0001396,M0001397,M0001400,M0028610,M0045788","ED-10Y","2017-06-28","Fill=Previous",usedf = True)
```

### 12.交易登录函数tlogon

**`w.tlogon(BrokerID, DepartmentID, LogonAccount, Password, AccountType, options, func)`**

可以登录资金账号或者量化模拟账号，登录成功时系统自动为登录号生成一个登录ID logonID, 作为登录账号的唯一标示.

- **参数说明**

| 参数         | 类型       | 可选 | 默认值 | 说明                                                         |
| :----------- | :--------- | :--- | :----- | :----------------------------------------------------------- |
| BrokerID     | str / list | 否   | 无     | 输入模拟交易或期货实盘交易的经纪商ID，经纪商ID可借助代码生成器获取, 模拟交易为"0000" |
| DepartmentID | str        | 否   | 无     | 输入模拟交易或实盘交易的经纪商营业部ID。(绝大部分证券和期货柜台无需指定营业部代码，即填0；请使用命令生成器确认详情) |
| LogonAccount | str        | 否   | 否     | 输入模拟交易或实盘交易的资金账号. 若是模拟交易，账号需在Wind终端WTTS模块开通，其中： 股票（沪深A股+沪市B股+深市B股）模拟账号为WFT账号+01， 期货（中金、上期、大商、郑商）模拟账号为WFT账号+02， 衍生品（上交所期权）模拟账号为WFT账号+03， 港股模拟账号为WFT账号+04 |
| Password     | str        | 否   | 否     | 输入资金账号对应的资金密码模拟交易资金密码为任意值           |
| AccountType  | str        | 否   | 否     | 账户的市场类型。参数值含义如下： SHSZ：深圳上海A CZC：郑商所 SHF：上期所 DCE：大商所 CFE：中金所 SHO：上证期权 HK：港股 |
| options      | str        | 是   | ”“     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |
| func         | str        | 是   | None   | 输入CTP委托/成交回报的回调函数, 期货CTP账号登录下, 通过回调函数返回委托或成交信息，其中： 001：委托回报， 4002：成交回报。 |

**注**：

1. `w.tlogon`支持向量操作，也即每个参数都可以使用数组输入，对于只有一个元素的参数会自动扩充；
2. Wind终端WTTS模块开通模拟交易账号，其中股票模拟账号为：WFT账号+01，期货为WFT账号+02，衍生品为WFT账号+03，港股为WFT账号+04。
3. `w.tlogon`可以登录实盘资金账号或者模拟交易账号，登录成功时系统自动生成一个登录号登录ID，用于标识登录账号。退出登录时也是使用登录ID登出。

- **返回说明**

该函数返回WindData对象，包含以下成员：

| 字段       | 解释               | 说明                                                         |
| :--------- | :----------------- | :----------------------------------------------------------- |
| .ErrorCode | 错误码             | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| .Field     | 返回数据的字段名称 | 返回登录信息的字段。字段含义如下： LogonID： 返回登录账号的登录ID， LogonAccount：返回登录时输入的登录账号， AccountType：返回账号类型，即账号所属市场， ErrorCode：返回登录错误码，正常登录错误码为0， ErrorMsg：返回登录错误信息  例如：终端账号为w0817573登录期权模拟交易账户`.Fields=[LogonID,LogonAccount,AccountType,ErrorCode,ErrorMsg]` |
| .Data      | 返回数据的值       | 返回登录信息字段对应的具体值, 如.Data=[[3],[W081757303],[SHO],[0],[]] |

- **示例说明**

```python
# Wind终端账号为W0812638的用户终端WTTS模块创建了'W081263801'股票模拟交易账号，'W081263802'期货模拟交易账号, 则登录代码为同时登录两个账号
LogonID=w.tlogon('0000',0,['w081263801','w081263802'],'000000',['sh','cfe']) 

# 登录股票模拟账号
w.tlogon("0000","","W081756801","****","SHSZ")
```

### 13.交易登出函数tlogout

**`w.tlogout(LogonID, options)`**

根据账号登录时的logonID退出登录

- **参数说明**

| 参数    | 类型 | 可选 | 默认值 | 说明                                                         |
| :------ | :--- | :--- | :----- | :----------------------------------------------------------- |
| LogonID | str  | 否   | 无     | logon登录返回或 tquery('LogonID')查询返回，输入LogonID登出，输入LogonID登出。登出时调用LogonID即可，只有单个交易登录时可缺省。 |
| options | str  | 是   | ”“     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

**注**:

1. `w.tlogout`的登录参数LogonID支持的格式为“0”、0、LogonID = "1".
2. 只有一个交易登录时，登出可不输入LogonID。

- **返回说明**

该函数返回WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，`.ErrorCode =0`表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表 | 返回登出信息字段对应的具体值, 如`.Data=[[1],[0],[logout]]`   |
| Field     | 指标列表 | 返回登录信息的字段，其中： LogonID：登录返回的ID ErrorCode：返回登录错误码。正常登录错误码为0， ErrorMsg：返回登录错误信息  例如: 终端账号为w0817573登录期权模拟交易账户`.Fields=[LogonID,LogonAccount,AccountType,ErrorCode,ErrorMsg]` |

### 14.交易委托下单函数torder

**`w.torder(SecurityCode, TradeSide, OrderPrice, OrderVolume, options)`**

用于登录账号的委托下单

- **参数说明**

| 参数         | 类型     | 可选 | 默认值 | 说明                                                         |
| :----------- | :------- | :--- | :----- | :----------------------------------------------------------- |
| SecurityCode | str      | 否   | 无     | 输入委托下单证券代码, 如“600000.SH”，可输入交易代码，此时需指定MarketType |
| TradeSide    | str      | 否   | 否     | 输入委托下单的交易方向, 根据不同品种选择交易方向. 参数值含义如下： Buy / 1: 买入开仓、证券买入, Short / 2: 卖出开仓, Cover / 3: 买入平仓, Sell / 4: 卖出平仓、证券卖出, CoverToday / 5: 买入平今仓, SellToday / 6 卖出平今仓, ShortCovered / 7: 备兑开仓, CoverCovered / 8: 备兑平仓 |
| OrderPrice   | str或int | 否   | 否     | 输入委托下单的委托价格格式: “10.12”、10.12                   |
| OrderVolume  | str或int | 否   | 否     | 输入委托下单的委托数量格式：“100”、100                       |
| options      | str      | 是   | “”     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数       | 类型 | 可选 | 默认值 | 说明                                                         |
| :--------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| OrderType  | str  | 是   | “LMT”  | 输入委托方式，默认为限价交易 "OrderType=LMT"。 参数值含义如下： LMT / 0： 限价委托， BOC / 1: 对方最优价格委托， BOP / 2: 本方最优价格委托， ITC / 3: 即时成交剩余撤销， B5TC / 4: 最优五档剩余撤销， FOK / 5: 全额成交或撤销委托(市价FOK)， B5TL / 6: 最优五档剩余转限价， ALO: 竞价限价盘， ACO: 竞价盘， ELO: 增强限价盘， SLO: 特别限价盘， FOK_LMT: 全额成交或撤销委托(限价FOK)， EXE: 期权行权， MTL: 市价剩余转限价。  深证支持方式为LMT / 0, BOC / 1, BOP / 2, ITC / 3, B5TC / 4, FOK / 5 上证支持方式为LMT / 0, B5TC / 4, B5TL / 6 期权支持方式为LMT / 0, ITC / 3, FOK / 5, FOK_LMT , EXE, MTL 港股支持方式为LMT / 0, ALO, ACO, ELO, SLO 期货支持方式为LMT / 0 |
| HedgeType  | str  | 是   | “SPEC” | 选择投机套保类型，可选参数。默认为"HedgeType=Spec", 选择套保需要专门的保账号。HedgeType可取值如下： Spec：投机 Hedge：套保 |
| LogonID    | str  | 是   | 否     | logon登录返回或 tquery('LogonID')查询返回，用于区分多个账号同时登录,输入登录ID, 单账号时可不填，多账号时必选,来自于账户登录的登录ID，如 "LogonID=1" |
| MarketType | str  | SH   | “SH”   | 输入市场类型，SecurityCode为交易码时需要填写，默认"MarketType=SH", 参数值含义如下： SZ / 0: 证券-深圳, SH / 1: 证券-上海, OC / 2: 证券-深圳特（三版）, HK / 6: 证券-港股, CZC / 7: 商品期货(郑州), SHF / 8: 商品期货(上海), DCE / 9: 商品期货(大连), CFE / 10: 股指期货(中金) |

**注**：

1. 本命令支持向量操作，也即每个参数都可以使用数组输入，对于只有一个元素的参数会自动扩充；
2. 只有一个交易登录时，可以不输入LogonID，否则一定需要输入，即用LogonID=xxxx方式输入；
3. 当用户输入的代码没有带.的市场后缀时，需要提供MarketType，MarketType可以取：0/SZ; 1/SH; 2/OC; 6/HK; 7/CZC; 8/SHF; 9/DCE; 10/CFE;
4. 通过w.tquery(‘order’,requestid=XXX)查询委托情况;
5. 期货套保账号时一定需要加上HedgeType=HEDG/1，因为缺省是投机HedgeType =SPEC/0

- **返回说明**

该函数返回WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表 | 返回登录信息字段对应的具体值, 如.Data=[[3],[W081757303],[SHO],[0],[]] |
| Field     | 指标列表 | 返回委托下单信息的字段。字段含义如下： RequestID：请求ID, SecurityCode：委托下单的证券代码, TradeSide：买卖方向, OrderPrice：委托价格, OrderVolume：委托数量, HedgeType：投机保值类型, OrderType：委托类型, LogonID：登录账号返回的登录ID, ErrorCode：错误ID,若成功则返回0, ErrorMsg：报错字符串  例如: 以10.3元委托下单买入000001.SZ 100股. `Fields=[RequestID,SecurityCode,TradeSide,OrderPrice,OrderVolume,OrderType,LogonID,ErrorCode,ErrorMsg]` |

### 15.交易撤销委托函数tcancel

**`w.tcancel(OrderNumber, options)`**

用于撤销w.torder发出的委托请求

- **参数说明**

| 参数        | 类型 | 可选 | 默认值 | 说明                                                         |
| :---------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| OrderNumber | str  | 否   | 无     | 输入撤销委托对应的委托编号,委托下单时会生成委托编号, 通过w.tquery("Order")可获得委托编号，委托编号在撤销委托时使用。 |
| options     | str  | 是   | ""     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数       | 类型 | 可选 | 默认值 | 说明                                                         |
| :--------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| LogonID    | str  | 是   | 否     | tlogon登录返回或 tquery('LogonID')查询返回，用于区分多个账号同时登录,输入撤单账号对应的登录ID单账户登录可选，多账户登录必选. |
| MarketType | str  | 是   | "SH"   | 输入市场类型，SecurityCode为交易码时需要填写，默认"MarketType=SH"。参数值含义如下： 参数值含义如下： SZ / 0: 证券-深圳, SH / 1: 证券-上海, OC / 2: 证券-深圳特（三版）, HK / 6: 证券-港股, CZC / 7: 商品期货(郑州), SHF / 8: 商品期货(上海), DCE / 9: 商品期货(大连), CFE / 10: 股指期货(中金) |

**注：**

1. 本命令支持向量操作，也即每个参数都可以使用数组输入，对于只有一个元素的参数会自动扩充；
2. 只有一个交易登录时，可以不输入LogonID，否则一定需要输入，即用LogonID=xxxx方式输入；
3. 当用户有很多笔不同市场的下单时，RequestID可能会有重复，此时需要使用MarketType区别，MarketType可以取：0/SZ; 1/SZ; 2/OC; 6/HK; 7/CZC; 8/SHF; 9/DCE; 10/CFE。

- **返回说明**

该函数返回WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，`.ErrorCode =0`表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表 | 返回撤销信息字段对应的具体值, 如`.Data=[[3],[W081757303],[SHO],[0],[]]` |
| Field     | 指标列表 | 返回撤销委托信息的字段，其中: OrderNumber：委托编号, ErrorCode：错误编号, ErrorMsg：错误信息,如: 撤销登录ID为1，委托编号为250的委托  `.Fields=[OrderNumber,LogonID,ErrorCode,ErrorMsg]` |

### 16.交易情况查询函数tquery

**`w.tquery(qrycode, options)`**

用于查询交易相关信息

- **参数说明**

| 参数      | 类型 | 可选 | 默认值 | 说明                                                         |
| :-------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| queryType | str  | 否   | 无     | 输入需要查询的内容，例如： Capital：资金查询, Position：持仓查询, Order：当日委托查询, Trade：当日成交查询, Account：股东账号查询, LogonID：登录ID查询 |
| options   | str  | 是   | ""     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数        | 类型 | 可选 | 默认值   | 说明                                                         |
| :---------- | :--- | :--- | :------- | :----------------------------------------------------------- |
| LogonID     | str  | 是   | 否       | 输入撤单账号对应的登录ID单账户登录可选，多账户登录必选.      |
| RequestID   | str  | 是   | 否       | 输入查询对应的请求ID，请求ID系统自动生成.当日委托查询2/order时可以依据委托torder返回的requestID查询。例如"RequestID=3". |
| OrderNumber | str  | 是   | 否       | 输入委托号查询委托，"Qrycode=Order"时有意义，委托号来源于w.tquery("Order")获得的OrderNumber |
| MarketType  | str  | 是   | "SH"     | 输入市场类型，SecurityCode为交易码时需要填写，默认"MarketType=SH"。参数含义如下： 参数值含义如下： SZ / 0: 证券-深圳, SH / 1: 证券-上海, OC / 2: 证券-深圳特（三版）, HK / 6: 证券-港股, CZC / 7: 商品期货(郑州), SHF / 8: 商品期货(上海), DCE / 9: 商品期货(大连), CFE / 10: 股指期货(中金) |
| OrderType   | str  | 是   | 全部委托 | 输入查询委托的委托类型，默认是查询全部委托.Withdrawable 可撤 |
| WindCode    | str  | 是   | 否       | 输入查询指定证券的信息"WindCode=002311.SZ", Qrycode=Order/Position/Trade时 |
| BrokerID    | str  | 是   | 否       | 营业部查询4/department时，必填。例如L"BrokerID=0000"。       |

**注:**

1. 除qrycode外，本命令支持向量操作，也即其他每个参数都可以使用数组输入，对于只有一个元素的参数会自动扩充；
2. 只有一个交易登录时，可以不输入LogonID，否则一定需要输入，即用LogonID=xxxx方式输入。
3. qrycode可取：Capital资金查询；Position持仓查询；Order当日委托查询；Trade当日成交查询； broker 经济商查询； LogonID登录ID查询, Account登录账号查询。
4. 当日委托查询Order时可以依据委托Order返回的RequestID查询，该查询立即返回，返回服务器已经返回的信息。

- **返回说明**

该函数返回WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Data      | 数据列表 | 返回查询信息的具体值,                                        |
| Field     | 指标列表 | 返回查询信息的字段                                           |

**当QueryCode =Capital进行股票、期货、期权账号资金查询时, ResFields返回值的字段说明如下：**

| 股票返回字段                               | 期货返回字段                                  | 期权返回字段                                  |
| :----------------------------------------- | :-------------------------------------------- | :-------------------------------------------- |
| MoneyType：货币类型                        | MoneyType                                     | MoneyType：货币类型                           |
| AvailableFund：资金可用                    | AvailableFund                                 | AvailableFund：资金可用                       |
| SecurityValue：持仓市值                    | BalanceFund：资金余额                         | BalanceFund：资金余额                         |
| FundAsse：资金资产                         | FetchFund：可取资金                           | FundAsset：资金资产                           |
| TotalAsset：总资产                         | ExerciseMargin：履约保证金                    | TotalAsset：总资产                            |
| Profit：总盈亏                             | RealFrozenMarginA：当日开仓预冻结金额         | Profit：总盈亏                                |
| FundFrozen：冻结资金                       | RealFrozenMarginB：当日开仓预冻结保证金和费用 | FundFrozen：冻结资金                          |
| OtherFund：其他资金HoldingProfit：盯市盈亏 | FetchFund：可取资金                           | ExerciseMargin：履约保证金                    |
| BuyFund：今买入额                          | TotalFloatProfit                              | RealFrozenMarginA：当日开仓预冻结金额         |
| SellFund：今卖出额                         | InitRightsBalance                             | RealFrozenMarginB：当日开仓预冻结保证金和费用 |
| Remark：说明                               | FloatRightsBal：浮动客户权益                  | HoldingProfit：盯市盈亏                       |
| Customer：客户号                           | RealDrop：盯市平仓盈亏                        | CurrRightsBalance：当前客户权益               |
| AssetAccount：资金账号                     | FrozenFare：冻结费用                          | CustomerMargin：客户保证金                    |
| LogonID：登录ID                            | CustomerMargin：客户保证金                    | Customer：客户号                              |
| ErrorCode：错误码                          | RealOpenProfit：盯市开仓盈亏                  | AssetAccount：资金账号                        |
| --                                         | FloatOpenProfit：浮动开仓盈亏                 | LogonID：登录ID                               |
| --                                         | Interest：预计利息                            | ErrorCode：错误码                             |
| --                                         | Customer：客户号                              | --                                            |
| --                                         | AssetAccount：资金账号                        | --                                            |
| --                                         | LogonID：登录ID                               | --                                            |
| --                                         | ErrorCode：错误码                             | --                                            |
| --                                         | ErrorMsg：错误信息                            | --                                            |

**当qrycode=Position进行股票、期货、期权账号当日委托查询时, ResFields返回值的字段具体说明如下：**

| 股票返回字段                | 期货返回字段                     | 期权返回字段                          |
| :-------------------------- | :------------------------------- | :------------------------------------ |
| SecurityCode：交易品种代码  | SecurityCode：交易品种代码       | SecurityCode：交易品种代码            |
| SecurityName：交易品种名称  | SecurityName：交易品种名称       | SecurityName：交易品种名称            |
| SecurityBalance：股份余额   | CostPrice ：成本价格             | SecurityForzen ：股份冻结             |
| SecurityAvail：股份可用     | LastPrice ：最新价格             | CostPrice ：成本价格                  |
| SecurityForzen：股份冻结    | TradeSide：交易方向              | LastPrice：最新价格                   |
| TodayBuyVolume：当日买入量  | BeginVolume ：期初数量           | TradeSide：交易方向                   |
| TodaySellVolume：当日卖出量 | EnableVolume ：可用数量          | EnableVolume：可用数量                |
| SecurityVolume：当前拥股数  | TodayRealVolume ：当日可平仓数   | TodayOpenVolume ：当日开仓可用数      |
| CallVolume：可申赎数量      | TodayOpenVolume ：当日开仓可用数 | TotalFloatProfit：总浮动盈            |
| CostPrice：成本价格         | HoldingProfit ：盯市盈亏         | RealFrozenMarginA：当日开仓预冻结金额 |
| TradingCost：当前成本       | TotalFloatProfit ：总浮动盈      | MoneyType ：货币类型                  |
| LastPrice：最新价格         | PreMargin ：上交易日保证金       | LogonID：登录ID                       |
| HoldingValue：市值          | MoneyType ：货币类型             | OptionType ：期权类型                 |
| Profit：盈亏                | LogonID:登录ID                   | ErrorCode ：错误码                    |
| MoneyType：货币类型         | ErrorCode:错误码                 | ErrorMsg：错误信息                    |
| LogonID:登录ID              | ErrorMsg：错误信息               | --                                    |
| ErrorCode:错误码            | --                               |                                       |
| ErrorMsg：错误信息          | --                               | --                                    |

**当qrycode=Order进行股票、期货、期权账号当日委托查询时, ResFields返回值的字段具体说明如下：**

| 股票返回字段                  | 期货返回字段                | 期权返回字段                  |
| :---------------------------- | :-------------------------- | :---------------------------- |
| OrderNumber：柜台委托编号     | OrderNumber：柜台委托编号   | OrderNumber：柜台委托编号     |
| OrderStatus：委托状态         | OrderStatus：委托状态       | OrderStatus：委托状态         |
| SecurityCode：交易品种代码    | SecurityCode：交易品种代码  | SecurityCode：交易品种代码    |
| SecurityName：交易品种名称    | SecurityName：交易品种名称  | SecurityName：交易品种名称    |
| TradeSide：交易方向           | TradeSide：交易方向         | TradeSide：交易方向           |
| OrderPrice：委托价格          | OrderPrice：委托价格        | OrderPrice：委托价格          |
| OrderVolume：委托数量         | OrderVolume：委托数量       | OrderVolume：委托数量         |
| OrderTime：委托时间           | OrderTime：委托时间         | OrderTime：委托时间           |
| TradedPrice：成交均价         | TradedPrice：成交均价       | TradedPrice：成交均价         |
| TradedVolume：成交数量        | TradedVolume：成交数量      | TradedVolume：成交数量        |
| CancelVolume：撤单数量        | CancelVolume：撤单数量      | CancelVolume：撤单数量        |
| LastPrice：最新价格           | LastPrice：最新价格         | LastPrice：最新价格           |
| MadeAmt：成交金额             | PreMargin ：开仓冻结保证金  | MadeAmt：成交金额             |
| OrderFrozenFund：委托冻结资金 | TotalFrozenCosts:冻结总费用 | OrderFrozenFund：委托冻结资金 |
| HedgeType：套保标志           | HedgeType：套保标志         | HedgeType：套保标志           |
| MoneyType:货币类型            | Remark：说明                | MoneyType:货币类型            |
| Remark:说明                   | LogonID：登录ID             | Remark:说明                   |
| LogonID：登录ID               | QryPostStr：请求信号        | LogonID：登录ID               |
| QryPostStr：请求信号          | OrderDate：委托日期         | QryPostStr：请求信号          |
| OrderDate：委托日期           | ErrorCode：错误码           | OptionType：期权类型          |
| ErrorCode：错误码             | ErrorMsg：错误信息          | OrderDate：委托日期           |
| ErrorMsg：错误信息            | --                          | ErrorCode：错误码             |
| --                            | --                          | ErrorMsg：错误信息            |

其中：OrderStatus包含Normal(正常)、Cancelled（撤单）、Invalid（无效）、Dealing（处理中）选项

**当qrycode=Trade进行股票、期货、期权账号当日成交查询时, ResFields返回值的字段具体说明如下：**

| 股票返回字段                          | 期货返回字段                                 | 期权返回字段               |
| :------------------------------------ | :------------------------------------------- | :------------------------- |
| OrderNumber：柜台委托编号             | OrderNumber：柜台委托编号                    | OrderNumber：柜台委托编号  |
| TradedNumber：成交编号                | TradedNumber：成交编号TradedNumber：成交编号 |                            |
| TradedStatus：成交状态                | TradedStatus：委托状态                       | TradedStatus：委托状态     |
| SecurityCode：交易品种代码            | SecurityCode：交易品种代码                   | SecurityCode：交易品种代码 |
| SecurityName：交易品种名称            | SecurityName：交易品种名称                   | SecurityName：交易品种名称 |
| TradeSide：交易方向                   | TradeSide：交易方向                          | TradeSide：交易方向        |
| TradedTime：委托价格                  | OrderPrice：委托价格                         | OrderPrice：委托价格       |
| OrderVolume：委托数量                 | OrderVolume：委托数量                        | OrderVolume：委托数量      |
| OrderTime：委托时间                   | OrderTime：委托时间                          | OrderTime：委托时间        |
| TradedTime:交易时间                   | TradedTime:交易时间TradedTime:交易时间       |                            |
| TradedPrice：成交均价                 | TradedPrice：成交均价                        | TradedPrice：成交均价      |
| TradedVolume：成交数量                | TradedVolume：成交数量                       | TradedVolume：成交数量     |
| CancelVolume：撤单数量                | CancelVolume：撤单数量                       | CancelVolume：撤单数量     |
| LastPrice：最新价格                   | LastPrice：最新价格                          | LastPrice：最新价格        |
| MadeAmt：成交金额                     | AmountPerHand ：每手吨数                     | MadeAmt：成交金额          |
| MoneyType:货币类型HedgeType：套保标志 | OrderType:委托类型                           |                            |
| Remark:说明                           | TotalFrozenCosts：冻结总费用                 | MoneyType:货币类型         |
| LogonID：登录ID                       | DropProfit：平仓盈亏                         | Remark:说明                |
| QryPostStr：请求信号                  | DropFloatFrofit：平仓浮动盈亏                | LogonID：登录ID            |
| OrderDate：委托日期                   | Remark:说明                                  | QryPostStr：请求信号       |
| TradedDate：成交日期                  | LogonID：登录ID                              | OptionType：期权类型       |
| ErrorCode：错误码                     | QryPostStr：请求信号                         | OrderDate：委托日期        |
| ErrorMsg：错误信息                    | OrderDate：委托日期                          | TradedDate：成交日期       |
| --                                    | ErrorCode：错误码                            | ErrorCode：错误码          |
| --                                    | ErrorMsg：错误信息                           | ErrorMsg：错误信息         |

其中: TradedStatus包含Normal(正常)、Cancelled（撤单）、Invalid（无效）

**当qrycode=Account进行账号查询时, ResFields返回值的具体说明如下：**

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误码   | 函数返回的错误码。函数如果成功运行，ErrorCode=0。如果返回码等于其他值，可根据错误码查找错误原因 |
| Fields    | 指标列表 | 字段含义如下： ShareholderStatus：股东状态, MainShareholderFlag：主股东标志, AccountType：账号类型, MarketType：市场代码, Shareholder：股东代码, AssetAccount：资金账号, Customer：客户号, Seat：席位号, LogonID：登录ID, ErrorCode：错误码, ErrorMsg：错误信息 |
| Data      | 数据列表 | 返回查到信息                                                 |

**当qrycode=LogonID进行账号查询时, ResFields返回值的具体说明如下：**

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误码   | 函数返回的错误码。函数如果成功运行，ErrorCode=0。如果返回码等于其他值，可根据错误码查找错误原因 |
| Fields    | 指标列表 | 返回的字段信息。字段含义如下： LogonID：登录ID, LogonAccount：登录账号, AccountType：账号类型, ErrorCode：错误码, ErrorMsg：错误信息 |
| Data      | 数据列表 | 返回查到信息                                                 |

### 17.获取组合报表数据函数WPF

**`w.wpf(productname, tablename, options)`**

用来获取资产管理系统PMS以及组合管理系统AMS某一段时间组合的业绩和市场表现的报表数据。

- **参数说明**

| 参数        | 类型 | 可选 | 默认值 | 说明                                                         |
| :---------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| productName | str  | 否   | 无     | 输入组合ID或组合名称, 取自Wind终端PMS或AMS模块.如: "全球投资组合管理演示" |
| tablename   | str  | 否   | 否     | 输入报表的指标名称如: NetHoldingValue、                      |
| options     | str  | 是   | ""     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数        | 类型 | 可选 | 默认值     | 说明                                                         |
| :---------- | :--- | :--- | :--------- | :----------------------------------------------------------- |
| view        | str  | 是   | 否         | 选择组合管理模块：“AMS” 或“PMS”                              |
| Owner       | str  | 是   | 否         | 可选参数, view=PMS且组合是别人共享的时，应给出组合创建人的Wind帐号, 如"Owner=W0817573" |
| date        | str  | 是   | 否         | 选择获取数据中截面指标的日期, 如: "date = 20180302"、        |
| startDate   | str  | 是   | 否         | 选择获取数据中区间指标的起始日期如: "startDate = 20180531"   |
| endDate     | str  | 是   | 否         | 选择获取数据中区间指标的截止日期如: " endDate = 20180731"    |
| Currency    | str  | 是   | "ORIGINAL" | 选择获取数据的货币类型，默认"Currency = ORIGINAL"。参数值含义如下： ORIGINAL：原始货币， HKD：港币， USD：美元， CNY：人民币 |
| sectorcode  | str  | 是   | 否         | 选择组合按资产或总市值进行分类如: "sectorcode=101"           |
| MarketCap   | str  | 是   | 否         | 选择组合按总市值分类, 此时"sectorcode=208"如: " sectorcode=208, MarketCap=1000,500,100,50" |
| displaymode | str  | 是   | 否         | 选择报表展示方式。参数值含义如下： 1：明细， 2：分类， 3：全部 |

**注**：

`wpf`函数支持输出DataFrame数据格式，需要函数添加参数`usedf = True`。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，`.ErrorCode=0`表示代码运行正常。若为其他则需查找错误原因. |
| Codes     | 组合列表 | 返回获取报表的组合名称                                       |
| Field     | 字段列表 | 返回获取报表的字段                                           |
| Times     | 组合列表 | 返回获取报表的本地时间戳                                     |
| Data      | 数据列表 | 返回查询信息的具体值                                         |

### 18.获取组合多维数据函数WPS

**`w.wps(PortfolioName, fields, options)`**

获取资产管理系统PMS以及组合管理系统AMS某一天组合的基本信息、业绩、市场表现和交易统计等方面的截面数据。

- **参数说明**

| 参数          | 类型 | 可选 | 默认值 | 说明                                                         |
| :------------ | :--- | :--- | :----- | :----------------------------------------------------------- |
| PortfolioName | str  | 否   | 无     | 输入组合ID或组合名称, 取自Wind终端PMS或AMS模块.如: "全球投资组合管理演示" |
| fields        | str  | 否   | 否     | 输入报表的指标名称如: NetHoldingValue、                      |
| options       | str  | 是   | ""     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数      | 类型 | 可选 | 默认值     | 说明                                                         |
| :-------- | :--- | :--- | :--------- | :----------------------------------------------------------- |
| view      | str  | 是   | 否         | 选择组合管理模块：“AMS” 或“PMS”                              |
| Owner     | str  | 是   | 否         | 可选参数, view=PMS且组合是别人共享的时，应给出组合创建人的Wind帐号, 如"Owner=W0817573" |
| date      | str  | 是   | 否         | 选择获取数据中截面指标的日期, 如: "date = 20180302"、        |
| startDate | str  | 是   | 否         | 选择获取数据中区间指标的起始日期如: "startDate = 20180531"   |
| endDate   | str  | 是   | 否         | 选择获取数据中区间指标的截止日期如: " endDate = 20180731"    |
| Currency  | str  | 是   | "ORIGINAL" | 选择获取数据的货币类型，默认"Currency = ORIGINAL"。参数值含义如下： ORIGINAL：原始货币， HKD：港币， USD：美元， CNY：人民币 |

**注**：

`wps`函数支持输出DataFrame数据格式，需要函数添加参数`usedf = True`。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Codes     | 组合列表 | 返回获取报表的组合名称                                       |
| Field     | 字段列表 | 返回获取报表的字段                                           |
| Times     | 组合列表 | 返回获取报表的本地时间戳                                     |
| Data      | 数据列表 | 返回查询信息的具体值                                         |

### 19.获取组合序列数据函数WPD

**`w.wpd(PortfolioName, fields, beginTime, endTime, options)`**

获取资产管理系统PMS以及组合管理系统AMS一段时间组合的持仓和业绩表现等日序列数据。

- **参数说明**

| 参数          | 类型   | 可选 | 默认值       | 说明                                                         |
| :------------ | :----- | :--- | :----------- | :----------------------------------------------------------- |
| PortfolioName | String | 否   | 无           | 输入组合ID或组合名称, 取自Wind终端PMS或AMS模块.如: "全球投资组合管理演示" |
| fields        | str    | 否   | 否           | 输入报表的指标名称如: NetHoldingValue                        |
| beginTime     | str    | 是   | endTime      | 输入获取数据的起始日期，为空默认为截止日期如: "2016-01-01"、“20160101”、datetime/date类型 |
| endTime       | str    | 是   | 系统当前时间 | 输入获取数据的截止日期，为空默认为系统当前日期，如: "2016-01-05"、“20160105”、datetime/date类型 |
| options       | str    | 是   | ""           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数     | 类型 | 可选 | 默认值 | 说明                                                         |
| :------- | :--- | :--- | :----- | :----------------------------------------------------------- |
| view     | str  | 是   | 否     | 选择组合管理模块：“AMS” 或“PMS”                              |
| Owner    | str  | 是   | 否     | 选择组合创建人, view=PMS且组合是别人共享的时，应给出组合创建人的Wind帐号，如"Owner=W0817573" |
| Period   | str  | 是   | 'D'    | 取值周期。参数值含义如下： D：天， W：周， M：月， Q：季度， S：半年， Y：年 |
| Fill     | str  | 是   | 否     | 空值填充方式。参数值含义如下： Previous：沿用前值， Blank：返回空值。 如需选择自设数值填充，在`options`添加“ShowBlank=X", 其中X为自设数。 |
| Currency | str  | 是   | ""     | 选择获取数据的货币类型，默认"Currency = ORIGINAL"。参数值含义如下： ORIGINAL：原始货币， HKD：港币， USD：美元， CNY：人民币 |

**注**：

`wpd`函数支持输出DataFrame数据格式，需要函数添加参数`usedf = True`。

- **返回说明**

如果不指定`usedf=True`，该函数将返回一个WindData对象，包含以下成员：

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Codes     | 组合列表 | 返回获取报表的组合名称                                       |
| Field     | 字段列表 | 返回获取报表的字段                                           |
| Times     | 组合列表 | 返回获取报表的本地时间戳                                     |
| Data      | 数据列表 | 返回查询信息的具体值                                         |

### 20.组合上传函数WUPF

在终端组合管理系统中新建组合后, 根据量化策略可以点击‘调整持仓’或‘导入持仓’按钮手动调整组合持仓. 为了实现程序化调仓和回测的执行, 量化平台提供了WUPF函数对组合进行调仓. 下面就介绍利用WUPF函数对组合管理系统中的组合进行程序化调仓的实现, 注意在组合调仓前需要在组合管理系统中新建组合. 在‘资管WPF’下, 点击‘组合上传(WUPF)’按钮，进入组合上传页面.

![组合上传方式](https://wx.wind.com.cn/ApiHelpCenter/ApiHelpCenterWeb/WindFiles/images/20231107/1b1ca6e7-d0e7-4af0-9479-1c23c162f628.png)这里Wind账号默认为终端账号，选择终端已存在组合的名称后, 下面可以看到三种组合上传方式, 依次为‘持仓上传’，‘权重上传’和‘流水上传’, 按导航就能生成组合上传所需的代码。

**`wupf(PortfolioName, TradeDate, WindCode, Quantity, CostPrice, options)`**

- **参数说明**

| 参数          | 类型 | 可选 | 默认值 | 说明                                                         |
| :------------ | :--- | :--- | :----- | :----------------------------------------------------------- |
| PortfolioName | str  | 否   | 无     | 输入组合ID或组合名称, 取自Wind终端PMS模块.如: "全球投资组合管理演示" |
| TradeDate     | str  | 否   | 否     | 输入调整持仓的日期.如: "20151231"                            |
| WindCode      | str  | 否   | 否     | 输入调整持仓的品种, 当上传多个持仓的时候可以输入数组.现金视为一种证券，现金数量为其金额，价格为1，目前仅支持上传一笔现金。如: "600000.SH, 000001.SZ ,CNY " |
| Quantity      | str  | 否   | 否     | 输入调整品种的持仓数量, 当上传多个持仓的时候可以输入数组. 股票为股，期货为手，现金为其数额，必须为整数, 当卖出时可为负数，如: "100, 100, 10000" |
| CostPrice     | str  | 是   | 否     | 输入调整持仓的成本价格(含佣金等交易费用)，默认为证券调仓日收盘价，现金价格为指定1.如: "10.17,10.19,1" |
| options       | str  | 是   | ""     | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数          | 类型 | 可选 | 默认值   | 说明                                                         |
| :------------ | :--- | :--- | :------- | :----------------------------------------------------------- |
| Owner         | str  | 是   | 否       | 输入组合拥有者的Wind用户账号，默认为当前账户, 当组合是别人共享的，则填入组合创建人的Wind帐号例："Owner=W0817573" |
| Direction     | str  | 是   | "Long"   | 输入调仓品种的多空方向，对期货品种有效。默认"Direction=Long"。参数值含义如下： Long：多方 Short：空方 |
| HedgeType     | str  | 是   | "Spec"   | 选择投机套保类型，可选参数。默认为"HedgeType=Spec", 选择套保需要专门的保账号。HedgeType可取值如下： Spec：投机 Hedge：套保 |
| CreditTrading | str  | 是   | 否       | 输入是否调仓品种是否为融资融券交易例: CreditTrading=No,No,No |
| TotalAsset    | str  | 是   | 10000000 | 总资产                                                       |
| Method        | str  | 是   | 否       | 输入调仓品种的调仓方式。参数值含义如下： BuySell：买卖调仓(会增减现金)， InOut：划入划出调仓(不会增减现金) |
| AssetType     | str  | 是   | 否       | 选择证券类型，AssetType可取为： Margin: 融资融券， Cash: 现金， Equity: 股票， Bond: 债券， Repo: 债券回购， Fund: 基金， Cmdty: 期货， SFP: 券商理财产品， Trust: 信托产品， BFP: 银行理财产品, Pfund: 阳光私募  后台可以自动自动解析资产类别，因此除融资融券字段外，无需设置相应类别。一旦在此设置，后台不做类别错误检查。 |
| type          | str  | 是   | 持仓上传 | 输入调整持仓的上传方式。默认为持仓上传。参数值含义如下： “flow"：流水上传， ”weight“：权重上传。 |

- **返回说明**

| 返回码    | 解释     | 说明                                                         |
| :-------- | :------- | :----------------------------------------------------------- |
| ErrorCode | 错误ID   | 返回代码运行错误码，.ErrorCode =0表示代码运行正常。若为其他则需查找错误原因. |
| Field     | 字段列表 | 返回上传调仓的返回字段, .Fields=[ErrorMessage]               |
| Data      | 数据列表 | 错误信息。如果上传调仓成功，返回`.Data=[[OK]]`               |

#### 流水上传

在该模式下，你可以调整组合中的现金配置或者调整仓位。

1. 调整现金：通过调整现金可以增减组合中的现金数额, 数额为正即增加组合现金, 为负即减少组合现金. 此外还可以选择相应币种类型.
2. 调整持仓 ：调整持仓分两种情况：买卖调仓和资产划转，其中买卖调仓会扣减或增加现金，而资产划转不会。

当证券买入时，‘买卖数量’记为正；当证券卖出时，‘买卖数量’记负，其与‘信用交易’和‘交易类型’的关系如下表：

| 买卖数量 | 信用交易 | 买卖类型                                                     |
| :------- | :------- | :----------------------------------------------------------- |
| 正       | 否       | 证券买入/买入多单-long/买入空单-short/正回购-short/逆回购-long |
| 负       | 否       | 证券卖出/卖出空单-short/卖出多单-long                        |
| 正       | 是       | 融资买入-long/买券还券-short                                 |
| 负       | 是       | 卖券还款-long/融券卖出-short                                 |

这里要注意只有股票的融资融券交易才是有实际意义的.

#### 权重上传

权重上传是在当前总资产下,按一定权重将持仓日组合的所有持仓上传,每次上传的持仓即视为当前组合的最新持仓，最小调仓单位为1股或1手。

**注：**

1. 初次权重上传之前组合为空，上传组合持仓时，如果不上传总资产，则总资产默认为10000000，反之则以上传的总资产为准；
2. 再次权重上传之前组合不为空，上传组合持仓时，不用调整总资产；

对于权重上传，持仓权重和信用交易的关系的含义情况如下

| 持仓权重 | 信用交易 | 含义                 |
| :------- | :------- | :------------------- |
| 正       | 否       | 证券买入/逆回购/多开 |
| 负       | 否       | 正回购/空开          |
| 正       | 是       | 融资买入             |
| 负       | 是       | 融券卖出             |

#### 持仓上传

持仓上传是将调仓日组合的所有持仓情况上传, 包括现金持仓. 持仓截面的每次上传即视为当前组合的最新持仓，持仓上传对历史持仓没有记忆性。持仓上传分调整持仓和调整现金两种：

1. 调整现金：通过调整现金可以确定调仓日组合的现金持仓情况金， 并可以选择相应币种类型；
2. 调整持仓：调整持仓是将调仓日组合的持仓情况上传。

**注: **

1. 通过调整现金可以确定调仓日组合的现金持仓情况金. 并可以选择相应币种类型;
2. 可选参数也可以用list实现；
3. 如果调仓的品种对应是同一天，则日期参数可以只保留一个，同样调仓方向相同也可以只保留一个。

其中，持仓数量和信用交易的关系的含义情况如下

| 持仓数量 | 信用交易 | 含义                 |
| :------- | :------- | :------------------- |
| 正       | 否       | 证券买入/逆回购/多开 |
| 负       | 否       | 正回购/空开          |
| 正       | 是       | 融资买入             |
| 负       | 是       | 融券卖出             |

#### 重置组合

如果需要将组合中的持仓信息和资金信息全部清空，可按照如下方式设置`w.wupf`:

**`w.wupf(portfolioName, "", "", "", "reset=true")`**

### 21.获取区间内日期序列tdays

**`w.tdays(beginTime , endTime, options)`**

用来获取一个时间区间内的某种规则下的日期序列。

- **参数说明**

| 参数      | 类型 | 可选 | 默认值       | 说明                                                         |
| :-------- | :--- | :--- | :----------- | :----------------------------------------------------------- |
| beginTime | str  | 是   | endTime      | 时间序列的起始日期，支持日期宏                               |
| endTime   | str  | 是   | 系统当前时间 | 时间序列的结束日期，支持日期宏                               |
| options   | str  | 是   | ”“           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数            | 类型 | 可选 | 默认值    | 说明                                                         |
| :-------------- | :--- | :--- | :-------- | :----------------------------------------------------------- |
| Days            | str  | 是   | 'Trading' | 日期选项。参数值含义如下： Weekdays: 工作日， Alldays：日历日， Trading：交易日 |
| Period          | str  | 是   | 'D'       | 取值周期。参数值含义如下： D：天， W：周， M：月， Q：季度， S：半年， Y：年 |
| TradingCalendar | str  | 是   | 'SSE'     | 选择不同交易所的交易日历，默认'SSE'上交所                    |

- **示例说明**

```python
# 取上交所2018年5月13日至6月13日的交易日期序列，交易所为空默认为上交所
date_list=w.tdays("2018-05-13", "2018-06-13"," ")
date_list
```

### 22.获取某一偏移值对应的日期tdaysoffset

**`w.tdaysOffset(offset, beginTime, options)`**

用于将基准日期前推若干周期得到符合选定日期类型的日期

- **参数说明**

| 参数      | 类型 | 可选 | 默认值       | 说明                                                         |
| :-------- | :--- | :--- | :----------- | :----------------------------------------------------------- |
| offset    | int  | 否   | 否           | 偏移参数，>0后推，<0前推                                     |
| beginTime | str  | 是   | 系统当前时间 | 参照日期，支持日期宏                                         |
| options   | str  | 是   | ""           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数            | 类型 | 可选 | 默认值    | 说明                                                         |
| :-------------- | :--- | :--- | :-------- | :----------------------------------------------------------- |
| Days            | str  | 是   | 'Trading' | 日期选项。参数含义如下： Weekdays: 工作日 Alldays：日历日 Trading：交易日 |
| Period          | str  | 是   | 'D'       | 取值周期。参数值含义如下： D：天， W：周， M：月， Q：季度， S：半年， Y：年 |
| TradingCalendar | str  | 是   | 'SSE'     | 选择不同交易所的交易日历，默认'SSE'上交所                    |

- **示例说明**

```python
# 取从今天往前推10个月的日历日
import datetime
today = datetime.date.today() 
w.tdaysoffset(-10, today.isoformat(), "Period=M;Days=Alldays")
```

### 23. 获取某个区间内日期数量tdayscount

#### **`w.tdayscount(beginTime, endTime, options)`**

命令返回某个日期区间内指定日期类型日期的总数。

- **参数说明**

| 参数      | 类型 | 可选 | 默认值       | 说明                                                         |
| :-------- | :--- | :--- | :----------- | :----------------------------------------------------------- |
| beginTime | str  | 是   | endTime      | 时间序列的起始日期，支持日期宏                               |
| endTime   | str  | 是   | 系统当前时间 | 时间序列的结束日期，支持日期宏                               |
| options   | str  | 是   | ""           | `options`以字符串的形式集成多个参数，具体见代码生成器。如无相关参数设置，可以不给option赋值或者使用`options=""` |

- **集成在`options`中的参数**

`options`以字符串的形式集成了多个参数。以下列举了一些常用的参数：

| 参数            | 类型 | 可选 | 默认值    | 说明                                                         |
| :-------------- | :--- | :--- | :-------- | :----------------------------------------------------------- |
| Days            | str  | 是   | 'Trading' | 日期选项。参数值含义如下： Weekdays: 工作日， Alldays：日历日， Trading：交易日 |
| TradingCalendar | str  | 是   | 'SSE'     | 选择不同交易所的交易日历，默认'SSE'上交所                    |

- **示例说明**

```python
# 统计2018年交易日天数
days=w.tdayscount("2018-01-01", "2018-12-31", "").Data[0]
days
```

### 24. 日期宏说明

#### 通用日期宏

支持相对日期表达方式，相对日期周期包括:交易日TD、日历日：D、日历周：W、日历月：M、日历季：Q、日历半年：S、日历年：Y。

**相关说明**

1. 以’-’代表前推，数字代表N个周期，只支持整数；后推没有负号，比如’-5D’表示从当前最新日期前推5个日历日；
2. 截止日期若为’’空值，取系统当前日期；
3. 可对日期宏进行加减运算，比如’ED-10d’。

**举例：**

1. 起始日期为1个月前，截至日期为最新 StartDate=’-1M’,EndDate=’’
2. 起始日期为前推10个交易日，截至日期为前推5个交易日 StartDate=’-10TD’,EndDate=’-5TD’

#### 特殊日期宏

| 宏名称   | 助记符 | 宏名称   | 助记符 | 宏名称   | 助记符 |
| :------- | :----- | :------- | :----- | :------- | :----- |
| 截止日期 | ED     | 今年一季 | RQ1    | 本月初   | RMF    |
| 开始日期 | SD     | 今年二季 | RQ2    | 本周一   | RWF    |
| 去年一季 | LQ1    | 今年三季 | RQ3    | 上周末   | LWE    |
| 去年二季 | LQ2    | 最新一期 | MRQ    | 上月末   | LME    |
| 去年三季 | LQ3    | 本年初   | RYF    | 上半年末 | LHYE   |
| 去年年报 | LYR    | 下半年初 | RHYF   | 上年末   | LYE    |
| 上市首日 | IPO    | --       | --     | --       | --     |

```python
# 用日期宏IPO的示例，获取股票600039.SH上市首日至20180611的收盘价
error_code,data=w.wsd("600039.SH", "close", 'IPO', "2018-06-11", usedf=True)
data.head()
# 用日期宏本月初的示例，获取000001.SZ本月初至20180611的收盘价
from datetime import datetime
td = datetime.today().strftime("%Y%m%d")
error_code,data=w.wsd("600039.SH", "close", 'RMF', td, usedf=True)
data
```