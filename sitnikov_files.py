import json
import tkinter as tk

import my as my


def fetch_xyz_data():
	return x1_seq, y1_seq, x2_seq, y2_seq, z_seq


class MessageBox(tk.Tk):
	def __init__(self):
		super().__init__()
		save1_btn = tk.Label(self, text="Сохранить данные симуляции?")
		save_btn= tk.Button(self, text="Сохранить", command=self.confirm)
		dont_save_btn = tk.Button(self, text="Не сохранять", command=self.decline)
		cancel_btn = tk.Button(self, text="Отмена", command=self.cancel)
		save1_btn.pack()
		save_btn.pack(side=tk.LEFT)
		dont_save_btn.pack(side=tk.LEFT)
		cancel_btn.pack(side=tk.LEFT)

		proceed_to_exit = False

	def confirm(self):
		create_xyz_log()
		proceed_to_exit = True
		self.destroy()

	def decline(self):
		proceed_to_exit = True
		self.destroy()

	def cancel(self):
		self.destroy()



def add_xyz_entry(file_path='saves//sitnikov_save.xyz', comment=''):
	'''Принимает название файла и комментарий, добавляет к концу файла новое положение системы'''
	x1, y1, x2, y2, z =fetch_xyz_data()

	with open(file_path, 'a') as file:
		file.write("3")
		file.write(comment)
		file.write("star"+" "+x1+" "+y1+" 0")
		file.write("star "+x2+" "+y2+" 0")
		file.write("planet 0 0" + z)

def create_xyz_log(filename='saves//sitnikov_save.xyz', comment=''):

	x1_seq, y1_seq, x2_seq, y2_seq, z_seq = fetch_xyz_data()
	for x1, y1, x2, y2, z in zip(x1_seq, y1_seq, x2_seq, y2_seq, z_seq):
		add_xyz_entry((x1, y1, x2, y2, z), file_path=filename, comment=comment)

def load_configuration(file='sitnikov_cfg.json'):
	'''Возвращает словарь с настройками из файла file'''
	config = {}
	with open(file, 'r') as cfg:
		config = json.load(cfg)
	return config

def ask_save():
	'''Создаёт окно MessageBox, с подтверждением выхода без сохранения данных'''
	confirm_exit = MessageBox()
	confirm_exit.mainloop()
	return confirm_exit


