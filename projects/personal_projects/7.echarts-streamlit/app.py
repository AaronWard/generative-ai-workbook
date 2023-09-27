import pandas as pd
import streamlit as st
from streamlit_chat import message
from streamlit_echarts import st_echarts

def main():
    ###################### Title and main panel configuration #################################
    st.set_page_config(
        page_title="Streamlit x Apache ECharts 📈",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )
    chart_count = 1

    st.title("Streamlit x Apache ECharts 📈")
    upload = st.file_uploader("Upload CSV file", type="csv")

    if upload is not None:
        data = pd.read_csv(upload)
        st.session_state['data'] = data
    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] =[]


    ###################### Side Bar #################################
    with st.sidebar:
        st.sidebar.title(f"Visualizations")
        side_vis = None

    def get_chart(data):

        # Filter out rows where DIAGNOSED_COVID is not 1 and drop rows with null DIAGNOSES_DATE
        data = data[data['DIAGNOSED_COVID'] == 1].dropna(subset=['DIAGNOSES_DATE'])
        
        # Group by DIAGNOSES_DATE and count the number of cases per date
        covid_cases_by_date = data.groupby('DIAGNOSES_DATE').size().reset_index(name='cases_count')
        
        # Sort by date
        covid_cases_by_date.sort_values(by='DIAGNOSES_DATE', inplace=True)
        
        dates = covid_cases_by_date['DIAGNOSES_DATE'].tolist()
        cases_count = covid_cases_by_date['cases_count'].cumsum().tolist()

        option = {
                "tooltip": {"trigger": 'axis', "position": [20, '40%']},
                "title": {"left": 'center', "text": 'COVID-19 Cases Over Time'},
                "toolbox": {
                    "feature": {
                        "dataZoom": {"yAxisIndex": 'none'},
                        "restore": {},
                        "saveAsImage": {}
                    }
                },
                "xAxis": {"type": 'category', "boundaryGap": True, "data": dates},
                "yAxis": {"type": 'value', "boundaryGap": [0, "5%"]},
                "dataZoom": [
                        {"type": 'inside', "start": 0, "end": 100},
                        {"start": 0, "end": 10}
                    ],
                "series": [
                    {
                        "name": 'COVID-19 Cases',
                        "type": 'line',
                        "symbol": 'none',
                        "sampling": 'lttb',
                        "itemStyle": {"color": 'rgb(255, 70, 131)'},
                        "areaStyle": {
                            "color": {
                                "type": 'linear', "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": 'rgb(255, 158, 68)'},
                                    {"offset": 1, "color": 'rgb(255, 70, 131)'}
                                ]
                            }
                        },
                        "data": cases_count
                    }
                ]
            }
        return option
    
    ###################### Chat Interface #################################

    response_container = st.container()
    # Here we will have a container for user input text box
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_area("Your question goes here:", key='input', height=100)
            submit_button = st.form_submit_button(label='Send')

            if submit_button:
                if 'data' in st.session_state:
                    st.session_state['messages'].append(user_input)
                    st.session_state['messages'].append("Here is your chart :)")

                    with response_container:
                        for i in range(len(st.session_state['messages'])):
                            if (i % 2) == 0:
                                message(st.session_state['messages'][i], is_user=True, key=str(i) + '_user')
                            else:
                                message(st.session_state['messages'][i], key=str(i) + '_AI')
                                with st.sidebar:
                                    st_echarts(get_chart(st.session_state['data']), key=chart_count)
                                    chart_count += 1
                else:
                    st.warning('No data provided')


#Invoking main function
if __name__ == '__main__':
    main()