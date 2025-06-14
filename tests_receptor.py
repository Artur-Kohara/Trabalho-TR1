import numpy as np
from receptor import Receptor
from transmissor import Transmitter

# Configuração genérica para os testes
config = {}
rx = Receptor(config)
tx = Transmitter(config)

def test_bits2Text():
    bits = "0100100001100101011011000110110001101111"  # "Hello"
    resultado = rx.bits2Text(bits)
    assert resultado == "Hello", f"Esperado 'Hello', mas retornou '{resultado}'"

################################################################################
# Demodulação (portadora)
################################################################################

def test_demodule_ask():
    # Sinal ASK com 3 bits: "101"
    bps = 100
    onda = np.sin(2 * np.pi * 1000 * np.linspace(0, 0.01, bps, endpoint=False))
    zero = np.zeros(bps)
    sinal = np.concatenate([onda, zero, onda])
    resultado = rx.demodule_ask(sinal, bit_samples=bps)
    assert resultado == "101", f"Esperado '101', mas retornou '{resultado}'"

def test_demodule_fsk():
    bits = "101"
    f0, f1, fs, dur = 1000, 2000, 10000, 0.01
    t = np.linspace(0, dur, int(fs * dur), endpoint=False)
    sinal = []
    for bit in bits:
        f = f1 if bit == "1" else f0
        sinal.extend(np.sin(2 * np.pi * f * t))
    sinal = np.array(sinal)
    resultado = rx.demodule_fsk(sinal, f0=f0, f1=f1, fs=fs, dur=dur)
    assert resultado == "101", f"Esperado '101', mas retornou '{resultado}'"

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
