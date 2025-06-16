#Arquivo de testes simples para os métodos da classe transmissor

from transmissor import Transmitter
import numpy as np

def test_text2Binary():
  transmitter = Transmitter({})
  # Teste com caractere 'A' (ASCII 65 = 01000001)
  result = transmitter.text2Binary("A")
  expected = [0,1,0,0,0,0,0,1]
  print(f"text2Binary('A'): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")
  
  # Teste com string 'Hi'
  result = transmitter.text2Binary("Hi")
  # H = 72 (01001000), i = 105 (01101001)
  expected = [0,1,0,0,1,0,0,0, 0,1,1,0,1,0,0,1]
  print(f"text2Binary('Hi'): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")


################################################
# Funções de teste para enquadramentos
################################################

def test_chCountFraming():
  transmitter = Transmitter({})
  bit_stream = [1,0,1,1,0,0,1,0, 1,1,0,1,0,1,0,0, 1,0,1]  # 19 bits
  
  # Teste com frame_size=8 bits
  result = transmitter.chCountFraming(bit_stream, 8)
  # Esperado: 
  # - Primeiro quadro: tamanho (00001000) + 8 bits
  # - Segundo quadro: tamanho (00001000) + 8 bits
  # - Terceiro quadro: tamanho (00000011) + 3 bits
  expected = [
      [0,0,0,0,1,0,0,0, 1,0,1,1,0,0,1,0],
      [0,0,0,0,1,0,0,0, 1,1,0,1,0,1,0,0],
      [0,0,0,0,0,0,1,1, 1,0,1]
  ]
  print(f"chCountFraming (frame_size=8): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")

def test_byteInsertionFraming():
  transmitter = Transmitter({})
  bit_stream = [0,1,1,1,1,1,1,0, 1,0,1,0,1,0,1,0]  #Contém flag no início
  
  result = transmitter.byteInsertionFraming(bit_stream, 16)
  # Esperado: flag + (escape + flag) + dados + flag
  expected = [
      [0,1,1,1,1,1,1,0,  # Flag inicial
        0,1,1,1,1,1,0,1,  # Escape (0x7D)
        0,1,1,1,1,1,1,0,  # Flag
        1,0,1,0,1,0,1,0,  # Dados
        0,1,1,1,1,1,1,0]  # Flag final
  ]
  print(f"byteInsertionFraming: {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")

def test_bitInsertionFraming():
  transmitter = Transmitter({})
  bit_stream = [1,1,1,1,1,0,1,1,1,1,1,1,0]  # Duas sequências de cinco 1s
  
  result = transmitter.bitInsertionFraming(bit_stream, 13)
  #Esperado: flag + dados com 0 inserido após cada cinco 1s + flag
  expected = [
      [0,1,1,1,1,1,1,0,  #Flag
        1,1,1,1,1,0,0,1,1,1,1,1,0,1,0, #Dados com bits 0 inseridos
        0,1,1,1,1,1,1,0]  #Flag
  ]
  print(f"bitInsertionFraming: {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")


##########################################################
# Funções de teste para modulação digital (banda base)
##########################################################

