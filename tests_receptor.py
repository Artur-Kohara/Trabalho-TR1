import numpy as np
from receptor import Receptor

# Configuração genérica para os testes
config = {}
rx = Receptor(config)

def test_bits2Text():
    bits = "0100100001100101011011000110110001101111"  # "Hello"
    resultado = rx.bits2Text(bits)
    assert resultado == "Hello", f"Esperado 'Hello', mas retornou '{resultado}'"

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

def test_chCountUnframing():
    frame_data = [1, 0, 1, 0, 1, 0, 1, 0]  # 8 bits
    tamanho = [0, 0, 0, 0, 1, 0, 0, 0]  # 8 bits = 8 em decimal
    frame = tamanho + frame_data
    resultado = rx.chCountUnframing([frame])
    assert resultado == "10101010", f"Esperado '10101010', mas retornou '{resultado}'"

def test_byteInsertionUnframing():
    flag = [0, 1, 1, 1, 1, 1, 1, 0]
    escape = [0, 1, 1, 1, 1, 1, 0, 1]
    byte = [1, 0, 1, 0, 1, 0, 1, 0]
    frame = flag + byte + flag
    resultado = rx.byteInsertionUnframing([frame])
    assert resultado == "10101010", f"Esperado '10101010', mas retornou '{resultado}'"

def rodar_todos_os_testes():
    test_bits2Text()
    test_demodule_ask()
    test_demodule_fsk()
    test_chCountUnframing()
    test_byteInsertionUnframing()
    print("Todos os testes passaram com sucesso.")

if __name__ == "__main__":
    rodar_todos_os_testes()
