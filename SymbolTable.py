class SymbolTable:
    def __init__(self):
        self.symbol_table_class = []
        self.symbol_table_subroutine = []
        pass

    def define(self, name, kind, typ):
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

    def var_count(self, kind):
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
