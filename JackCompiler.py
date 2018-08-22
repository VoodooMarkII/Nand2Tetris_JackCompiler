import os
import sys
import JackTokenizer
import CompilationEngine


class JackCompiler:
    """
    Compile the single *.jack file or all *.jack files in a directory.
    This component compile *.jack files and generate *.vm files in the same directory.

    Note: *T.xml file will be created as medium. Please ignore it.

    Usage: Initialize the JackCompile with path then call run() method.

    Attribute:
        input_filenames: Store the path of input *jack files to be compiled.
        tokenizer_output_filename: The xml filename during current compiling process.
    """
    def __init__(self, input_path):
        """
        This method create the list which stores the *.jack files.

        :param input_path: (string) The path of input *.jack files. Single file or directory are both acceptable.

        :raise IOError: An error occurs during read/write operation.
        """
        self.input_filenames = []
        self.tokenizer_output_filename = ''
        if os.path.isdir(input_path):
            path = os.listdir(input_path)
            for filename in path:
                if filename.split('.')[-1] == 'jack':
                    self.input_filenames.append(os.path.join(input_path, filename))
            if len(self.input_filenames) == 0:
                raise IOError('Jack file not found.')
        elif os.path.isfile(input_path):
            if input_path.split('.')[1] == 'jack':
                self.input_filenames.append(input_path)
            else:
                raise IOError('Error input file type.')
        else:
            raise IOError('Folder "%s" does not exist.' % input_path)

    def run(self):
        """
        Compile all files in input_filenames. Generate xml and vm files.

        :return: 0
        """
        for input_filename in self.input_filenames:
            self.tokenizer_output_filename = str(input_filename.split('.')[0]) + 'T.xml'
            print('Compiling ' + input_filename)

            # Tokenizer generate xml file for CompilationEngine
            with open(input_filename) as in_f:
                with open(self.tokenizer_output_filename, 'w') as out_f:
                    jt = JackTokenizer.JackTokenizer(in_f, out_f)
                    while jt.has_more_tokens():
                        token_type = jt.token_type()
                        if token_type == 'KEYWORD':
                            jt.keyword()
                        elif token_type == 'SYMBOL':
                            jt.symbol()
                        elif token_type == 'IDENTIFIER':
                            jt.identifier()
                        elif token_type == 'INT_CONST':
                            jt.int_val()
                        elif token_type == 'STRING_CONST':
                            jt.string_val()
                        jt.advance()
                    jt.save_xml()

            # Compile and generate VM code
            CompilationEngine.CompilationEngine(self.tokenizer_output_filename)
        print('Compiling finished.')
        return 0


def main(argv=None):
    jc = JackCompiler(argv)
    jc.run()


if __name__ == '__main__':
    main(sys.argv[1])
