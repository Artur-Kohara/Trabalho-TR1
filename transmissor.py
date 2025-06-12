# Esse arquivo consiste na classe do transmissor e seus métodos.

class Transmitter:
  #Config é um parâmetro passado na inicialização que controla aspectos do funcionamento do transmissor. ex: bitrate, codificação etc
  def __init__ (self,config):
    self.config = config

  #Método que recebe uma string e retorna o trem de bits equivalente
  def text2Binary (self, text):
    bitStream = ""
    for c in text:
        unicodeValue = ord(c)  #Valor Unicode de cada caractere
        binary = format(unicodeValue, '08b')  #Converte para byte binário
        bitStream += binary  #Concatena o resultado na string final
        bitStream = [int(bit) for bit in bitStream] #Retorna lista de inteiros 
    return bitStream
  
  #############################################
  # Opções de enquadramento
  #############################################
  
  #Enquadramento por contagem de caracteres
  #Recebe um trem de bits (lista de inteiros), e o tamanho do frame (32 bits ou 4 bytes)
  #Retorna uma lista de frames, onde cada frame é uma lista de inteiros
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

  #Enquadramento por 
  def 
