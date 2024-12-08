import requests
import json
import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE_URL_ARG = "https://api.mercadolibre.com/sites/MLA/search"
API_BASE_URL_CHL = "https://api.mercadolibre.com/sites/MLC/search"
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"

def get_exchange_rates():
    try:
        response = requests.get(EXCHANGE_RATE_API)
        data = response.json()
        return {
            'ARS': data['rates']['ARS'],
            'CLP': data['rates']['CLP']
        }
    except Exception as e:
        print(f"Error al obtener tasas de cambio: {e}")
        return None

def search_product(product, country_url):
    params = {
        'q': product,
        'limit': 5,
        'sort': 'relevance'
    }
    response = requests.get(country_url, params=params)
    if response.status_code == 200:
        data = response.json()
        raw_results = data.get('results', [])
        
        filtered_results = [
            {
                'title': item.get('title', 'Sin título'),
                'price': item.get('price', 0),
                'link': item.get('permalink', 'Enlace no disponible'),
                'currency': item.get('currency_id', '')
            }
            for item in raw_results if item.get('price') is not None
        ]
        
        return filtered_results if filtered_results else [{"title": "No se encontraron productos", "price": 0, "link": "", "currency": ""}]
    else:
        return [{"title": "Error al buscar productos", "price": 0, "link": "", "currency": ""}]

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        print(f"Received request: {request}")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(get_exchange_rates): 'exchange_rates',
                executor.submit(search_product, request.strip(), API_BASE_URL_ARG): 'argentina',
                executor.submit(search_product, request.strip(), API_BASE_URL_CHL): 'chile'
            }
            
            results = {'exchange_rates': None, 'argentina': [], 'chile': []}
            
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    print(f"Error en {key}: {e}")
        
        if results['exchange_rates']:
            for country in ['argentina', 'chile']:
                for result in results[country]:
                    if result['currency'] == 'ARS':
                        result['price_usd'] = result['price'] / results['exchange_rates']['ARS']
                    elif result['currency'] == 'CLP':
                        result['price_usd'] = result['price'] / results['exchange_rates']['CLP']
        
        response = json.dumps(results, ensure_ascii=False)
        client_socket.send(response.encode())
    except Exception as e:
        print(f"Error handling client: {e}")
        error_response = json.dumps({'argentina': [{"title": "Error interno", "price": 0, "link": "", "currency": ""}],
                                     'chile': [{"title": "Error interno", "price": 0, "link": "", "currency": ""}],
                                     'exchange_rates': None})
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