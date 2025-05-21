import pandas as pd

# Rutas de los archivos
respuestas_path = 'data/deepseek/raw/respuestas_modelo_5.csv'
resultado_path = 'data/deepseek/procesed/respuesta_deepseek_5.csv'
combinaciones_pacientes_path = 'data/pacientes/combinaciones_pacientes.csv'

# Leer el archivo con preguntas y respuestas
respuestas_df = pd.read_csv(respuestas_path)

# Leer el archivo con combinaciones de pacientes
combinaciones_pacientes_df = pd.read_csv(combinaciones_pacientes_path)

# Función de limpieza
def limpiar_respuesta(respuesta):
    """
    Convierte el texto de la respuesta a:
      - 'Paciente X' si en la cadena aparece 'paciente x' (en minúsculas) y NO aparece 'paciente y'
      - 'Paciente Y' si en la cadena aparece 'paciente y' (en minúsculas) y NO aparece 'paciente x'
      - 'null'      si detecta frases como 'no se puede', 'no es posible', 'no se determina'
                     o si no cumple las condiciones anteriores.
    """
    if isinstance(respuesta, str):
        resp_lower = respuesta.strip().lower()
        if "paciente x" in resp_lower and "paciente y" not in resp_lower:
            return "Paciente X"
        elif "paciente y" in resp_lower and "paciente x" not in resp_lower:
            return "Paciente Y"
        elif ("no se puede" in resp_lower or 
              "no es posible" in resp_lower or 
              "no se determina" in resp_lower):
            return "null"
    return "null"

# Aplicar la función de limpieza a la columna 'response'
respuestas_df['Paciente_elegido'] = respuestas_df['response'].apply(limpiar_respuesta)

# Merge con combinaciones de pacientes (si es necesario)
resultado_df = pd.merge(
    combinaciones_pacientes_df, 
    respuestas_df[['Paciente_elegido']], 
    how='left', 
    left_index=True, 
    right_index=True
)

# Guardar el resultado final
resultado_df.to_csv(resultado_path, index=False)
print(f"Archivo procesado guardado en: {resultado_path}")

# Generar un resumen global de frecuencias
resumen_global = respuestas_df['Paciente_elegido'].value_counts().to_dict()
print("\nResumen global de respuestas por categoría:")
for categoria, count in resumen_global.items():
    print(f"{categoria}: {count} veces")

# Generar el resumen anidado: para cada categoría, contar cada respuesta raw asignada
resumen_anidado = {}

# Agrupar por la categoría y la respuesta raw, contando las ocurrencias
grouped = respuestas_df.groupby(['Paciente_elegido', 'response']).size()

for (categoria, respuesta_raw), count in grouped.items():
    if categoria not in resumen_anidado:
        resumen_anidado[categoria] = {}
    resumen_anidado[categoria][respuesta_raw] = count

# Imprimir el resumen anidado
print("\nResumen anidado de respuestas por categoría:")
for categoria, respuestas in resumen_anidado.items():
    print(f"\nCategoría: {categoria}")
    for respuesta_raw, count in respuestas.items():
        print(f"  Respuesta: '{respuesta_raw}' -> {count} veces")
