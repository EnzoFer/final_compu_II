import socket
import threading

def handle_client(client_socket):
    # Recibir solicitud del cliente
    product = client_socket.recv(1024).decode('utf-8')
    print(f"Buscando productos relacionados con: {product}")

    # Realizar scraping concurrente
    results = {}
    threads = []

    def scrape_ml():
        results['Mercado Libre'] = scrape_mercado_libre(product)

    def scrape_amz():
        results['Amazon'] = scrape_amazon(product)

    t1 = threading.Thread(target=scrape_ml)
    t2 = threading.Thread(target=scrape_amz)

    t1.start()
    t2.start()
    threads.append(t1)
    threads.append(t2)

    for thread in threads:
        thread.join()

    # Imprimir los resultados antes de enviarlos
    print("Enviando resultados:", results)

    # Enviar resultados al cliente
    client_socket.send(json.dumps(results).encode('utf-8'))
    client_socket.close()

def main():
    print("Inicializando servidor...")
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket creado.")
        server.bind(('localhost', 12345))
        print("Socket enlazado en el puerto 12345.")
        server.listen(5)
        print("Servidor escuchando en el puerto 12345...")
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        return

    while True:
        try:
            print("Esperando conexiones...")
            client_socket, addr = server.accept()
            print(f"Conexión establecida con {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
        except Exception as e:
            print(f"Error manejando cliente: {e}")

if __name__ == '__main__':
    main()
