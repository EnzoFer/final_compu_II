import socket
import json

def send_request(product):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('server', 8888))
    client.send(product.encode())
    response = client.recv(8192).decode()
    client.close()
    return json.loads(response)

def display_results(country, results, exchange_rates):
    print(f"\nResultados encontrados en {country.capitalize()}:")
    for result in results:
        print(f"Título: {result['title']}")
        if result['currency'] == 'ARS':
            print(f"Precio: ARS ${result['price']:,.2f}")
            if 'price_usd' in result:
                print(f"Precio en USD: ${result['price_usd']:,.2f}")
        elif result['currency'] == 'CLP':
            print(f"Precio: CLP ${result['price']:,.0f}")
            if 'price_usd' in result:
                print(f"Precio en USD: ${result['price_usd']:,.2f}")
        else:
            print(f"Precio: {result['currency']} {result['price']:,.2f}")
        print(f"Enlace: {result['link']}")
        print()

if __name__ == "__main__":
    while True:
        product = input("Ingrese el nombre del producto a buscar (o 'salir' para terminar): ")
        if product.lower() == 'salir':
            break
        results = send_request(product)
        exchange_rates = results.get('exchange_rates')
        if exchange_rates:
            print(f"Tasas de cambio actuales: 1 USD = {exchange_rates['ARS']:.2f} ARS, 1 USD = {exchange_rates['CLP']:.2f} CLP")
        display_results('argentina', results['argentina'], exchange_rates)
        display_results('chile', results['chile'], exchange_rates)