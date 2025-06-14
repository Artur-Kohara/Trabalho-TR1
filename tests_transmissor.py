#Arquivo de testes simples para os métodos da classe transmissor

from transmissor import Transmitter

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
        1,1,1,1,1,0,0,1,1,1,1,1,0,1,0,  #Dados com bits 0 inseridos
        0,1,1,1,1,1,1,0]  #Flag
  ]
  print(f"bitInsertionFraming: {result} | Esperado: {expected} | {'✅' if result == expected else '❌'}\n")

if __name__ == "__main__":
  test_text2Binary() #OK
  
  #Enquadramentos
  test_chCountFraming() #OK
  test_byteInsertionFraming() #OK
  test_bitInsertionFraming() #OK

  #Modulação digital (banda base)