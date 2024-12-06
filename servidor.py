import requests
import json
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

API_BASE_URL = "https://api.mercadolibre.com/sites/MLA/search"

def search_product(product):
    params = {
        'q': product,
        'limit': 50  # Obtener más resultados para un mejor filtrado
    }
    response = requests.get(API_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        raw_results = data.get('results', [])
        
        # Filtrar resultados válidos con precio y ordenarlos por precio ascendente
        filtered_results = [
            {
                'title': item.get('title', 'Sin título'),
                'price': item.get('price', float('inf')),
                'link': item.get('permalink', 'Enlace no disponible')
            }
            for item in raw_results if item.get('price') is not None
        ]
        filtered_results.sort(key=lambda x: x['price'])  # Ordenar por precio

        # Retornar los mejores 5 resultados
        return filtered_results[:5] if filtered_results else [{"title": "No se encontraron productos", "price": "", "link": ""}]
    else:
        return [{"title": "Error al buscar productos", "price": "", "link": ""}]

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        print(f"Received request: {request}")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(search_product, request.strip())
            results = future.result()
        
        response = json.dumps(results, ensure_ascii=False)
        client_socket.send(response.encode())
    except Exception as e:
        print(f"Error handling client: {e}")
        error_response = json.dumps([{"title": "Error interno", "price": "", "link": ""}])
        client_socket.send(error_response.encode())
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen(5)
    print("Server listening on port 8888")

    while True:
        client, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
