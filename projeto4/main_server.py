#####################################################
# Camada Física da Computação
# Enricco Gemha
# 15/09/2022
# Projeto 4
####################################################


from itertools import count
from enlace import *
from utils import *
import time
import numpy as np

# python -m serial.tools.list_ports (communication port label)

serial_name = '/dev/cu.usbmodem1201'
msg_server = Message()
verifier = Verifier(from_server=False)


def main():
    com1 = enlace(serial_name); com1.enable(); print("Abriu a comunicação")
    try:
        msg_server.set_msg_type(2)
        msg_server.set_HEAD()
        pkg_handshake_from_server = msg_server.make_pkg()

        rxBuffer, _ = com1.getData(1); com1.rx.clearBuffer(); time.sleep(.1)
        print('1 byte de sacrifício recebido. Limpou o buffer')

        idle = True
        while idle:
            if not(com1.rx.getIsEmpty()):
                handshake_from_client, _ = com1.getData(14)
                handshake_is_correct = verifier.verify_handshake(handshake_from_client)
                if handshake_is_correct:
                    print("Handshake está correto."); idle = False
            time.sleep(1)
        com1.sendData(pkg_handshake_from_server); time.sleep(.1)
        
        img_received_bin = b''
        
        counter = 1
        number_of_packages = handshake_from_client[3]
        while counter <= number_of_packages:
            timer1 = Timer(2)
            timer2 = Timer(20)
            while True:
                pkg_type3 = [0]
                if not(com1.rx.getIsEmpty()):
                    pkg_type3, payload_from_pkg_type3 = get_pkg_type3(com1)
                pkg_is_type3 = verifier.verify_pkg_type3(pkg_type3)
                if not(pkg_is_type3):
                    time.sleep(1)
                    if timer2.is_timeout():
                        msg_server.set_msg_type(5)
                        msg_server.set_HEAD()
                        pkg_type5 = msg_server.make_pkg()
                        com1.sendData(pkg_type5); time.sleep(.1)
                        print('Comunicação encerrada'); idle = True; com1.disable()
                    if timer1.is_timeout():
                        timer1.reset()
                    continue
                if pkg_is_type3:
                    eop_is_correct = verifier.verify_eop(pkg_type3)
                    order_is_correct = (counter == pkg_type3[4])
                    if eop_is_correct and order_is_correct:
                        msg_server.set_msg_type(4)
                        msg_server.set_last_pkg_sucesfully_received(counter)
                        msg_server.set_HEAD()
                        pkg_type4 = msg_server.make_pkg()
                        com1.sendData(pkg_type4); time.sleep(.1)
                        counter += 1
                        img_received_bin += payload_from_pkg_type3
                        break
                    if not(eop_is_correct) or not(order_is_correct):
                        msg_server.set_msg_type(6)
                        msg_server.set_HEAD(expected_pkg_number=counter)
                        pkg_type6 = msg_server.make_pkg()
                        com1.sendData(pkg_type6); time.sleep(.1)
                        break

        img_received_name = 'projeto4/img/recebido.PNG'
        f = open(img_received_name, 'wb')
        f.write(img_received_bin)
        f.close()
        print('Arquivo recebido integralmente.\nTransmissão bem sucedida'); com1.disable()





    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()


    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
