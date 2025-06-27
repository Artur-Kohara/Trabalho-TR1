# Arquivo onde será desenvolvido o receptor do sistema de comunicação
import numpy as np

class Receiver:
  def __init__(self, config):
    self.config = config

  def receive(self, bits):
    text = self.bits2Text(bits)
    print(f"[Rx] Texto: {text}")
    return text

  def bits2Text(self, bits):
    # Pega o trem de bits e separa em blocos de 8 bits(1 byte)
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    chars = [''.join(map(str, b)) for b in chars]  # Converte cada bloco de bits para string
    # Transforma cada bloco de bits em um inteiro e depois em um caractere (ASCII)
    return ''.join(chr(int(b, 2)) for b in chars)
  
################################################################################
# Demodulação (portadora)
################################################################################

  def demoduleASK(self, signal, bit_samples=100, treshold=0.1):
    """
    signal: array de float, contendo o signal modulado ASK
    bit_samples: número de amostras por bit
    treshold: limiar de decisão da presença de onda
    return: lista de bits
    """
    bits = []

    # Percorre o signal em segments de tamanho bit_samples
    for i in range(0, len(signal), bit_samples):
      # Extrai um segment (correspondente a um bit)
      segment = signal[i:i+bit_samples]
      # Cálculo de energia média do segment (eleva ao quadrado cada amostra e tira a média)
      energy = np.mean(np.square(segment))

      if energy > treshold:
        bits.append(1)
      else:
        bits.append(0)

    return bits

  def demoduleFSK(self, signal, f0, f1, A=1, bit_samples=100):
    """
    Demodula um sinal FSK.

    signal: vetor de floats com o sinal modulado FSK
    f0: frequência associada ao bit 0
    f1: frequência associada ao bit 1
    A: amplitude da portadora (mesmo usado na modulação)
    bit_samples: número de amostras por bit (padrão: 100)
    return: lista de bits
    """
    bits = []
    # Vetor de tempo normalizado de 0 até (quase) 1, com bit_samples amostras
    # Isso representa o tempo de um bit, dividido em partes iguais
    t = np.array([j / bit_samples for j in range(bit_samples)])

    # Sinais senoidais de referência para as frequências f0 e f1
    ref_0 = A * np.sin(2 * np.pi * f0 * t)
    ref_1 = A * np.sin(2 * np.pi * f1 * t)

    # O sinal é percorrido em blocos de bit_samples amostras, cada um representando um bit
    for i in range(0, len(signal), bit_samples):
      segment = signal[i:i + bit_samples]
      # Garante que o último segmento tenha tamanho suficiente (evita erros com pedaços incompletos)
      if len(segment) < bit_samples:
        break

      # Para cada segmento, calcula-se o produto escalar (correlação) com os sinais de referência
      # Se o sinal tem frequência próxima de f1, a correlação com ref_1 será maior (em valor absoluto)
      # Se for f0, a correlação com ref_0 será maior
      cor_0 = np.dot(segment, ref_0)
      cor_1 = np.dot(segment, ref_1)

      # Compara a semelhança do sinal com cada referência.
      # O bit é 1 se o sinal se parece mais com f1; senão, é 0.
      bit = 1 if abs(cor_1) > abs(cor_0) else 0
      bits.append(bit)

    return bits
  
  def demodule8QAM(self, signal, A=1, f=1000, symbol_samples=100):
    """
    Demodula um sinal 8-QAM.
    signal: np.array com o sinal QAM
    A: amplitude usada na modulação
    f: frequência da portadora
    symbol_samples: número de amostras por símbolo (padrão: 100)
    return: lista de bits
    """
    bits = []
    # Vetor de tempo normalizado no intervalo [0, 1) com symbol_samples amostras
    t = np.arange(symbol_samples) / symbol_samples
    cos_wave = np.cos(2 * np.pi * f * t)
    sin_wave = np.sin(2 * np.pi * f * t)

    # Mapa reverso: de (I, Q) → bits
    constellation = {
      (A, 0):     (0, 0, 0),
      (A, A):     (0, 0, 1),
      (0, A):     (0, 1, 1),
      (-A, A):    (0, 1, 0),
      (-A, 0):    (1, 1, 0),
      (-A, -A):   (1, 1, 1),
      (0, -A):    (1, 0, 1),
      (A, -A):    (1, 0, 0),
    }

    # Extrai símbolos do sinal, cada símbolo tem symbol_samples amostras
    # Verifica se há amostras suficientes
    for i in range(0, len(signal), symbol_samples):
      s = signal[i:i+symbol_samples]
      if len(s) < symbol_samples:
        break

      # Estima I e Q por correlação com cosseno e seno
      # (multiplica por 2 / symbol_samples → normalização da correlação)
      I = np.dot(s, cos_wave) * 2 / symbol_samples
      Q = -np.dot(s, sin_wave) * 2 / symbol_samples  # sinal negativo por definição da modulação

      # Arredondar para múltiplos válidos de A (−A, 0, A)
      I_hat = A * round(I / A)
      Q_hat = A * round(Q / A)

      # Tratar casos extremos com pequena margem de erro numérica
      # Garante que I_hat e Q_hat estejam dentro dos limites da constelação
      # I_hat e Q_hat devem estar entre -A e A
      I_hat = max(min(I_hat, A), -A)
      Q_hat = max(min(Q_hat, A), -A)

      # Usa o dicionário da constelação para recuperar os 3 bits correspondentes ao símbolo detectado
      bits_tuple = constellation.get((I_hat, Q_hat))

      bits.extend(bits_tuple)

    return bits
  
