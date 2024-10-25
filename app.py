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



tab1, tab2 = st.tabs(["Pronosticos", "Resultados"])
usuarios = pd.DataFrame({'Usuario': ['Seleccionar', 'Alex', 'Gerry', 'Giorgio', 'Mike']})
usuario_activo = st.sidebar.selectbox('Usuario', usuarios['Usuario'])

# Credenciales de Supabase
url = st.secrets["url"]
key = st.secrets["key"]
# url = 'https://uehrgoqjfbdbkkyumtpw.supabase.co'
# key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVlaHJnb3FqZmJkYmtreXVtdHB3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwOTA3MDE1MywiZXhwIjoyMDI0NjQ2MTUzfQ.KIIsWOhJx7sPYYP6Wdvdq6S4vPJ8vrSrZbs-vG6kBWw'
supabase_client = create_client(url, key)

# Extraer la tabla de drivers
drivers = supabase_client.table('drivers').select("*").execute()
drivers = pd.DataFrame(drivers.data)
drivers = drivers.sort_values(by='driverId')
drivers = drivers['driverName']

admin = supabase_client.table('admin_control').select("*").execute()
race_inicial = admin.data[0]['RaceNo']
race_final = admin.data[1]['RaceNo']
st.write(race_inicial)
st.write(race_final)
admin_tbl = pd.DataFrame(admin.data)

resultados = supabase_client.table('Resultados').select("id,Race No,Race,Place,Result").execute()
resultados = pd.DataFrame(resultados.data)
resultados_all = resultados.copy()

pronosticos_all = supabase_client.table('Pronosticos').select("id,Race No,Race,Place,User,Forecast,Result").execute()
pronosticos_all = pd.DataFrame(pronosticos_all.data)
pronosticos_all = pronosticos_all[((pronosticos_all['Race No'] >= race_inicial) & (pronosticos_all['Race No'] <= race_final)) & ((pronosticos_all['Place'] != "Top 3") & (pronosticos_all['Place'] != "Top 5"))]
pronosticos_all = pronosticos_all.sort_values(by='id')
# pronosticos_all_pivot = pronosticos_all.pivot(index=None, columns='User', values='Forecast')

if current_time > hora_limite:
    st.dataframe(pronosticos_all)

#función para actualizar data en supabase
def upload_forecast(dataframe: pd.DataFrame):
    data = dataframe.to_dict(orient="records")
    try:
        # Inserta o actualiza los datos en Supabase
        response = supabase_client.table('Pronosticos').upsert(data).execute()
        return response
    except Exception as e:
        return e

def upload_results(dataframe: pd.DataFrame):
    data = dataframe.to_dict(orient="records")
    try:
        # Inserta o actualiza los datos en Supabase
        response = supabase_client.table('Resultados').upsert(data).execute()
        return response
    except Exception as e:
        return e

# Extraer la tabla de users

if usuario_activo != "Seleccionar":
    users = supabase_client.table('users').select("*").eq("user", usuario_activo).execute()
    if users.data:
        user_id = str(users.data[0]['id'])
        none_pswd = users.data[0]['password']
        user_pswd = str(users.data[0]['password'])
        # st.write(user_id)
        # st.write(user_pswd)

        if none_pswd is None:
            st.sidebar.caption("Registra tu password para ingresar tus pronosticos")
            new_password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Registrar Password"):
                supabase_client.table('users').update({"password": new_password}).eq("id", user_id).execute()
                st.sidebar.write("Tu password ha sido registrado, para continuar selecciona un usuario diferente y posteriormente vuelve a seleccionar tu usuario para que se actualice la información")

        

        else:
            current_password = st.sidebar.text_input("Ingresa tu Password", type="password")
            if current_password == user_pswd and current_time < hora_limite:
            # if current_password == user_pswd:
                pronosticos = supabase_client.table('Pronosticos').select("id,Race No,Race,Place,User,Forecast").eq("User", usuario_activo).neq("Place", "Top 3").neq("Place", "Top 5").order('id', desc=False).execute()
                pronosticos = pd.DataFrame(pronosticos.data)
                pronosticos = pronosticos.sort_values(by='id')
                pronosticos = pronosticos[(pronosticos['Race No'] >= race_inicial) & (pronosticos['Race No'] <= race_final)]
                edited_pronosticos = st.data_editor(pronosticos, column_config={
                    "Forecast": st.column_config.SelectboxColumn(options=drivers)
                }, disabled=["Race No", "Race", "Place", "Fecha Carrera", "User", "Result", "id"], hide_index=True)
                if st.button('Cargar pronosticos'):
                    # response = upload_to_supabase(edited_pronosticos)
                    upload_forecast(edited_pronosticos)
                    st.write(f'Tus pronosticos han sido actualizados correctamente, recuerda que los puedes editar hasta el : {hora_limite}')
            if usuario_activo == "Mike" and current_password == user_pswd:
                race_inicial_update = st.sidebar.number_input("Ingresa la carrera inicial", step=1)
                race_final_update = st.sidebar.number_input("Ingresa la carrera Final", step=1)
                if st.sidebar.button('Actualizar Race Filter'):
                    data, count = supabase_client.table('admin_control').update({'RaceNo': race_inicial_update}).eq('id', 1).execute()
                    data, count = supabase_client.table('admin_control').update({'RaceNo': race_final_update}).eq('id', 2).execute()
                    st.sidebar.write('La configuración de las carreras ha sido cargado')

                # st.write('resultados')
                resultados = resultados[(resultados['Race No'] >= race_inicial) & (resultados['Race No'] <= race_final)]
                st.write('resultados')
