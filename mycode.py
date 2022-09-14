import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px



def make_price_sparks(d):
    data = d

    df = pd.DataFrame(data, columns=['N'])
    start = [d[0]] * len(d)
    fig = px.line(df, width=150, height=75)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_xaxes(visible=False, showticklabels=False)

    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    c = 'white'
    if d[0] >= d[len(d)-1]:
        c = 'rgba(204, 62, 62, 255)'
    else:
        c = 'rgba(38, 166, 91, 255)'

    l2 = fig.add_scatter(y=start, mode="lines", line=dict(color=c))

    for trace in fig['data']:
        trace['showlegend'] = False

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20)
    )



    fig.update_traces(
        hoverinfo='skip'
    )
    return fig


def make_adv_dec_bar(data):
    adv_df = pd.DataFrame(data, columns=['direction', 'count'])

    fig = px.bar(adv_df, x='count', y='direction', text='count',  orientation='h', height=350,
        color='direction',
        color_discrete_map={
            data[0][0]: 'rgba(204, 62, 62, 255)',
            data[1][0]: 'rgba(204, 62, 62, 255)',
            data[2][0]: 'rgba(204, 62, 62, 255)',
            data[3][0]: 'rgba(108, 122, 137, 255)',
            data[4][0]: 'rgba(38, 166, 91, 255)',  
            data[5][0]: 'rgba(38, 166, 91, 255)',  
            data[6][0]: 'rgba(38, 166, 91, 255)',  
        })
    
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'xaxis_showgrid':False, 
        'yaxis_showgrid':False,
        # 'yaxis_visible':False, 
        # 'yaxis_showticklabels':False,
        'xaxis_visible':False, 
        'xaxis_showticklabels':False,
        # 'bargap':0,
        # 'bargroupgap':0
    })

    for trace in fig['data']:
        trace['showlegend'] = False
        trace['width'] = .85
        trace['textfont'] = dict(
            family="sans serif",
            size=18,
            color="white",
        )

    fig.update_traces(
        hoverinfo='skip',
        marker_line_width=0,
        # textposition="inside"
    )
    return fig




def make_cpi(data):
    adv_df = pd.DataFrame(data, columns=['month', 'cpi'])

    fig = px.bar(adv_df, x='month', y='cpi', text='cpi',  orientation='v', height=350)
    
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'xaxis_showgrid':False, 
        'yaxis_showgrid':False,
        'yaxis_visible':False, 
        'yaxis_showticklabels':False,
        # 'xaxis_visible':False, 
        # 'xaxis_showticklabels':False,
        # 'bargap':0,
        # 'bargroupgap':0
    })

    for trace in fig['data']:
        trace['showlegend'] = False
        trace['width'] = .75
        trace['textfont'] = dict(
            family="sans serif",
            size=20,
            color="white",
        )

    fig.update_traces(
        hoverinfo='skip',
        marker_line_width=0,
        # textposition="inside"
    )
    return fig