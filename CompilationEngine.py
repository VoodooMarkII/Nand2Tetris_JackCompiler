import xml.dom.minidom
import SymbolTable
import VMWriter


class CompilationEngine:
    ARITHMETIC_OPCODES = {
        '+': 'add',
        '-': 'sub',
        '=': 'eq',
        '>': 'gt',
        '<': 'lt',
        '&': 'and',
        '|': 'or'
    }

    ARITHMETIC_UNARY_OPCODE = {
        '-': 'neg',
        '~': 'not'
    }

    STACK_SYMBOL_KIND = {
        'argument': 'argument',
        'var': 'local',
        'field': 'this',
        'static': 'static'
    }

    def __init__(self, input_filename, output_file=None):
        self.input_filename = input_filename
        self.output_file = output_file
        self.symbol_table = SymbolTable.SymbolTable()
        self.subroutine_type = ''

        self.in_xml = xml.dom.minidom.parse(self.input_filename)
        self.input_child_node_idx = 1

        self.vm_writer = VMWriter.VMWriter(input_filename[:-5])

        self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
        self.doc = xml.dom.minidom.Document()
        while self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'class':
            self.compile_class()
        self.__save_xml()

        pass

    def compile_class(self):
        if self.current_token.childNodes[0].nodeValue == 'class':
            class_node = self.doc.createElement('class')
            self.doc.appendChild(class_node)
            class_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("Keyword 'class' expected.")

        if self.current_token.nodeName == 'identifier':
            class_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError('className expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
            class_node.appendChild(self.current_token)
            self.__idx_advance()
            while self.current_token.nodeName == 'keyword' and \
                    self.current_token.childNodes[0].nodeValue in ['static', 'field']:
                self.compile_class_var_dec(class_node)
            while self.current_token.nodeName == 'keyword' and \
                    self.current_token.childNodes[0].nodeValue in ['constructor', 'function', 'method']:
                self.compile_subroutine_dec(class_node)
        else:
            raise SyntaxError("'{' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
            class_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'}' expected.")

    def compile_class_var_dec(self, father_node):
        if self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['static', 'field']:
            class_var_dec_node = self.doc.createElement('classVarDec')
            father_node.appendChild(class_var_dec_node)
            class_var_dec_node.appendChild(self.current_token)
            kind = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
        else:
            raise SyntaxError("'static' or 'method' expected.")

        if self.current_token.nodeName == 'identifier' or \
                self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
            class_var_dec_node.appendChild(self.current_token)
            typ = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
        else:
            raise SyntaxError('Type expected.')

        if self.current_token.nodeName == 'identifier':
            class_var_dec_node.appendChild(self.current_token)
            name = self.current_token.childNodes[0].nodeValue
            self.symbol_table.define(name, kind, typ)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
            class_var_dec_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                class_var_dec_node.appendChild(self.current_token)
                name = self.current_token.childNodes[0].nodeValue
                self.symbol_table.define(name, kind, typ)
                self.__idx_advance()
            else:
                raise SyntaxError('Identifier expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            class_var_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_subroutine_dec(self, father_node):
        self.symbol_table.clean_subroutine_table()
        if self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['constructor', 'function', 'method']:
            subroutine_dec_node = self.doc.createElement('subroutineDec')
            father_node.appendChild(subroutine_dec_node)
            subroutine_dec_node.appendChild(self.current_token)
            self.subroutine_type = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
        else:
            raise SyntaxError("Keyword 'constructor', 'function' or 'method' expected.")

        if self.current_token.nodeName == 'identifier' or \
                self.current_token.childNodes[0].nodeValue in ['void', 'int', 'char', 'boolean']:
            subroutine_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError('Type expected.')

        if self.current_token.nodeName == 'identifier':
            subroutine_dec_node.appendChild(self.current_token)
            typ = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        if self.subroutine_type == 'method':
            self.symbol_table.define('this', 'argument', typ)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            subroutine_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'(' expected.")

        self.compile_parameter_list(subroutine_dec_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
            subroutine_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("')' expected.")

        self.compile_subroutine_body(subroutine_dec_node)

    def compile_parameter_list(self, father_node):
        parameter_list_node = self.doc.createElement('parameterList')
        father_node.appendChild(parameter_list_node)
        if self.current_token.nodeName == 'identifier' or \
                self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
            parameter_list_node.appendChild(self.current_token)
            typ = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                parameter_list_node.appendChild(self.current_token)
                name = self.current_token.childNodes[0].nodeValue
                self.symbol_table.define(name, 'argument', typ)
                self.__idx_advance()
            else:
                raise SyntaxError('Identifier expected.')

            while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
                parameter_list_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'identifier' or \
                        self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
                    parameter_list_node.appendChild(self.current_token)
                    typ = self.current_token.childNodes[0].nodeValue
                    self.__idx_advance()
                    if self.current_token.nodeName == 'identifier':
                        parameter_list_node.appendChild(self.current_token)
                        name = self.current_token.childNodes[0].nodeValue
                        self.symbol_table.define(name, 'argument', typ)
                        self.__idx_advance()
        else:
            empty_text_node = self.doc.createTextNode('')
            parameter_list_node.appendChild(empty_text_node)

    def compile_subroutine_body(self, father_node):
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
            subroutine_body_node = self.doc.createElement('subroutineBody')
            father_node.appendChild(subroutine_body_node)
            subroutine_body_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'{' expected.")

        while self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'var':
            self.compile_var_dec(subroutine_body_node)

        self.compile_statements(subroutine_body_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
            subroutine_body_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'}' expected.")

    def compile_var_dec(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'var':
            var_dec_node = self.doc.createElement('varDec')
            father_node.appendChild(var_dec_node)
            var_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("Keyword 'var' expected.")

        if self.current_token.nodeName == 'identifier' or \
                self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
            var_dec_node.appendChild(self.current_token)
            typ = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
        else:
            raise SyntaxError('Type expected.')

        if self.current_token.nodeName == 'identifier':
            var_dec_node.appendChild(self.current_token)
            name = self.current_token.childNodes[0].nodeValue
            self.symbol_table.define(name, 'local', typ)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
            var_dec_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                var_dec_node.appendChild(self.current_token)
                name = self.current_token.childNodes[0].nodeValue
                self.symbol_table.define(name, 'local', typ)
                self.__idx_advance()
            else:
                raise SyntaxError('Identifier expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            var_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_statements(self, father_node):
        statements_node = self.doc.createElement('statements')
        father_node.appendChild(statements_node)
        while self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['let', 'if', 'while', 'do', 'return']:
            if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'let':
                self.compile_let(statements_node)
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'if':
                self.compile_if(statements_node)
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'while':
                self.compile_while(statements_node)
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'do':
                self.compile_do(statements_node)
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'return':
                self.compile_return(statements_node)

    def compile_let(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'let':
            let_node = self.doc.createElement('letStatement')
            father_node.appendChild(let_node)
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'let' expected.")

        if self.current_token.nodeName == 'identifier':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '[':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression(let_node)
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ']':
                let_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("']' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '=':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression(let_node)
        else:
            raise SyntaxError("'=' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_if(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'if':
            if_node = self.doc.createElement('ifStatement')
            father_node.appendChild(if_node)
            if_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'if' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            if_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'(' expected.")

        self.compile_expression(if_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
            if_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("')' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
            if_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'{' expected.")

        self.compile_statements(if_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
            if_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'}' expected.")

        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'else':
            if_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
                if_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("'{' expected.")
            self.compile_statements(if_node)
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
                if_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("'}' expected.")

        pass

    def compile_while(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'while':
            while_node = self.doc.createElement('whileStatement')
            father_node.appendChild(while_node)
            while_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'while' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            while_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'(' expected.")

        self.compile_expression(while_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
            while_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("')' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
            while_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'{' expected.")

        self.compile_statements(while_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
            while_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'(' expected.")

    def compile_do(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'do':
            do_node = self.doc.createElement('doStatement')
            father_node.appendChild(do_node)
            do_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'do' expected.")

        if self.current_token.nodeName == 'identifier':
            do_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        # Process subroutineCall.
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            do_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression_list(do_node)
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                do_node.appendChild(self.current_token)
                self.__idx_advance()
        elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '.':
            do_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                do_node.appendChild(self.current_token)
                self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                do_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression_list(do_node)
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                    do_node.appendChild(self.current_token)
                    self.__idx_advance()
        else:
            raise SyntaxError('subroutineCall expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            do_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_return(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'return':
            return_node = self.doc.createElement('returnStatement')
            father_node.appendChild(return_node)
            return_node.appendChild(self.current_token)
            self.vm_writer.write_return()
            self.__idx_advance()
        else:
            raise SyntaxError("'return' expected.")

        if not (self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';'):
            self.compile_expression(return_node)
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            return_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_expression(self, father_node):
        expression_node = self.doc.createElement('expression')
        father_node.appendChild(expression_node)
        self.compile_term(expression_node)
        while self.current_token.nodeName == 'symbol' and \
                self.current_token.childNodes[0].nodeValue in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            expression_node.appendChild(self.current_token)
            op_code = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
            self.compile_term(expression_node)
            if op_code == '*':
                self.vm_writer.write_function('Math.multiply', 2)
            elif op_code == '/':
                self.vm_writer.write_function('Math.divide', 2)
            else:
                self.vm_writer.write_arithmetic(self.ARITHMETIC_OPCODES[op_code])

    def compile_term(self, father_node):
        term_node = self.doc.createElement('term')
        father_node.appendChild(term_node)
        if self.current_token.nodeName in ['integerConstant', 'stringConstant']:
            term_node.appendChild(self.current_token)
            if self.current_token.nodeName =='integerConstant':
                self.vm_writer.write_push('constant',self.current_token.childNodes[0].nodeValue)
            else:
                string =self.current_token.childNodes[0].nodeValue
                self.vm_writer.write_push('constant',len(string))
                self.vm_writer.write_function('String.new','1')
                string=list(map(ord,string))
                for char in string:
                    self.vm_writer.write_push('constant',char)
            self.__idx_advance()

        elif self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['true', 'false', 'null', 'this']:
            term_node.appendChild(self.current_token)
            self.__idx_advance()

        # Processing varName, varName[expression] and subroutineCall
        elif self.current_token.nodeName == 'identifier':
            term_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '[':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression(term_node)
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ']':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                else:
                    raise SyntaxError("']' expected.")

            elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression_list(term_node)
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
            elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '.':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'identifier':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                    self.compile_expression_list(term_node)
                    if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                        term_node.appendChild(self.current_token)
                        self.__idx_advance()

        # Processing (expression)
        elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            term_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression(term_node)
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("'(' expected.")

        # Processing unaryOp term
        elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue in ['-', '~']:
            term_node.appendChild(self.current_token)
            unary_opcode = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
            self.compile_term(term_node)
            self.vm_writer.write_arithmetic(self.ARITHMETIC_UNARY_OPCODE[unary_opcode])

        # Processing subroutineCall
        else:
            raise SyntaxError('Term expected.')

    def compile_expression_list(self, father_node):
        expression_list_node = self.doc.createElement('expressionList')
        father_node.appendChild(expression_list_node)
        if not (self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')'):
            self.compile_expression(expression_list_node)
            while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
                expression_list_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression(expression_list_node)
        else:
            empty_text_node = self.doc.createTextNode('')
            expression_list_node.appendChild(empty_text_node)

    def __idx_advance(self):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            self.input_child_node_idx = self.input_child_node_idx + 1
            self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
            if not isinstance(self.current_token, xml.dom.minidom.Element):
                self.__idx_advance()

    def __save_xml(self):
        self.output_file.write(self.doc.toprettyxml(indent='  '))
