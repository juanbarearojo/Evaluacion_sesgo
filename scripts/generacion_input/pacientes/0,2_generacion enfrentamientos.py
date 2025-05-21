'''
Este código realiza la lectura de un archivo CSV que contiene datos de pacientes. 
Luego, genera todas las combinaciones posibles de pares de filas de este DataFrame utilizando los índices de las filas. 
Para cada par de filas, crea una nueva fila que contiene datos de ambas filas originales, etiquetando las columnas de una fila con "X" y las de la otra con "Y".
Todas estas filas combinadas se almacenan en un nuevo DataFrame. Finalmente, este DataFrame se guarda en un nuevo archivo CSV en la ruta especificada, 
y se imprime un mensaje confirmando la ubicación del archivo de salida.
'''
import itertools  # Importa itertools, que contiene funciones para crear iteradores eficientes.
import csv  # Importa el módulo csv para manejo de archivos CSV.
import os  # Importa os para interactuar con el sistema operativo, como manejar rutas de archivos.
import pandas as pd  # Importa pandas y le asigna el alias 'pd', útil para manipulación y análisis de datos.

# LECTURA DE LOS DATOS
df = pd.read_csv('data/pacientes/pacientes_usados.csv')  # Lee el archivo CSV en un DataFrame de pandas.
ruta_salida = "data/pacientes/combinaciones_pacientes.csv"  # Define la ruta donde se guardará el archivo CSV de salida.

# Generar todas las combinaciones posibles de los índices de las filas
combinations = list(itertools.combinations(df.index, 2))  # Genera una lista de todas las combinaciones posibles de índices de filas, tomados de dos en dos.

# Crear una lista para almacenar las combinaciones
combined_rows = []  # Inicializa una lista vacía para almacenar las filas combinadas.

# Combinar las filas basadas en los índices
for i, j in combinations:  # Itera sobre cada par de índices generados en combinations.
    combined_row = pd.Series({  # Crea una Serie (fila) combinando los datos de las dos filas correspondientes a los índices i y j.
        'ID X': df.loc[i, 'ID'],
        'Edad X': df.loc[i, 'Edad'],
        'Sexo X': df.loc[i, 'Sexo'],
        'Crimen X': df.loc[i, 'Crimen'],
        'Clase Social X': df.loc[i, 'Clase Social'],
        'Enfermedad X': df.loc[i, 'Enfermedad'],
        'Consumo Drogas X': df.loc[i, 'Consumo Drogas'],
        'Educacion X': df.loc[i, 'Educacion'],
        'Religion X': df.loc[i, 'Religion'],
        'ID Y': df.loc[j, 'ID'],
        'Edad Y': df.loc[j, 'Edad'],
        'Sexo Y': df.loc[j, 'Sexo'],
        'Crimen Y': df.loc[j, 'Crimen'],
        'Clase Social Y': df.loc[j, 'Clase Social'],
        'Enfermedad Y': df.loc[j, 'Enfermedad'],
        'Consumo Drogas Y': df.loc[j, 'Consumo Drogas'],
        'Educacion Y': df.loc[j, 'Educacion'],
        'Religion Y': df.loc[j, 'Religion']
    })
    combined_rows.append(combined_row)  # Añade la fila combinada a la lista combined_rows.

# Crear un nuevo DataFrame con las combinaciones
combinations_df = pd.DataFrame(combined_rows)  # Crea un nuevo DataFrame a partir de la lista de filas combinadas.

# Guardar el DataFrame en un archivo CSV
combinations_df.to_csv(ruta_salida, index=False)  # Guarda el DataFrame resultante en un archivo CSV en la ruta especificada, sin incluir el índice.

print(f"Salidas guardadas en: {ruta_salida}")  # Imprime un mensaje confirmando la ubicación del archivo guardado.
