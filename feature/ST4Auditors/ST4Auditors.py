import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextBrowser, QFileDialog
from PyQt6.QtCore import Qt
import random
import datetime
import hashlib

class SampleSelectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Seleção de Amostras')
        self.setGeometry(100, 100, 700, 400)

        self.label_input = QLabel('Arquivo de Entrada:', self)
        self.label_input.setGeometry(50, 50, 150, 20)

        self.input_file_entry = QLineEdit(self)
        self.input_file_entry.setGeometry(200, 50, 200, 20)

        self.browse_input_button = QPushButton('Selecionar Arquivo', self)
        self.browse_input_button.setFixedSize(150, 25)  # Defina a largura e altura desejadas em pixels
        self.browse_input_button.setGeometry(410, 45, 100, 20)
        self.browse_input_button.clicked.connect(self.browse_input_file)

        self.label_output = QLabel('Arquivo de Saída:', self)
        self.label_output.setGeometry(50, 100, 150, 20)

        self.output_file_entry = QLineEdit(self)
        self.output_file_entry.setGeometry(200, 100, 200, 20)

        self.browse_output_button = QPushButton('Selecionar Arquivo', self)
        self.browse_output_button.setFixedSize(150, 25)  # Defina a largura e altura desejadas em pixels
        self.browse_output_button.setGeometry(410, 95, 100, 20)
        self.browse_output_button.clicked.connect(self.browse_output_file)

        self.label_samples = QLabel('Número de Amostras:', self)
        self.label_samples.setGeometry(50, 150, 150, 20)

        self.n_samples_entry = QLineEdit(self)
        self.n_samples_entry.setGeometry(200, 150, 100, 20)

        self.label_seed = QLabel('Semente Personalizada:', self)
        self.label_seed.setGeometry(50, 200, 150, 20)

        self.seed_entry = QLineEdit(self)
        self.seed_entry.setGeometry(200, 200, 100, 20)

        self.execute_button = QPushButton('Executar Seleção de Amostras', self)
        self.execute_button.setGeometry(200, 250, 200, 30)
        self.execute_button.clicked.connect(self.selecionar_amostras)

        self.result_text = QTextBrowser(self)
        self.result_text.setGeometry(50, 300, 450, 80)
        self.result_text.setOpenExternalLinks(True)

    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter('Arquivos CSV (*.csv);;Arquivos Excel (*.xlsx)')

        selected_file, _ = file_dialog.getOpenFileName()

        if selected_file:
            self.input_file_entry.setText(selected_file)

    def browse_output_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter('Arquivos CSV (*.csv);;Arquivos Excel (*.xlsx)')

        selected_file, _ = file_dialog.getSaveFileName()

        if selected_file:
            self.output_file_entry.setText(selected_file)

    def selecionar_amostras(self):
        input_file = self.input_file_entry.text()
        output_file = self.output_file_entry.text()
        n_samples_str = self.n_samples_entry.text()
        custom_seed = self.seed_entry.text() if self.seed_entry.text() else None

        if not n_samples_str:
            self.result_text.setPlainText("Digite o número de amostras.")
            return

        try:
            n_samples = float(n_samples_str)
        except ValueError:
            self.result_text.setPlainText("Número de amostras inválido. Digite um número válido.")
            return

        random_state = custom_seed if custom_seed is not None else self.get_current_seed()

        df = self.load_dataframe(input_file)

        if n_samples > len(df):
            self.result_text.setPlainText(f"O número de amostras solicitadas ({n_samples}) é maior do que o número de registros no arquivo ({len(df)}).")
        else:
            selected_samples = df.sample(n=int(n_samples), random_state=random_state)

            if output_file.endswith('.csv'):
                selected_samples.to_csv(output_file, index=False)
            elif output_file.endswith('.xlsx'):
                selected_samples.to_excel(output_file, index=False, engine='openpyxl')
            else:
                self.result_text.setPlainText("Formato de arquivo de saída não suportado. Use um arquivo CSV ou XLSX.")

            sha256_hash = hashlib.sha256()
            with open(input_file, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            md5_hash = hashlib.md5()
            with open(input_file, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)

            result = f"Hashes SHA256/MD5 do arquivo {input_file}:\n" \
                     f"SHA256: {sha256_hash.hexdigest()}\n" \
                     f"MD5: {md5_hash.hexdigest()}\n" \
                     f"Seed utilizado para amostragem: {random_state}\n" \
                     f"{int(n_samples)} amostras selecionadas e salvas em {output_file}."

            self.result_text.setPlainText(result)

    def get_current_seed(self):
        current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return hash(current_datetime) % (2**32 - 1)

    def load_dataframe(self, file_path):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError("Formato de arquivo não suportado. Use um arquivo CSV ou XLSX.")

def main():
    app = QApplication(sys.argv)
    window = SampleSelectionApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
