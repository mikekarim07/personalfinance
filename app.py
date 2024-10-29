import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="Personal Finance", page_icon="🏆", layout="wide")

st.header('Fam Personal Finance')
st.image("Finance logo.jpg", width=360)


current_time = datetime.now()
year = '2024'
month = '7'
day = '19'
hora = '15'
minuto = '00' 
hora_limite = datetime.strptime(f"{year}-{month}-{day} {hora}:{minuto}", '%Y-%m-%d %H:%M')

st.write(current_time)

# Credenciales de Supabase
url = st.secrets["url"]
key = st.secrets["key"]
supabase_client = create_client(url, key)

# Extraer la tabla de DataFinances
finances = supabase_client.table('DataFinances').select("*").execute()
finances = pd.DataFrame(finances.data)
finances = finances.sort_values(by='ForecastDate')
finances = finances[["ForecastDate", "Type", "FromTo", "Description", "Forecast"]]
finances[Cummulative] = finances['Forecast'].cumsum()
 
st.dataframe(finances, hide_index=True)
