#!/usr/bin/env python3

import sys
import logging
import math

from PIL import Image

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QDialog, QTextEdit, QLabel, QWidget, QLineEdit


class MarqueeView:

    table_styles = 'margin:0; padding:0; vertical-align:middle; border-spacing: 0; border-collapse: collapse;'
    td_styles = 'background-color: black; margin:0; padding:0; vertical-align:middle;'

    @staticmethod
    def gcd(a, b):
        if a < b:
            return MarqueeView.gcd(b, a)
        if abs(b) < 0.001:
            return a
        else:
            return MarqueeView.gcd(b, a - math.floor(a / b) * b)

    @staticmethod
    def html_base(content):
        return ''.join([
            '<html>',
            '<head>',
            '<body>',
            content,
            '</body>',
            '</head>',
            '</html>'
        ])

    @staticmethod
    def table(content, styles):
        return ''.join([
            '<table style="{0}">'.format(styles),
            content,
            '<table>'
        ])

    @staticmethod
    def row(content, styles):
        return ''.join([
            '<tr style="{0}">'.format(styles),
            content,
            '</tr>'
        ])

    @staticmethod
    def cell(content, styles):
        return ''.join([
            '<td style="{0}">'.format(styles),
            content,
            '</td>'
        ])

    @staticmethod
    def led_divs(inner_size, outer_width, outer_height, inner_margin_h, inner_margin_v, inner_color):
        return ''.join([
            '<div style="max-width: {0}px; max-height: {1}px;">'.format(outer_width, outer_height),
            '<div style="margin: {0}px {1}px {0}px {1}px; min-width: {2}px; min-height: {2}px; background-color: {3}; '
            'border-radius: 50%;">'.format(inner_margin_h, inner_margin_v, inner_size, inner_color),
            '</div>',
            '</div>',
        ])

    def __init__(self, image_path, num_leds_h, num_leds_v, led_size, led_pitch_h, led_pitch_v):
        img = Image.open(image_path).convert("RGB")
        self.image_path = image_path
        self.num_leds_h = num_leds_h
        self.num_leds_v = num_leds_v
        self.led_size = led_size
        self.led_pitch_h = led_pitch_h
        self.led_pitch_v = led_pitch_v
        self.led_div_dims = self._set_led_div_dimensions()
        self.html = self._create_html(img)

    def _set_led_div_dimensions(self):
        border_size_h = (self.led_pitch_h / 2) - (self.led_size / 2)
        border_size_v = (self.led_pitch_v / 2) - (self.led_size / 2)
        unit_size = MarqueeView.gcd(border_size_h, border_size_v)
        inner_size = int(round(self.led_size / unit_size))
        inner_margin_h = int(round(border_size_h / unit_size))
        inner_margin_v = int(round(border_size_v / unit_size))
        outer_width = inner_size + (inner_margin_h * 2)
        outer_height = inner_size + (inner_margin_v * 2)
        return (inner_size,
                outer_width,
                outer_height,
                inner_margin_h,
                inner_margin_v)

    def _create_html(self, img):
        if (self.num_leds_h, self.num_leds_v) == img.size:
            rows_html = ''
            for v in range(self.num_leds_v):
                row_html = ''
                for h in range(self.num_leds_h):
                    coord = (h, v)
                    div_html = MarqueeView.led_divs(self.led_div_dims[0],
                                                    self.led_div_dims[1],
                                                    self.led_div_dims[2],
                                                    self.led_div_dims[3],
                                                    self.led_div_dims[4],
                                                    '#{0:02x}{1:02x}{2:02x}'.format(*img.getpixel(coord)))
                    row_html = '{0}{1}'.format(row_html, MarqueeView.cell(div_html, MarqueeView.td_styles))
                rows_html = '{0}{1}'.format(rows_html, MarqueeView.row(row_html, ''))
            table_html = MarqueeView.table(rows_html, MarqueeView.table_styles)
            return MarqueeView.html_base(table_html)
        return MarqueeView.html_base('<p>Invalid Image</p>')


options = (
    {'name': 'num_leds_h', 'ctrl_type': QLineEdit, 'help': 'HELP'},
    {'name': 'num_leds_v', 'ctrl_type': QLineEdit, 'help': 'HELP'},
    {'name': 'LED_size', 'ctrl_type': QLineEdit, 'help': 'HELP'},
    {'name': 'led_pitch_h', 'ctrl_type': QLineEdit, 'help': 'HELP'},
    {'name': 'led_pitch_w', 'ctrl_type': QLineEdit, 'help': 'HELP'},
    {'name': 'display_width', 'ctrl_type': QLineEdit, 'help': 'HELP'}
)


class RenderDialog(QDialog):

    @staticmethod
    def title_from_name(name):
        return name.replace('_', ' ').title()

    def __init__(self, opts, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Marquee Renderer')
        self.main_layout = QHBoxLayout()
        self.opts_layout = QVBoxLayout()
        self.text_boxes = {}
        self.view_port = QWebEngineView()
        marquee_view = MarqueeView('marquees/1942_s.png', 128, 32, 2.5, 4, 4)
        self.view_port.setHtml(marquee_view.html)
        self._create_opt_inputs(opts)
        self.main_layout.addLayout(self.opts_layout)
        self.main_layout.addWidget(self.view_port)
        self.setLayout(self.main_layout)
        # self.setLayout(self.opts_layout)

    def _create_user_input_widget(self, *args):
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        for arg in args:
            layout.addWidget(arg)
        self.opts_layout.addWidget(widget)

    def _create_title_label(self, opt):
        title_label = QLabel()
        title_label.setToolTip(opt['help'])
        title_label.setFixedWidth(100)
        title_label.setText(RenderDialog.title_from_name(opt['name']))
        return title_label

    def _create_input_field(self, opt):
        widgets = [self._create_title_label(opt)]
        field = opt['ctrl_type']()
        self.text_boxes[opt['name']] = field
        widgets.append(field)
        self._create_user_input_widget(*widgets)

    def _create_opt_inputs(self, opts):
        for opt in opts:
            self._create_input_field(opt)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
    # pyqtRemoveInputHook()
    app = QApplication(sys.argv)
    # controller = Controller()
    # controller.show_main_window()
    dialog = RenderDialog(options)
    dialog.show()
    sys.exit(app.exec_())
