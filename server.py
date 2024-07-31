import socket
import selectors

HOST = '127.0.0.1'  # Dirección del servidor
PORT = 65123        # Puerto de escucha

# Crear un selector para manejar eventos de I/O
sel = selectors.DefaultSelector()

# Función para aceptar nuevas conexiones
def accept(sock):
    '''función que el servidor usa para aceptar nuevas conexiones de clientes'''
    conn, addr = sock.accept() 
    print(f'Conectado a: {addr}')
    conn.setblocking(False) #pasa a estar en no bloqueante el modo del servidor
    sel.register(conn, selectors.EVENT_READ, read)

# Función para leer datos de los clientes y realizar broadcast
def read(conn):
    '''función que lee mensajes de los clientes y envía esos mensajes a todos los demás clientes.'''
    try:
        data = conn.recv(1024)
        if data:
            if data == b'__DESCONECTAR__':
                print(f'Cliente se desconectó voluntariamente: {conn.getpeername()}')
                sel.unregister(conn)
                conn.close()
            else:
                broadcast(data, conn)
        else:
            print(f'Cliente desconectado: {conn.getpeername()}')
            sel.unregister(conn)
            conn.close()
    except ConnectionResetError:
        print(f'Cliente desconectado abruptamente: {conn.getpeername()}')
        sel.unregister(conn)
        conn.close()

# Función para enviar mensajes a todos los clientes conectados excepto al remitente
def broadcast(message, sender_conn):
    '''función que envía el mensaje a todos los clientes conectados, excepto al que envió el mensaje original.'''
    for key in sel.get_map().values():  #Recorre todos los sockets que sel está vigilando.
        sock = key.fileobj #Obtiene el socket del cliente.
        if sock is not sender_conn and sock is not server:
            try:
                sock.sendall(message)
            except Exception as e:
                print(f'Error enviando mensaje a {sock.getpeername()}: {e}')

# Crear y configurar el socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen() #Configura el socket para aceptar conexiones.
server.setblocking(False) # Hace que el socket no se bloquee
sel.register(server, selectors.EVENT_READ, accept)

print(f'Servidor iniciado en {HOST} :{PORT}')

try:
    while True:
        events = sel.select() #Espera a que ocurran eventos en los sockets y los obtiene.
        for key, mask in events:
            callback = key.data #Obtiene la función que debe manejar el evento.
            callback(key.fileobj) # Llama a la función con el socket correspondiente.
except KeyboardInterrupt:
    print('Servidor detenido')
finally:
    sel.close()
    server.close()
