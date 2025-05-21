from openai import OpenAI
import os
from datasets import Dataset
import pandas as pd
import re
import concurrent.futures
from tqdm import tqdm  # Para la barra de progreso

# Configuración de la API y rutas de archivos
api_key_deepseek = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key_deepseek, base_url="https://api.deepseek.com")
prompts_file_path = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\pacientes\prompt_usado.txt"
csv_base_path = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\deepseek\raw"

def process_prompt(idx, line):
    """
    Procesa la línea, separa la información en dos partes y realiza la llamada a la API.
    Devuelve un diccionario que incluye:
      - index_sent: índice asignado al enviar el prompt.
      - index_received: índice recibido (igual al enviado) para control de calidad.
      - question, context y response.
    """
    line = line.strip()
    # Separa "Instrucciones/rol" de "Opciones de pacientes"
    parts = re.split(r'Opciones de pacientes:', line)
    if len(parts) == 2:
        question_part = parts[0].strip()
        context_part_and_more = parts[1].strip()
        # Separamos "Respuesta esperada" si existe
        context_and_response_expected = re.split(r'Respuesta esperada:', context_part_and_more)
        context_part = (context_and_response_expected[0].strip() 
                        if len(context_and_response_expected) == 2 
                        else context_part_and_more)
    else:
        question_part = line
        context_part = ''

    # Llamada a la API con dos mensajes:
    # - "system": el prompt principal (question_part)
    # - "user": el contexto (context_part)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": question_part},
            {"role": "user", "content": context_part},
        ],
        stream=False
    )
    
    answer = response.choices[0].message.content

    # Se asigna el mismo índice recibido para control de calidad
    index_sent = idx
    index_received = idx

    return {
        'index_sent': index_sent,
        'index_received': index_received,
        'question': question_part,
        'context': context_part,
        'response': answer
    }

# Lectura del archivo con prompts
with open(prompts_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Se procesan todas las líneas del archivo
lines_to_process = lines

results = []
# Se especifica un mayor número de trabajadores para enviar más peticiones en paralelo.
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(process_prompt, idx, line) 
               for idx, line in enumerate(lines_to_process, start=1)]
    
    # Barra de progreso para monitorear el avance
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Procesando prompts"):
        result = future.result()
        results.append(result)

# Ordenamos los resultados según el índice asignado al enviar el prompt
results_sorted = sorted(results, key=lambda x: x['index_sent'])

# Verificación de control de calidad: se comprueba que index_sent y index_received coincidan
for item in results_sorted:
    if item['index_sent'] != item['index_received']:
        raise ValueError(f"Desajuste en índices: Enviado {item['index_sent']} - Recibido {item['index_received']}")

# Crea un dataset a partir de los resultados y muestra el total procesado
dataset = Dataset.from_pandas(pd.DataFrame(results_sorted))
total_prompts = len(dataset)
print("Número total de prompts procesados:", total_prompts)

# Guarda los resultados en un archivo CSV
output_csv = os.path.join(csv_base_path, "respuestas_modelo.csv")
df = pd.DataFrame(results_sorted)
df.to_csv(output_csv, index=False)
print("Respuestas guardadas en:", output_csv)
