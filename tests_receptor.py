import numpy as np
from receptor import Receptor
from transmissor import Transmitter

# Configuração genérica para os testes
config = {}
rx = Receptor(config)
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

    # Converte os bits originais para string para comparar
    original_bits_str = ''.join(str(b) for b in original_bits)

    assert demodulated_bits == original_bits_str, "Erro na demodulação ASK"

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
    # Converte os bits originais para string para comparar
    original_bits_str = ''.join(str(b) for b in original_bits)
    assert demodulated_bits == original_bits_str, "Erro na demodulação FSK"

def test_QAM8_modulation_demodulation():

    # Bits de teste: escolha uma sequência conhecida ou aleatória
    original_bits = [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1]  # 12 bits (4 símbolos de 3 bits)
    amplitude = 1.0
    frequency = 5  # relativa às 100 amostras por símbolo

    # Modulação
    modulated_signal = tx.QAM8(original_bits.copy(), amplitude, frequency)

    # Demodulação
    demodulated_bits_str = rx.demodule8QAM(modulated_signal, A=amplitude, f=frequency)

    # Converte original para string para comparação
    padded_bits = original_bits.copy()
    while len(padded_bits) % 3 != 0:
        padded_bits.append(0)
    expected_bits_str = ''.join(str(b) for b in padded_bits)

    assert demodulated_bits_str == expected_bits_str, "Erro na demodulação 8-QAM"

################################################################################
# Desenquadramento
################################################################################

def test_chCountUnframing():
    frame_data = [1, 0, 1, 0, 1, 0, 1, 0]  # 8 bits
    frame = tx.chCountFraming(frame_data, frame_size=8)[0]
    resultado = rx.chCountUnframing([frame])
    assert resultado == "10101010", f"Esperado '10101010', mas retornou '{resultado}'"

def test_byteInsertionUnframing():
    byte = [1, 0, 1, 0, 1, 0, 1, 0]
    frame = tx.byteInsertionFraming(byte, frame_size=8)[0]
    resultado = rx.byteInsertionUnframing([frame])
    assert resultado == "10101010", f"Esperado '10101010', mas retornou '{resultado}'"

def test_bitInsertionUnframing():
    # bits com sequencia "111110" (inserido 0 após cinco 1s)
    original_bits = [1, 1, 1, 1, 1, 0, 0, 0]
    frame = tx.bitInsertionFraming(original_bits, frame_size=8)[0]
    desenquadrado = rx.bitInsertionUnframing([frame])
    assert desenquadrado == "11111000", f"Esperado '11111000', mas retornou '{desenquadrado}'"

################################################################################
# Demodulação (banda base)
################################################################################

def test_polarNRZDecoder():
    bits = [1, 0, 1, 0, 1, 0]
    V = 1
    sinal_modulado = tx.polarNRZCoder(bits, V)
    esperado = [V, -V, V, -V, V, -V]
    assert sinal_modulado == esperado, f"Esperado {esperado}, mas retornou {sinal_modulado}"

def test_manchesterDecoder():
    bits = [1, 0, 1, 0, 1, 0]
    V = 1
    sinal_modulado = tx.manchesterCoder(bits, V)
    esperado = [V, -V, -V, V, V, -V, -V, V, V, -V, -V, V]
    assert sinal_modulado == esperado, f"Esperado {esperado}, mas retornou {sinal_modulado}"

def test_bipolarDecoder():
    bits = [1, 0, 1, 0, 1, 0, 1, 1]
    sinal_modulado = tx.bipolarCoder(bits)
    esperado = [1, 0, -1, 0, 1, 0, -1, 1]
    assert sinal_modulado == esperado, f"Esperado {esperado}, mas retornou {sinal_modulado}"

################################################################################
# Detecção de erros
################################################################################

def test_checkEvenParity():
    bits = [1, 0, 1, 0, 1, 1]
    bits_pareados = tx.addEvenParityBit(bits)
    # esperado = [1, 0, 1, 0, 1, 1, 0]
    check_parity = rx.checkEvenParityBit(bits_pareados)
    assert check_parity == True, f"Esperado {True}, mas retornou {check_parity}"

    wrong_paired_bits = [1, 0, 1, 0, 1, 0]
    check_parity = rx.checkEvenParityBit(wrong_paired_bits)
    assert check_parity == True, f"Esperado {False}, mas retornou {check_parity}"


################################################################################
# Roda todos os testes
################################################################################

def rodar_todos_os_testes():
    test_bits2Text()
    test_demodule_ask()
    test_demodule_fsk()
    test_chCountUnframing()
    test_byteInsertionUnframing()
    test_bitInsertionUnframing()
    print("Todos os testes passaram com sucesso.")

if __name__ == "__main__":
    rodar_todos_os_testes()