################################################################################
# Demodulação (banda base)
################################################################################

  def polarNRZDecoder(self, signal, V=1):
    """
    Decodifica um sinal modulado polar NRZ
    signal: lista de amplitudes do sinal modulado
    V: amplitude do sinal (padrão = 1)
    return: lista de bits
    """
    bits = []
    for amplitude in signal:
      if amplitude >= V:
        bits.append(1)
      elif amplitude <= -V:
        bits.append(0)
  
    return bits
  
  def manchesterDecoder(self, signal):
    """
    Decodifica um sinal modulado Manchester
    signal: lista de amplitudes do sinal modulado
    return: lista de bits
    """
    bits = []
    # Itera sobre os índices do sinal, de 2 em 2, porque cada bit codificado ocupa dois valores no sinal
    for i in range(0, len(signal), 2):
      # Se a primeira metade está alta (1) e a segunda está baixa (0), representa um bit 1
      if (signal[i] == 1) and (signal[i + 1] == 0):
        bits.append(1)
      #Se a primeira metade está baixa (0) e a segunda está alta (1), representa um bit 0
      elif (signal[i] == 0) and (signal[i + 1] == 1):
        bits.append(0)
  
    return bits
  
  def bipolarDecoder(self, signal):
    """
    Decodifica um sinal bipolar AMI
    signal: lista de amplitudes (valores como 0, +1 ou -1)
    V: valor da amplitude (padrão: 1)
    return: lista de bits
    """
    bits = []

    for i in range(0, len(signal)):
      bit = signal[i]
      if bit == 0:
        bits.append(0)
      else:
        bits.append(1)

    return bits

################################################################################
# Desenquadramentos
################################################################################

  def chCountUnframing(self, bitStream):
    """
    Desfaz o enquadramento por contagem de caracteres.
    bitStream: lista de bits (inteiros) no formato [header + dados] * N
    return: lista de bits contendo apenas os dados reais, sem os cabeçalhos.
    """
    i = 0
    recovered_bits = []

    while i < len(bitStream):
        if i + 8 > len(bitStream):
            break  # Não há bits suficientes para o cabeçalho

        # Lê os primeiros 8 bits como cabeçalho (tamanho do frame)
        size_bits = bitStream[i:i+8]
        # Transforma cada elemento em string, concatena, converte os bits para decimal e transforma em inteiro
        frame_size = int(''.join(map(str, size_bits)), 2)

        # Recupera os dados do frame conforme o tamanho informado
        start = i + 8
        end = start + frame_size
        data_bits = bitStream[start:end]

        # Adiciona os dados ao bitstream final
        recovered_bits.extend(data_bits)

        # Avança para o próximo quadro
        i = end

    return recovered_bits
  
  def byteInsertionUnframing(self, bitStream):
    """
    Desenquadra um trem de bits com inserção de bytes.
    Detecta as flags, remove-as e trata escapes.
    bitStream: lista de bits (int) com vários quadros serializados.
    return: lista de bits original, sem bytes de escape nem flags.
    """
    flag = [0, 1, 1, 1, 1, 1, 1, 0]   # 0x7E
    escape = [0, 1, 1, 1, 1, 1, 0, 1] # 0x7D
    recovered_bits = []
    i = 0
    n = len(bitStream)

    while i <= n - 8:
        # Verifica início da flag
        if bitStream[i:i+8] == flag:
            i += 8  # pula flag inicial
            frame_data = []

            # Lê até encontrar próxima flag
            while (i <= n - 8) and (bitStream[i:i+8] != flag):
                byte = bitStream[i:i+8]

                # Verifica se encontrou escape
                if byte == escape and i + 16 <= n:
                    # Caso encontre escape, lê o próximo byte como dado e adiciona ao resultado
                    next_byte = bitStream[i+8:i+16]
                    frame_data.extend(next_byte)
                    i += 16
                else:
                    # Caso não seja escape, adiciona o byte atual ao resultado
                    frame_data.extend(byte)
                    i += 8

            # Se encontrar uma flag final, descarta ela
            if bitStream[i:i+8] == flag:
                i += 8

            # Junta os dados tratados
            recovered_bits.extend(frame_data)
        else:
            i += 1  # avança para tentar encontrar a próxima flag

    return recovered_bits
  
  def bitInsertionUnframing(self, frames):
    """
    Desenquadra os frames por inserção de bits
    frames: lista de frames, onde cada frame é uma lista de bits
    return: string com o trem de bits desenquadrado
    """
    bitStream = []
    flag = [0, 1, 1, 1, 1, 1, 1, 0]
    
    for frame in frames:
      # Verifica se o quadro começa e termina com a flag
      if frame[:8] == flag and frame[-8:] == flag:
        # Remove a flag do início e do fim do quadro
        data_bits = frame[8:-8]

        # Remove os bits 0 inseridos após cinco bits 1
        cleaned_data = self.removeBit0(data_bits)
        bitStream.extend(cleaned_data)

    # Converte a lista de bits para uma string de bits
    return ''.join(map(str, bitStream))
  
  # Função auxiliar que remove o bit 0 inserido após cinco bits 1 seguidos
  def removeBit0(self, frame_data):
    cleaned_data = []
    counter = 0
    i = 0

    while i < len(frame_data):
      bit = frame_data[i]
      cleaned_data.append(bit)

      if bit == 1:
        counter += 1
      else:
        counter = 0

      if counter == 5:
        # Pula o próximo bit (deve ser o 0 inserido)
        i += 1
        counter = 0
      i += 1

    return cleaned_data
  
