class SymbolTable:
    """
    Create and manage the symbol table of a class during the compiling process.
    The table contains name, kind, type and index.
    """
    def __init__(self):
        self.symbol_table_class = []
        self.symbol_table_subroutine = []
        pass

    def define(self, name, kind, typ):
        """
        This method add a record to symbol table. Redefinition will be checked before adding it to the table.

        :param name: (string) The name of the symbol
        :param kind: (string) The kind of the symbol. In list ['static', 'field', 'argument', 'local']
        :param typ: (string) Data type of the symbol
        :return: 0

        :raise
            Syntax Error: Redefinition of symbol.
        """
        index = self.var_count(kind)
        if kind in ['static', 'field']:
            if len(self.symbol_table_class) == 0 or \
                    not list(filter(lambda dict_item: name == dict_item['name'], self.symbol_table_class)):
                self.symbol_table_class.append({'name': name, 'kind': kind, 'type': typ, 'index': index})
            else:
                raise SyntaxError(name + ' redefined.')
        elif kind in ['argument', 'local']:
            if len(self.symbol_table_subroutine) == 0 or \
                    not list(filter(lambda dict_item: name == dict_item['name'], self.symbol_table_subroutine)):
                self.symbol_table_subroutine.append({'name': name, 'kind': kind, 'type': typ, 'index': index})
            else:
                raise SyntaxError(name + ' redefined.')
        return 0

    def var_count(self, kind):
        """
        Lookup the symbol table and return the number of given kind in the symbol table.

        :param kind:
        :return: The number of given kind in the symbol table.
        """
        if kind in ['static', 'field']:
            if len(self.symbol_table_class) == 0:
                return 0
            else:
                return len(list(filter(lambda dict_item: kind == dict_item['kind'], self.symbol_table_class)))
        elif kind in ['argument', 'local']:
            if len(self.symbol_table_subroutine) == 0:
                return 0
            else:
                return len(list(filter(lambda dict_item: kind == dict_item['kind'], self.symbol_table_subroutine)))
        pass

    def kind_of(self, name):
        kind = self.search_symbol(name)['kind']
        return kind

    def type_of(self, name):
        typ = self.search_symbol(name)['type']
        return typ

    def index_of(self, name):
        index = self.search_symbol(name)['index']
        return index

    def clean_subroutine_table(self):
        self.symbol_table_subroutine = []

    def search_symbol(self, name):
        if list(filter(lambda symbol_dict: name == symbol_dict['name'], self.symbol_table_class)):
            result = list(filter(lambda symbol_dict: name == symbol_dict['name'], self.symbol_table_class))[0]

        elif list(filter(lambda symbol_dict: name == symbol_dict['name'], self.symbol_table_subroutine)):
            result = list(filter(lambda symbol_dict: name == symbol_dict['name'], self.symbol_table_subroutine))[0]
        else:
            return None
        return result
