from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlScheme
from PyQt5.QtGui import QFont, QIcon
import json
import os


class WexBrowser():
    def __init__(self):
        # Загрузка настроек
        self.settings_file = "wexbrowser_settings.json"
        self.load_settings()
        
        self.window = QWidget()
        self.window.setWindowTitle("WexBrowser")
        self.window.setMinimumSize(1024, 768)
        
        # Применяем глобальную тему сразу
        self.apply_global_theme()

        self.user_agents = {
            "Windows: Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.158 Safari/537.36",
            "Windows: Firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/140.0.4.",
            "Windows: Edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/138.0.3351.95",
            "Windows: OperaGX": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/120.0.5543.93. (Edition GX-CN)",
            "Windows: Yandex": "	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.8.1.468 Yowser/2.5 Safari/537.36",
            "Mac: Safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5. Safari/605.1.15",
            "Android: Chrome": "Mozilla/5.0 (Linux; Android 11; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
            "iPhone: Safari": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5. Mobile/15E148 Safari/604.1"
        }

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Панель навигации
        self.nav_bar = QWidget()
        self.nav_bar.setFixedHeight(60)
        self.nav_bar.setObjectName("navBar")
        
        self.horizontal = QHBoxLayout()
        self.horizontal.setContentsMargins(10, 5, 10, 5)
        
        # Кнопки навигации
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.setToolTip("Назад")

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(40, 40)
        self.forward_btn.setToolTip("Вперёд")

        self.reload_btn = QPushButton("↻")
        self.reload_btn.setFixedSize(40, 40)
        self.reload_btn.setToolTip("Обновить")

        # Поле ввода URL
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Введите URL или поисковый запрос...")
        self.input_url.setFixedHeight(40)
        self.input_url.setObjectName("urlInput")

        # Кнопка перехода
        self.search_btn = QPushButton("Перейти")
        self.search_btn.setFixedSize(80, 40)
        self.search_btn.setObjectName("searchBtn")

        # Кнопка меню
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setToolTip("Меню")

        # Добавление виджетов в layout
        self.horizontal.addWidget(self.back_btn)
        self.horizontal.addWidget(self.forward_btn)
        self.horizontal.addWidget(self.reload_btn)
        self.horizontal.addSpacing(10)
        self.horizontal.addWidget(self.input_url)
        self.horizontal.addWidget(self.search_btn)
        self.horizontal.addSpacing(10)
        self.horizontal.addWidget(self.menu_btn)
        
        self.nav_bar.setLayout(self.horizontal)
        self.layout.addWidget(self.nav_bar)

        # Браузер
        self.browser = QWebEngineView()
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        self.browser.page().profile().cookieStore().deleteAllCookies()
        
        # Применяем сохраненный User Agent
        self.apply_user_agent(self.settings_data.get("user_agent", "Windows: Chrome"))

        # HLS, Исправляет ошибку с воспроизведением видео
        scheme = QWebEngineUrlScheme(b"http")
        scheme.setFlags(QWebEngineUrlScheme.SecureScheme)
        QWebEngineUrlScheme.registerScheme(scheme)

        # Подключение сигналов
        self.search_btn.clicked.connect(self.navigate)
        self.input_url.returnPressed.connect(self.navigate)
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.menu_btn.clicked.connect(self.settings)
        
        self.browser.urlChanged.connect(self.update_urlbar)

        self.layout.addWidget(self.browser)
        self.browser.setUrl(QUrl("https://google.com"))

        self.window.setLayout(self.layout)
        self.apply_styles()
        self.window.show()

    def load_settings(self):
        """Загрузка настроек из файла"""
        default_settings = {
            "theme": "dark",
            "user_agent": "Windows: Chrome"
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings_data = json.load(f)
            else:
                self.settings_data = default_settings
                self.save_settings()
        except:
            self.settings_data = default_settings

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def apply_global_theme(self):
        """Применение глобальной темы ко всему приложению"""
        if self.settings_data["theme"] == "dark":
            self.window.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
            """)
        else:
            self.window.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
            """)

    def apply_styles(self):
        """Применение стилей в зависимости от темы"""
        if self.settings_data["theme"] == "dark":
            # Темная тема
            self.nav_bar.setStyleSheet("""
                QWidget#navBar {
                    background-color: #2d2d2d;
                    border-bottom: 1px solid #404040;
                }
            """)
            
            nav_button_style = """
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 16px;
                    min-width: 40px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QPushButton:pressed {
                    background-color: #606060;
                }
                QPushButton:disabled {
                    background-color: #333333;
                    color: #666666;
                }
            """
            
            self.back_btn.setStyleSheet(nav_button_style)
            self.forward_btn.setStyleSheet(nav_button_style)
            self.reload_btn.setStyleSheet(nav_button_style)
            self.menu_btn.setStyleSheet(nav_button_style)
            
            self.input_url.setStyleSheet("""
                QLineEdit#urlInput {
                    background-color: #404040;
                    color: #ffffff;
                    border: 2px solid #505050;
                    border-radius: 8px;
                    padding: 0 12px;
                    font-size: 14px;
                    selection-background-color: #4285f4;
                }
                QLineEdit#urlInput:focus {
                    border-color: #4285f4;
                }
            """)
            
            self.search_btn.setStyleSheet("""
                QPushButton#searchBtn {
                    background-color: #4285f4;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#searchBtn:hover {
                    background-color: #3367d6;
                }
                QPushButton#searchBtn:pressed {
                    background-color: #2851a3;
                }
            """)
        else:
            # Светлая тема
            self.nav_bar.setStyleSheet("""
                QWidget#navBar {
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #dadce0;
                }
            """)
            
            nav_button_style = """
                QPushButton {
                    background-color: #ffffff;
                    color: #5f6368;
                    border: 1px solid #dadce0;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 16px;
                    min-width: 40px;
                }
                QPushButton:hover {
                    background-color: #f1f3f4;
                    border-color: #c4c7c5;
                }
                QPushButton:pressed {
                    background-color: #e8eaed;
                }
                QPushButton:disabled {
                    background-color: #f8f9fa;
                    color: #bdc1c6;
                }
            """
            
            self.back_btn.setStyleSheet(nav_button_style)
            self.forward_btn.setStyleSheet(nav_button_style)
            self.reload_btn.setStyleSheet(nav_button_style)
            self.menu_btn.setStyleSheet(nav_button_style)
            
            self.input_url.setStyleSheet("""
                QLineEdit#urlInput {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #dadce0;
                    border-radius: 8px;
                    padding: 0 12px;
                    font-size: 14px;
                    selection-background-color: #1a73e8;
                }
                QLineEdit#urlInput:focus {
                    border-color: #1a73e8;
                }
            """)
            
            self.search_btn.setStyleSheet("""
                QPushButton#searchBtn {
                    background-color: #1a73e8;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#searchBtn:hover {
                    background-color: #1669d6;
                }
                QPushButton#searchBtn:pressed {
                    background-color: #1257b3;
                }
            """)

    def navigate(self):
        """Переход по URL"""
        url = self.input_url.text().strip()
        if not url:
            return
            
        if not url.startswith(("http://", "https://")):
            if '.' in url:
                url = "https://" + url
            else:
                url = "https://www.google.com/search?q=" + url.replace(' ', '+')
        
        self.browser.setUrl(QUrl(url))

    def update_urlbar(self, q):
        """Обновление URL в адресной строке"""
        self.input_url.setText(q.toString())
        self.input_url.setCursorPosition(0)

    def apply_user_agent(self, ua_name):
        """Устанавливает выбранный User-Agent для браузера"""
        if ua_name in self.user_agents:
            selected_ua = self.user_agents[ua_name]
            self.browser.page().profile().setHttpUserAgent(selected_ua)
            self.browser.reload()

    def apply_all_settings(self, theme_name, ua_name):
        """Применяет все настройки одновременно"""
        # Сохраняем настройки
        self.settings_data["theme"] = theme_name
        self.settings_data["user_agent"] = ua_name
        self.save_settings()
        
        # Применяем тему
        self.apply_global_theme()
        self.apply_styles()
        
        # Применяем User Agent
        self.apply_user_agent(ua_name)

    def settings(self):
        """Окно настроек"""
        settings_window = QDialog(self.window)
        settings_window.setWindowTitle("WexBrowser - Настройки")
        settings_window.setFixedSize(500, 350)
        settings_window.setModal(True)

        # Основной layout
        main_layout = QVBoxLayout(settings_window)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Группа выбора темы
        theme_group = QGroupBox("Внешний вид")
        theme_layout = QVBoxLayout(theme_group)

        theme_combo = QComboBox()
        theme_combo.addItems(["Тёмная тема", "Светлая тема"])
        theme_combo.setCurrentText("Тёмная тема" if self.settings_data["theme"] == "dark" else "Светлая тема")
        theme_layout.addWidget(theme_combo)

        main_layout.addWidget(theme_group)

        # Группа выбора User-Agent
        ua_group = QGroupBox("User-Agent (идентификация браузера)")
        ua_layout = QVBoxLayout(ua_group)

        ua_combo = QComboBox()
        ua_combo.addItems(self.user_agents.keys())
        ua_combo.setCurrentText(self.settings_data.get("user_agent", "Windows: Chrome"))
        ua_layout.addWidget(ua_combo)

        ua_info = QLabel("Определяет, как сайты видят ваше устройство и браузер")
        ua_info.setStyleSheet("color: #666; font-size: 12px; margin-top: 5px;")
        ua_info.setWordWrap(True)
        ua_layout.addWidget(ua_info)

        main_layout.addWidget(ua_group)

        # Кнопка применения всех настроек
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(lambda: self.apply_all_settings(
            "dark" if theme_combo.currentText() == "Тёмная тема" else "light",
            ua_combo.currentText()
        ))
        apply_btn.clicked.connect(settings_window.close)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(settings_window.close)

        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)

        # Применяем стили к окну настроек в зависимости от текущей темы
        if self.settings_data["theme"] == "dark":
            settings_window.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #404040;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #ffffff;
                }
                QComboBox {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #505050;
                    border-radius: 3px;
                    padding: 5px;
                    min-width: 200px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #404040;
                    color: #ffffff;
                    selection-background-color: #4285f4;
                }
                QPushButton {
                    background-color: #4285f4;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3367d6;
                }
                QPushButton:pressed {
                    background-color: #2851a3;
                }
            """)
        else:
            settings_window.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    color: #000000;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #dadce0;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #000000;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #dadce0;
                    border-radius: 3px;
                    padding: 5px;
                    min-width: 200px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #000000;
                    selection-background-color: #1a73e8;
                }
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1669d6;
                }
                QPushButton:pressed {
                    background-color: #1257b3;
                }
            """)

        settings_window.exec_()


app = QApplication([])
app.setApplicationName("WexBrowser")
app.setApplicationVersion("1.0")

window = WexBrowser()
app.exec_()
