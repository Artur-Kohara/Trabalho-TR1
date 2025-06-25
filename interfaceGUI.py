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
      'enquadramento': 'chCount',
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
    for bp in ["ask", "fsk", "qam"]:
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
    texto = self.entry.get_text()
    self.config['enquadramento'] = self.combo_enq.get_active_text()
    self.config['edc'] = self.combo_edc.get_active_text()
    self.config['banda_base'] = self.combo_bb.get_active_text()
    self.config['banda_passante'] = self.combo_bp.get_active_text()

    # TODO: executar o transmissor com as configs, gerar sinal
    # Exemplo placeholder: onda senoidal simples
    t = np.linspace(0, 1, 1000)
    y = np.sin(2 * np.pi * 5 * t)

    self.ax.clear()
    self.ax.plot(t, y)
    self.canvas.draw()

  def on_receive_clicked(self, button):
    # TODO: executar receptor, obter texto
    self.result_label.set_text("Texto recebido: (simulação)")

def main():
  win = InterfaceGTK()
  win.connect("destroy", Gtk.main_quit)
  win.show_all()
  Gtk.main()

if __name__ == "__main__":
  main()

