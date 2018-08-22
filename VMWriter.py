import os


class VMWriter:

    def __init__(self, filename):
        """
        Open the vm file and get ready to write command to it.
        Note:
        1) It will override the current file if it already existed.
        2) Use close() method after all manipulation.

        :param filename: (string) The output file name without extension '.vm'.
        """
        self.filename = filename + '.vm'

        if os.path.isfile(self.filename):
            print(self.filename + ' exists. It will be replaced.')
            os.remove(self.filename)
        self.file = open(self.filename, 'a')

    def write_push(self, segment, index):
        """
        :param segment: (string) In list['constant', 'local', 'argument', 'static', 'this', 'that, 'pointer', 'temp']
        :param index: (int) Offset of given segment
        :return: (string) VM push command with given segment and index
        """
        cmd = 'push {segment} {index}'.format(segment=segment, index=index)
        self.file.write(cmd + '\n')
        return cmd

    def write_pop(self, segment, index):
        """
        :param segment: (string) In list['local', 'argument', 'static', 'this', 'that', 'pointer', 'temp']
        :param index: (int) Offset of given segment
        :return: (string) VM pop command with given segment and index
        """
        cmd = 'pop {segment} {index}'.format(segment=segment, index=index)
        self.file.write(cmd + '\n')
        return cmd

    def write_arithmetic(self, cmd):
        """
        :param cmd: (string) In the list['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        :return: (string) VM arithmetic command with given segment and index
        """
        self.file.write(cmd + '\n')
        return cmd

    def write_label(self, label):
        cmd = 'label {label}'.format(label=label)
        self.file.write(cmd + '\n')
        return cmd

    def write_goto(self, label):
        cmd = 'goto {label}'.format(label=label)
        self.file.write(cmd + '\n')
        return cmd

    def write_if(self, label):
        cmd = 'if-goto {label}'.format(label=label)
        self.file.write(cmd + '\n')
        return cmd

    def write_call(self, name, n_args):
        """
        :param name: (string) Function name
        :param n_args: (int) The number of argument of callee
        :return: (string) VM call command
        """
        cmd = 'call {name} {n_args}'.format(name=name, n_args=n_args)
        self.file.write(cmd + '\n')
        return cmd

    def write_function(self, name, n_locals):
        """
        :param name: (string) Function name
        :param n_locals: (int) The number of local variables of callee
        :return: (string) VM function label
        """
        cmd = 'function {name} {n_locals}'.format(name=name, n_locals=n_locals)
        self.file.write(cmd + '\n')
        return cmd

    def write_return(self):
        cmd = 'return'
        self.file.write(cmd + '\n')
        return cmd

    def close(self):
        self.file.close()
