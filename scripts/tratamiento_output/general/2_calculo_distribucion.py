import pandas as pd
from pathlib import Path

# =============================================================================
# Configuración de rutas y modelo
# =============================================================================
modelo = "deepseek"  # Cambia este valor para utilizar otro modelo

# Directorios base
base_dir = Path("data") / modelo / "conjunto_verificado"
pacientes_dir = Path("data") / "pacientes"

# Aseguramos que el directorio base exista (para guardar salidas)
base_dir.mkdir(parents=True, exist_ok=True)

# Definición de rutas de archivos
ruta_respuestas = base_dir / f"respuestas_{modelo}_verificado.csv"
ruta_distribucion_pacientes = pacientes_dir / "distribucion_pacientes.csv"
ruta_distribucion_eleccion = base_dir / "distribucion_eleccion.csv"
ruta_ids_elegidos = base_dir / "ids_elegidos.csv"
ruta_proporciones_ajustadas = base_dir / "proporciones_ajustadas.csv"

# =============================================================================
# Cargar datos
# =============================================================================
# Archivo CSV con las respuestas generadas por el modelo
df = pd.read_csv(ruta_respuestas)

# Distribución inicial de pacientes
distribucion_pacientes = pd.read_csv(ruta_distribucion_pacientes, index_col=0)

# =============================================================================
# Configuración de categorías y DataFrames de salida
# =============================================================================
categorias = [
    'Menor de edad', 'Adultez', 'Ancianidad',          # Edad
    'Hombre', 'Mujer',                                 # Sexo
    'No ha cometido ningún crimen', 'Ha cometido Crimen menor', 'Ha cometido Crimen violento', 
    'Ha cometido Crimen sexual', 'Ha cometido Crimen grave',   # Crimen
    'Clase baja', 'Clase media', 'Clase alta',                   # Clase social
    'No tiene ninguna enfermedad', 'Enfermedad degenerativa', 'Enfermedad crónica', 
    'Enfermedad mental', 'Enfermedad terminal',                  # Enfermedad
    'No consume drogas', 'Consume alcohol', 'Consume tabaco', 'Consume cannabis', 
    'Consume cocaína', 'Consume drogas duras',                   # Consumo de drogas
    'Sin estudios', 'Primaria', 'Secundaria', 'Grado Técnico', 'Grado Universitario y superior',  # Educación
    'Cristianismo', 'Budismo', 'Islam', 'Judaismo', 'Hinduismo', 'Ateismo'  # Religión
]

# DataFrame para almacenar la distribución (inicialmente en 0)
distribucion = pd.DataFrame(0.0, index=categorias, 
                            columns=['Edad', 'Sexo', 'Crimen', 'Clase social', 
                                     'Enfermedad', 'Consumo drogas', 'Educacion', 'Religion'])

# DataFrame para contar cuántas veces se elige cada paciente
ids_elegidos = pd.DataFrame(0, index=range(250), columns=['Veces Elegido'])

# =============================================================================
# Función para actualizar la distribución y el conteo de IDs elegidos
# =============================================================================
def actualizar_distribucion(paciente, id_paciente):
    distribucion.loc[paciente['Edad'], 'Edad'] += 1
    distribucion.loc[paciente['Sexo'], 'Sexo'] += 1
    distribucion.loc[paciente['Crimen'], 'Crimen'] += 1
    distribucion.loc[paciente['Clase Social'], 'Clase social'] += 1
    distribucion.loc[paciente['Enfermedad'], 'Enfermedad'] += 1
    distribucion.loc[paciente['Consumo Drogas'], 'Consumo drogas'] += 1
    distribucion.loc[paciente['Educacion'], 'Educacion'] += 1
    distribucion.loc[paciente['Religion'], 'Religion'] += 1

    ids_elegidos.loc[id_paciente, 'Veces Elegido'] += 1

# =============================================================================
# Actualizar la distribución según las elecciones en el DataFrame
# =============================================================================
for index, row in df.iterrows():
    # IDs de los pacientes
    id_x = row['ID X']
    id_y = row['ID Y']
    
    # Saltar filas donde no se ha elegido un paciente
    if pd.isnull(row['Paciente_elegido']):
        continue
    
    if row['Paciente_elegido'] == 'Paciente X':
        paciente = {
            'Edad': row['Edad X'],
            'Sexo': row['Sexo X'],
            'Crimen': row['Crimen X'],
            'Clase Social': row['Clase Social X'],
            'Enfermedad': row['Enfermedad X'],
            'Consumo Drogas': row['Consumo Drogas X'],
            'Educacion': row['Educacion X'],
            'Religion': row['Religion X']
        }
        actualizar_distribucion(paciente, id_x)
    
    elif row['Paciente_elegido'] == 'Paciente Y':
        paciente = {
            'Edad': row['Edad Y'],
            'Sexo': row['Sexo Y'],
            'Crimen': row['Crimen Y'],
            'Clase Social': row['Clase Social Y'],
            'Enfermedad': row['Enfermedad Y'],
            'Consumo Drogas': row['Consumo Drogas Y'],
            'Educacion': row['Educacion Y'],
            'Religion': row['Religion Y']
        }
        actualizar_distribucion(paciente, id_y)

# =============================================================================
# Guardar resultados intermedios
# =============================================================================
# Guardar la distribución actualizada
distribucion.to_csv(ruta_distribucion_eleccion, index=True)

# Ordenar ids_elegidos (por ejemplo, de mayor a menor "Veces Elegido")
ids_elegidos_sorted = ids_elegidos.sort_values(by='Veces Elegido', ascending=False)
ids_elegidos_sorted.to_csv(ruta_ids_elegidos, index=True)

# =============================================================================
# Cálculo de Proporciones Ajustadas y Normalización
# =============================================================================
E_total = 31125  # Total de enfrentamientos, ejemplo
proporciones_ajustadas = distribucion.copy()

for categoria in categorias:
    for columna in distribucion.columns:
        E_i = distribucion.loc[categoria, columna]  # "Victorias" de la categoría en la columna
        # Se obtiene T_i de la distribución de pacientes (si la columna existe)
        T_i = distribucion_pacientes.loc[categoria, columna] if columna in distribucion_pacientes.columns else 0
        
        if T_i > 0:
            # Se calcula la suma total de T_i en la columna
            T_total = distribucion_pacientes[columna].sum()
            if T_total > 0:
                proporciones_ajustadas.loc[categoria, columna] = (E_i / E_total) / (T_i / T_total)
            else:
                proporciones_ajustadas.loc[categoria, columna] = 0
        else:
            proporciones_ajustadas.loc[categoria, columna] = 0

# Normalización por columna para que las proporciones sumen 1
for columna in proporciones_ajustadas.columns:
    col_sum = proporciones_ajustadas[columna].sum()
    if col_sum != 0:
        proporciones_ajustadas[columna] = proporciones_ajustadas[columna] / col_sum

# Guardar el DataFrame de proporciones ajustadas
proporciones_ajustadas.to_csv(ruta_proporciones_ajustadas, index=True)

# =============================================================================
# Mensajes de confirmación
# =============================================================================
print(f"Proporciones ajustadas guardadas en '{ruta_proporciones_ajustadas}'.")
print(f"IDs elegidos ordenados guardados en '{ruta_ids_elegidos}'.")
