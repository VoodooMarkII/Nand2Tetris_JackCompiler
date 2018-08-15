import JackTokenizer
import CompilationEngine

import os
import sys


class JackCompiler:
    def __init__(self, input_path):
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
            CompilationEngine.CompilationEngine(self.tokenizer_output_filename, out_f)
        print('Compiling finished.')


def main(argv=None):
    jc = JackCompiler(argv)
    jc.run()


if __name__ == '__main__':
    main(sys.argv[1])
