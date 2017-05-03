class FileParser(object):
    def __init__(self, file_name):
        #self._file_name = file_name
        self._file_object = open(file_name, 'r')
        self._params_table = self._file_object.readlines()
        for line_index in range(len(self._params_table)):
            self._params_table[line_index] = self._params_table[line_index].split('\t')

    def getParamsTable(self):
        for item in self._params_table:
            item[1] = float(item[1])
            item[2] = float(item[2])
            item[3] = float(item[3])
        return self._params_table
