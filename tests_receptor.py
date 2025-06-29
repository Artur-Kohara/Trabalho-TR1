import numpy as np
from receptor import Receiver
from transmissor import Transmitter

# Configuração genérica para os testes
config = {}
rx = Receiver(config)
tx = Transmitter(config)

def test_bits2Text():
  bits = tx.text2Binary("Hello")
  resultado = rx.bits2Text(bits)
  assert resultado == "Hello", f"Esperado 'Hello', mas retornou '{resultado}'"

################################################################################
# Demodulação (portadora)
################################################################################

def test_demodule_ask():
  original_bits = [1, 0, 1, 1, 0, 0, 1]
  amplitude = 1.0
  frequency = 5  # em Hz ou unidades relativas a 100 amostras por bit

  # Modula os bits
  modulated_signal = tx.ASK(original_bits, amplitude, frequency)

  # Demodula o sinal
  demodulated_bits = rx.demoduleASK(modulated_signal)

  assert demodulated_bits == original_bits, "Erro na demodulação ASK"

def test_demodule_fsk():
  original_bits = [1, 0, 1, 1, 0, 0, 1]
  A = 1.0
  f0 = 5  # Frequência para bit 0
  f1 = 10  # Frequência para bit 1
  bit_samples = 100  # Número de amostras por bit
  # Modula os bits
  modulated_signal = tx.FSK(original_bits, A, f1, f0)
  # Demodula o sinal
  demodulated_bits = rx.demoduleFSK(modulated_signal, f0, f1, A, bit_samples)
  assert demodulated_bits == original_bits, "Erro na demodulação FSK"

def test_QAM8_demodulation():
  # Bits de teste: escolha uma sequência conhecida ou aleatória
  original_bits = [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1]  # 12 bits (4 símbolos de 3 bits)
  amplitude = 1.0
  frequency = 5  # relativa às 100 amostras por símbolo

  # Modulação
  modulated_signal = tx.QAM8(original_bits.copy(), amplitude, frequency)

  # Demodulação
  demodulated_bits_str = rx.demodule8QAM(modulated_signal, A=amplitude, f=frequency)

  assert demodulated_bits_str == original_bits, "Erro na demodulação 8-QAM"

################################################################################
# Desenquadramento
################################################################################

def test_chCountUnframing():
  frame_data = [1, 0, 1, 0, 1, 0, 1, 0]  # 8 bits
  framed_bits = tx.chCountFraming(frame_data, frame_size=8, edc_type="Hamming")
  bitStream = [bit for frame in framed_bits for bit in frame]
  resultado = rx.chCountUnframing(bitStream, "Hamming")
  assert resultado == frame_data, f"Esperado {frame_data}, mas retornou {resultado}"

def test_byteInsertionUnframing():
  bits = [1, 0, 1, 0, 1, 0, 1, 0]
  framed_bits = tx.byteInsertionFraming(bits, frame_size=8, edc_type="Bit de Paridade Par")
  bitStream = [bit for frame in framed_bits for bit in frame]
  resultado = rx.byteInsertionUnframing(bitStream, "Bit de Paridade Par")
  assert resultado == bits, f"Esperado {bits}, mas retornou {resultado}"

def test_bitInsertionUnframing():
  original_bits = [1, 1, 1, 1, 1, 0, 0, 0]
  framed_bits = tx.bitInsertionFraming(original_bits, frame_size=8, edc_type="Bit de Paridade Par")
  bitStream = [bit for frame in framed_bits for bit in frame]
  desenquadrado = rx.bitInsertionUnframing(bitStream, "Bit de Paridade Par")
  assert desenquadrado == original_bits, f"Esperado {original_bits}, mas retornou {desenquadrado}"

################################################################################
# Demodulação (banda base)
################################################################################

def test_polarNRZDecoder():
  bits = [1, 0, 1, 0, 1, 0]
  V = 1
  sinal_modulado = tx.polarNRZCoder(bits, V)
  sinal_demodulado = rx.polarNRZDecoder(sinal_modulado, V)
  assert sinal_demodulado == bits, f"Esperado {bits}, mas retornou {sinal_demodulado}"

