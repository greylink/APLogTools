import os
import tkinter as tk
from tkinter import simpledialog, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from configparser import ConfigParser
import LogParser
from rules_config import CONFIG_FILE


class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("LOG Configs")

        # 读取配置文件,不存在，则创建
        self.config = ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            self.create_default_config()

        # 尝试读取配置文件
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)

            if 'settings' not in self.config:
                self.config['settings'] = {'last_selected_folder': ''}

        # 创建按钮
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.buttons = {}
        self.current_rule_name = None # Initialize current_rule_name

        for rule_name in self.config['log_rules']:
            button = tk.Button(self.button_frame, text=rule_name, command=lambda name=rule_name: self.load_config_by_name(name))
            button.pack(side=tk.LEFT, padx=5)
            self.buttons[rule_name] = button  # Store the button reference

        # 新建规则
        new_rule_button = tk.Button(master, text="新建规则", command=self.create_new_rule)
        new_rule_button.pack(pady=10)

        # 创建文本编辑框
        self.text_editor = tk.Text(master, height=10, width=50)
        self.text_editor.pack(pady=10)

        # 添加保存按钮
        save_button = tk.Button(master, text="保存配置", command=self.save_config)
        save_button.pack(pady=10)


        # 获取最后一次选择的文件夹
        self.last_selected_folder = self.config.get('settings', 'last_selected_folder', fallback='')
        # Add a button for file selection
        select_file_button = tk.Button(master, text="Select File", command=self.select_file, width=28, height=4)
        select_file_button.pack(pady=10)


        # 创建drop
        self.file_label = tk.Label(self.master, text="Drop Files Here(no work)", relief=tk.SUNKEN, width=30, height=2)
        self.file_label.pack(pady=20)
        # 启用拖放功能
        self.file_label.drop_target_register(DND_FILES)
        self.file_label.dnd_bind('<<Drop>>', self.handle_drop)

        self.update_button_list()

        # 显示默认配置
        default_rule = list(self.config['log_rules'].keys())[0]
        self.current_rule_name = default_rule
        self.load_config_by_name(default_rule)

    def load_config_by_name(self, rule_name):
        # 根据名称加载对应的配置
        self.current_rule_name = rule_name  # Set current_rule_name to the default rule

        print("当前 current_rule_name = " + self.current_rule_name)
        
        config_text = self.config['log_rules'][rule_name]
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(tk.END, config_text)

        # 更新按钮颜色
        for name, button in self.buttons.items():
            if name == rule_name:
                button.configure(bg='orange')
                self.current_rule_name = rule_name
            else:
                button.configure(bg='white')

    def save_config(self):
        # 保存配置到文件
        rule_name = self.current_rule_name
        config_text = self.text_editor.get(1.0, tk.END).strip().replace('\r\n', '\n')

        # Check if the rule_name already exists
        if rule_name not in self.config['log_rules']:
            # If it doesn't exist, add it to the config
            self.config['log_rules'][rule_name] = ''

        # Update the configuration with the new text
        self.config['log_rules'][rule_name] = config_text

        # Save the updated configuration to the file
        with open(CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)
            configfile.flush()
            
    def select_file(self):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(initialdir=self.last_selected_folder)

        # Check if a file was selected
        if file_path:
            # Update last_selected_folder with the selected folder
            self.last_selected_folder = os.path.dirname(file_path)

            # Update the last selected folder in the configuration file
            self.config.set('settings', 'last_selected_folder', self.last_selected_folder)
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)
                configfile.flush()

            # Perform the handle_file function with the selected file
            self.handle_file(file_path)

    def handle_drop(self, event):
        # 检查是否为文件拖放事件
        print(" on handle_drop!")
        if event.data:
            file_path = event.data
            print(f"文件路径: {file_path}")
            self.handle_file(file_path)
        else:
            print("非文件拖放事件")

    def handle_file(self, file_path):
        # 处理文件
        print(f"文件路径: {file_path}")
        if self.current_rule_name is not None:
            print("handle_filecurrent_rule_name = " + self.current_rule_name)
            LogParser.process_logs(file_path, self.current_rule_name)
        else:
            print("未选择规则")

    def create_new_rule(self):
        # 使用 tkinter.simpledialog 获取新规则的名称和配置
        new_rule_name = tk.simpledialog.askstring("新建规则", "请输入新规则的名称：")
        new_rule_config = tk.simpledialog.askstring("新建规则", f"请输入规则 '{new_rule_name}' 的配置：")

        # 检查是否取消了新建规则
        if new_rule_name is not None and new_rule_config is not None:
            # 更新配置文件和界面
            self.config['log_rules'][new_rule_name] = new_rule_config
            self.current_rule_name = new_rule_name  # Set current_rule_name
            self.update_button_list()

            # 加载新规则的配置
            self.load_config_by_name(new_rule_name)
            # 保存新规则的配置到文件
            self.save_config()

    def update_button_list(self):
        # 清除现有按钮
        for button in self.button_frame.winfo_children():
            button.destroy()

        # 创建新按钮
        for rule_name in self.config['log_rules']:
            button = tk.Button(self.button_frame, text=rule_name, command=lambda name=rule_name: self.load_config_by_name(name))
            button.pack(side=tk.LEFT, padx=5)
            self.buttons[rule_name] = button

    def create_default_config(self):
        default_config = {
            'settings': {
                'last_selected_folder': '',
        },
            'log_rules': {
                'call': 'ImsPhoneCallTracker|IMS_REGISTRATION_STATE|GET_CURRENT_CALLS|RequestManager|RILJ|qcrilNr',
                'mms': 'Mms-debug|MmsSmsProvider|Mms     :',
                'sms': 'onSendSmsResult',
            }
        }

        # 如果配置文件不存在，则创建并写入默认配置
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.read_dict(default_config)
                self.config.write(configfile)
                configfile.flush()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ConfigEditor(root)
    root.mainloop()
