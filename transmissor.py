#Esse arquivo consiste na classe do transmissor e seus métodos.

import numpy as np

class Transmitter:
  #Config é um parâmetro passado na inicialização que controla aspectos do funcionamento do transmissor. ex: bitrate, codificação etc
  def __init__ (self,config):
    self.config = config

  #Método que recebe uma string e retorna o trem de bits equivalente
  def text2Binary(self, text):
    bitStream = []
    for c in text:
      unicodeValue = ord(c)  # Valor Unicode de cada caractere
      binary = format(unicodeValue, '08b')  # Converte para byte binário
      # Converte cada caractere binário para inteiro e adiciona à lista
      bitStream.extend([int(bit) for bit in binary])  
    return bitStream
  
  
  #############################################
  # Opções de enquadramento
  #############################################

  #Enquadramento por contagem de caracteres
  #Recebe um trem de bits (lista de inteiros), e o tamanho do quadro 
  #Retorna uma lista de quadros, onde cada quadro é uma lista de inteiros
  def chCountFraming(self, bitStream, frame_size):
    frames = [] 
    stream_size = len(bitStream)  

    #Loop para dividir o bitstream em quadros de tamanho frame_size
    for i in range(0, stream_size, frame_size):
        frame_data = bitStream[i: i + frame_size]  #Fatia o bitstream em quadros de tamanho frame_size
        frame_size_bits = len(frame_data)  #Pode ser menor que frame_size no último quadro
        #Converte o tamanho do quadro (em bits) para uma lista de inteiros representando o binário
        frame_size_binary = [int(bit) for bit in format(frame_size_bits, '08b')]  #8 bits para o tamanho (ate 11111111 = 255)
        frame = frame_size_binary + frame_data  #Concatenando a contagem de tamanho com os dados binários
        frames.append(frame) 

    return frames

  #Enquadramento com flags e inserção de bytes
  #Recebe um trem de bits (lista de inteiros), e o tamanho inicial do quadro (vai aumentar com inserção de flags e possivelmente de escape)
  #Retorna uma lista de quadros, onde cada quadro é uma lista de inteiros
  def byteInsertionFraming(self, bitStream, frame_size):
    frames = []
    flag = [0,1,1,1,1,1,1,0] #0x7E
    escape = [0,1,1,1,1,1,0,1] #0x7D

    stream_size = len(bitStream)
    i = 0

    #Inserção de flags e divisão do bitstream em quadros
    while i < stream_size:
      #Fatia o bitstream em quadros de tamanho inicial frame_size
      frame_data = bitStream[i:i + frame_size]
      #Verificar se a sequência de flag ocorre no quadro e aplicar byte de escape
      frame_data = self.insertEscapeBytes(frame_data, flag, escape)
      frame = flag + frame_data + flag
      frames.append(frame)
      #Avançar para o próximo quadro
      i += frame_size

    return frames

  #Função auxiliar que insere bytes de escape quando encontra flag ou escape na fatia do quadro
  #Recebe fatia do quadro, byte de flag e byte de escape, em que todos são listas de bits
  #Retorna lista de bits com os bytes de escape inseridos quando necessário
  def insertEscapeBytes(self,frame_data,flag,escape):
    inserted_data = []
    i = 0
    frame_size_bits = len(frame_data)

    #Processa os bits de byte em byte
    while i < frame_size_bits:
      #Pega o próximo byte (n precisa estar completo)
      byte = frame_data[i:i+8] if i+8 <= frame_size_bits else frame_data[i:]
      #Verifica se byte == flag ou escape, so pega bytes completos 
      if len(byte) == 8 and (byte == flag or byte == escape):
        inserted_data.extend(escape) #Adiciona escape antes do byte
      inserted_data.extend(byte) #Adiciona byte apos escape 
      i += 8 #Próximo byte
    
    return inserted_data

  #Enquadramento com flags e inserção de bits
  #Recebe um trem de bits (lista de inteiros), e o tamanho inicial do quadro (vai aumentar com inserção de flags e possivelmente de bits)
  #Retorna uma lista de quadros, onde cada quadro é uma lista de inteiros
  def bitInsertionFraming (self, bitStream, frame_size):
    frames = []
    flag = [0,1,1,1,1,1,1,0] #0x7E

    stream_size = len(bitStream)
    i = 0

    #Inserção de flags e divisão do bitstream em quadros
    while i < stream_size:
      #Fatia o bitstream em quadros de tamanho inicial frame_size
      frame_data = bitStream[i:i + frame_size]
      #Verificar se a sequência de 5 bits 1 seguidos ocorre e aplicar bit 0 após a sequência
      frame_data = self.insertBit0(frame_data)
      frame = flag + frame_data + flag
      frames.append(frame)
      #Avançar para o próximo quadro
      i += frame_size

    return frames

  #Função auxiliar que insere bit 0 após uma sequência de cinco bits '1' seguidos
  #Recebe fatia do quadro
  #Retorna lista de bits com o bit 0 inserido caso necessário
  def insertBit0(self,frame_data):
    inserted_data = []
    i = 0
    frame_size_bits = len(frame_data)
    counter = 0

    while i < frame_size_bits:
      bit = frame_data[i]
      if bit == 1:
        counter += 1
        inserted_data.append(bit) #Adiciona bit 1 à lista
      else: 
        counter = 0
        inserted_data.append(bit) #Adiciona bit 0 à lista
      if counter == 5:
        inserted_data.append(0) #Adiciona bit 0 após sequência de cinco bits '1' seguidos
        counter = 0
      i += 1 #Avançar para o próximo bit
    
    return inserted_data 

  
  #############################################
  # Protocolos de detecção de erros
  #############################################
  '''
  #Protocolo bit de paridade par
  def bitParity(self,):

  #Protocolo CRC
  def CRC(self,):

  #Protocolo Hamming
  def Hamming(sefl,):
  '''

  #############################################
  # Modulação digital (banda base) 
  #############################################

  #Modulação NRZ Polar: bit = 1 -> sinal em +V e bit = 0 -> sinal em -V
  #Recebe um trem de bits (lista de bits) e a amplitude do sinal (V), por padrão = 1
  #Retorna lista de amplitudes do sinal modulado
  def polarNRZCoder(self, bitStream, V=1):
    modulated_signal = []

    for bit in bitStream:
      modulated_signal.append(V if bit == 1 else -V)

    return modulated_signal

  #Modulação Manchester: 0 é representado por [0, 1] e 1 por [1, 0], oq simula a operação xor entre o trem de bits e o clock, adicionando sincronia
  #Recebe um trem de bits (lista de bits)
  #Retorna um sinal modulado (lista de bits)
  def manchesterCoder(self,bitStream):
    modulated_signal = []

    for bit in bitStream:
      if bit == 0:
        modulated_signal.extend([0, 1]) #0 é representado por [0, 1]. OBS:extend já achata a lista
      else:
        modulated_signal.extend([1, 0]) #1 é representado por [1, 0]

    return modulated_signal

  #Modulação Bipolar(AMI): 0 é representado por 0 e 1 alterna entre V e -V, com V=1 por padrão
  #Recebe um trem de bits (lista de bits)
  #Retorna lista de amplitudes do sinal modulado
  def bipolarCoder(self,bitStream,V=1):
    modulated_signal = []
    last_polarity = -V  #Começa invertido para que o primeiro 1 seja +V

    for bit in bitStream:
      if bit == 0:
        modulated_signal.append(0)  #0 é representado por [0, 0]
      else:
        #Alterna a polaridade para cada 1
        last_polarity = V if last_polarity == -V else -V
        modulated_signal.append(last_polarity)  # 1 é representado por V ou -V

    return modulated_signal


  #############################################
  # Modulação por portadora (banda passante) 
  #############################################

  #Modulação por chaveamento de amplitude: se bit = 1 -> seno com amplitude A. Senão -> amplitude 0
  #Recebe o trem de bits (lista de bits), a Amplitude do seno e a frequência
  #Retorna o sinal modulado pelo chaveamento de amplitude
  def ASK(self, bitStream, A, f):
    sig_size = len(bitStream)
    signal = np.zeros(sig_size * 100, dtype = float) #Cria sinal nulo com 100 amostras por bit

    for i in range(sig_size):
      #Se o bit for 1, gera 100 amostras da portadora com amplitude A
      if bitStream[i] == 1:
        for j in range(100):
          signal[i*100 + j] = A * np.sin(2*np.pi*f*j/100) #j/100 funciona como o tempo t
      #Se o bit for 0, gera 100 amostras nulas 
      else:
        for j in range(100):
          signal[i*100 + j] = 0
              
    return signal

  #Modulação por chaveamento de frequência: se bit = 1 -> portadora com frequência f1. Senão portadora com frequência f2
  #Recebe o trem de bits (lista de bits), a Amplitude do seno e as 2 frequências
  #Retorna o sinal modulado pelo chaveamento de frequência
  def FSK(self, bitStream, A, f1,f2):
    sig_size = len(bitStream)
    signal = np.zeros(sig_size * 100, dtype = float) #Cria sinal nulo com 100 amostras por bit

    for i in range(sig_size):
      #Se o bit for 1, gera 100 amostras da portadora com frequência f1
      if bitStream[i] == 1:
        for j in range(100):
          signal[i*100 + j] = A * np.sin(2*np.pi*f1*j/100) #j/100 funciona como o tempo t
      #Se o bit for 0, gera 100 amostras da portadora com frequência f2
      else:
        for j in range(100):
          signal[i*100 + j] = A * np.sin(2*np.pi*f2*j/100) #j/100 funciona como o tempo t
              
    return signal

  #Modulação por quadratura e amplitude 8QAM: segue uma contelação em que cada ponto corresponde a 3 bits
  #Recebe o trem de bits (lista de bits), a Amplitude e frequência do seno
  #Retorna o sinal modulado pelo chaveamento de quadratura e amplitude
  def QAM8(self,bitStream,A,f):
    # Adiciona zeros ao final caso não seja múltiplo de 3
    while len(bitStream) % 3 != 0:
      bitStream.append(0)

    sig_size = len(bitStream)
    num_symbols = len(bitStream) // 3
    signal = np.zeros(num_symbols * 100, dtype=float)  # 100 amostras por símbolo

    #Associa o trio de bits à uma tupla (I,Q)
    constellation = {
        (0,0,0): (A,0),          
        (0,0,1): (A,A),          
        (0,1,1): (0,A),          
        (0,1,0): (-A,A),         
        (1,1,0): (-A,0),         
        (1,1,1): (-A,-A),        
        (1,0,1): (0,-A),         
        (1,0,0): (A,-A)          
    }

    #Percorrendo o trem de bits e mapeando os símbolos
    for i in range(0, sig_size, 3):  # Lê 3 bits de cada vez
      #Cria tupla de 3 bits do bitStream
      bits = tuple(bitStream[i:i + 3])

      I,Q = constellation[bits]

      #Calcula o sinal para esse símbolo com 100 amostras por bit
      for j in range(100):
        index = (i//3)*100+j
        #Sinal modulado = I*cos(2πft) - Q*sin(2πft)
        signal[index] = I*np.cos(2*np.pi*f*j/100) - Q*np.sin(2*np.pi*f*j/100)

    return signal
      
      
  #############################################
  # Protocolos de detecção de erros (EDC)
  #############################################

  #Adiciona bit de paridade ao final do bitStream. Bit = 0 se soma de 1's for par e 1 se ímpar
  #TODO: add essa linha no receptor: no receptor, verifica-se se a soma dos bits é par. Ao adicionar o bit de paridade, a soma é par se não houver erro.
  #Recebe trem de bits (lista de bits)
  #Retorna o trem de bits, adicionando um bit de paridade ao final
  def addEvenParityBit(self,bitStream):
    sum_ones = sum(bitStream)
    parity = sum_ones % 2  #0 se par, 1 se ímpar
    return bitStream + [parity]

  #Calcula e adiciona o CRC usando o polinômio gerador pré definido, neste caso o CRC-7 = 0x87 ou 1000 0111 (grau 7)
  #Recebe trem de bits (lista de bits)
  #Retorna o trem de bits, adicionando o CRC ao final
  def addCRC(self,bitStream):
    gen_poly = [1,0,0,0, 0,1,1,1]
    dividend = list(bitStream) + [0]*(len(gen_poly)-1) #Cópia de bitStream, adicionando n zeros ao final, em que n é o grau do polinômio (grau 7)

    for i in range(len(bitStream)):
      #Se o bit atual for 1, faz XOR com cada bit do polinômio gerador
      if dividend[i] == 1:
        for j in range (len(gen_poly)): 
          dividend[i+j] = dividend[i+j] ^ gen_poly[j]

    #Os últimos 7 bits (grau) do dividendo são o CRC
    crc = dividend[-7:]
    return bitStream + crc

  def addHamming(self, ... ):