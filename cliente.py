import socket
import json

def send_request(product):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8888))
    client.send(product.encode())
    response = client.recv(4096).decode()
    client.close()
    return json.loads(response)

if __name__ == "__main__":
    while True:
        product = input("Ingrese el nombre del producto a buscar (o 'salir' para terminar): ")
        if product.lower() == 'salir':
            break
        results = send_request(product)
        print(f"\nResultados encontrados para '{product}':")
        for result in results:
            print(f"Título: {result['title']}")
            print(f"Precio: ARS ${result['price']:,.2f}")
            print(f"Enlace: {result['link']}")
            print()