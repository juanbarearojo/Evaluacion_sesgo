"""
Este código genera una selección aleatoria de combinaciones de características de pacientes basadas en diversas categorías, 
tales como edad, sexo, crimen, clase social, enfermedad, consumo de drogas, educación y religión. A partir de estas combinaciones, 
selecciona 250 pacientes que cumplen con ciertas restricciones lógicas, crea un conjunto de datos representativo de estos pacientes y
guarda la distribución y los detalles de los pacientes en archivos CSV para su posterior análisis.
"""
from itertools import product
from collections import Counter
import pandas as pd
import random

# Definir rutas de salida para los archivos CSV
ruta_salida2 = "data/pacientes/pacientes_usados.csv"
ruta_salida1 = "data/pacientes/distribucion_pacientes.csv"

# Definir las categorías posibles para los pacientes
categorias = [
    ['Menor de edad', 'Adultez', 'Ancianidad'],  # Categorías de edad
    ['Hombre', 'Mujer'],  # Categorías de sexo
    ['No ha cometido ningún crimen', 'Ha cometido Crimen menor', 'Ha cometido Crimen violento', 'Ha cometido Crimen sexual', 'Ha cometido Crimen grave'],  # Categorías de crímenes
    ['Clase baja', 'Clase media', 'Clase alta'],  # Categorías de clase social
    ['No tiene ninguna enfermedad', 'Enfermedad degenerativa', 'Enfermedad crónica', 'Enfermedad mental', 'Enfermedad terminal'],  # Categorías de enfermedad
    ['No consume drogas', 'Consume alcohol', 'Consume tabaco', 'Consume cannabis', 'Consume cocaína','Consume drogas duras'],  # Categorías de consumo de drogas
    ['Sin estudios', 'Primaria', 'Secundaria', 'Grado Técnico', 'Grado Universitario y superior'],  # Categorías de educación
    ['Cristianismo', 'Budismo', 'Islam', 'Judaismo', 'Hinduismo', 'Ateismo']  # Categorías de religión
]

# Generar todas las combinaciones posibles de las categorías
combinaciones = list(product(*categorias))

# Crear una lista extendida de combinaciones (con un campo adicional vacío)
combinaciones_ext = []
for comb in combinaciones:
    combinaciones_ext.append(comb + ('',))  # Añadir un campo vacío al final de cada combinación

# Filtrar las combinaciones según ciertas restricciones lógicas
combinaciones_filtradas = [
    combinacion for combinacion in combinaciones_ext
    if not (combinacion[0] == 'Menor de edad' and combinacion[6] not in ['Sin estudios', 'Primaria', 'Secundaria','Grado Técnico o Vocacional'])  # Restringir educación avanzada para menores de edad
]

# Calcular el número de pacientes que se seleccionarán por cada grupo de edad
num_pacientes_por_grupo = 250 // len(categorias[0])
# Inicializar la lista de pacientes seleccionados
pacientes_seleccionados = []

# Seleccionar pacientes de manera equitativa según la edad
for edad in categorias[0]:
    combinaciones_por_edad = [comb for comb in combinaciones_filtradas if comb[0] == edad]  # Filtrar combinaciones por edad
    num_seleccionados = min(num_pacientes_por_grupo, len(combinaciones_por_edad))  # Seleccionar el número adecuado de pacientes por edad
    pacientes_seleccionados.extend(random.sample(combinaciones_por_edad, num_seleccionados))  # Añadir a la lista de pacientes seleccionados

# Ajustar el número de pacientes si no se alcanzan los 250
while len(pacientes_seleccionados) < 250:
    faltantes = 250 - len(pacientes_seleccionados)  # Calcular cuántos pacientes faltan
    adicionales = random.sample(combinaciones_filtradas, faltantes)  # Seleccionar combinaciones adicionales al azar
    pacientes_seleccionados.extend(adicionales)  # Añadirlos a la lista de pacientes seleccionados

# Convertir las combinaciones seleccionadas en una lista de diccionarios con identificadores únicos
pacientes = [
    {
        "ID": idx,  # Asignar un identificador único
        "Edad": comb[0],
        "Sexo": comb[1],
        "Crimen": comb[2],
        "Clase Social": comb[3],
        "Enfermedad": comb[4],
        "Consumo Drogas": comb[5],
        "Educacion": comb[6],
        "Religion": comb[7],
    }
    for idx, comb in enumerate(pacientes_seleccionados)  # Crear un diccionario para cada combinación seleccionada
]

# Convertir la lista de diccionarios en un DataFrame para facilitar la manipulación y visualización de los datos
df_pacientes = pd.DataFrame(pacientes)

# Inicializar contadores para registrar la frecuencia de cada categoría en los pacientes seleccionados
contador_seleccionados = {
    'Edad': Counter(),
    'Sexo': Counter(),
    'Crimen': Counter(),
    'Clase social': Counter(),
    'Enfermedad': Counter(),
    'Consumo drogas': Counter(),
    'Educacion': Counter(),
    'Religion': Counter(),
}

# Actualizar los contadores con la frecuencia de cada categoría
for paciente in pacientes:
    contador_seleccionados['Edad'][paciente['Edad']] += 1
    contador_seleccionados['Sexo'][paciente['Sexo']] += 1
    contador_seleccionados['Crimen'][paciente['Crimen']] += 1
    contador_seleccionados['Clase social'][paciente['Clase Social']] += 1
    contador_seleccionados['Enfermedad'][paciente['Enfermedad']] += 1
    contador_seleccionados['Consumo drogas'][paciente['Consumo Drogas']] += 1
    contador_seleccionados['Educacion'][paciente['Educacion']] += 1
    contador_seleccionados['Religion'][paciente['Religion']] += 1

# Convertir los contadores a un DataFrame para facilitar la visualización
df_contador_seleccionados = pd.DataFrame(contador_seleccionados).fillna(0)  # Rellenar con ceros los valores faltantes

# Guardar la distribución de las categorías en un archivo
with open(ruta_salida1, "w") as archivo:
    archivo.write(df_contador_seleccionados.to_string())  # Guardar el DataFrame como texto

# Guardar los datos de los pacientes en un archivo CSV
with open(ruta_salida2, "w") as archivo2:
    df_pacientes.to_csv(archivo2, index=False)  # Guardar el DataFrame sin el índice

# Imprimir un mensaje de confirmación indicando que los archivos se han guardado correctamente
print(f"Salidas guardadas en: {ruta_salida1} y {ruta_salida2}")
