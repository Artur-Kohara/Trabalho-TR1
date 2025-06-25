import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy as np
from transmissor import Transmitter
from receptor import Receiver

class InterfaceGTK(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, title="Simulador de Comunicação")
    self.set_default_size(800, 600)

    self.config = {
      'framing': 'chCount',
      'edc': 'paridade',
      'banda_base': 'nrz',
      'banda_passante': 'ask'
    }

    self.tx = Transmitter(self.config)
    self.rx = Receiver(self.config)

    # Layout principal
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.add(vbox)

    # Entrada de texto
    self.entry = Gtk.Entry()
    self.entry.set_placeholder_text("Digite o texto para transmissão")
    vbox.pack_start(self.entry, False, False, 0)

    # Configurações (comboboxes)
    self._add_comboboxes(vbox)

    # Botões
    self._add_buttons(vbox)

    # Área do gráfico
    self.fig = Figure(figsize=(5, 4), dpi=100)
    self.ax = self.fig.add_subplot(111)
    self.canvas = FigureCanvas(self.fig)
    vbox.pack_start(self.canvas, True, True, 0)

    # Resultado
    self.result_label = Gtk.Label(label="Texto recebido aparecerá aqui")
    vbox.pack_start(self.result_label, False, False, 0)

  def _add_comboboxes(self, vbox):
    # Enquadramento
    self.combo_enq = Gtk.ComboBoxText()
    for enq in ["chCount", "byteInsertion", "bitInsertion"]:
      self.combo_enq.append_text(enq)
    self.combo_enq.set_active(0)
    vbox.pack_start(self.combo_enq, False, False, 0)

    # EDC
    self.combo_edc = Gtk.ComboBoxText()
    for edc in ["paridade", "crc", "hamming"]:
      self.combo_edc.append_text(edc)
    self.combo_edc.set_active(0)
    vbox.pack_start(self.combo_edc, False, False, 0)

    # Banda base
    self.combo_bb = Gtk.ComboBoxText()
    for bb in ["nrz", "manchester", "bipolar"]:
      self.combo_bb.append_text(bb)
    self.combo_bb.set_active(0)
    vbox.pack_start(self.combo_bb, False, False, 0)

    # Banda passante
    self.combo_bp = Gtk.ComboBoxText()
    for bp in ["ask", "fsk", "8qam"]:
      self.combo_bp.append_text(bp)
    self.combo_bp.set_active(0)
    vbox.pack_start(self.combo_bp, False, False, 0)

  def _add_buttons(self, vbox):
    btn_tx = Gtk.Button(label="Transmitir")
    btn_tx.connect("clicked", self.on_transmit_clicked)
    vbox.pack_start(btn_tx, False, False, 0)

    btn_rx = Gtk.Button(label="Receber")
    btn_rx.connect("clicked", self.on_receive_clicked)
    vbox.pack_start(btn_rx, False, False, 0)

  def on_transmit_clicked(self, button):
    text = self.entry.get_text()

    # Atualiza config com seleção do usuário
    self.config['framing'] = self.combo_enq.get_active_text()
    self.config['edc'] = self.combo_edc.get_active_text()
    self.config['banda_base'] = self.combo_bb.get_active_text()
    self.config['banda_passante'] = self.combo_bp.get_active_text()

    self.tx = Transmitter(self.config)

    # 1️⃣ Texto para bits
    bits = self.tx.text2Binary(text)

    # 2️⃣ Enquadramento
    frame_size = 32  # valor fixo ou configurable depois
    if self.config['framing'] == 'chCount':
        frames = self.tx.chCountFraming(bits, frame_size)
    elif self.config['framing'] == 'byteInsertion':
        frames = self.tx.byteInsertionFraming(bits, frame_size)
    else:  # bitInsertion
        frames = self.tx.bitInsertionFraming(bits, frame_size)

    # Junta os frames em um único trem de bits
    framed_bits = [bit for frame in frames for bit in frame]

    # 3️⃣ EDC
    if self.config['edc'] == 'paridade':
        edc_bits = self.tx.addEvenParityBit(framed_bits)
    elif self.config['edc'] == 'crc':
        edc_bits = self.tx.addCRC(framed_bits)
    else:  # hamming
        edc_bits = self.tx.addHamming(framed_bits)

    # 4️⃣ Banda base
    if self.config['banda_base'] == 'nrz':
        bb_signal = self.tx.polarNRZCoder(edc_bits)
    elif self.config['banda_base'] == 'manchester':
        bb_signal = self.tx.manchesterCoder(edc_bits)
    else:  # bipolar
        bb_signal = self.tx.bipolarCoder(edc_bits)

    # 5️⃣ Banda passante
    if self.config['banda_passante'] == 'ask':
        mod_signal = self.tx.ASK(bb_signal, A=1, f=5)
    elif self.config['banda_passante'] == 'fsk':
        mod_signal = self.tx.FSK(bb_signal, A=1, f1=5, f2=10)
    else:  # 8qam
        mod_signal = self.tx.QAM8(bb_signal, A=1, f=5)

    # Armazena para receptor
    self.last_signal = mod_signal

    # Plota
    self.ax.clear()
    self.ax.plot(mod_signal)
    self.canvas.draw()

  def on_receive_clicked(self, button):
    if not hasattr(self, 'last_signal'):
        self.result_label.set_text("Erro: Nenhum sinal transmitido!")
        return

    # Passo 1: demodulação
    bp = self.config['banda_passante']
    if bp == 'ask':
        bits_bb_str = self.rx.demoduleASK(self.last_signal)
    elif bp == 'fsk':
        bits_bb_str = self.rx.demoduleFSK(self.last_signal, f0=1, f1=2)
    elif bp == '8qam':
        bits_bb_str = self.rx.demodule8QAM(self.last_signal)
    else:
        self.result_label.set_text("Erro: Modulação desconhecida")
        return

    # Converte bits_bb_str para lista de ints
    bits_bb = [int(b) for b in bits_bb_str]

    # Passo 2: decodificação banda base
    bb = self.config['banda_base']
    if bb == 'nrz':
        bits_str = self.rx.polarNRZDecoder(bits_bb)
    elif bb == 'manchester':
        bits_str = self.rx.manchesterDecoder(bits_bb)
    elif bb == 'bipolar':
        bits_str = self.rx.bipolarDecoder(bits_bb)
    else:
        self.result_label.set_text("Erro: Codificação desconhecida")
        return

    # Converte para lista de ints
    bits = [int(b) for b in bits_str]

    # Passo 3: desenquadramento
    # Primeiro transforma em lista de frames (ex: lista de listas de bits)
    # Vamos supor que você tenha recebido frames já agrupados ou faça isso por outro método
    # Aqui vamos simular que cada 16 bits são um frame (exemplo, ajuste se necessário)
    frame_size = 32  # ou outro valor conforme seu protocolo
    frames = [bits[i:i+frame_size] for i in range(0, len(bits), frame_size)]

    fr = self.config['framing']
    if fr == 'chCount':
        desenq_str = self.rx.chCountUnframing(frames)
    elif fr == 'byteInsertion':
        desenq_str = self.rx.byteInsertionUnframing(frames)
    elif fr == 'bitInsertion':
        desenq_str = self.rx.bitInsertionUnframing(frames)
    else:
        self.result_label.set_text("Erro: Enquadramento desconhecido")
        return

    desenq_bits = [int(b) for b in desenq_str]

    # Passo 4: EDC
    edc = self.config['edc']
    if edc == 'paridade':
        ok = self.rx.checkEvenParityBit(desenq_bits)
        if not ok:
            self.result_label.set_text("Erro de paridade detectado!")
            return
        bits_final = desenq_bits[:-1]
    elif edc == 'crc':
        ok = self.rx.checkCRC(desenq_bits.copy())  # passa cópia, pois o método altera
        if not ok:
            self.result_label.set_text("Erro de CRC detectado!")
            return
        bits_final = desenq_bits[:-7]  # remove CRC, se necessário
    elif edc == 'hamming':
        bits_corrigido_str, err_pos = self.rx.checkHamming(desenq_bits)
        bits_final = [int(b) for b in bits_corrigido_str]
        if err_pos != 0:
            self.result_label.set_text(f"Hamming corrigiu erro na posição {err_pos}")
    else:
        self.result_label.set_text("Erro: EDC desconhecido")
        return

    # Passo 5: bits para texto
    text_out = self.rx.bits2Text(bits_final)

    # Exibe o texto recebido
    self.result_label.set_text(f"Texto recebido: {text_out}")


def main():
  win = InterfaceGTK()
  win.connect("destroy", Gtk.main_quit)
  win.show_all()
  Gtk.main()