################################################################################
# Detecção de erros
################################################################################

  def checkEvenParityBit(self, bitStream):
    '''
    Verifica se a soma dos bits 1 é par. Ao adicionar o bit de paridade, a soma é par se não houver erro
    bitstream: Lista de bits com o bit de paridade no final
    return: True se a paridade estiver correta, False se a paridade estiver incorreta
    '''
    # Pega o último bit da lista (bit de paridade)
    parity_bit = bitStream[-1]
    # Recalcula a paridade do trem de bits original (sem o último bit de paridade)
    sum_ones = sum(bitStream[:-1])
    # 0 se for par, 1 se for ímpar
    parity = sum_ones % 2

    # Compara se o bit de paridade enviado bate com a paridade do trem de bits
    if parity == parity_bit:
      return True
    else:
      return False
  
  def checkCRC(self, bitStream):
    '''
    Verifica se o bitStream tem o CRC correto
    bitStream: Lista de bits com o CRC no final
    return: True se o CRC estiver correto, False se o CRC estiver incorreto
    '''
    gen_poly = [1,0,0,0, 0,1,1,1]
    degree = len(gen_poly) - 1 #Grau do polinômio

    for i in range((len(bitStream)) - degree):
      #Se o bit atual for 1, faz XOR com cada bit do polinômio gerador
      if bitStream[i] == 1:
        for j in range (len(gen_poly)): 
          bitStream[i+j] = bitStream[i+j] ^ gen_poly[j]

    #Os últimos 7 bits (grau) do dividendo são o resto da divisão
    remainder = bitStream[-degree:]

    # Se o resto for igual a zero, o CRC está correto
    if remainder == [0] * degree:
      return True
    else:
      return False

  def checkHamming(self, bitStream):
    """
    Verifica e corrige um erro de 1 bit usando código de Hamming
    bitStream: lista de bits codificada com Hamming (incluindo paridade)
    return: (string de bits corrigidos sem bits de paridade, posição do erro ou 0 se não houve erro)
    """
    n = len(bitStream)
    # Armazeno o número de bits de paridade
    p = 0
    # Determina quantos bits de paridade existem com base no tamanho
    while 2**p < n + 1:
      p += 1

    # Variável para armazenar a posição do erro caso exista
    error_pos = 0

    # Verifica cada bit de paridade
    for i in range(p):
      parity_pos = 2**i
      parity = 0

      # Percorre todas as posições do bitStream
      for j in range(1, n+1):
        # Faz "and" entre a posição atual e a posição de paridade
        # Verifica se a potência de 2 (parity_pos) compõe a posição j
        # (Usando o "and" ambos ficam em representação binária)
        # Ex: 011(j) & 010(parity_pos=2) = 1, então entra no if (2 compõe o número 3)
        if j & parity_pos:
          # Faz XOR do bit de paridade com o bit atual e salva o recovered_bitsado da paridade
          parity ^= bitStream[j-1]

      # Salva a posição do erro usando os bits de paridade diferentes de 0
      if parity != 0:
        error_pos += parity_pos

    # Corrige o erro se necessário (error_pos > 0, ou seja, os bits de paridade deram diferente de 0)
    if error_pos != 0 and error_pos <= n:
        bitStream[error_pos - 1] ^= 1  # Inverte o bit errado

    # Remove bits de paridade (posições de potência de 2)
    corrected_bitStream = []
    for i in range(1, n+1):
      # Se a posição não é uma potência de 2, adiciona o bit ao stream corrigido
      if not self._is_power_of_two(i):
        corrected_bitStream.append(bitStream[i-1])

    # Converte a lista de bits corrigidos para string
    corrected_bitStream = ''.join(map(str, corrected_bitStream))
    return corrected_bitStream, error_pos

  # Função auxiliar que verifica se um número é uma potência de dois
  def _is_power_of_two(self, x):
    # Retorna True se x for uma potência de dois, False caso contrário
    # Verifica se x é diferente de zero e faz "and" entre x e (x-1)
    # Sempre que se faz "and" entre um número que é potência de dois e seu antecessor, o recovered_bitsado é 0
    # Exemplo: 4 (100) & 3 (011) = 0
    return x != 0 and (x & (x - 1)) == 0