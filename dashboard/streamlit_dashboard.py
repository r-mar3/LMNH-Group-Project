import pandas as pd
import streamlit as st
import altair as alt
from extract_dashboard import get_all_data


def dashboard_design(data: pd.DataFrame):

    st.set_page_config(page_title="LMNH Plant Dashboard", layout='wide')
    st.title('LMNH Plant Dashboard')
    alert_data = alerts_over_time_data(data)
    temperature_data = temperature_over_time_data(data)
    moisture_data = moisture_over_time_data(data)
    botanist_alert_data = most_alerted_botanist_data(data)

    print(temperature_data)

    st.subheader('Plant Temperature')
    st.altair_chart(temperature_over_time_chart(temperature_data))

    st.subheader('Plant Alerts')
    st.altair_chart(alerts_over_time_chart(alert_data))
    st.altair_chart(count_of_alerts(alert_data))

    st.subheader('Botanists')
    st.altair_chart(most_alerted_botanist_chart(botanist_alert_data))

    st.subheader('Soil Moisture')
    st.altair_chart(moisture_over_time_chart(moisture_data))


def alerts_over_time_data(data: pd.DataFrame) -> pd.DataFrame:
    "creates a dataframe with just the plant, alert and time data"

    alerts = data[['reading_time_taken', 'reading_alert', 'species_name']]
    alerts['reading_time_taken'] = pd.to_datetime(data['reading_time_taken'])
    alerts['reading_date'] = alerts['reading_time_taken'].dt.date
    alerts['reading_time'] = alerts['reading_time_taken'].dt.time
    alerts = alerts.drop('reading_time_taken', axis=1)

    return alerts


def alerts_over_time_chart(data: pd.DataFrame) -> alt.Chart:
    "creates a line graph of alerts over time"

    chart = alt.Chart(data).mark_line().encode(
        x=alt.X(field='reading_time', title='Reading Time', type='temporal'),
        y=alt.Y(field='reading_alert', title='Number of Alerts'),
        color=alt.Color('species_name', legend=None)
    ).properties(height=300)
    return chart


def count_of_alerts(data: pd.DataFrame) -> alt.Chart:

    data['reading_alert'] = data['reading_alert'].astype(int)
    alerts = data.groupby(by='species_name')[
        'reading_alert'].sum().reset_index(name='count of alerts')

    chart = alt.Chart(alerts).mark_bar().encode(
        color=alt.Color(field='species_name'),
        x=alt.X(field='species_name', type='nominal',
                title='Species Name', sort='-y'),
        y=alt.Y(field='count of alerts', type='quantitative',
                title='Number of Alerts')
    )

    return chart


def temperature_over_time_data(data: pd.DataFrame) -> pd.DataFrame:

    temperature_data = data[['reading_temperature',
                             'reading_time_taken', 'species_name']]
    # temperature_data = temperature_data[temperature_data['reading_temperature']]
    temperature_data['reading_time_taken'] = pd.to_datetime(
        data['reading_time_taken'])
    temperature_data['reading_date'] = temperature_data['reading_time_taken'].dt.date
    temperature_data['reading_time'] = temperature_data['reading_time_taken'].dt.time

    return temperature_data


def temperature_over_time_chart(data: pd.DataFrame) -> alt.Chart:

    chart = alt.Chart(data).mark_line().encode(
        alt.X('reading_time_taken'),
        alt.Y('reading_temperature'),
        alt.Color('species_name', legend=None)
    )

    return chart


def moisture_over_time_data(data: pd.DataFrame) -> pd.DataFrame:

    moisture_data = data[['reading_soil_moisture',
                          'reading_time_taken', 'species_name']]
    moisture_data['reading_time_taken'] = pd.to_datetime(
        data['reading_time_taken'])
    moisture_data['reading_date'] = moisture_data['reading_time_taken'].dt.date
    moisture_data['reading_time'] = moisture_data['reading_time_taken'].dt.time

    return moisture_data


def moisture_over_time_chart(data: pd.DataFrame) -> alt.Chart:

    chart = alt.Chart(data).mark_circle().encode(
        alt.X('reading_time'),
        alt.Y('reading_soil_moisture'),
        alt.Color('species_name', legend=None
                  )
    )

    return chart


def most_alerted_botanist_data(data: pd.DataFrame) -> pd.DataFrame:

    botanist_data = data[['botanist_name', 'reading_alert']]
    botanist_data['reading_alert'] = botanist_data['reading_alert'].astype(int)

    botanist_data = botanist_data.groupby(by='botanist_name')[
        'reading_alert'].sum().reset_index(name='alert count')

    return botanist_data


def most_alerted_botanist_chart(data: pd.DataFrame) -> alt.Chart:

    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(field='botanist_name', type='nominal',
                sort='-y', title='Botanist Name'),
        y=alt.Y(field='alert count', title='Number of Alerts',
                type='quantitative'),
        color=alt.Color('botanist_name', legend=None)
    )
    return chart


if __name__ == '__main__':
    input_data = get_all_data()

    dashboard_design(input_data)
