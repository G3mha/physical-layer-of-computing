import time
import numpy as np
from math import ceil


class Message():
    def __init__(self):
        self.EOP = b'\xAA\xBB\xCC\xDD'

    def set_msg_type(self, msg_type):
        self.msg_type = msg_type

    def set_amount_of_pkgs(self, amount_of_pkgs):
        self.amount_of_pkgs = amount_of_pkgs
    
    def set_last_pkg_sucesfully_received(self, last_pkg_sucesfully_received):
        self.last_pkg_sucesfully_received = last_pkg_sucesfully_received

    def set_HEAD(self, current_pkg_number=0, current_payload_size=0, expected_pkg_number=0):

        if self.msg_type == 1: # handshake from client to server (question)
            server_ID = 9 # server ID attached to message
            list_HEAD = [self.msg_type,0,0,self.amount_of_pkgs,0,server_ID,0,0,0,0]
        
        if self.msg_type == 2: # handshake from server to client (answer)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,0,0,0]

        if self.msg_type == 3: # data from client to server (payload not 0)
            list_HEAD = [self.msg_type,0,0,self.amount_of_pkgs,current_pkg_number,current_payload_size,0,0,0,0]

        if self.msg_type == 4: # payload check from server to client (sucessfully received)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,self.last_pkg_sucesfully_received,0,0]

        if self.msg_type == 5: # timeout connection from any to other (end communication)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,0,0,0]

        if self.msg_type == 6: # error on package from server to client (missing bytes or incorrect format or unexpected package)
            list_HEAD = [self.msg_type,0,0,0,0,0,expected_pkg_number,0,0,0]

        self.HEAD = bytes(list_HEAD)

    def set_list_payload(self, list_payload):
        self.list_payload = list_payload

    def make_pkg(self):
        payload = self.list_payload[self.current_pkg_number]
        pkg = self.HEAD + payload + self.EOP
        return pkg



def timer(tempo_ref):
    tempo_atual = float(time.time())
    referencia = float(tempo_atual-tempo_ref)
    return referencia 

def verifica_handshake(head, is_server):
    """
    Função que verifica se o handshake é a resposta esperada (SIM)
    """
    handshake = head[:2] # primeiro e segundo bytes do head
    delta_t = 0
    conferencia = bytes([5,1])
    if not is_server:
        conferencia = bytes([4,0])
    while delta_t <= 5: # loop para gerar o timeout
        tempo_atual = float(time.time())
        if handshake == conferencia: # 5 é a mensagem de handshake e 1 é a resposta positiva
            print('Handshake realizado com sucesso')
            return True
        delta_t = atualiza_tempo(tempo_atual)
    return False

def verifica_eop(pacote, head):
    """
    Função que verifica se o payload é o mesmo que o esperado e se o pacote está correto
    """
    # head = pacote[:10]
    tamanho = head[2]
    eop = pacote[10+tamanho:]
    if eop == b'\xAA\xAA\xAA\xAA':
        print('Payload recebido integramente. Esperando novo pacote')
        return True
    print('Erro no EOP enviado. Tente novamente.')
    return False

def verifica_ordem(recebido, numero_do_pacote_atual):
    """
    Como combinado o byte que diz o número do pacote é o de número 4 do head ,
    função que será utilizada pelo server
    """
    head = recebido[0:11]
    numero_do_pacote = head[3]
    if numero_do_pacote == numero_do_pacote_atual:
        return True
    return False


def monta_payload(img):
    """
    Lembremos que o payload tem tamanho máximo de 114 bytes, então se uma informação tiver um tamanho maior
    terá que enviar pacotes de 114 ou menos até que a informação inteira seja recebida
    """
    img_bin = open(img,'rb').read()
    tamanho = len(img_bin)
    pacotes = ceil(tamanho/114)
    payloads = []
    for i in range(pacotes):
        if i == (pacotes-1):
            payload = img_bin[114*i:tamanho]
            print('tamanho do ultimo payload ' , len(payload))
        else:
            payload = img_bin[114*i:(i+1)*114]
            print('tamanho dos payloads intermediarios : ',len(payload))
        payloads.append(payload)
    return payloads

def reagrupamento(lista_dos_payloads,tamanho_total_da_info, numero_de_pacotes_recebidos):
    """
    Nessa função iremos juntar os payloads dos pacotes recebidos e verificar se o número de pacotes recebidos foi correto 
    """
    info_total = ''
    for payload in lista_dos_payloads:
        info_total += payload
    
    if numero_de_pacotes_recebidos == tamanho_total_da_info:
        return True
    else:
        return False
        
def tratar_pacote_recebido(pacote):

    tamanho_pacote = len(pacote)
    head = pacote[0:10]

    tamanho = head[2]
    payload = pacote[10:10+tamanho]

    eop = pacote[10+tamanho:len(pacote)]
    # eop = pacote[tamanho_pacote-4:tamanho_pacote]

    return head,payload,eop
    

def retirando_informacoes_do_head(head):

    # tamanho_pacote = len(pacote)
    # head = pacote[0:10]

    tamanho_do_payload = head[2]
    numero_do_pacote = head[3]
    numero_total_de_pacotes = head[4]
    # payload = pacote[10:10+tamanho]

    # eop = pacote[10+tamanho:len(pacote)]
    # eop = pacote[tamanho_pacote-4:tamanho_pacote]

    return tamanho_do_payload,numero_do_pacote, numero_total_de_pacotes