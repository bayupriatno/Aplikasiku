import os
import zipfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
from kivy_garden.webview import WebView
from kivy.uix.button import Button

class InstallerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = os.path.join(primary_external_storage_path(), "WebInstallerSites")
        os.makedirs(self.base_dir, exist_ok=True)
        self.refresh_site_list()

    def refresh_site_list(self):
        self.ids.site_list.clear_widgets()
        for site_name in os.listdir(self.base_dir):
            site_path = os.path.join(self.base_dir, site_name)
            if os.path.isdir(site_path):
                btn_open = Button(text=f"Buka: {site_name}", size_hint_y=None, height=40)
                btn_open.bind(on_release=lambda x, s=site_name: self.load_site(s))

                btn_delete = Button(text="Hapus", size_hint_y=None, height=40)
                btn_delete.bind(on_release=lambda x, s=site_name: self.delete_site(s))

                box = BoxLayout(size_hint_y=None, height=40)
                box.add_widget(btn_open)
                box.add_widget(btn_delete)
                self.ids.site_list.add_widget(box)

    def select_file(self, filepaths):
        if not filepaths:
            return
        filepath = filepaths[0]
        self.extract_and_save(filepath)

    def extract_and_save(self, zip_path):
        try:
            site_name = os.path.splitext(os.path.basename(zip_path))[0]
            site_path = os.path.join(self.base_dir, site_name)
            os.makedirs(site_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(site_path)
            self.refresh_site_list()
            self.show_message("Website berhasil diinstal.")
        except Exception as e:
            self.show_message(str(e))

    def load_site(self, site_name):
        index_path = os.path.join(self.base_dir, site_name, "index.html")
        if os.path.exists(index_path):
            self.ids.webview.source = f"file://{index_path}"
        else:
            self.show_message("index.html tidak ditemukan.")

    def delete_site(self, site_name):
        import shutil
        path = os.path.join(self.base_dir, site_name)
        if os.path.exists(path):
            shutil.rmtree(path)
            self.refresh_site_list()
            self.show_message("Website dihapus.")

    def show_message(self, message):
        popup = Popup(title="Info",
                      content=Label(text=message),
                      size_hint=(0.8, 0.3))
        popup.open()

class WebInstallerApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        return InstallerLayout()

if __name__ == '__main__':
    WebInstallerApp().run()