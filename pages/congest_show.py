
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import xml.etree.ElementTree as ET
import sqldata as sqldata
import datetime

# 기본설정 - 한글폰트
#print(plt.rcParams['font.family'])
plt.rcParams['font.family'] = "Malgun Gothic"
plt.rcParams['axes.unicode_minus'] = False
# 기본설정 - 디자인
# css_file = "style.css"

predict_df = sqldata.sql_predict()
# st.dataframe(predict_df)
forecast_df = sqldata.sql_forecast()

# 1. 모델 - *2주간의 예측 바+선그래프
# 2. 모델 - 추후 2주간의 예측 혼잡도 지수

# selected_area = st.session_state.get('selected_area', )

if st.session_state:
    selected_area = st.session_state["selected_area"]
    selected_date = str(st.session_state["selected_date"])
    selected_time = str(st.session_state["selected_time"]).zfill(2)

else:
    selected_area = "강남 MICE 관광특구"
    selected_date = "2024-06-23"
    selected_time = "00"    

    st.session_state["selected_area"] = selected_area
    st.session_state["selected_date"] = selected_date
    st.session_state["selected_time"] = selected_time
    
st.text(selected_area)
st.text(selected_date)
st.text(selected_time+":00")

def extract_congest(area):
    result = forecast_df[(forecast_df['AREA_NM'] == area)]
    return result[['FCST_TIME', 'FCST_PPLTN']]

predict_chart = extract_congest(selected_area)
predict_chart.drop_duplicates(inplace=True)

cond1 = predict_chart["FCST_TIME"] >= selected_date
cond2 = predict_chart["FCST_TIME"] <= str(pd.to_datetime(selected_date)+datetime.timedelta(days=30))
# cond3 = predict_chart["FCST_TIME"] == selected_time

bar = predict_chart[cond1 & cond2]

import matplotlib.dates as mdates

if len(bar) > 0:
    df = pd.DataFrame(
        {
            "FCST_TIME":pd.to_datetime(bar["FCST_TIME"]),
            "FCST_PPLTN":bar["FCST_PPLTN"].map(float)
        })

    fig, ax = plt.subplots()
    ax.plot('FCST_TIME', 'FCST_PPLTN', data=df)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # plt.ylim(0,max(bar["FCST_PPLTN"].map(float))*1.1)
    st.pyplot(fig)


# 혼잡도 예측 모델 임시 데이터
# AREA_NM = '강남역'
# congest_result = '88.8%'
# congest_style = '<b style="font-family:serif; color:#8675FF; font-size: 60px;">📋congest_result </b>'
# AREA_CONGEST_LVL = '보통'
# AREA_CONGEST_MSG = '''사람이 몰려있을 수 있지만 크게 붐비지는 않아요. 도보 이동에 큰 제약이 없어요.'''
# AREA_PPLTN_MIN = '32000'
# AREA_PPLTN_MAX = '34000'


st.divider()



if selected_date and selected_time and selected_area:
    with st.container():
        st.subheader(selected_area, '의 연령별/성별 분포 그래프')

        cond1 = forecast_df["FCST_TIME"] >= selected_date
        cond2 = forecast_df["FCST_TIME"] <= str(pd.to_datetime(selected_date)+datetime.timedelta(days=14))

        # cond3 = predict_df["PPLTN_TIME"] == selected_time
        chart = forecast_df[cond1 & cond2].copy()
        chart.drop_duplicates(subset=["FCST_TIME"],inplace=True)
        chart.sort_values(by="FCST_TIME", inplace=True)
        chart.reset_index(drop=True, inplace=True)

        chart_data2 = pd.DataFrame(
            {
                "예측일자" : chart['FCST_TIME'],
                # "예측시간" : chart['PPLTN_TIME']+":00",
                # "요일" : chart['DAY_NAME'],
                # "예상유동인구" : chart['FCST_PPLTN'],
                # "10대" : chart['PPLTN_RATE_10'].map(float),
                # "20대" : chart['PPLTN_RATE_20'].map(float),
                # "30대" : chart['PPLTN_RATE_30'].map(float),
                # "40대" : chart['PPLTN_RATE_40'].map(float),
                # "50대" : chart['PPLTN_RATE_50'].map(float),
                # "60대" : chart['PPLTN_RATE_60'].map(float),
                # "70대" : chart['PPLTN_RATE_70'].map(float),
                "남자": chart["MALE_PPLTN_RATE"],
                "여자": chart["FEMALE_PPLTN_RATE"]                
            }
        )
        chart_data2["예측일자"] = pd.to_datetime(chart_data2["예측일자"])
        chart_data2.set_index("예측일자", inplace=True)
        chart_data2 = chart_data2.applymap(float)

        # fig = plt.figure()
        # bar_plot = plt.barh(chart_data2)
        # st.pyplot(fig)
        # st.line_chart(chart_data2.applymap(float))
        
        st.text("남자")
        
        fig, ax = plt.subplots()
        ax.plot(chart_data2.index, chart_data2["남자"])
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        st.pyplot(fig)
        
        st.text("여자")
        
        fig, ax = plt.subplots()
        ax.plot(chart_data2.index, chart_data2["여자"])
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        st.pyplot(fig)
# # # 6. api - 현재 연령 분포