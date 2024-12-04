import socket
import json

def main():
    # Crear socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))  # Conectar al servidor

    # Solicitar producto al usuario
    product = input("Ingrese el producto que desea buscar: ")

    # Enviar consulta al servidor
    client.send(product.encode('utf-8'))

    try:
        # Recibir respuesta del servidor
        response = client.recv(1024).decode('utf-8')  # Recibe 1024 bytes como máximo
        print("Respuesta recibida del servidor:", response)  # Agrega esta línea
        results = json.loads(response)

        # Mostrar resultados
        print("\nResultados:")
        for platform, products in results.items():
            print(f"\n{platform}:")
            for product in products:
                print(f"- {product['name']} (${product['price']}) - {product['url']}")

    except Exception as e:
        print(f"Error al recibir los resultados: {e}")


    client.close()

if __name__ == '__main__':
    main()
