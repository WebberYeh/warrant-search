import requests
import pandas as pd
import sys
import numpy as np
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from IPython.display import display
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

class warrant():
	def select_warrtype(self):
		warr_type = widgets.ToggleButtons(
		    options={'認購':1, '認售':2},
		    #value='1',
		    description='類型:',
		    disabled=False,
		    button_style='', # 'success', 'info', 'warning', 'danger' or ''
		    )
		return(warr_type)

	def select_STOCKID(self):
		STOCK_ID = widgets.Combobox(
		    placeholder='Select or Insert a Stock',
		    options=self.getSTOCKID(),  #dtype: tuple
		    description='選擇標的:',
		    ensure_option=True,
		    disabled=False
		)
		return(STOCK_ID)

	def getSTOCKID(self):
		df = pd.DataFrame(pd.read_csv("上市權證標的.csv"),columns=["index","標的代碼","公司名稱"])
		df2 = pd.DataFrame(pd.read_csv("上櫃權證標的.csv"),columns=["index","標的代碼","公司名稱"])
		df['標的'] = df['標的代碼'].map(str) + " " + df['公司名稱'].map(str)
		df2['標的'] = df2['標的代碼'].map(str) + " " + df2['公司名稱'].map(str)
		df = df.drop(["index","標的代碼","公司名稱"], axis=1)
		df2 = df2.drop(["index","標的代碼","公司名稱"], axis=1)

		twt = pd.DataFrame(['$TWT台股指'], columns=["標的"])
		dfa = pd.concat([twt,df,df2], axis=0)

		dfs = dfa.sort_values(by=['標的'])
		dfs.index = range(len(dfs))
		arr = np.array(dfs["標的"])
		ALL_STOCK = tuple(arr)
		return ALL_STOCK

	def set_detail(self):
		tag1 = widgets.BoundedFloatText(
		    value=-20,
		    min=-100.0,
		    max=100.0,
		    step=0.1,
		    description='高於:',
		    disabled=False
		    )
		tag2 = widgets.BoundedFloatText(
		    value=3,
		    min=0,
		    max=100.0,
		    step=0.1,
		    description='高於:',
		    disabled=False
		    )
		tag3 = widgets.BoundedIntText(
		    value=30,
		    min=0,
		    max=365,
		    step=1,
		    description='大於:',
		    disabled=False
		    )
		tag4 = widgets.BoundedIntText(
		    value=90,
		    min=0,
		    max=100,
		    step=1,
		    description='低於:',
		    disabled=False
		    )
		tags = [tag1, tag2, tag3, tag4]
		tab = widgets.Tab()
		tab.children = tags
		tab.set_title(0, "價內外(價外負值)")  #tag1
		tab.set_title(1, "實質槓桿(絕對值)")  #tag2
		tab.set_title(2, "剩餘天數")          #tag3
		tab.set_title(3, "流通在外比例")      #tag4
		return tab,tag1,tag2,tag3,tag4

	def select_WARRANTID(self, Warrant_List):
		WARRANT_ID = widgets.Combobox(
	        placeholder='Select or Insert WarrantID',
	        options=Warrant_List, #dtype: tuple
	        description='選擇權證:',
	        ensure_option=True,
	        disabled=False
	        )
		return(WARRANT_ID)

	def search_warrant(self, warr_type, STOCK_ID):

		url = "https://www.warrantwin.com.tw/eyuanta/ws/GetWarData.ashx"

		datastr = '{"format":"JSON","factor":{"columns":["FLD_WAR_ID","FLD_WAR_NM","FLD_WAR_TYPE","FLD_UND_ID","FLD_UND_NM","FLD_OBJ_TXN_PRICE","FLD_OBJ_UP_DN","FLD_OBJ_UP_DN_RATE","FLD_WAR_UP_DN","FLD_WAR_UP_DN_RATE","FLD_WAR_TXN_PRICE","FLD_WAR_TXN_VOLUME","FLD_WAR_TTL_VOLUME","FLD_WAR_TTL_VALUE","FLD_WAR_BUY_PRICE","FLD_WAR_BUY_VOLUME","FLD_WAR_SELL_PRICE","FLD_WAR_SELL_VOLUME","FLD_DUR_START","FLD_LAST_TXN","FLD_DUR_END","FLD_OPTION_TYPE","FLD_N_ISSUE_UNIT","FLD_OUT_TOT_BAL_VOL","FLD_OUT_VOL_RATE","FLD_N_STRIKE_PRC","FLD_N_UND_CONVER","FLD_CHECK_PRC","FLD_PERIOD","FLD_IV_CLOSE_PRICE","FLD_IV_BUY_PRICE","FLD_IV_SELL_PRICE","FLD_DELTA","FLD_THETA","FLD_IN_OUT","FLD_LEVERAGE","FLD_BUY_SELL_RATE","FLD_N_LIMIT_PRC","FLD_FIN_EXP","FLD_FIN_EXP_RATIO","FLD_PFR","FLD_PFR_PCT"],"condition":[{"field":"FLD_UND_ID","values":["%s"]},{"field":"FLD_WAR_TYPE","values":["%s"]}],"orderby":{"field":"FLD_WAR_ID","sort":"ASC"}},"callback":12}' % (STOCK_ID, warr_type)
		post_data = {'data': datastr}

		hs = {
		    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
		}

		res = requests.post(url, data=post_data, headers=hs)

		df = pd.DataFrame(res.json()["result"])
		df.columns = ['權證代碼','權證名稱','權證種類','FLD_UND_ID','FLD_UND_NM','標的收盤價','標的漲跌價錢','標的漲跌%','權證漲跌價錢','權證漲跌幅',
		              '成交價','成交量','FLD_WAR_TTL_VOLUME','成交金額','買價','買量','賣價','賣量','上市日','最後交易日','到期日',
		              '型態','發行張數','流通在外張數','流通比','履約價','行使比例','FLD_CHECK_PRC','剩餘天數','成交隱波','買隱波',
		              '賣隱波','DELTA','THETA','價內外','實質槓桿','買賣價差比','FLD_N_LIMIT_PRC','FLD_FIN_EXP','FLD_FIN_EXP_RATIO',
		              'FLD_PFR','FLD_PFR_PCT']
		
		df = df.drop(columns=['權證種類','FLD_UND_ID','FLD_UND_NM','FLD_WAR_TTL_VOLUME','成交金額','FLD_CHECK_PRC',
		                      'FLD_N_LIMIT_PRC','FLD_FIN_EXP','FLD_FIN_EXP_RATIO','FLD_PFR','FLD_PFR_PCT'])

		#replace value from e.g. (1. 10%價內 to 10; 2. 10%價外 to -10; 3. 0.0%價平 to 0)
		df.loc[df["價內外"].str.split("%").str[1] =="價外" ,'價內外']= "-"+(df["價內外"].str.split("%").str[0])
		df.loc[df["價內外"].str.split("%").str[1] =="價內" ,'價內外']= (df["價內外"].str.split("%").str[0])
		df.loc[df["價內外"].str.split("%").str[1] =="價平" ,'價內外']= (df["價內外"].str.split("%").str[0])

		#rearrange column
		df_rearrange = df[['權證代碼', '權證名稱', '履約價', '價內外', '剩餘天數', '實質槓桿', '買隱波', '流通比', '成交價',
                   '買量', '買價', '賣價', '賣量', '成交量', '上市日', 
                   '最後交易日', '到期日', '型態', '發行張數', '流通在外張數', 
                   '行使比例', 'DELTA','THETA', '買賣價差比', '成交隱波', '賣隱波', 
                   '標的收盤價', '標的漲跌價錢', '標的漲跌%', '權證漲跌價錢', '權證漲跌幅']]

        #replace 市價 to -99.99 (doesn't have 5 ticks data to replace) and raplace "blank string" to nan as float
		df_rearrange = df_rearrange.replace('市價', -99.99, regex=True)
		df_rearrange = df_rearrange.replace(r'^\s*$', np.nan, regex=True)

		df_rearrange = df_rearrange.astype({"履約價": float, "價內外": float, "剩餘天數": int, "實質槓桿": float, "買隱波": float, 
                                    "流通比": float, "買量": float, "買價": float, "賣價": float, "賣量": float, "成交量": float, 
                                    "行使比例": float, "DELTA": float, "THETA": float, "買賣價差比": float, "成交隱波": float, 
                                    "賣隱波": float, "標的收盤價": float, "標的漲跌價錢": float, "標的漲跌%": float, 
                                    "權證漲跌價錢": float, "權證漲跌幅": float})


		#df_rearrange.to_csv("%s-%s.csv" % (STOCK_ID,warr_type), encoding = "utf_8_sig", float_format="%.2f", index=False)
		return df_rearrange


	def show_fiveticks(self, WARRANT_ID):
		
		url = "https://www.warrantwin.com.tw/eyuanta/ws/Quote.ashx?type=mem_ta5&symbol=%s" %WARRANT_ID

		hs = {
		    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
		}

		res = requests.get(url, headers=hs)
		res.json()["items"]
		df = pd.DataFrame(list(res.json()["items"].items()), columns=["d","value"])

		#webpage data saved in dict which (101~110 as 5 ticks price, 113~122 as volume, and 129 as flat price)
		dff = df[(df["d"].astype(float) <= 122) | (df["d"].astype(float) == 129)]
		dff

		#might have no 101~122 if not all 5 ticks for buy/sell exist 
		for index in range(101,111):
		    dfmissing = pd.DataFrame({'d': [index], 'value': [0.0]})
		#    dff = dff.append({'d': index, 'value': 0.0},  ignore_index=True) if dff[dff["d"] == str(index)].empty else dff
		    dff = pd.concat([dff,dfmissing], axis=0) if dff[dff["d"] == str(index)].empty else dff  #use concat to replace append

		for index in range(113,123):
		    dfmissing = pd.DataFrame({'d': [index], 'value': [0.0]})
		#    dff = dff.append({'d': index, 'value': 0.0},  ignore_index=True) if dff[dff["d"] == str(index)].empty else dff
		    dff = pd.concat([dff,dfmissing], axis=0) if dff[dff["d"] == str(index)].empty else dff  #use concat to replace append

		dff = dff.astype(float)
		dfs = dff.sort_values(by=['d'])
		dfs.index = range(len(dfs))

		#create a new dataframe to assign value to represent columns
		buyprice = [dfs.loc[0]["value"],dfs.loc[2]["value"],dfs.loc[4]["value"],dfs.loc[6]["value"],dfs.loc[8]["value"]]
		sellprice = [dfs.loc[1]["value"],dfs.loc[3]["value"],dfs.loc[5]["value"],dfs.loc[7]["value"],dfs.loc[9]["value"]]
		buyamount = [dfs.loc[10]["value"],dfs.loc[12]["value"],dfs.loc[14]["value"],dfs.loc[16]["value"],dfs.loc[18]["value"]]
		sellamount = [dfs.loc[11]["value"],dfs.loc[13]["value"],dfs.loc[15]["value"],dfs.loc[17]["value"],dfs.loc[19]["value"]]
		df_fivetick = pd.DataFrame({'買量':pd.Series(buyamount, dtype='int'), '買價':pd.Series(buyprice, dtype='float'),
		                           '賣價':pd.Series(sellprice, dtype='float'), '賣量':pd.Series(sellamount, dtype='int')})

		#replace 0 to nan and replace (-999999999.00 which means 市價 to 買價[1] or 賣價[1])
		df_fivetick = df_fivetick.replace({'0':np.nan, 0:np.nan})
		df_fivetick = df_fivetick.replace(-999999999.00,((df_fivetick["賣價"].loc[1]) if (df_fivetick["賣價"].loc[0]) == -999999999.00 else (df_fivetick["買價"].loc[1])), regex=True)

		#display float values to only 2 decimal places
		f = dict.fromkeys(df_fivetick.select_dtypes('float').columns, "{:.2f}")

		#color buy/sell price value to (red if >flat price; green if <flat price; black if =flat price; and color background to green if =0.01)
		df_fivetick_color = df_fivetick.style.applymap(lambda x: 'color : red' if x>dfs.loc[20]["value"] else ('color : green' if x<dfs.loc[20]["value"] else ('background-color : green; color : white' if x==0.01 else 'color : black')), subset = pd.IndexSlice[:, ['買價', '賣價']]).format(f).hide(axis='index')
		return(df_fivetick_color)


	def history_biv(self, WARRANT_ID):

		url = "https://www.warrantwin.com.tw/eyuanta/ws/GetWarHistory.ashx?type=iv&symbol=%s" %WARRANT_ID

		hs = {
		    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
		}
		res = requests.get(url, headers=hs)
		df = pd.DataFrame(res.json()["result"])
		dff = df[["Date", "BIV"]]
		dff.columns = ["日期", "買隱波"]

		dff = dff.astype({"買隱波": float}) 
		plt.plot(dff['日期'], dff['買隱波'])
		plt.xlabel("Date")
		plt.ylabel("Buy IV")
		plt.title("History BIV of %s" % WARRANT_ID)
		plt.gca().axes.xaxis.set_ticklabels([])
		plt.rcParams['figure.figsize'] = [12, 5]
		plt.locator_params(axis='y', nbins=20)
		plt.grid(axis="y")
		return(plt.show())


