import streamlit as st


def get_database_connection():
    pass


if __name__ == '__main__':
    st.title('Plant Dashboard')
    with st.sidebar:
        time_scale_selection = st.radio(
            'Select Time Scale',
            ['Minute', 'Hour', 'Day']
        )
