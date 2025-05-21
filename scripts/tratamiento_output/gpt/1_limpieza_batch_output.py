import os
import glob
import json
import re
import pandas as pd

# Ruta al directorio que contiene los archivos JSONL
directory_path = 'data/gpt/lotes_gpt_jsonl/output/lote5/'

# Ruta al archivo CSV de combinaciones
csv_path = 'data/gpt/lotes_gpt_jsonl/output/conjuntos_instancias/respuesta_gpt_lote_5.csv'
csv_path_original = 'data/pacientes/combinaciones_pacientes.csv'

# Patrones específicos para diferentes combinaciones de mensajes, los más específicos primero
pattern_x_general = re.compile(r'Paciente.?X', re.IGNORECASE)
pattern_y_general = re.compile(r'Paciente.?Y', re.IGNORECASE)

# Lista para almacenar los pacientes encontrados
pacientes = []

# Obtener la lista de archivos .jsonl en el directorio
archivos_jsonl = sorted(glob.glob(os.path.join(directory_path, '*.jsonl')))
print(archivos_jsonl)
# Leer cada archivo JSONL y extraer datos
for file_path in archivos_jsonl:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    entry = json.loads(line.strip())
                    response = entry.get("response", {})
                    body = response.get("body", {})
                    choices = body.get("choices", [])
                    for choice in choices:
                        message = choice.get("message", {})
                        content = message.get("content", "")
                        
                        # Evalúa primero los patrones más específicos
                        if pattern_x_general.search(content):  # Paciente X general
                            pacientes.append('Paciente X')
                        elif pattern_y_general.search(content):  # Paciente Y general
                            pacientes.append('Paciente Y')
                        else:
                            pacientes.append('null')
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON line in file {file_path}: {str(e)} - line content: {line}")
                    pacientes.append('null')
    except (IOError, OSError) as e:
        print(f"Error reading file {file_path}: {e}")
        pacientes.append('null')

# Leer el archivo CSV existente
try:
    df_original = pd.read_csv(csv_path_original)
    
    # Si el número de pacientes es menor que el número de filas en el CSV, rellenar con 'null'
    if len(pacientes) < len(df_original):
        pacientes.extend(['null'] * (len(df_original) - len(pacientes)))
    
    # Truncar la lista de pacientes si es mayor al número de filas en el CSV
    pacientes = pacientes[:len(df_original)]

    # Añadir la columna de pacientes al DataFrame original
    df_original['Paciente_elegido'] = pacientes

    # Guardar el DataFrame actualizado en el nuevo archivo CSV
    df_original.to_csv(csv_path, index=False)
    print(f"Columna de pacientes añadida y datos guardados en el archivo {csv_path}")
except FileNotFoundError:
    print(f"Archivo {csv_path_original} no encontrado.")
except pd.errors.EmptyDataError:
    print(f"Archivo {csv_path_original} está vacío.")
except Exception as e:
    print(f"Error procesando el archivo CSV: {e}")
