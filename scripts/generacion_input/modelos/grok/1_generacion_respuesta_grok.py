import os
import re
import time
import pandas as pd
from datasets import Dataset
from openai import OpenAI
from tqdm import tqdm
import openai  # para acceder a las excepciones de OpenAI

# ========================================
# 1. Configuración de rutas, cliente y archivos de checkpoint
# ========================================
prompts_file_path = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\pacientes\prompt_usado.txt"
csv_base_path = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\grok\raw\respuesta_modelo"
checkpoint_file = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\checkpoint.txt"

# Clave API (mantenla segura y no la expongas públicamente)
XAI_API_KEY = "Tu api Key"

# Inicializa el cliente de OpenAI
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"  # Ajusta según tu endpoint
)

# ========================================
# 2. Recuperar el checkpoint (último prompt procesado)
# ========================================
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        try:
            start_index = int(f.read().strip())
        except ValueError:
            start_index = 0
else:
    start_index = 0

# ========================================
# 3. Lectura de todas las líneas y creación del dataset
# ========================================
with open(prompts_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

qa_pairs = []
for line in lines:
    line = line.strip()
    # Separa la parte de "Instrucciones/rol" de "Opciones de pacientes"
    parts = re.split(r'Opciones de pacientes:', line)
    if len(parts) == 2:
        question_part = parts[0].strip()
        context_part_and_more = parts[1].strip()
        context_and_response_expected = re.split(r'Respuesta esperada:', context_part_and_more)
        context_part = (context_and_response_expected[0].strip()
                        if len(context_and_response_expected) == 2
                        else context_part_and_more)
    else:
        question_part = line
        context_part = ''
    
    qa_pairs.append({
        'question': question_part,
        'context': context_part
    })

dataset = Dataset.from_pandas(pd.DataFrame(qa_pairs))
total_prompts = len(dataset)
print(f"Se van a procesar {total_prompts} prompts.")
print(f"Reanudando desde el prompt {start_index}.")

# ========================================
# 4. Preparar o cargar los DataFrames para guardar respuestas (5 en total)
# ========================================
num_respuestas = 5
df_respuestas = []
for i in range(num_respuestas):
    csv_filename = f"{csv_base_path}_{i+1}.csv"
    if os.path.exists(csv_filename):
        # Cargar el CSV existente para no sobrescribir las respuestas previas
        df = pd.read_csv(csv_filename, encoding='utf-8')
    else:
        df = pd.DataFrame(columns=["prompt_index", "question", "context", "respuesta"])
    df_respuestas.append(df)

# ========================================
# 5. Procesamiento iterativo: máximo 1100 prompts por iteración y 8 iteraciones por ejecución
# ========================================
max_requests_per_iter = 1100  # prompts a procesar en cada iteración
max_iterations = 8            # número máximo de iteraciones en esta ejecución
current_index = start_index
iteration_count = 0

while iteration_count < max_iterations and current_index < total_prompts:
    iter_end = min(current_index + max_requests_per_iter, total_prompts)
    print(f"\n--- Iniciando iteración {iteration_count + 1} (prompts {current_index} a {iter_end - 1}) ---")
    
    # Variable para almacenar el instante en que se recibe la última respuesta de la API
    last_api_time = None

    for idx in tqdm(range(current_index, iter_end), desc=f"Iteración {iteration_count + 1}", unit="prompt"):
        row = dataset[idx]
        question = row["question"]
        context = row["context"]
        
        messages = [
            {"role": "system", "content": question},
            {"role": "user", "content": context}
        ]
        
        # Realizar la llamada a la API; en caso de error por límite, esperar y reintentar.
        try:
            completion = client.chat.completions.create(
                model="grok-2-1212",  # Ajusta según el modelo que uses
                messages=messages,
                n=num_respuestas
            )
        except openai.error.RateLimitError as e:
            print(f"\nRateLimitError en el prompt {idx + 1}: {e}\nEsperando 60 segundos antes de reintentar...")
            time.sleep(60)
            completion = client.chat.completions.create(
                model="grok-2-1212",
                messages=messages,
                n=num_respuestas
            )
        
        # Actualizar el tiempo de la última respuesta recibida
        last_api_time = time.time()
        
        # Guardar las respuestas: se agregan al final de cada DataFrame
        for choice_idx, choice in enumerate(completion.choices):
            respuesta_text = choice.message.content
            new_row = pd.DataFrame({
                "prompt_index": [idx],
                "question": [question],
                "context": [context],
                "respuesta": [respuesta_text]
            })
            df_respuestas[choice_idx] = pd.concat([df_respuestas[choice_idx], new_row], ignore_index=True)
    
    # Actualizar el índice global y el contador de iteraciones
    current_index = iter_end
    iteration_count += 1
    
    # Guardar el checkpoint para reanudar la próxima ejecución desde aquí
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        f.write(str(current_index))
    print(f"Checkpoint guardado: siguiente prompt a procesar = {current_index}")
    
    # Guardar o actualizar los CSV (se escribe todo, incluyendo respuestas previas)
    for i in range(num_respuestas):
        csv_filename = f"{csv_base_path}_{i+1}.csv"
        df_respuestas[i].to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Se ha guardado/actualizado el archivo: {csv_filename}")
    
    # Esperar hasta que hayan transcurrido 3600 segundos + 10 minutos (4200 segundos)
    # desde que se recibió la última respuesta (última llamada a la API)
    if last_api_time is not None:
        elapsed_since_last_api = time.time() - last_api_time
        total_wait_time = 3600 + 600  # 4200 segundos en total
        if elapsed_since_last_api < total_wait_time:
            sleep_time = total_wait_time - elapsed_since_last_api
            print(f"Iteración {iteration_count} completada. Esperando {sleep_time:.2f} segundos hasta la siguiente iteración.")
            time.sleep(sleep_time)
        else:
            print("La iteración tomó más de 4200 segundos desde la última respuesta, iniciando la siguiente sin pausa adicional.")
    else:
        print("No se registró tiempo de respuesta, procediendo sin espera adicional.")

print("\nProceso completado (o se llegó al final de los prompts).")
