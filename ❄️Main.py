import streamlit as st
import pandas as pd
import numpy as np
import snowflake.connector
import json
import plotly.express as px
import sys
sys.path.insert(0, '/')
import mycode
import datetime
st.set_page_config(layout="wide")


# MAIN BODY 
parems = st.experimental_get_query_params()
port_id = parems['port'][0]
st.title( port_id )
st.session_state['line_offset'] = 0

# CONNECT TO SNOWFLAKE  
conn = snowflake.connector.connect( user= st.secrets["user"],
                                    password= st.secrets["password"],
                                    account= st.secrets["account"],
                                    role = st.secrets["role"],
                                    warehouse = st.secrets["warehouse"],
                                    session_parameters={
                                        'QUERY_TAG': 'Streamlit',
                                    })

# function to run queries on Snowflake
def run_query(query): 
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()



# get last 2 days of open market
mx_date = run_query("select distinct price_date from STOCKFEED.META.ALL_PRICE_DATE ORDER BY PRICE_DATE DESC limit 2")

start_date = st.empty()
end_date = st.empty()

with st.sidebar:
    with st.expander("Create New Portfolio", expanded=False):
        with st.form(key='create_port_form', clear_on_submit=True):
            new_port = st.text_input('', placeholder='Portfolio ID')
            add_port_btn = st.form_submit_button(label='Create')

            if add_port_btn:
                run_query( f"""insert into str_app.usrdata.assets values('{new_port}', 'SNOW')""" )
                st.experimental_set_query_params(port=new_port)


    with st.form(key='add_asset_form', clear_on_submit=True):
        ticker = st.text_input('Add Ticker(s)', placeholder='Ticker')
        add_ticker_btn = st.form_submit_button(label='Add')

        if add_ticker_btn:
            run_query( f"""insert into str_app.usrdata.assets values('{port_id}', '{ticker}')""" )
    
    if 'start_date' not in st.session_state:
        start_date = st.date_input("Start Date", datetime.date(mx_date[1][0].year, mx_date[1][0].month, mx_date[1][0].day))
    else:
        start_date = st.date_input("Start Date", st.session_state['start_date'])

    if 'end_date' not in st.session_state:
        end_date = st.date_input("End Date", datetime.date(mx_date[0][0].year, mx_date[0][0].month, mx_date[0][0].day))
    else:
        end_date = st.date_input("End Date", st.session_state['end_date'] )

    if start_date:
        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date

    if end_date:
        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date

# Get all assets in specific port ID
assets = run_query(f"select distinct TICKER from str_app.usrdata.assets where id='{port_id}';")
query_portfolio = []

for qp in assets:
    query_portfolio.append(qp[0])


asset_str = ', '.join(f"'{w}'" for w in query_portfolio) #the list that is charted on the page (array of stocks/assets)






    




import pandas as pd
# table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
# port_list = ['SNOW','MSFT','AMZN','QQQ','SPY']#table[0].Symbol.to_numpy()
# port_list = table[0].Symbol.to_numpy()


asset_list = run_query( f""" select TICKER from str_app.usrdata.assets where id='{port_id}'; """ )
sp_str = ', '.join(f"'{ w[0].upper() }'" for w in asset_list)


st.write( f"""Between {start_date} and {end_date}""" )


# GET MOST CURRENT PRICE DATE

ticker_current = run_query(
    f"""
    select distinct t.TICKER, PRICE_DATE, PRICE, trade_count, volume
    from "STOCKFEED"."META"."ALL_PRICE_DATE"
        t inner join str_app.usrdata.assets a on t.TICKER = UPPER(a.TICKER) 
    where a.id = '{port_id}'
    and price_date = '{end_date}'
    order by 1
    """
)


# get previous compare price from assets
ticker_prev = run_query(
    f"""
    select distinct t.TICKER, PRICE_DATE, PRICE, trade_count, volume
    from "STOCKFEED"."META"."ALL_PRICE_DATE"
        t inner join str_app.usrdata.assets a on t.TICKER = UPPER(a.TICKER) 
    where a.id = '{port_id}'
    and price_date = '{start_date}'
    order by 1
    """
)

ticker_hist = run_query(
    f"""
        select distinct object_construct('t',t.ticker,
            'p',array_agg(price::number(38,4) ) within group (order by price_date asc)
        ) as data

        from "STOCKFEED"."META"."ALL_PRICE_DATE"
            t inner join str_app.usrdata.assets a on t.TICKER = UPPER(a.TICKER) 
            and price_date between '{start_date}' and '{end_date}'
        where a.id = '{port_id}'
        group by t.ticker
    """
)



