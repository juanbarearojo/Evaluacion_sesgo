import json  # Importa el módulo JSON para trabajar con datos en formato JSON
import os    # Importa el módulo OS para interactuar con el sistema operativo

# Ruta de los archivos
archivo_entrada = 'data/gpt/prompt_gpt_usado.txt'  # Define la ruta del archivo de entrada que contiene los datos
directorio_salida = 'data/gpt/lotes_gpt_jsonl/input/'  # Define la ruta del directorio donde se guardarán los archivos de salida

# Leer las líneas del archivo
with open(archivo_entrada, 'r', encoding='utf-8') as file:  # Abre el archivo de entrada en modo lectura con codificación UTF-8
    datos = file.readlines()  # Lee todas las líneas del archivo y las almacena en la lista 'datos'

# Eliminar los saltos de línea
datos = [linea.strip() for linea in datos]  # Elimina los espacios en blanco y saltos de línea al inicio y final de cada línea

# Dividir las combinaciones en lotes de 100
lotes = [datos[i:i + 1000] for i in range(0, len(datos), 1000)]  # Divide la lista 'datos' en sublistas de 1000 elementos cada una

# Asegurar que el directorio de salida exista
os.makedirs(directorio_salida, exist_ok=True)  # Crea el directorio de salida si no existe, sin generar error si ya existe

# Función para crear un archivo jsonl
def crear_archivo_jsonl(lote, indice_lote):
    archivo_salida = f'{directorio_salida}lote_{indice_lote + 1}.jsonl'  # Define el nombre del archivo de salida basado en el índice del lote
    with open(archivo_salida, 'w', encoding='utf-8') as file:  # Abre el archivo de salida en modo escritura con codificación UTF-8
        for index, combinacion in enumerate(lote):  # Itera sobre cada combinación en el lote con su índice
            json_data = {
                "custom_id": f"request-{indice_lote}-{index}",  # Crea un ID único para la solicitud
                "method": "POST",  # Define el método HTTP a utilizar
                "url": "/v1/chat/completions",  # Define la URL del endpoint
                "body": {
                    "model": "gpt-3.5-turbo-0125",  # Especifica el modelo de lenguaje a utilizar
                    "messages": [
                        {
                            "role": "user",  # Define el rol del mensaje
                            "content": combinacion  # Inserta el contenido de la combinación actual
                        }
                    ],
                    "max_tokens": 1000  # Establece el número máximo de tokens en la respuesta
                }
            }
            file.write(json.dumps(json_data) + '\n')  # Escribe el objeto JSON en el archivo, seguido de un salto de línea

# Crear los archivos jsonl para cada lote
for indice, lote in enumerate(lotes):  # Itera sobre cada lote con su índice
    crear_archivo_jsonl(lote, indice)  # Llama a la función para crear el archivo jsonl correspondiente

print(f"Se han generado {len(lotes)} archivos jsonl en {directorio_salida}")  # Imprime un mensaje indicando la cantidad de archivos generados y su ubicación

