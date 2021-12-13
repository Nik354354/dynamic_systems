import json
def fetch_xyz_data():
	# return x1_seq, y1_seq, x2_seq, y2_seq, z_seq
	pass

def add_xyz_entry(coords, file_path='saves//sitnikov_save.xyz', comment=''):
	'''Принимает координаты, название файла и комментарий, добавляет к концу файла новое положение системы'''
	x1, y1, x2, y2, z = coords
	'''with open(filename, 'a') as file:
		3
		comment
		star x1 y1 0
		star x2 y2 0
		planet 0 0 z'''

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