# Esse arquivo consiste na classe do transmissor e seus métodos.

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

  #TODO: corrigir frame_size, acho que tem erro 
  #Enquadramento por contagem de caracteres
  #Recebe um trem de bits (lista de inteiros), e o tamanho do quadro (32 bits ou 4 bytes)
  #Retorna uma lista de quadros, onde cada quadro é uma lista de inteiros
  def chCountFraming(self, bitStream, frame_size=32):
    frames = [] 
    stream_size = len(bitStream)  

    #Loop para dividir o bitstream em quadros de tamanho frame_size
    for i in range(0, stream_size, frame_size):
        frame_data = bitStream[i: i + frame_size]  #Fatia o bitstream em quadros de tamanho frame_size
        frame_size_bits = len(frame_data)  #Pode ser menor que 32 bits no último quadro
        #Converte o tamanho do quadro (em bits) para uma lista de inteiros representando o binário
        frame_size_binary = [int(bit) for bit in format(frame_size_bits, '06b')]  #6 bits para o tamanho (ate 100000 = 32)
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
