import json
import threading
import time
import tkinter as tk
from tkinter import filedialog
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class MQTTLogPlayer:
    def __init__(self, root):
        # AWS IoT Coreの接続情報
        self.root_ca_path = ""
        self.certificate_path = ""
        self.private_key_path = ""
        self.client_id = "mqtt-logger"

        # MQTT Brokerの接続情報
        self.broker_address = "localhost"
        self.broker_port = 1883

        # AWSIoTMQTTClientオブジェクトを作成する
        self.client = AWSIoTMQTTClient(self.client_id)

        # 認証情報を設定するself.client
        self.client.configureEndpoint(self.broker_address, self.broker_port)
        # self.client.configureCredentials(self.root_ca_path, self.private_key_path, self.certificate_path)

        # MQTT Brokerへ接続
        self.client.connect()

        # GUIを作成する
        self.root = root
        self.root.title("MQTT Log Player")

        # ログファイルを選択するボタンを作成する
        self.log_file_path = tk.StringVar()
        self.log_file_path.set("")
        self.log_file_label = tk.Label(self.root, text="Log file:")
        self.log_file_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.log_file_entry = tk.Entry(self.root, textvariable=self.log_file_path)
        self.log_file_entry.grid(row=0, column=1, padx=10, pady=10)
        self.log_file_button = tk.Button(self.root, text="Select", command=self.select_log_file)
        self.log_file_button.grid(row=0, column=2, padx=10, pady=10)

        # # トピック名を入力するエントリーを作成する
        # self.topic_name = tk.StringVar()
        # self.topic_name.set("")
        # self.topic_name_label = tk.Label(self.root, text="Topic name:")
        # self.topic_name_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        # self.topic_name_entry = tk.Entry(self.root, textvariable=self.topic_name)
        # self.topic_name_entry.grid(row=1, column=1, padx=10, pady=10)

        # 再生速度を設定するスケールを作成する
        self.speed = tk.DoubleVar()
        self.speed.set(1.0)
        self.speed_label = tk.Label(self.root, text="Speed:")
        self.speed_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.speed_scale = tk.Scale(self.root, from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.speed)
        self.speed_scale.grid(row=2, column=1, padx=10, pady=10)

        # 再生位置を指定するスケールを作成する
        self.position = tk.IntVar()
        self.position.set(0)
        self.position_label = tk.Label(self.root, text="Position:")
        self.position_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.position_scale = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.position)
        self.position_scale.grid(row=3, column=1, padx=10, pady=10)

        # 再生、一時停止、停止ボタンを作成する
        self.play_button = tk.Button(self.root, text="Play", command=self.play)
        self.play_button.grid(row=4, column=0, padx=10, pady=10)
        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause)
        self.pause_button.grid(row=4, column=1, padx=10, pady=10)
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop)
        self.stop_button.grid(row=4, column=2, padx=10, pady=10)

        # ログファイルから読み込んだメッセージのリスト
        self.messages = []

        # 再生中かどうかを表すフラグ
        self.playing = False

        # ログファイルからメッセージを読み込む
        self.load_messages()

    def select_log_file(self):
        # ログファイルを選択するダイアログを表示する
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        self.log_file_path.set(file_path)

        # ログファイルからメッセージを読み込む
        self.load_messages()

    def load_messages(self):
        # ログファイルからメッセージを読み込む
        self.messages = []
        log_file_path = self.log_file_path.get()
        if log_file_path:
            with open(log_file_path, "r") as f:
                log_data = json.load(f)
                self.messages = log_data["messages"]

    def play(self):
        # 再生を開始する
        self.playing = True
        self.position.set(0)
        threading.Thread(target=self.play_thread).start()

    def pause(self):
        # 再生を一時停止する
        self.playing = False

    def stop(self):
        # 再生を停止する
        self.playing = False
        # self.client.disconnect()

    def play_thread(self):
        # 再生を実行するスレッド
        start_time = None
        total_time = None
        for i, message in enumerate(self.messages):
            # 再生が停止されたらループを抜ける
            if not self.playing:
                break

            # トピック名とメッセージを送信する
            topic_name = message["name"]
            data = message["data"]
            self.client.publish(topic_name, json.dumps(data), 0)
            print(topic_name, ": ", data)

            # timestampから待機時間を計算する
            timestamp = message["timestamp"]
            if start_time is None:
                start_time = timestamp
            elif total_time is None:
                total_time = timestamp - start_time
            else:
                time.sleep((timestamp - start_time) / total_time / self.speed.get())

            # 再生位置を更新する
            self.position.set(int((i + 1) / len(self.messages) * 100))

    def start(self):
        # GUIを開始する
        self.root.mainloop()


app = MQTTLogPlayer(tk.Tk())
app.start()