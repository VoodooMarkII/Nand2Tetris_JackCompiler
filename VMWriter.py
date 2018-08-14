import os


class VMWriter:
    def __init__(self, filename):
        self.filename = filename + '.vm'

        if os.path.isfile(self.filename):
            print(self.filename + ' exists. It will be replaced.')
            os.remove(self.filename)
        self.file = open(self.filename, 'a')

    def write_push(self, segment, index):
        """
        :param segment: in list[constant, local, argument, static, this, that, pointer, temp]
        :param index: Offset of given segment
        :return: VM push command with given segment and index
        """
        cmd = 'push {segment} {index}'.format(segment=segment, index=index)
        self.file.write(cmd + '\n')
        return cmd

    def write_pop(self, segment, index):
        """
        :param segment: in list[local, argument, static, this, that, pointer, temp]
        :param index: Offset of given segment
        :return: VM pop command with given segment and index
        """
        cmd = 'pop {segment} {index}'.format(segment=segment, index=index)
        self.file.write(cmd + '\n')
        return cmd

    def write_arithmetic(self, cmd):
        """
        :param cmd: in the list[add, sub, neg, eq, gt, lt, and, or, not]
        :return:  VM arithmetic command with given segment and index
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
        cmd = 'call {name} {n_args}'.format(name=name, n_args=n_args)
        self.file.write(cmd + '\n')
        return cmd

    def write_function(self, name, n_locals):
        cmd = 'function {name} {n_locals}'.format(name=name, n_locals=n_locals)
        self.file.write(cmd + '\n')
        return cmd

    def write_return(self):
        cmd = 'return'
        self.file.write(cmd + '\n')
        return cmd

    def close(self):
        self.file.close()
