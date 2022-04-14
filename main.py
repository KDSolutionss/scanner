import socket
import threading
import urllib.request
from queue import Queue

a = threading.Lock()


def sc_tcp(port, host):
    # Сканирование порта по tcp
    socket.setdefaulttimeout(0.5)
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # осуществляется подключение
        sock_tcp.connect((host, port))
    except (socket.timeout, OSError):
        pass
    try:
        # осуществляется отправка сообщение и ожидается ответ
        sock_tcp.send(b'hello world')
        data = sock_tcp.recv(1024)
        # по принятому сообщению определяется работающий на открытом порте протокол
        if b'HTTP' in data:
            print(port, "TCP HTTP")
        elif b'SSH' in data:
            print(port, "TCP SSH")
        elif data[0:2].isdigit():
            print(port, "TCP SMTP")
        elif data[0] == b'+':
            print(port, "TCP POP3")
        else:
            print(port, 'TCP undefined')
    except socket.error:
        pass


def condition(port, protocol):
    try:
        isOpen = socket.getservbyport(port, protocol)
    except OSError:
        return False
    return isOpen


def checkAccess(port, adress):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as scanner:
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        try:
            # icmp протокол поможет среагировать на возникшую исключительную ситуацию,то есть закрытый порт
            scanner.sendto(b'ping', (adress, port))
            sock1.settimeout(1)
            sock1.recvfrom(1024)
            return False
        except socket.timeout:
            # если исключительной ситуации не возникло,то осуществить проверку,работает ли протокол на указанном порте
            return condition(port, 'udp')
        except socket.error:
            sock1.close()
            return False


def sc_udp(port, adress):
    # Сканирование порта по udp
    if checkAccess(port, adress):
        print('port {} is open'.format(port))


def main(adress):
    #обработка отсутствия доступа в интернет
    def connect():
        try:
            urllib.request.urlopen('http://google.com')
            return True
        except:
            print("no connection")
            return False

    if not connect():
        return
    #обработка неразрешенности доменного имени в ip адрес
    try:
        host = socket.gethostbyname(adress)
    except:
        print("no match")
        return

    def threader():
        #осуществление параллельной реализации
        while True:
            worker = q.get()
            sc_tcp(worker, host)
            q.task_done()

    q = Queue()

    for x in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    for worker in range(1, 1000):
        q.put(worker)

    q.join()


if __name__ == '__main__':
    adress = input('Введите адрес: ')
    main(adress)
    for port in range(1, 65535):
        sc_udp(port, adress)
