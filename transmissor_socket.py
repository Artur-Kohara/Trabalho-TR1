import socket
import pickle
from transmissor import Transmitter

HOST = '127.0.0.1'
PORT = 5000

# Define transmissor como cliente
def socketTrasmission(config_transmissao):
    text = config_transmissao['text']
    framing = config_transmissao['framing']
    edc = config_transmissao['edc']
    mod_bb = config_transmissao['modulacao_bb']
    mod_bp = config_transmissao['modulacao_bp']

    tx = Transmitter({})

    # Texto para bits
    bits = tx.text2Binary(text)

    # Enquadramento
    if framing == "Cont. de Caracteres":
        frames = tx.chCountFraming(bits, 32)
    elif framing == "Inserção de Bits":
        frames = tx.bitInsertionFraming(bits, 32)
    elif framing == "Inserção de Bytes":
        frames = tx.byteInsertionFraming(bits, 32)
    else:
        frames = [bits]  # fallback

    # Unifica os frames em uma única lista de bits
    framed_stream = [bit for frame in frames for bit in frame]

    # EDC
    if edc == "Bit de Paridade Par":
        edc_stream = tx.addEvenParityBit(framed_stream)
    elif edc == "CRC":
        edc_stream = tx.addCRC(framed_stream)
    elif edc == "Hamming":
        edc_stream = tx.addHamming(framed_stream)
    else:
        edc_stream = framed_stream

    # Modulação BB (banda base)
    if mod_bb == "NRZ":
        signal_bb = tx.polarNRZCoder(framed_stream)
    elif mod_bb == "Manchester":
        signal_bb = tx.manchesterCoder(framed_stream)
    elif mod_bb == "Bipolar":
        signal_bb = tx.bipolarCoder(framed_stream)
    else:
        signal_bb = edc_stream

    # Modulação por portadora
    if mod_bp == "ASK":
        modulated_signal = tx.ASK(framed_stream, A=1, f=1000)
    elif mod_bp == "FSK":
        modulated_signal = tx.FSK(framed_stream, A=1, f1=2000, f2=1000)
    elif mod_bp == "8-QAM":
        modulated_signal = tx.QAM8(framed_stream, A=1, f=1000)
    else:
        modulated_signal = signal_bb

    # Dados a serem enviados
    package = {
        'signal_bb': signal_bb,
        'signal_bp': modulated_signal,
        'text': text,
        'config': {
            'framing': framing,
            'edc': edc,
            'modulacao_bb': mod_bb,
            'modulacao_bp': mod_bp
        }
    }

    # Serializa e envia
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(pickle.dumps(package))
        print("[Tx] Pacote enviado")