def test_manchesterDecoder():
  bits = [1, 0, 1, 0, 1, 0]
  sinal_modulado = tx.manchesterCoder(bits)
  sinal_demodulado = rx.manchesterDecoder(sinal_modulado)
  assert sinal_demodulado == bits, f"Esperado {bits}, mas retornou {sinal_demodulado}"

def test_bipolarDecoder():
  bits = [1, 0, 1, 0, 1, 0, 1, 1]
  V = 1
  sinal_modulado = tx.bipolarCoder(bits, V)
  sinal_demodulado = rx.bipolarDecoder(sinal_modulado)
  assert sinal_demodulado == bits, f"Esperado {bits}, mas retornou {sinal_demodulado}"

################################################################################
# Detecção de erros
################################################################################

def test_checkEvenParity():
  bits = [1, 0, 1, 0, 1, 1]
  bits_pareados = tx.addEvenParityBit(bits)
  # esperado = [1, 0, 1, 0, 1, 1, 0]
  check_parity = rx.checkEvenParityBit(bits_pareados)
  assert check_parity == bits, f"Esperado {bits}, mas retornou {check_parity}"

  wrong_paired_bits = [1, 0, 1, 0, 1, 0]
  check_parity = rx.checkEvenParityBit(wrong_paired_bits)
  assert check_parity == False, f"Esperado {False}, mas retornou {check_parity}"

def test_checkCRC():
  bits = [1,1,0,0, 1,0,1,0, 0,1,1,0]
  bits_CRC = tx.addCRC(bits)
  result = rx.checkCRC(bits_CRC)
  assert result == bits, f"Esperado {bits}, mas retornou {result}"

  wrong_CRC_bits = [1, 0, 1, 0, 0,1,1,1,1,1,1]
  result = rx.checkCRC(wrong_CRC_bits)
  assert result == False, f"Esperado {False}, mas retornou {result}"

def test_checkHamming():
  bits = [1, 0, 1, 0, 1, 1]
  bits_hamming = tx.addHamming(bits)
  result = rx.checkHamming(bits_hamming)
  esperado = [1,0,1,0,1,1]
  assert result == esperado, f"Esperado {esperado}, mas retornou {result}"

  bits_hamming_wrong = [0,1,1,0,0,0,1,1,0,0,1]
  result = rx.checkHamming(bits_hamming_wrong)
  esperado = [1,1,0,1,0,0,1]
  assert result == esperado, f"Esperado {esperado}, mas retornou {result}"

################################################################################
# Fluxo completo de transmissão e recepção
################################################################################

def test_full_transmission_reception():
  # Transmissão
  text = "t"
  bits = tx.text2Binary(text)
  print(f"Bits transmitidos: {bits}")
  framed_bits = tx.byteInsertionFraming(bits, frame_size=8, edc_type="Hamming")
  print(f"Frames transmitidos: {framed_bits}")
  bitStream = [bit for frame in framed_bits for bit in frame]
  modulated_signal = tx.polarNRZCoder(bitStream, 1)
  print(f"Sinal transmitido: {modulated_signal}")

  # Recepção
  print("###############################")
  demodulated_bits = rx.polarNRZDecoder(modulated_signal, 1)
  print(f"Sinal demodulado: {demodulated_bits}")
  unframed_bits = rx.byteInsertionUnframing(demodulated_bits, "Hamming")
  print(f"Bits desenquadrados e sem EDC: {unframed_bits}")
  received_text = rx.bits2Text(unframed_bits)
  assert received_text == text, f"Esperado {text}, mas retornou {received_text}"

################################################################################
# Roda todos os testes
################################################################################

def rodar_todos_os_testes():
  test_bits2Text()
  # Demodulações (portadora)
  test_demodule_ask()
  test_demodule_fsk()
  test_QAM8_demodulation()
  # Desenquadramento
  test_chCountUnframing()
  test_byteInsertionUnframing()
  test_bitInsertionUnframing()
  # Demodulações (banda base)
  test_polarNRZDecoder()
  test_manchesterDecoder()
  test_bipolarDecoder()
  # Detecção de erros
  test_checkEvenParity()
  test_checkCRC()
  test_checkHamming()
  # Fluxo completo de transmissão e recepção
  test_full_transmission_reception()
  print("Todos os testes passaram com sucesso.")

if __name__ == "__main__":
  rodar_todos_os_testes()
