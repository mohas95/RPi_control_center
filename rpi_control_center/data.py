import time, os, csv, datetime

str_format = '%Y%m%d%H%M%S'
readable_format = '%Y/%m/%d %H:%M:%S'

class csv_handler():
	"""
	A class that maintains a csv file management system. This class is particularly
	useful for  short-term logging data onto csv files continuously, while maintaining storage capacity.

	Attributes
    ----------
	base_dir : str
		Path to the directory used for storing CSV file.
	filename : str
		Base file name used to identify CSV files used in the management system.
	max_file_size : int
		Set maximum file size in bytes, in which a CSV file will be maintained.
	max_handling_size : int
		Set maximum size in bytes, of all csv files in management system will be maintained before purging full csv files.
	data_files : list(dict())
		List of dictionaries with attributes of files maintained by the handler.
	writing_to : str
		Path to the file being written to.
	total_size : int
		Total size, in bytes, of all csv files in maintained in the management system.

	Methods
	-------
	__init__(self, base_dir ='log/', filename='pi_data', max_file_size =89000, max_handling_size = 5000000):
		Initialize class object parameters.
	__call__(self, data):
		Transfer data to csv_file pointed at the writing_to attribute when class object is called.
	check_files(self):
		Checks and updates the parameters of the file management system.
	purge_data_files(self, all_files = False):
		Purges data files of the file manegement sysetem.
	find_ts_path(self, ts, data_files):
		Returns the filepath of a given timestamp if it exists.
	push_to_csv(self, csv_file, data):
		Push data in dictionary form to csv file.
	"""

	def __init__(self, base_dir ='log/', filename='pi_data', max_file_size =89000, max_handling_size = 5000000):
		'''
		constructs all necessary attributes for the csv_handler object.
			Parameters
			----------
				base_dir : str
					Path to the directory used for storing CSV file.
				filename : str
					Base file name used to identify CSV files used in the management system.
				max_file_size : int
					Set maximum file size in kb, in which a CSV file will be maintained.
				max_handling_size : int
					Set maximum size in kb, of all csv files in management system will be maintained before purging full csv files.
		'''
		if not os.path.exists(base_dir): os.makedirs(base_dir)

		self.base_dir = base_dir
		self.filename = filename
		self.max_file_size = max_file_size *1000
		self.max_handling_size = max_handling_size *1000
		self.data_files, self.writing_to, self.total_size = self.check_files()

	def __call__(self, data):
		'''
		Transfer data to csv_file pointed at the writing_to attribute when class object is called.
			Parameters
			----------
				data : <class dict>
					Dictionary with key and values to be written to the csv file pointed by the written_to attribute
		'''
		self.check_files()
		if not self.writing_to:
			ts = datetime.datetime.now().strftime(str_format)
			self.writing_to = f'{self.base_dir}{ts}_{self.filename}.csv'
		self.push_to_csv(self.writing_to, data)
		self.check_files()

	def check_files(self):
		'''
		Checks and updates the parameters of the file management system.
			Returns
			-------
			(self.data_files, self.writing_to, self.total_size) : <class tuple>
				data_files, writing_to, total_size attributes of csv_handler object
		'''
		data_file_paths = [self.base_dir+file for file in os.listdir(self.base_dir) if os.path.isfile(self.base_dir+file) and self.filename in file and '.csv' in file]

		data_files = []
		total_size = 0

		for file in data_file_paths:
			file_stats = os.stat(file)

			data_file = {   'file': file,
							'size': file_stats.st_size,
							'last_modified': datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime(readable_format),
							'status': 'active' if file_stats.st_size <= self.max_file_size else 'full'
						  }

			total_size += data_file['size']
			data_files.append(data_file)

		self.data_files = data_files
		self.total_size = total_size

		if self.total_size > self.max_handling_size: self.purge_data_files()
		active_files = [file for file in data_files if file['status'] == 'active']

		if active_files:
			ts = max([datetime.datetime.strptime(file['file'].split('_')[0].split('/')[-1], str_format) for file in active_files]).strftime(str_format)
			self.writing_to = self.find_ts_path(ts, active_files)
		elif not active_files:
			self.writing_to = None

		return self.data_files, self.writing_to, self.total_size

	def purge_data_files(self, all_files = False):
		'''
		Purges data files of the file manegement sysetem.
			Parameters
			----------
				all_files : bool
					Determines purging all files(True) or full files(False) only
		'''
		if all_files:
			for  data_file in self.data_files:
				os.remove(data_file['file'])
				self.data_files.remove(data_file)
		else:
			for data_file in self.data_files:
				if data_file['status'] =='full':
					os.remove(data_file['file'])
					self.data_files.remove(data_file)
				else:
					pass

		self.total_size = sum([file['size'] for file in self.data_files])

	def find_ts_path(self, ts, data_files):
		'''
		Returns the filepath of a given timestamp if it exists.
			Parameters
			----------
				ts : str
					timestamp in string format
				data_files : <class dict>
					dictionary of file attributes, must have 'file' key with path to file to be checked
			Returns
			-------
				file_path : str
					If ts is found in the file path, file path string
				None:
					If ts is not in found in file path, None
		'''
		for file in data_files:
			if ts in file['file']:
				file_path = file['file']
				return file_path
			else:
				return None

	def push_to_csv(self, csv_file, data):
		'''
		Push data in dictionary form to csv file.
			Parameters
			----------
				csv_file : str
					path to csv file
				data : <class dict>
					dictionary with key and values to be transfered to csv file
		'''
		fieldnames = [label for label, paremeter in data.items()]

		if not os.path.isfile(csv_file):
			with open(csv_file, 'w', newline='') as file:
				writer = csv.DictWriter(file, fieldnames =fieldnames)
				writer.writeheader()
				writer.writerow(data)
		else:
			with open(csv_file, 'a', newline='') as file:
				writer = csv.DictWriter(file, fieldnames =fieldnames)
				writer.writerow(data)

if __name__ == '__main__':

	################################################### CSV Handler test code
	test_data = {'hello': 13, 'poop':'34013'}

	test_csv = csv_handler(filename='test_data')

	print(test_csv.data_files)
	print(test_csv.writing_to)
	print(test_csv.total_size)

	test_csv(test_data)


	lol_csv = csv_handler()

	lol_csv(test_data)

	print(lol_csv.data_files)
	print(lol_csv.writing_to)
	print(lol_csv.total_size)