def test_polarNRZCoder():
  transmitter = Transmitter({})
  
  # Teste básico com bits alternados
  result = transmitter.polarNRZCoder([1, 0, 1, 0])
  expected = [1, -1, 1, -1]
  print(f"polarNRZCoder([1,0,1,0]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste com amplitude diferente
  result = transmitter.polarNRZCoder([1, 0], V=2)
  expected = [2, -2]
  print(f"polarNRZCoder([1,0], V=2): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste com sequência de 1s
  result = transmitter.polarNRZCoder([1, 1, 1])
  expected = [1, 1, 1]
  print(f"polarNRZCoder([1,1,1]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")

def test_manchesterCoder():
  transmitter = Transmitter({})
  
  # Teste básico com bits alternados
  result = transmitter.manchesterCoder([1, 0])
  expected = [1, 0, 0, 1]
  print(f"manchesterCoder([1,0]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste com sequência de 0s
  result = transmitter.manchesterCoder([0, 0])
  expected = [0, 1, 0, 1]
  print(f"manchesterCoder([0,0]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste com sequência de 1s
  result = transmitter.manchesterCoder([1, 1])
  expected = [1, 0, 1, 0]
  print(f"manchesterCoder([1,1]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")

def test_bipolarCoder():
  transmitter = Transmitter({})
  
  # Teste básico com bits alternados
  result = transmitter.bipolarCoder([1, 0, 1, 0])
  expected = [1, 0, -1, 0]
  print(f"bipolarCoder([1,0,1,0]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste com sequência de 1s (deve alternar polaridade)
  result = transmitter.bipolarCoder([1, 1, 1])
  expected = [1,-1,1]
  print(f"bipolarCoder([1,1,1]): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste com amplitude diferente
  result = transmitter.bipolarCoder([1, 0, 1], V=2)
  expected = [2,0,-2]
  print(f"bipolarCoder([1,0], V=2): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")


##########################################################
# Funções de teste para modulação por portadora
##########################################################

def test_ASK():
  transmitter = Transmitter({})
  
  # Teste básico com bits alternados
  bits = [1, 0, 1]
  result = transmitter.ASK(bits, A=1.0, f=1.0)
  
  # Verifica o tamanho do sinal (100 amostras por bit)
  print(f"ASK tamanho do sinal: {len(result)} | Esperado: {len(bits)*100} | {'✅' if len(result) == len(bits)*100 else '❌'}")
  
  # Verifica amostras específicas
  print(f"ASK primeiro bit (deve ter seno): {result[:5]} | Esperado: não zeros | {'✅' if any(result[:100]) else '❌'}")
  print(f"ASK segundo bit (deve ser zero): {result[100:105]} | Esperado: [0,0,0,0,0] | {'✅' if not any(result[100:200]) else '❌'}")
  print(f"ASK terceiro bit (deve ter seno): {result[200:205]} | Esperado: não zeros | {'✅' if any(result[200:300]) else '❌'}\n")

def test_FSK():
  transmitter = Transmitter({})
  
  # Teste básico com bits alternados
  bits = [1, 0, 1]
  result = transmitter.FSK(bits, A=1.0, f1=1.0, f2=2.0)
  
  # Verifica o tamanho do sinal
  print(f"FSK tamanho do sinal: {len(result)} | Esperado: {len(bits)*100} | {'✅' if len(result) == len(bits)*100 else '❌'}")
  
  # Verifica amostras específicas
  print(f"FSK primeiro bit (f1=1.0): {result[:5]} | Padrão esperado para f=1.0 | {'✅' if result[1] > 0.06 and result[1] < 0.07 else '❌'}")
  print(f"FSK segundo bit (f2=2.0): {result[100:105]} | Padrão esperado para f=2.0 | {'✅' if result[101] > 0.125 and result[101] < 0.126 else '❌'}")
  print(f"FSK terceiro bit (f1=1.0): {result[200:205]} | Padrão esperado para f=1.0 | {'✅' if result[201] > 0.06 and result[201] < 0.07 else '❌'}\n")

def test_QAM8():
  transmitter = Transmitter({})
  A = 1.0
  f = 1.0
  tol = 1e-6  # Tolerância para comparação de floats

  # Teste 1: Símbolo [1,0,1] -> (I, Q) = (0, -A)
  bits = [1, 0, 1]
  result = transmitter.QAM8(bits, A, f)
  
  # Verificação de valores
  # Para (I,Q) = (0,-1), s(t) = 0*cos(2πft) - (-1)*sin(2πft) = sin(2πft)
  expected_sample_0 = 0.0  # sin(0) = 0
  expected_sample_25 = 1.0  # sin(2π*0.25) = sin(π/2) = 1
  expected_sample_50 = 0.0  # sin(2π*0.5) = sin(π) = 0
  
  print(f"QAM8 [1,0,1] amostra 0: {result[0]} | Esperado: {expected_sample_0} | {'✅' if abs(result[0] - expected_sample_0) < tol else '❌'}")
  print(f"QAM8 [1,0,1] amostra 25: {result[25]} | Esperado: {expected_sample_25} | {'✅' if abs(result[25] - expected_sample_25) < tol else '❌'}")
  print(f"QAM8 [1,0,1] amostra 50: {result[50]} | Esperado: {expected_sample_50} | {'✅' if abs(result[50] - expected_sample_50) < tol else '❌'}")

  # Teste 2: Símbolo [0,0,0] -> (I, Q) = (A, 0)
  bits = [0, 0, 0]
  result = transmitter.QAM8(bits, A, f)
  
  # Para (I,Q) = (1,0), s(t) = 1*cos(2πft) - 0*sin(2πft) = cos(2πft)
  expected_sample_0 = 1.0  # cos(0) = 1
  expected_sample_25 = 0.0  # cos(2π*0.25) = cos(π/2) ≈ 0
  expected_sample_50 = -1.0  # cos(2π*0.5) = cos(π) = -1
  
  print(f"QAM8 [0,0,0] amostra 0: {result[0]} | Esperado: {expected_sample_0} | {'✅' if abs(result[0] - expected_sample_0) < tol else '❌'}")
  print(f"QAM8 [0,0,0] amostra 25: {result[25]} | Esperado: {expected_sample_25} | {'✅' if abs(result[25] - expected_sample_25) < tol else '❌'}")
  print(f"QAM8 [0,0,0] amostra 50: {result[50]} | Esperado: {expected_sample_50} | {'✅' if abs(result[50] - expected_sample_50) < tol else '❌'}")

  # Teste 3: Símbolo [0,0,1] -> (I, Q) = (A, A)
  bits = [0, 0, 1]
  result = transmitter.QAM8(bits, A, f)
  
  # Para (I,Q) = (1,1), s(t) = cos(2πft) - sin(2πft)
  expected_sample_0 = 1.0  # cos(0) - sin(0) = 1 - 0 = 1
  expected_sample_12 = 0.0  # cos(2π*0.12) ≈ cos(43.2°) ≈ 0.73, sin(43.2°) ≈ 0.68 → 0.73 - 0.68 ≈ 0.05
  # Vamos calcular o valor exato para t=0.125 (j=12.5, mas j é inteiro)
  t = 12/100
  expected_sample_12 = np.cos(2*np.pi*f*t) - np.sin(2*np.pi*f*t)
  
  print(f"QAM8 [0,0,1] amostra 0: {result[0]} | Esperado: {1.0} | {'✅' if abs(result[0] - 1.0) < tol else '❌'}")
  print(f"QAM8 [0,0,1] amostra 12: {result[12]} | Esperado: {expected_sample_12} | {'✅' if abs(result[12] - expected_sample_12) < tol else '❌'}")

  # Teste 4: Preenchimento de bits [1,0] -> completa para [1,0,0] -> (I,Q) = (A, -A)
  bits = [1, 0]
  result = transmitter.QAM8(bits, A, f)
  
  # Para (I,Q) = (1,-1), s(t) = cos(2πft) - (-1)*sin(2πft) = cos(2πft) + sin(2πft)
  expected_sample_0 = 1.0  # cos(0) + sin(0) = 1 + 0 = 1
  expected_sample_25 = 1.0  # cos(π/2) + sin(π/2) = 0 + 1 = 1
  
  print(f"QAM8 [1,0] preenchido amostra 0: {result[0]} | Esperado: {1.0} | {'✅' if abs(result[0] - 1.0) < tol else '❌'}")
  print(f"QAM8 [1,0] preenchido amostra 25: {result[25]} | Esperado: {1.0} | {'✅' if abs(result[25] - 1.0) < tol else '❌'}")

  # Teste 5: Múltiplos símbolos [0,0,0, 1,0,1]
  bits = [0,0,0, 1,0,1]
  result = transmitter.QAM8(bits, A, f)
  
  # Primeiro símbolo [0,0,0] (índices 0-99)
  print(f"QAM8 múltiplos símbolos - primeiro símbolo amostra 0: {result[0]} | Esperado: {1.0} | {'✅' if abs(result[0] - 1.0) < tol else '❌'}")
  
  # Segundo símbolo [1,0,1] (índices 100-199)
  print(f"QAM8 múltiplos símbolos - segundo símbolo amostra 100: {result[100]} | Esperado: {0.0} | {'✅' if abs(result[100] - 0.0) < tol else '❌'}\n")


##########################################################
# Funções de teste para detecção de erro
##########################################################

def test_addEvenParityBit():
  transmitter = Transmitter({})
  
  # Teste 1: Número par de 1s (deve adicionar 0)
  bits = [1, 0, 1, 0]  # 2 uns (par)
  result = transmitter.addEvenParityBit(bits)
  expected = bits + [0]
  print(f"addEvenParityBit({bits}): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste 2: Número ímpar de 1s (deve adicionar 1)
  bits = [1, 1, 1, 0]  # 3 uns (ímpar)
  result = transmitter.addEvenParityBit(bits)
  expected = bits + [1]
  print(f"addEvenParityBit({bits}): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste 3: Stream vazio (deve adicionar 0)
  bits = []  # 0 uns (par)
  result = transmitter.addEvenParityBit(bits)
  expected = bits + [0]
  print(f"addEvenParityBit({bits}): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste 4: Todos 1s (par)
  bits = [1, 1, 1, 1]  # 4 uns (par)
  result = transmitter.addEvenParityBit(bits)
  expected = bits + [0]
  print(f"addEvenParityBit({bits}): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}")
  
  # Teste 5: Todos 0s (par)
  bits = [0, 0, 0, 0]  # 0 uns (par)
  result = transmitter.addEvenParityBit(bits)
  expected = bits + [0]
  print(f"addEvenParityBit({bits}): {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")


def test_addCRC():
  transmitter = Transmitter({})
  
  # Teste 1: Bitstream simples que deve gerar CRC conhecido
  bits = [1, 0, 1, 0]  # 0xA
  result = transmitter.addCRC(bits)
  expected_crc = [0,1,1,0,1,1,0]
  expected_result = bits + expected_crc
  print(f"addCRC({bits}): {result[-7:]} | CRC Esperado: {expected_crc} | {'✅' if result[-7:] == expected_crc else '❌'}")

  # Teste : Bitstream simples que deve gerar CRC conhecido
  bits = [0,0,0,1]  
  result = transmitter.addCRC(bits)
  expected_crc = [0,0,0,0,1,1,1]
  expected_result = bits + expected_crc
  print(f"addCRC({bits}): {result[-7:]} | CRC Esperado: {expected_crc} | {'✅' if result[-7:] == expected_crc else '❌'}")
  
  # Teste 2: Bitstream vazio (deve retornar apenas o CRC)
  bits = []
  result = transmitter.addCRC(bits)
  expected_crc = [0,0,0,0,0,0,0]
  expected_result = bits + expected_crc
  print(f"addCRC({bits}): {result} | Esperado: {expected_result} | {'✅' if result == expected_result else '❌'}")
  
  # Teste 3: Bitstream com todos 1s
  bits = [1, 1, 1, 1]  # 0xF
  result = transmitter.addCRC(bits)
  expected_crc = [0,1,0,1,1,0,1]
  print(f"addCRC({bits}): {result[-7:]} | CRC Esperado: {expected_crc} | {'✅' if result[-7:] == expected_crc else '❌'}")
  
  # Teste 4: Bitstream longo
  bits = [1,1,0,0, 1,0,1,0, 0,1,1,0]  # 0xCA6
  result = transmitter.addCRC(bits)
  # Verificação indireta - testando propriedades do CRC
  print(f"addCRC(long stream): CRC length={len(result[-7:])} | Esperado: 7 | {'✅' if len(result[-7:]) == 7 else '❌'}")
  
  # Teste 5: Verificação round-trip
  bits = [1, 0, 1, 1, 0, 1]
  crc_appended = transmitter.addCRC(bits)
  # Deve ser possível verificar recalculando
  verification = transmitter.addCRC(crc_appended)
  # Os últimos 7 bits devem ser zeros
  print(f"Verificação round-trip: {verification[-7:]} | Esperado: [0,0,0,0,0,0,0] | {'✅' if all(b == 0 for b in verification[-7:]) else '❌'}\n")


################################################
# Chama as funções de teste
################################################

if __name__ == "__main__":
  test_text2Binary() #OK
  
  #Enquadramentos
  test_chCountFraming() #OK
  test_byteInsertionFraming() #OK
  test_bitInsertionFraming() #OK

  #Modulação digital (banda base)
  test_polarNRZCoder() #OK
  test_manchesterCoder() #OK
  test_bipolarCoder() #OK

  #Modulação por portadora (banda passante)
  test_ASK() #OK
  test_FSK() #OK
  test_QAM8() #TODO: checar com mais calma
  
  #Detecção de erro
  test_addEvenParityBit() #OK
  test_addCRC() #Acho que OK