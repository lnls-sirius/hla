class FileParser(object):
    def __init__(self, file_name):
        self.__file_name = file_name
        self.__file_object = open(file_name, 'r')
        self.__params_table = self.__file_object.readlines()
        for line_index in range(len(self.__params_table)):
            self.__params_table[line_index] = self.__params_table[line_index].split('\t')

    def getParamsTable(self):
        for item in self.__params_table:
            item[2] = float(item[2])
            item[3] = float(item[3])
        return self.__params_table
