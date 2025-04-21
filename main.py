from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import get_color_from_hex as rgb
import base64, zlib, marshal, re

class Decoder:
    @staticmethod
    def decode(script: str) -> str:
        try:
            result = script
            for _ in range(7):
                new_result = Decoder.try_decode_once(result)
                if new_result == result:
                    break
                result = new_result
            result = Decoder.clean_lambda_stub(result)
            return result
        except Exception as e:
            return f"[!] Decode Error:\n{str(e)}"

    @staticmethod
    def try_decode_once(data: str) -> str:
        try: return base64.b64decode(data).decode()
        except: pass
        try: return zlib.decompress(base64.b64decode(data)).decode()
        except: pass
        try: return str(marshal.loads(base64.b64decode(data)))
        except: pass
        try:
            if "base64" in data and "eval" in data:
                inner = re.findall(r"b64decode\(['\"]?(.*?)['\"]?\)", data)
                if inner:
                    decoded = base64.b64decode(inner[0]).decode()
                    return decoded
        except: pass
        return data

    @staticmethod
    def clean_lambda_stub(code: str) -> str:
        code = re.sub(r"eval\(lambda: ?(.*?)\)\(\)", r"\1", code)
        code = re.sub(r"exec\(lambda: ?(.*?)\)\(\)", r"\1", code)
        code = re.sub(r"lambda: ?exec\((.*?)\)", r"\1", code)
        return code

class WebSlammerDecoder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self.input = TextInput(hint_text='Paste encrypted Python code here...', size_hint_y=0.4, background_color=rgb('#1e1e1e'), foreground_color=rgb('#ffffff'), cursor_color=rgb('#ffffff'))
        self.add_widget(self.input)
        self.decode_btn = Button(text='Decode', size_hint_y=0.1, background_color=rgb('#333333'), color=rgb('#ffffff'))
        self.decode_btn.bind(on_press=self.decode_script)
        self.add_widget(self.decode_btn)
        self.output = TextInput(hint_text='Decoded output will appear here...', readonly=True, background_color=rgb('#1e1e1e'), foreground_color=rgb('#00ff88'), cursor_color=rgb('#ffffff'))
        self.add_widget(self.output)

    def decode_script(self, instance):
        raw = self.input.text.strip()
        decoded = Decoder.decode(raw)
        self.output.text = decoded

class WebSlammerApp(App):
    def build(self):
        Window.clearcolor = rgb('#121212')
        return WebSlammerDecoder()

if __name__ == '__main__':
    WebSlammerApp().run()
