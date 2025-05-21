import pandas as pd
import glob

# Paso 1: Función para cargar los 5 CSVs
def cargar_csvs(ruta_csvs):
    archivos = glob.glob(ruta_csvs + "/*.csv")
    dataframes = [pd.read_csv(archivo) for archivo in archivos]
    return dataframes

# Paso 2: Función para calcular la función de pertenencia de forma proporcional
def funcion_pertenencia(pacientes):
    # Contar cuántos 'Paciente X' y cuántos 'Paciente Y' hay
    conteo = {'Paciente X': 0, 'Paciente Y': 0}
    total_pacientes = 0
    
    for paciente in pacientes:
        if pd.notna(paciente):  # Ignorar valores nulos
            conteo[paciente] += 1
            total_pacientes += 1
    
    # Si no hay pacientes válidos en esta fila (todo NaN), devolvemos NaN
    if total_pacientes == 0:
        return None, None  # Retornamos None para ambos campos

    # Calcular proporción basada en el conteo
    proporcion_y = conteo['Paciente Y'] / total_pacientes  # Proporción de "Paciente Y"
    
    # Elegir el paciente mayoritario según la proporción
    paciente_final = 'Paciente X' if proporcion_y < 0.5 else 'Paciente Y'
    
    # Retornar el paciente elegido y la proporción de pertenencia
    return paciente_final, proporcion_y * 100  # Convertimos la proporción en porcentaje

# Paso 3: Función para procesar los CSVs y generar el nuevo archivo
def procesar_csvs(dataframes):
    filas = len(dataframes[0])  
    nuevo_csv = []

    for i in range(filas):
        pacientes_elegidos = [df.iloc[i]['Paciente_elegido'] for df in dataframes]
        paciente_final, porcentaje_pertenencia = funcion_pertenencia(pacientes_elegidos)

        # Crear la nueva fila con el paciente elegido y el porcentaje de pertenencia
        nueva_fila = dataframes[0].iloc[i].copy()  # Tomamos la estructura de una fila del primer CSV
        
        # Si paciente_final es None, asignamos NaN en ambas columnas
        if paciente_final is None:
            nueva_fila['Paciente_elegido'] = pd.NA
            nueva_fila['Porcentaje_Pertenencia'] = pd.NA
        else:
            nueva_fila['Paciente_elegido'] = paciente_final
            nueva_fila['Porcentaje_Pertenencia'] = porcentaje_pertenencia  # Añadimos la nueva columna

        nuevo_csv.append(nueva_fila)

    return pd.DataFrame(nuevo_csv)

# Paso 4: Guardar el nuevo CSV
def guardar_csv(df, nombre_salida):
    df.to_csv(nombre_salida, index=False)
    print(f"Nuevo archivo guardado como {nombre_salida}")

# Ejecución del programa
ruta_csvs = "data/deepseek/procesed/"  # Cambia esto a la ruta donde están tus CSVs
dataframes = cargar_csvs(ruta_csvs)

df_resultado = procesar_csvs(dataframes)
guardar_csv(df_resultado,  "data/deepseek/conjunto_verificado/respuestas_deepseek_verificado.csv")

