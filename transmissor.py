#Esse arquivo consiste na classe do transmissor e seus métodos.

import numpy as np
import matplotlib.pyplot as plt

class Transmitter:

  #Config é um parâmetro passado na inicialização que controla aspectos do funcionamento do transmissor. ex: bitrate, codificação etc
  def __init__(self, config=None):
    # Configuração padrão otimizada
    self.default_config = {
        'V': 1.0,          #Amplitude para modulações de banda base (float)
        'A': 1.0,          #Amplitude para modulações de banda passante (float)
        'f': 2.0,          #Frequência base (float)
        'f1': 2.0,         #Frequência para bit 1 (FSK) (float)
        'f2': 4.0,         #Frequência para bit 0 (FSK) (float)
        'frame_size': 32,  #Tamanho do quadro em bits (int)
    }
    
    # Mescla configurações
    self.config = {**self.default_config, **(config or {})}
    
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
  def chCountFraming(self, bitStream, frame_size, edc_type):
    frames = [] 
    stream_size = len(bitStream)  

    #Loop para dividir o bitstream em quadros de tamanho frame_size
    for i in range(0, stream_size, frame_size):
        frame_data = bitStream[i: i + frame_size]  #Fatia o bitstream em quadros de tamanho frame_size
        #Aplica EDC na parte de dados do quadro
        if edc_type == "Bit de Paridade Par":
          edc_frame = self.addEvenParityBit(frame_data)
        elif edc_type == "CRC":
          edc_frame = self.addCRC(frame_data)
        elif edc_type == "Hamming":
          edc_frame = self.addHamming(frame_data)
        frame_size_bits = len(frame_data)  #Pode ser menor que frame_size no último quadro
        #Converte o tamanho do quadro (em bits) para uma lista de inteiros representando o binário
        frame_size_binary = [int(bit) for bit in format(frame_size_bits, '08b')]  #8 bits para o tamanho (ate 11111111 = 255)
        frame = frame_size_binary + edc_frame  #Concatenando a contagem de tamanho com os dados binários
        frames.append(frame) 

    return frames

  #Enquadramento com flags e inserção de bytes
  #Recebe um trem de bits (lista de inteiros), e o tamanho inicial do quadro (vai aumentar com inserção de flags e possivelmente de escape)
  #Retorna uma lista de quadros, onde cada quadro é uma lista de inteiros
  def byteInsertionFraming(self, bitStream, frame_size, edc_type):
    frames = []
    flag = [0,1,1,1,1,1,1,0] #0x7E
    escape = [0,1,1,1,1,1,0,1] #0x7D

    stream_size = len(bitStream)
    i = 0

    #Inserção de flags e divisão do bitstream em quadros
    while i < stream_size:
      #Fatia o bitstream em quadros de tamanho inicial frame_size
      frame_data = bitStream[i:i + frame_size]
      #Aplica EDC na parte de dados do quadro
      if edc_type == "Bit de Paridade Par":
        edc_frame = self.addEvenParityBit(frame_data)
      elif edc_type == "CRC":
        edc_frame = self.addCRC(frame_data)
      elif edc_type == "Hamming":
        edc_frame = self.addHamming(frame_data)
      #Verificar se a sequência de flag ocorre no quadro e aplicar byte de escape
      frame_with_escape = self.insertEscapeBytes(edc_frame, flag, escape)
      frame = flag + frame_with_escape + flag
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
  def bitInsertionFraming (self, bitStream, frame_size, edc_type):
    frames = []
    flag = [0,1,1,1,1,1,1,0] #0x7E

    stream_size = len(bitStream)
    i = 0

    #Inserção de flags e divisão do bitstream em quadros
    while i < stream_size:
      #Fatia o bitstream em quadros de tamanho inicial frame_size
      frame_data = bitStream[i:i + frame_size]
      #Aplica EDC na parte de dados do quadro
      if edc_type == "Bit de Paridade Par":
        edc_frame = self.addEvenParityBit(frame_data)
      elif edc_type == "CRC":
        edc_frame = self.addCRC(frame_data)
      elif edc_type == "Hamming":
        edc_frame = self.addHamming(frame_data)
      #Verificar se a sequência de 5 bits 1 seguidos ocorre e aplicar bit 0 após a sequência
      edc_frame = self.insertBit0(frame_data)
      frame = flag + edc_frame + flag
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
  # Modulação digital (banda base) 
  #############################################

  #Modulação NRZ Polar: bit = 1 -> sinal em +V e bit = 0 -> sinal em -V
  #Recebe um trem de bits (lista de bits) e a amplitude do sinal (V), por padrão = 1
  #Retorna lista de amplitudes do sinal modulado
  def polarNRZCoder(self, bitStream, V):
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

  #Modulação Bipolar(AMI): 0 é representado por 0 e 1 alterna entre V e -V
  #Recebe um trem de bits (lista de bits)
  #Retorna lista de amplitudes do sinal modulado
  def bipolarCoder(self,bitStream,V):
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

  #Adiciona bit de paridade ao final do frame. Bit = 0 se soma de 1's for par e 1 se ímpar
  #Recebe frame (lista de bits)
  #Retorna o trem de bits, adicionando um bit de paridade ao final
  def addEvenParityBit(self,frame):
    sum_ones = sum(frame)
    parity = sum_ones % 2  #0 se par, 1 se ímpar
    return frame + [parity]

  #Calcula e adiciona o CRC usando o polinômio gerador pré definido, neste caso o CRC-7 = 0x87 ou 1000 0111 (grau 7)
  #Recebe frame (lista de bits)
  #Retorna o trem de bits, adicionando o CRC ao final
  def addCRC(self,frame):
    gen_poly = [1,0,0,0, 0,1,1,1]
    degree = len(gen_poly) - 1 #Grau do polinômio
    dividend = frame.copy() + [0]*degree #Cópia de frame, adicionando n zeros ao final, em que n é o grau do polinômio (grau 7)

    for i in range(len(frame)):
      #Se o bit atual for 1, faz XOR com cada bit do polinômio gerador
      if dividend[i] == 1:
        for j in range (len(gen_poly)): 
          dividend[i+j] = dividend[i+j] ^ gen_poly[j]

    #Os últimos 7 bits (grau) do dividendo são o CRC
    crc = dividend[-degree:]
    return frame + crc

  #Calcula e adiciona os bits de paridade nas posições que são potências de 2
  #Recebe frame (lista de bits)
  #Retorna o trem de bits, com os bits de paridade adicionados nas posições corretas
  def addHamming(self, frame):
    #Calcula o número de bits de paridades necessários
    m = len(frame)
    p = 0
    while 2**p < m + p + 1: #Precisamos que 2**p seja pelo menos igual ao tamanho total após o hamming + 1 (caso em que não ha erro) para codificar todas as posições de erro
        p += 1
    num_parity_bits = p

    #Insere zeros nas posições que são potências de 2
    for i in range(num_parity_bits):
      frame.insert((2**i)-1,0) #-1 pq indexação começa em 0 

    #Tamanho total depois da inserção dos bits de paridade
    n = len(frame)

    #Calcula cada bit de paridade
    #Para cada bit de paridade, faz XOR dos bits que ele cobre
    for i in range(num_parity_bits):
      parity_pos = 2**i -1
      parity = 0

      #Percorre todas as posições do frame (indexação 1 para facilitar o cálculo)
      #parity_pos +1 pq: ex: i = 2, parity_pos = 3, os bits que i cobre são 100, 101, 110 e 111, todos começam a partir de 100(4) = parity_pos + 1
      for j in range(parity_pos+1, n+1):  
        #Verifica se a posição j (em binário) do frame tem o i-ésimo bit setado 
        #Condição é verdadeira para qualquer número diferente de zero. Ex: 010 & 010 = 010, que é != 0, então entra no if
        if j & (1<<i): #& faz and bit a bit. j está na sua representação binária. 1<<i desloca 1 i vezes à esquerda
          parity ^= frame[j-1] #j-1 para ajustar a indexação em 0

      #Atualiza paridade no bit de posição parity_pos
      frame[parity_pos] = parity 

    return frame


  #############################################
  # Plotagem de gráficos
  #############################################

  #Plota sinais de modulação digital em banda base.
  #Recebe trem de bits(lista de inteiros), tipo de modulação (string) e valor de tensão V(float)
  def plot_baseband(self, bitStream, modulation_type, V=None):
    if V is None:
      V = self.config['V']
    
    # Gera o sinal modulado
    if modulation_type.lower() == 'nrz':
      signal = self.polarNRZCoder(bitStream, V)
      time_scale = np.arange(len(signal))  # 1 amostra por bit
      bit_duration = 1
    elif modulation_type.lower() == 'manchester':
      signal = self.manchesterCoder(bitStream)
      # Corrige a escala de tempo: 2 amostras por bit, mas 1 unidade de tempo por bit
      time_scale = np.arange(0, len(bitStream), 0.5)
      bit_duration = 1
    elif modulation_type.lower() == 'bipolar':
      signal = self.bipolarCoder(bitStream, V)
      time_scale = np.arange(len(signal))
      bit_duration = 1
    else:
      raise ValueError("Tipo de modulação inválido")

    plt.figure(figsize=(12, 4))
    
    # Plotagem especial para Manchester
    if modulation_type.lower() == 'manchester':
      plt.step(time_scale, signal, where='post', linewidth=2)
      # Adiciona marcadores no MEIO de cada bit (transição Manchester)
      for i in range(len(bitStream)):
        plt.axvline(x=i + 0.5, color='g', linestyle=':', alpha=0.4)  # Linha no meio do bit
    else:
      plt.step(time_scale, signal, where='post', linewidth=2)
    
    # Configurações comuns
    plt.title(f"Modulação {modulation_type.upper()} - Bits: {bitStream}")
    plt.xlabel("Tempo (unidades de bit)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    
    # Limites do eixo Y
    if modulation_type.lower() == 'nrz':
      plt.ylim(-V*1.2, V*1.2)
    elif modulation_type.lower() == 'manchester':
      plt.ylim(-0.2, 1.2)
    else:  # bipolar
      plt.ylim(-V*1.2, V*1.2)
    
    # Marcadores de início de bit
    for i in range(len(bitStream) + 1):
      plt.axvline(x=i, color='r', linestyle='-', alpha=0.3)  # Linhas vermelhas marcando início de cada bit
    
    plt.tight_layout()
    plt.show()

  #Plota sinais de modulação digital em banda passante
  #Recebe trem de bits (lista de inteiros), tipo de modulação (string), Amplitude, frequência, frequência 1 e 2(FSK), em que todos são floats
  def plot_passband(self, bitStream, modulation_type, A=None, f=None, f1=None, f2=None):
    # Usa valores da configuração se não fornecidos
    A = A or self.config['A']
    f = f or self.config['f']
    f1 = A or self.config['f1']
    f2 = f or self.config['f2']
    
    # Gera o sinal modulado
    if modulation_type.lower() == 'ask':
        signal = self.ASK(bitStream, A, f)
        samples_per_bit = 100
    elif modulation_type.lower() == 'fsk':
        f1 = f1 or self.config['f1']
        f2 = f2 or self.config['f2']
        signal = self.FSK(bitStream, A, f1, f2)
        samples_per_bit = 100
    elif modulation_type.lower() == 'qam':
        signal = self.QAM8(bitStream, A, f)
        samples_per_bit = 33  # 100 amostras / 3 bits
    else:
        raise ValueError("Tipo de modulação inválido. Use 'ask', 'fsk' ou 'qam'")

    plt.figure(figsize=(12, 4))
    
    # Cria eixo de tempo em unidades de bit
    t = np.arange(len(signal)) / samples_per_bit
    
    # Plotagem
    plt.plot(t, signal, linewidth=1.5)
    
    # Configurações
    plt.title(f"Modulação {modulation_type.upper()} - Bits: {bitStream}")
    plt.xlabel("Tempo (em unidades de bit)")
    plt.ylabel("Amplitude")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Adiciona marcadores de bits
    num_bits = len(bitStream)
    for i in range(num_bits + 1):
        plt.axvline(x=i, color='r', linestyle=':', alpha=0.4)
    
    plt.tight_layout()
    plt.show()
