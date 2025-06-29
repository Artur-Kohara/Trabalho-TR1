# receiver_socket.py
import socket
import pickle
import numpy as np
from receptor import Receiver
from gi.repository import GLib

HOST = '127.0.0.1'
PORT = 5000
rx = Receiver({})

# Atualiza a interface GTK de forma thread-safe
def update_interface(gui, demod_bb, demod_bp, text):
    ax1 = gui.figure_rx_bb.gca()
    ax1.clear()
    ax1.plot(demod_bb)
    ax1.set_title("Demodulação Banda Base")
    gui.canvas_rx_bb.draw()

    ax2 = gui.figure_rx_bp.gca()
    ax2.clear()
    ax2.plot(demod_bp)
    ax2.set_title("Demodulação Portadora")
    gui.canvas_rx_bp.draw()

    gui.label_rx_text.set_text(text)
    return False

def start_receiver(gui):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("[Receptor] Aguardando conexão...")

        conn, addr = s.accept()
        with conn:
            print(f"[Receptor] Conectado a {addr}")
            data = b""
            while True:
                packet = conn.recv(4096)
                if not packet:
                    break
                data += packet

            packet = pickle.loads(data)
            signal_bb = packet['signal_bb']
            signal_bp = packet['signal_bp']
            config = packet['config']

            mod_bp = config.get("mod_bp")
            mod_bb = config.get("mod_bb")
            framing = config.get("framing")
            edc = config.get("edc")

            print(f"[Receptor] Config: {config}")

            # 1. Demodulação de portadora
            if mod_bp == "ASK":
                demod_bp = rx.demoduleASK(signal_bp)
            elif mod_bp == "FSK":
                demod_bp = rx.demoduleFSK(signal_bp, f0=1000, f1=2000)
            elif mod_bp == "8-QAM":
                demod_bp = rx.demodule8QAM(signal_bp)
            else:
                raise ValueError("Modulação de portadora inválida")

            # 2. Demodulação de banda base
            if mod_bb == "NRZ":
                demod_bb = rx.polarNRZDecoder(signal_bb)
            elif mod_bb == "Manchester":
                demod_bb = rx.manchesterDecoder(signal_bb)
            elif mod_bb == "Bipolar":
                demod_bb = rx.bipolarDecoder(signal_bb)
            else:
                raise ValueError("Modulação de banda base inválida")

            # 3. Desenquadramento
            if framing == "Cont. de Caracteres":
                if edc == "Bit de Paridade Par":
                    bitStream = rx.chCountUnframing(demod_bb, "Bit de Paridade Par")
                elif edc == "CRC":
                    bitStream = rx.chCountUnframing(demod_bb, "CRC")
                elif edc == "Hamming":
                    bitStream = rx.chCountUnframing(demod_bb, "Hamming")

            elif framing == "Inserção de Bits":
                if edc == "Bit de Paridade Par":
                    bitStream = rx.bitInsertionUnframing(demod_bb, "Bit de Paridade Par")
                elif edc == "CRC":
                    bitStream = rx.bitInsertionUnframing(demod_bb, "CRC")
                elif edc == "Hamming":
                    bitStream = rx.bitInsertionUnframing(demod_bb, "Hamming")

            elif framing == "Inserção de Bytes":
                if edc == "Bit de Paridade Par":
                    bitStream = rx.byteInsertionUnframing(demod_bb, "Bit de Paridade Par")
                elif edc == "CRC":
                    bitStream = rx.byteInsertionUnframing(demod_bb, "CRC")
                elif edc == "Hamming":
                    bitStream = rx.byteInsertionUnframing(demod_bb, "Hamming")

            else:
                raise ValueError("Enquadramento inválido")

            text = rx.receive(bitStream)

            # Atualizar interface
            GLib.idle_add(update_interface, gui, demod_bb, demod_bp, text)