tickers = []
deltas = []
sectors =[]
market_caps = []
vol = []
market_advance = [ ['-5%', 0], ['-3%', 0], ['-1%', 0], ['0%', 0], ['1%', 0], ['3%', 0], ['5%', 0] ]

for index, tckr in enumerate(ticker_current):
    tickers.append( ticker_current[index][0] )
    d = (ticker_current[index][2] - ticker_prev[index][2]) / ticker_current[index][2]
    deltas.append( (ticker_current[index][2] - ticker_prev[index][2]) / ticker_current[index][2]  )


    market_caps.append(1)
    if(d < -.05):
        market_advance[0][1] = market_advance[0][1] + 1
    if(d >= -.05 and d < -.03):
        market_advance[1][1] = market_advance[1][1] + 1
    if(d >= -.03 and d < -.01):
        market_advance[2][1] = market_advance[2][1] + 1
    if(d >= -.01 and d < 0.01):
        market_advance[3][1] = market_advance[3][1] + 1
    if(d >= 0.01 and d <= .03):
        market_advance[4][1] = market_advance[4][1] + 1
    if(d >= .03 and d <= .05):
        market_advance[5][1] = market_advance[5][1] + 1
    if(d > .05):
        market_advance[6][1] = market_advance[6][1] + 1



metrics = st.columns(5)
metrics[0].metric("Asset Count", len(ticker_hist))
metrics[1].metric("Avg Performance", "0")
metrics[2].metric("Expense Ratio", ".04%")
metrics[3].metric("Advancing", market_advance[0][1] + market_advance[1][1] + market_advance[2][1]  )
metrics[4].metric("Declining", market_advance[4][1] + market_advance[5][1] + market_advance[6][1] )



# top 3 columns at the start of the page
c1, c2, c3 = st.columns(3)
with c1:
    st.header('Advance / Decline')
    st.write('Assets bucketed based on which stocks price increased or decreased withen timeframe.')
    st.plotly_chart(mycode.make_adv_dec_bar(data=market_advance), use_container_width=True, config={'staticPlot': True})

with c2:
    st.header('USA CPI Index')
    st.write('United States Consumer Price Index (Inflation) numbers.')
    cpi = [ ['Jul', 0.0], ['Aug', 0.2], ['Sep', 0.4], ['Oct', 0.5], ['Nov', 0.2], ['Dec', 0.1], ['Jan', 0.5], ['Feb', 0.4] ]
    st.plotly_chart(mycode.make_cpi(data=cpi), use_container_width=True, config={'staticPlot': True})

with c3:
    st.header('Industry Split')
    st.write('Portfolio split by industry.')
    industry = run_query(
    f"""
        select FS_RBIC_ECONOMY, count(*) as CNT
        from STOCKFEED.META.TICK_INDUSTRY ind 
            inner join str_app.usrdata.assets a on lower(ind.ticker) = lower(a.ticker)
        where lower(a.id) = lower('{port_id}')
        GROUP BY 1
    """)
    df = st.dataframe(industry)




with st.expander("Asset Performance -", expanded=True):
    rc1, rc2, rc3 = st.columns(3)
    offset = 0
    num_charts = 40
    num_columns = 10

    st.markdown("""
        <style>
            .little-font {
                font-size:13px !important;
                padding:0px;
                margin:0px;
            }
            .med-font {
                font-size:18px !important;
                padding:0px;
                margin:0px;
            }
        </style>
        """, unsafe_allow_html=True)    

    for index, tckr in enumerate(ticker_hist):
        i = index + ( st.session_state['line_offset'] ) 

        if (index % num_columns) == 0 :
            cols = st.columns(num_columns)

        y =json.loads(ticker_hist[i][0])

        str_price = y["p"][0]
        end_price = y["p"][ len(y["p"])-1 ]

        trend = "❇️" if (end_price - str_price)>=0 else "🔻"

        cols[ index % num_columns ].subheader(f'{trend}{y["t"]}')
        cols[ index % num_columns ].markdown(f'<p class="med-font">{round((((end_price-str_price)/str_price)*100),2) }%</p><p class="little-font">${str_price} - ${end_price}</p>', unsafe_allow_html=True)
        # plot sparkline
        cols[ index % num_columns ].plotly_chart(mycode.make_price_sparks( y["p"] ), use_container_width = False, config = {'staticPlot': True} )

















