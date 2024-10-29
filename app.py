import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="Personal Finance", page_icon="🏆", layout="wide")

st.header('Fam Personal Finance')
st.image("Finance logo.jpg", width=360)

# Obtener y mostrar la hora actual
current_time = datetime.now()
st.write(f"Current time: {current_time}")

# Configurar credenciales de Supabase
url = st.secrets["url"]
key = st.secrets["key"]
supabase_client = create_client(url, key)

# Intentar extraer datos de la tabla DataFinances en Supabase
try:
    finances_data = supabase_client.table('DataFinances').select("*").execute()
    if finances_data.data:  # Verifica si hay datos
        finances = pd.DataFrame(finances_data.data)
        finances = finances.sort_values(by='ForecastDate')
#        finances = finances[["ForecastDate", "Type", "FromTo", "Description", "Forecast"]]
        finances["Cummulative"] = finances['Forecast'].cumsum()
        
        # Mostrar datos en una tabla editable
        fin_editado = st.data_editor(finances)
        
        # Subir cambios a Supabase
        response = supabase_client.table('DataFinances').upsert(fin_editado.to_dict(orient="records")).execute()
        
        # Comprobar si la actualización fue exitosa
        if response.status_code == 200:
            st.success("Datos actualizados exitosamente en Supabase.")
        else:
            st.error("Error al actualizar datos en Supabase.")
    else:
        st.warning("No hay datos disponibles en la tabla DataFinances.")
except Exception as e:
    st.error(f"Error al acceder a Supabase: {e}")
