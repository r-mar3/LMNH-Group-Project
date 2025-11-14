"""Runs the main plant dashboard visualisations"""
import pandas as pd
import streamlit as st
import altair as alt
from extract_dashboard import get_all_data


def dashboard_design(data: pd.DataFrame) -> None:
    """Defines the main design and layout of the dashboard"""
    st.set_page_config(page_title="LMNH Plant Dashboard", layout='wide')
    st.title('LMNH Plant Dashboard')

    st.metric('Alerts', data['reading_alert'].astype(int).sum(), border=True)

    alert_data = alerts_over_time_data(data)
    temperature_data = temperature_over_time_data(data)
    moisture_data = moisture_over_time_data(data)
    botanist_alert_data = most_alerted_botanist_data(data)

    with st.sidebar:
        plants = list(data['species_name'].unique())
        plants_filter = st.multiselect('Select Plants', plants, default=plants)

        botanists = list(data['botanist_name'].unique())
        botanists_filter = st.multiselect(
            'Select Botanists', botanists, default=botanists)

    st.subheader('Plant Temperature')
    st.altair_chart(temperature_over_time_chart(
        temperature_data, plants_filter))

    st.subheader('Plant Alerts')
    st.altair_chart(count_of_alerts(alert_data, plants_filter))

    st.subheader('Soil Moisture')
    st.altair_chart(moisture_over_time_chart(moisture_data, plants_filter))

    st.subheader('Botanists')
    st.altair_chart(most_alerted_botanist_chart(
        botanist_alert_data, botanists_filter))


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

    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(field='reading_time', title='Reading Time', type='temporal'),
        y=alt.Y(field='reading_alert', title='Number of Alerts'),
        color=alt.Color('species_name')
    ).properties(height=300)
    return chart


def count_of_alerts(data: pd.DataFrame, plants_filter: list) -> alt.Chart:

    data = data[data['species_name'].isin(plants_filter)]

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


def temperature_over_time_chart(data: pd.DataFrame, plants_filter: list) -> alt.Chart:

    data = data[data['species_name'].isin(plants_filter)]

    chart = alt.Chart(data).mark_line().encode(
        x=alt.X(field='reading_time_taken',
                type='temporal', title='Reading Time'),
        y=alt.Y(field='reading_temperature',
                type='quantitative', title='Temperature'),
        color=alt.Color('species_name')
    )

    return chart


def moisture_over_time_data(data: pd.DataFrame) -> pd.DataFrame:

    moisture_data = data[['reading_soil_moisture',
                          'reading_time_taken', 'species_name']]
    moisture_data['reading_time_taken'] = pd.to_datetime(
        data['reading_time_taken'])
    moisture_data['reading_date'] = moisture_data['reading_time_taken'].dt.date
    moisture_data['reading_time'] = moisture_data['reading_time_taken'].dt.time

    moisture_data = moisture_data[moisture_data['reading_soil_moisture'].between(
        0, 100)]

    return moisture_data


def moisture_over_time_chart(data: pd.DataFrame, plants_filter: list) -> alt.Chart:

    data = data[data['species_name'].isin(plants_filter)]

    chart = alt.Chart(data).mark_line().encode(
        x=alt.X(field='reading_time_taken',
                type='temporal', title='Reading Time'),
        y=alt.Y(field='reading_soil_moisture',
                type='quantitative', title='Soil Moisture'),
        color=alt.Color('species_name')
    )

    return chart


def most_alerted_botanist_data(data: pd.DataFrame) -> pd.DataFrame:

    botanist_data = data[['botanist_name', 'reading_alert']]
    botanist_data['reading_alert'] = botanist_data['reading_alert'].astype(int)

    botanist_data = botanist_data.groupby(by='botanist_name')[
        'reading_alert'].sum().reset_index(name='alert count')

    return botanist_data


def most_alerted_botanist_chart(data: pd.DataFrame, botanists_filter: list) -> alt.Chart:

    data = data[data['botanist_name'].isin(botanists_filter)]

    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(field='botanist_name', type='nominal',
                sort='-y', title='Botanist Name'),
        y=alt.Y(field='alert count', title='Number of Alerts',
                type='quantitative'),
        color=alt.Color('botanist_name')
    )
    return chart


if __name__ == '__main__':
    input_data = get_all_data()

    dashboard_design(input_data)
