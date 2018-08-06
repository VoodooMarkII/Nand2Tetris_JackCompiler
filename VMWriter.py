import os


class VMWriter:
    def __init__(self, filename):
        self.filename = filename + '.vm'

        if os.path.isfile(self.filename):
            print(self.filename+' exists. It will be replaced.')
            os.remove(self.filename)
        self.file = open(self.filename, 'a')

    def write_push(self, segment, index):
        """
        :param segment: in list[CONST,ARG,LCL,STATIC,THIS,THAT,POINTER,TEMP]
        :param index: Offset of given segment
        :return: VM push command with given segment and index
        """
        self.file.write('push %s %s\n' % (segment, index))

    def write_pop(self, segment, index):
        """
        :param segment: in list[ARG,LCL,STATIC,THIS,THAT,POINTER,TEMP]
        :param index: Offset of given segment
        :return: VM pop command with given segment and index
        """

        self.file.write('pop %s %s\n' % (segment, index))

    def write_arithmetic(self, command):
        """
        :param command: in the list[ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT)
        :return:  VM arithmetic command with given segment and index
        """
        self.file.write(command+'\n')

    def write_label(self, label):
        self.file.write('label %s\n' % label)

    def write_goto(self, label):
        self.file.write('goto %s\n' % label)

    def write_if(self, label):
        self.file.write('if-goto %s\n' % label)

    def write_call(self, name, n_args):
        self.file.write('call %s %d\n' % (name, n_args))

    def write_function(self, name, n_locals):
        self.file.write('function %s %s\n' % (name, n_locals))

    def write_return(self):
        self.file.write('return\n')

    def close(self):
        self.file.close()
