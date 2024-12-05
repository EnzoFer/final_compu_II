import socket
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
import json

API_BASE_URL = "https://api.mercadolibre.com/sites/MLA/search"

def search_product(product):
    params = {
        'q': product,
        'limit': 5
    }
    response = requests.get(API_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data.get('results', []):
            title = item.get('title', 'Sin título')
            price = item.get('price', 'Precio no disponible')
            link = item.get('permalink', 'Enlace no disponible')
            results.append({
                'title': title,
                'price': price,
                'link': link
            })
        return results if results else [{"title": "No se encontraron productos", "price": "", "link": ""}]
    else:
        return [{"title": "Error al buscar productos", "price": "", "link": ""}]

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request: {request}")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future = executor.submit(search_product, request)
        results = future.result()
    
    response = json.dumps(results)
    client_socket.send(response.encode())
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