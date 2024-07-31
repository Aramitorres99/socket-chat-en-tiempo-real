import socket
import threading #Permite ejecutar múltiples tareas (hilos) al mismo tiempo.
import sys #Proporciona acceso a algunas funciones del sistema, como la salida estándar.

HOST = '127.0.0.1'  # Dirección del servidor
PORT = 65123        # Puerto de envío

stop_receiving = False  # Variable para indicar cuándo detener la recepción

def receive_messages(sock):
    '''Función que se ejecuta en un hilo separado para recibir mensajes del servidor.'''
    global stop_receiving
    while not stop_receiving:
        try:
            message = sock.recv(1024)
            if not message:
                print("Conexión cerrada por el servidor.")
                break
            print('\nRecibido:', message.decode())
            print("Escribe tu mensaje: ", end="")
            sys.stdout.flush() #Asegura que el mensaje del prompt se muestre inmediatamente.
        except:
            if not stop_receiving:
                print("Error recibiendo el mensaje.")
            break
    sock.close() #Cierra el socket después de salir del bucle.

def send_messages(sock):
    '''Función que se ejecuta en un hilo separado para enviar mensajes al servidor.'''
    global stop_receiving
    while True:
        try:
            message = input("Escribe tu mensaje: ")
            if message.lower() == 'salir':
                print("Desconectando...")
                stop_receiving = True
                sock.sendall(b'__DESCONECTAR__')  # Enviar un mensaje especial
                sock.close()
                break
            sock.sendall(message.encode())
        except:
            print("Error enviando el mensaje.")
            break

def main():
    '''La función principal que ejecuta el cliente'''
    global stop_receiving
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # Crear hilos para manejar la recepción y envío de mensajes
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        send_thread = threading.Thread(target=send_messages, args=(s,))

        receive_thread.start()
        send_thread.start()

        send_thread.join() #Espera a que el hilo de envío termine.
        if s.fileno() != -1: # Verifica si el socket aún está abierto.
            s.close()
        stop_receiving = True
        receive_thread.join()

if __name__ == "__main__": # Verifica si el script se está ejecutando directamente (no importado como módulo).
    main() # Llama a la función principal para iniciar el cliente.
