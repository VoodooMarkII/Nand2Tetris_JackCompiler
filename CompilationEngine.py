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
        'local': 'local',
        'field': 'this',
        'static': 'static'
    }

    def __init__(self, input_filename, output_file=None):
        self.input_filename = input_filename
        self.output_file = output_file
        self.symbol_table = SymbolTable.SymbolTable()
        self.token_text = ''

        self.subroutine_name = ''
        self.subroutine_type = ''
        self.class_name = ''
        self.if_index = 0
        self.while_index = 0
        self.var_number = 0

        self.in_xml = xml.dom.minidom.parse(self.input_filename)
        self.input_child_node_idx = 0

        self.vm_writer = VMWriter.VMWriter(input_filename[:-5])

        self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
        self.doc = xml.dom.minidom.Document()

        while self.get_token() == 'class':
            self.compile_class()

    def compile_class(self):
        self.get_token()  # Compile className
        self.class_name = self.token_text
        self.next_token() #Compile {
        while self.get_token() in ['static', 'field']:
            self.compile_class_var_dec()
        while self.get_token() in ['constructor', 'function', 'method']:
            self.compile_subroutine_dec()
        self.get_token()#Compile }





    def compile_class_var_dec(self):
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
            name = typ = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
            self.subroutine_name = '%s.%s' % (self.class_name, name)
        else:
            raise SyntaxError('Identifier expected.')

        if self.subroutine_type == 'method':
            self.symbol_table.define('this', 'argument', typ)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            subroutine_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'(' expected.")

        parameter_number = self.compile_parameter_list(subroutine_dec_node)

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
            subroutine_dec_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("')' expected.")

        self.compile_subroutine_body(subroutine_dec_node)

    def compile_parameter_list(self, father_node):
        parameter_number = 0
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
                parameter_number = parameter_number + 1
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
        return parameter_number

    def compile_subroutine_body(self, father_node):
        self.var_number = 0
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
            subroutine_body_node = self.doc.createElement('subroutineBody')
            father_node.appendChild(subroutine_body_node)
            subroutine_body_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'{' expected.")

        while self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'var':
            self.compile_var_dec(subroutine_body_node)
        # if self.subroutine_type=='function':
        self.vm_writer.write_function(self.subroutine_name, self.var_number)
        if self.subroutine_type == 'method':
            self.vm_writer.write_push('argument', '0')
            self.vm_writer.write_pop('pointer', '0')
        elif self.subroutine_type == 'constructor':
            field_num = self.symbol_table.var_count('field')
            self.vm_writer.write_push('constant', str(field_num))
            self.vm_writer.write_call('Memory.alloc', '1')
            self.vm_writer.write_pop('pointer', '0')
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
            self.var_number = self.var_number + 1
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
                self.var_number = self.var_number + 1
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
        array_flag = False
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'let':
            let_node = self.doc.createElement('letStatement')
            father_node.appendChild(let_node)
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'let' expected.")

        if self.current_token.nodeName == 'identifier':
            let_node.appendChild(self.current_token)
            name = self.current_token.childNodes[0].nodeValue
            kind = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '[':
            array_flag = True
            let_node.appendChild(self.current_token)
            self.__idx_advance()
            self.vm_writer.write_push(self.STACK_SYMBOL_KIND[kind], index)
            self.compile_expression(let_node)
            self.vm_writer.write_arithmetic('add')
            self.vm_writer.write_pop('temp', '0')
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ']':
                let_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("']' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '=':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression(let_node)
            if array_flag:
                self.vm_writer.write_push('temp', '0')
                self.vm_writer.write_pop('pointer', '1')
                self.vm_writer.write_pop('that', '0')
            else:
                self.vm_writer.write_pop(self.STACK_SYMBOL_KIND[kind], index)
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
        self.vm_writer.write_arithmetic('not')
        if_index = self.if_index
        self.if_index += 1
        self.vm_writer.write_if('IF.' + str(if_index))

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
            self.vm_writer.write_goto('IF_EXIT.' + str(if_index))
            self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
                if_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("'{' expected.")
            self.vm_writer.write_label('IF.' + str(if_index))
            self.compile_statements(if_node)
            self.vm_writer.write_label('IF_EXIT.' + str(if_index))
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
                if_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("'}' expected.")
        else:
            self.vm_writer.write_label('IF.' + str(if_index))

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
        while_index = self.while_index
        self.while_index += 1
        self.vm_writer.write_label('WHILE.' + str(while_index))
        self.compile_expression(while_node)
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if('WHILE_EXIT.' + str(while_index))
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
        self.vm_writer.write_goto('WHILE.' + str(while_index))
        self.vm_writer.write_label('WHILE_EXIT.' + str(while_index))
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '}':
            while_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'(' expected.")

    def compile_do(self, father_node):
        nargs = 0
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'do':
            do_node = self.doc.createElement('doStatement')
            father_node.appendChild(do_node)
            do_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'do' expected.")

        if self.current_token.nodeName == 'identifier':
            do_node.appendChild(self.current_token)
            name = self.current_token.childNodes[0].nodeValue
            func_name = '%s.%s' % (self.class_name, name)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier expected.')

        # Process subroutineCall.
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            do_node.appendChild(self.current_token)
            self.__idx_advance()
            self.vm_writer.write_push('pointer', '0')
            nargs = self.compile_expression_list(do_node)
            func_name = ('%s.%s' % (self.class_name, name))
            self.vm_writer.write_call(func_name, str(nargs + 1))
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                do_node.appendChild(self.current_token)
                self.__idx_advance()
        elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '.':
            do_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                do_node.appendChild(self.current_token)
                if self.symbol_table.search_symbol(name):
                    segment = self.STACK_SYMBOL_KIND[self.symbol_table.kind_of(name)]
                    index = self.symbol_table.index_of(name)
                    self.vm_writer.write_push(segment, index)
                    name = self.symbol_table.type_of(name)
                    nargs += 1
                func_name = '%s.%s' % (name, self.current_token.childNodes[0].nodeValue)
                self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                do_node.appendChild(self.current_token)
                self.__idx_advance()
                nargs = nargs + self.compile_expression_list(do_node)
                self.vm_writer.write_call(func_name, str(nargs))
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                    do_node.appendChild(self.current_token)
                    self.__idx_advance()
        else:
            raise SyntaxError('subroutineCall expected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            do_node.appendChild(self.current_token)
            self.vm_writer.write_pop('temp', '0')
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_return(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'return':
            return_node = self.doc.createElement('returnStatement')
            father_node.appendChild(return_node)
            return_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'return' expected.")

        if not (self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';'):
            self.compile_expression(return_node)
        else:
            self.vm_writer.write_push('constant', '0')
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            return_node.appendChild(self.current_token)
            self.vm_writer.write_return()
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
                self.vm_writer.write_call('Math.multiply', '2')
            elif op_code == '/':
                self.vm_writer.write_call('Math.divide', '2')
            else:
                self.vm_writer.write_arithmetic(self.ARITHMETIC_OPCODES[op_code])

    def compile_term(self, father_node):
        nargs = 0
        term_node = self.doc.createElement('term')
        father_node.appendChild(term_node)
        if self.current_token.nodeName in ['integerConstant', 'stringConstant']:
            term_node.appendChild(self.current_token)
            if self.current_token.nodeName == 'integerConstant':
                self.vm_writer.write_push('constant', self.current_token.childNodes[0].nodeValue)
            else:
                string = self.current_token.childNodes[0].nodeValue
                self.vm_writer.write_push('constant', len(string))
                self.vm_writer.write_call('String.new', '1')
                string = list(map(ord, string))
                for char in string:
                    self.vm_writer.write_push('constant', char)
                    self.vm_writer.write_call('String.appendChar', 2)
            self.__idx_advance()

        elif self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['true', 'false', 'null', 'this']:
            term_node.appendChild(self.current_token)
            keyword = self.current_token.childNodes[0].nodeValue
            if keyword == 'true':
                self.vm_writer.write_push('constant', '0')
                self.vm_writer.write_arithmetic('not')
            elif keyword in ['false', 'null']:
                self.vm_writer.write_push('constant', '0')
            else:
                self.vm_writer.write_push('pointer', '0')
            self.__idx_advance()

        # Processing varName, varName[expression] and subroutineCall
        elif self.current_token.nodeName == 'identifier':
            term_node.appendChild(self.current_token)
            name = self.current_token.childNodes[0].nodeValue
            self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '[':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression(term_node)
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ']':
                    term_node.appendChild(self.current_token)
                    kind = self.symbol_table.kind_of(name)
                    index = self.symbol_table.index_of(name)
                    self.vm_writer.write_push(self.STACK_SYMBOL_KIND[kind], index)
                    self.vm_writer.write_arithmetic('add')
                    self.vm_writer.write_pop('pointer', '1')
                    self.vm_writer.write_push('that', '0')
                    self.__idx_advance()
                else:
                    raise SyntaxError("']' expected.")

            elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                self.vm_writer.write_push('pointer', '0')
                nargs = self.compile_expression_list(term_node)
                func_name = ('%s.%s' % (self.class_name, name))
                self.vm_writer.write_call(func_name, str(nargs + 1))
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
            elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '.':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'identifier':
                    term_node.appendChild(self.current_token)
                    if self.symbol_table.search_symbol(name):
                        segment = self.STACK_SYMBOL_KIND[self.symbol_table.kind_of(name)]
                        index = self.symbol_table.index_of(name)
                        self.vm_writer.write_push(segment, index)
                        name = self.symbol_table.type_of(name)
                        nargs += 1
                    func_name = '%s.%s' % (name, self.current_token.childNodes[0].nodeValue)
                    self.__idx_advance()
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                    nargs = nargs + self.compile_expression_list(term_node)
                    if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                        term_node.appendChild(self.current_token)
                        self.__idx_advance()
                self.vm_writer.write_call(func_name, str(nargs))
            else:
                kind = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                self.vm_writer.write_push(self.STACK_SYMBOL_KIND[kind], index)

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
        expression_number = 0
        expression_list_node = self.doc.createElement('expressionList')
        father_node.appendChild(expression_list_node)
        if not (self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')'):
            self.compile_expression(expression_list_node)
            expression_number = expression_number + 1
            while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
                expression_list_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression(expression_list_node)
                expression_number = expression_number + 1
        else:
            empty_text_node = self.doc.createTextNode('')
            expression_list_node.appendChild(empty_text_node)
        return expression_number

    def __idx_advance(self):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            self.input_child_node_idx = self.input_child_node_idx + 1
            self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
            if not isinstance(self.current_token, xml.dom.minidom.Element):
                self.__idx_advance()

    def advance(self):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            self.input_child_node_idx = self.input_child_node_idx + 1
            self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
            if not isinstance(self.current_token, xml.dom.minidom.Element):
                self.__idx_advance()

    def get_token(self):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            self.input_child_node_idx = self.input_child_node_idx + 1
            current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
            if not isinstance(current_token, xml.dom.minidom.Element):
                self.next_token()
            self.token_text = self.in_xml.documentElement.childNodes[self.input_child_node_idx].childNodes[0].nodeValue
        return self.token_text

    def peek(self):
        pass

    def __save_xml(self):
        self.output_file.write(self.doc.toprettyxml(indent='  '))
