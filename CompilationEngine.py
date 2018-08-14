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
        self.token_type = ''

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
        self.get_token()  # Compile {
        while self.next_token() in ['static', 'field']:
            self.compile_class_var_dec()
        while self.next_token() in ['constructor', 'function', 'method']:
            self.compile_subroutine_dec()
        self.get_token()  # Compile }

    def compile_class_var_dec(self):
        kind = self.get_token()  # Compiling class variable kind
        typ = self.get_token()  # Compling class variable type
        name = self.get_token()  # Compling class variable name
        self.symbol_table.define(name, kind, typ)

        while self.next_token() == ',':
            self.get_token()  # Compiling symbol ','
            name = self.get_token()  # Compiling class variable name
            self.symbol_table.define(name, kind, typ)

        self.get_token()  # Compiling symbol ';'

    def compile_subroutine(self):
        self.compile_subroutine_dec()
        self.compile_subroutine_body()

    def compile_subroutine_dec(self):
        self.symbol_table.clean_subroutine_table()
        self.subroutine_type = self.get_token()  # Compiling subroutine type
        self.get_token()  # Compiling return type
        name = typ = self.get_token()
        self.subroutine_name = '%s.%s' % (self.class_name, name)

        if self.subroutine_type == 'method':
            self.symbol_table.define('this', 'argument', typ)

        self.get_token()  # Compiling symbol '('

        parameter_number = self.compile_parameter_list()

        self.get_token()  # Compiling symbol ')'

        self.compile_subroutine_body()

    def compile_parameter_list(self):
        parameter_number = 0

        if self.next_token() in ['int', 'char', 'boolean']:
            typ = self.get_token()  # Compiling parameter type
            name = self.get_token()  # Compiling parameter name
            self.symbol_table.define(name, 'argument', typ)
            parameter_number += 1

        while self.next_token() == ',':
            self.get_token()  # Compiling symbol ','
            typ = self.get_token()
            name = self.get_token()
            self.symbol_table.define(name, 'argument', typ)
            parameter_number += 1
        return parameter_number

    def compile_subroutine_body(self):
        self.var_number = 0
        self.get_token()  # Compiling symbol '{'
        while self.next_token() == 'var':
            self.compile_var_dec()
        self.vm_writer.write_function(self.subroutine_name, self.var_number)
        if self.subroutine_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)
        elif self.subroutine_type == 'constructor':
            field_num = self.symbol_table.var_count('field')
            self.vm_writer.write_push('constant', field_num)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        self.compile_statements()

        self.get_token()  # Compiling symbol '}'

    def compile_var_dec(self):
        self.get_token()  # Compiling keyword 'var'
        typ = self.get_token()  # Compiling variable type
        name = self.get_token()  # Compiling variable name
        self.symbol_table.define(name, 'local', typ)
        self.var_number = self.var_number + 1

        while self.next_token() == ',':
            self.get_token()  # Compiling symbol ','
            name = self.get_token()  # Compiling variable name
            self.symbol_table.define(name, 'local', typ)
            self.var_number = self.var_number + 1

        if self.next_token() == ';':
            self.get_token()  # Compiling symbol ';'

    def compile_statements(self):
        while self.next_token() in ['let', 'if', 'while', 'do', 'return']:
            if self.next_token() == 'let':
                self.compile_let()
            elif self.next_token() == 'if':
                self.compile_if()
            elif self.next_token() == 'while':
                self.compile_while()
            elif self.next_token() == 'do':
                self.compile_do()
            elif self.next_token() == 'return':
                self.compile_return()

    def compile_let(self):
        is_array = False
        self.get_token()  # Compiling keyword 'let'
        name = self.get_token()
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)
        if self.next_token() == '[':
            self.get_token()  # Compiling symbol '['
            is_array = True
            self.vm_writer.write_push(self.STACK_SYMBOL_KIND[kind], index)
            self.compile_expression()
            self.vm_writer.write_arithmetic('add')
            self.vm_writer.write_pop('temp', 0)
            self.get_token()  # Compiling symbol ']'
        self.get_token()  # Compiling symbol '='
        self.compile_expression()
        if is_array:
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_pop('that', 0)
        else:
            self.vm_writer.write_pop(self.STACK_SYMBOL_KIND[kind], index)
        self.get_token()  # Compiling symbol ';'

    def compile_if(self):
        self.get_token()  # Compiling keyword 'if'
        self.get_token()  # Compiling symbol '('
        self.compile_expression()
        self.vm_writer.write_arithmetic('not')
        if_index = self.if_index
        self.if_index += 1
        self.vm_writer.write_if('IF.FALSE' + str(if_index))
        self.get_token()  # Compiling symbol ')'

        self.get_token()  # Compiling symbol '{'
        self.compile_statements()
        self.get_token()  # Compiling symbol '}'

        if self.next_token() == 'else':
            self.vm_writer.write_goto('IF_TRUE_EXIT.' + str(if_index))
            self.get_token()  # Compiling symbol '{'
            self.vm_writer.write_label('IF.FALSE' + str(if_index))
            self.compile_statements()
            self.vm_writer.write_label('IF_TRUE_EXIT.' + str(if_index))
            self.get_token()  # Compiling symbol '}'
        else:
            self.vm_writer.write_label('IF.FALSE' + str(if_index))

    def compile_while(self):
        self.get_token()  # Compiling keyword while
        self.get_token()  # Compiling symbol '('
        while_index = self.while_index
        self.while_index += 1
        self.vm_writer.write_label('WHILE.' + str(while_index))
        self.compile_expression()
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if('WHILE_EXIT.' + str(while_index))
        self.get_token()  # Compiling symbol ')'

        self.get_token()  # Compiling symbol '{'
        self.compile_statements()
        self.vm_writer.write_goto('WHILE.' + str(while_index))
        self.vm_writer.write_label('WHILE_EXIT.' + str(while_index))
        self.get_token()  # Compiling symbol '}'

    def compile_do(self):
        n_args = 0
        self.get_token()  # Compiling keyword do
        self.compile_subroutine_call()
        self.get_token()  # Compiling symbol ';'
        self.vm_writer.write_pop('temp', 0)

    def compile_subroutine_call(self):
        n_args = 0
        name = self.get_token()
        func_name = '{class_name}.{subroutine_name}'.format(class_name=self.class_name, subroutine_name=name)
        if self.next_token() == '(':  # Handling call self
            self.get_token()  # Compiling symbol '('
            self.vm_writer.write_push('pointer', 0)
            n_args = self.compile_expression_list()
            func_name = '{class_name}.{subroutine_name}'.format(class_name=self.class_name, subroutine_name=name)
            self.vm_writer.write_call(func_name, n_args + 1)
            self.get_token()  # Compiling symbol ')'
        elif self.next_token() == '.':  # Handling call other class's subroutine
            self.get_token()  # Compiling symbol '.'
            if self.symbol_table.search_symbol(name):  # Handling call method.
                segment = self.STACK_SYMBOL_KIND[self.symbol_table.kind_of(name)]
                index = self.symbol_table.index_of(name)
                self.vm_writer.write_push(segment, index)
                name = self.symbol_table.type_of(name)
                n_args += 1
            subroutine_name = self.get_token()  # Compiling subroutine name
            func_name = '{class_name}.{subroutine_name}'.format(class_name=name, subroutine_name=subroutine_name)
            self.get_token()  # Compiling symbol '('
            n_args += self.compile_expression_list()
            self.vm_writer.write_call(func_name, n_args)
            self.get_token()  # Compiling symbol ')'

    def compile_return(self):
        self.get_token()  # Compiling return
        if self.next_token() == ';':  # Handling return none
            self.vm_writer.write_push('constant', 0)
        else:  # Handling return expression
            self.compile_expression()
        self.get_token()  # Compiling symbol ';'

    def compile_expression(self):
        self.compile_term()
        while self.next_token() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op_code = self.get_token()
            self.compile_term()
            if op_code == '*':
                self.vm_writer.write_call('Math.multiply', '2')
            elif op_code == '/':
                self.vm_writer.write_call('Math.divide', '2')
            else:
                self.vm_writer.write_arithmetic(self.ARITHMETIC_OPCODES[op_code])

    def compile_term(self):
        n_args = 0
        #  Handling integer constant
        if self.next_token_type() == 'integerConstant':
            int_val = self.get_token()
            self.vm_writer.write_push('constant', int_val)
        # Handling string constant
        elif self.next_token_type() == 'stringConstant':
            string_val = self.get_token()
            self.vm_writer.write_push('constant', len(string_val))
            self.vm_writer.write_call('String.new', '1')
            string = list(map(ord, string_val))
            for char in string:
                self.vm_writer.write_push('constant', char)
                self.vm_writer.write_call('String.appendChar', 2)
        # Handling boolean and etc.
        elif self.next_token() in ['true', 'false', 'null', 'this']:
            keyword = self.get_token()
            if keyword == 'true':
                self.vm_writer.write_push('constant', '0')
                self.vm_writer.write_arithmetic('not')
            elif keyword in ['false', 'null']:
                self.vm_writer.write_push('constant', '0')
            else:
                self.vm_writer.write_push('pointer', '0')

        # Handling (expression)
        elif self.next_token() == '(':
            self.get_token()  # Compiling symbol '('
            self.compile_expression()
            self.get_token()  # Compiling symbol ')'

        # Handling unaryOp term
        elif self.next_token() in ['-', '~']:
            unary_opcode = self.get_token()
            self.compile_term()
            self.vm_writer.write_arithmetic(self.ARITHMETIC_UNARY_OPCODE[unary_opcode])

        # Handling subroutine call
        elif self.next_token(step=2) in ['(', '.']:
            self.compile_subroutine_call()

        # Handling varName and varName[expression]
        else:
            name = self.get_token()
            if self.next_token() == '[':
                self.get_token()  # Compiling symbol '['
                self.compile_expression()
                self.get_token()  # Compiling symbol ']'
                kind = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                self.vm_writer.write_push(self.STACK_SYMBOL_KIND[kind], index)
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)

    def compile_expression_list(self):
        expression_number = 0
        if not (self.next_token_type() == 'symbol' and self.next_token() == ')'):
            self.compile_expression()
            expression_number += 1
            while self.next_token_type() == 'symbol' and self.next_token() == ',':
                self.compile_expression()
                expression_number += 1
        return expression_number

    def get_token(self):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            self.input_child_node_idx = self.input_child_node_idx + 1
            current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
            if not isinstance(current_token, xml.dom.minidom.Element):
                self.get_token()
            self.token_text = self.in_xml.documentElement.childNodes[self.input_child_node_idx].childNodes[0].nodeValue
            self.token_type = self.in_xml.documentElement.childNodes[self.input_child_node_idx].nodeName
        return self.token_text

    def current_token(self):
        return self.token_text

    def current_token_type(self):
        return self.token_type

    def next_token(self, step=1):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            idx = self.input_child_node_idx + step
        else:
            return None
        while idx < len(self.in_xml.documentElement.childNodes) - 1:
            while not isinstance(self.in_xml.documentElement.childNodes[idx], xml.dom.minidom.Element):
                idx += 1
            return self.in_xml.documentElement.childNodes[idx].childNodes[0].nodeValue
        return None

    def next_token_type(self, step=1):
        if self.input_child_node_idx < len(self.in_xml.documentElement.childNodes) - 1:
            idx = self.input_child_node_idx + step
        else:
            return None
        while idx < len(self.in_xml.documentElement.childNodes) - 1:
            while not isinstance(self.in_xml.documentElement.childNodes[idx], xml.dom.minidom.Element):
                idx += 1
            return self.in_xml.documentElement.childNodes[idx].nodeName
        return None

