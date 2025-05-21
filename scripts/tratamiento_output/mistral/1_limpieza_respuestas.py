import pandas as pd

# Cargar los datos originales
respuestas_path = 'data/mistral/raw/respuesta_mistral_5.csv'  # Ruta al archivo con las respuestas
combinaciones_pacientes_path = 'data/pacientes/combinaciones_pacientes.csv'  # Ruta al archivo con las combinaciones de pacientes

respuestas_df = pd.read_csv(respuestas_path)
combinaciones_pacientes_df = pd.read_csv(combinaciones_pacientes_path)

# Limpiar la columna "Respuesta"
def limpiar_respuesta(respuesta):
    if isinstance(respuesta, str):
        respuesta = respuesta.strip().lower()
        if "paciente x" in respuesta and "paciente y" not in respuesta:
            return "Paciente X"
        elif "paciente y" in respuesta and "paciente x" not in respuesta:
            return "Paciente Y"
        elif "no se puede" in respuesta or "no es posible" in respuesta or "no se determina" in respuesta:
            return "null"
    return "null"

respuestas_df['Paciente_elegido'] = respuestas_df['Respuesta'].apply(limpiar_respuesta)

# Combinar los datos
# Asumiendo que ambas tablas tienen una columna en común para hacer la combinación, como un ID
# Puedes ajustar "ID" a la columna correspondiente en ambos archivos
resultado_df = pd.merge(combinaciones_pacientes_df, respuestas_df[['Paciente_elegido']], how='left', left_index=True, right_index=True)

# Guardar el resultado final
resultado_path = 'data/mistral/procesed/respuesta_mistral.csv'
resultado_df.to_csv(resultado_path, index=False)

print(f"Archivo procesado guardado en: {resultado_path}")
