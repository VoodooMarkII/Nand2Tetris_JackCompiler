import re
import xml.dom.minidom


class JackTokenizer:
    def __init__(self, in_file, out_file):
        self.in_file = in_file
        self.out_file = out_file
        self.lines_pure = self.remove_blank_and_comment(self.in_file)
        self.keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',
                         'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while',
                         'return']
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
        self.line_index = 0
        self.token_index = 0
        self.dst = ''
        self.doc = xml.dom.minidom.Document()
        self.token = self.doc.createElement('tokens')
        self.doc.appendChild(self.token)

    def has_more_tokens(self):
        return self.line_index != len(self.lines_pure) - 1 or self.lines_pure[-1] != ''

    def advance(self):
        self.lines_pure[self.line_index] = self.lines_pure[self.line_index].replace(self.dst, '', 1)
        if self.lines_pure[self.line_index] == '' and self.line_index != len(self.lines_pure) - 1:
            self.line_index = self.line_index + 1

    def token_type(self):
        self.lines_pure[self.line_index] = self.lines_pure[self.line_index].strip()
        #  Match keywords and identifiers
        pattern = re.compile(r'^[a-zA-Z_][\w_]*')
        self.dst = re.match(pattern, self.lines_pure[self.line_index])
        if self.dst is not None:
            self.dst = self.dst.group()
            if self.dst in self.keywords:
                return 'KEYWORD'
            else:
                return 'IDENTIFIER'
        #  Match symbols
        if self.lines_pure[self.line_index][0] in self.symbols:
            self.dst = self.lines_pure[self.line_index][0]
            return 'SYMBOL'
        #  Match integer constant
        pattern = re.compile(r'^[0-9]*')
        self.dst = re.match(pattern, self.lines_pure[self.line_index])
        if self.dst.group() != '':
            self.dst = self.dst.group()
            if 0 <= int(self.dst) <= 32767:
                return 'INT_CONST'
            else:
                raise SyntaxError('Integer is out of range of (0,32767).')
        #  Match string constant
        pattern = re.compile(r'".*?"')
        self.dst = re.match(pattern, self.lines_pure[self.line_index])
        if self.dst is not None:
            self.dst = self.dst.group()
            return 'STRING_CONST'
        raise SyntaxError('Invalid syntax in line: ' + self.lines_pure[self.line_index])

    def keyword(self):
        self.__write_xml('keyword', self.dst)
        return self.dst.upper()

    def symbol(self):
        self.__write_xml('symbol', self.dst)
        return self.dst.upper()

    def identifier(self):
        self.__write_xml('identifier', self.dst)
        return self.dst

    def int_val(self):
        self.__write_xml('integerConstant', self.dst)
        return self.dst

    def string_val(self):
        self.__write_xml('stringConstant', self.dst.strip('"'))
        return self.dst.strip('"')

    def save_xml(self):
        self.out_file.write(self.doc.toprettyxml(indent='  '))

    def __write_xml(self, token_type, val):
        node = self.doc.createElement(token_type)
        self.token.appendChild(node)
        node_name = self.doc.createTextNode(val)
        node.appendChild(node_name)

    @staticmethod
    def remove_blank_and_comment(file):
        lines_pure = []
        for line in file.readlines():
            if line.strip() in ['\n', '']:
                pass
            elif line.strip()[0:3] == '/**':
                pass
            elif line.strip()[0] == '*':
                pass
            elif line.strip()[0:2] == '*/':
                pass
            else:
                pattern = re.compile(r'//.*\n')
                line_pure = re.sub(pattern, '', line)  # Remove comment
                line_pure = line_pure.strip()
                if line_pure != '':  # Remove blank line
                    lines_pure.append(line_pure)
        return lines_pure
