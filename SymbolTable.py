class SymbolTable:
    def __init__(self):
        self.symbol_table_class = []
        self.symbol_table_subroutine = []
        pass

    def define(self, name, kind, type0):
        number=self.var_count(kind)
        if kind in ['static', 'field']:
            if len(self.symbol_table_class) == 0 or \
                    not list(filter(lambda dict_item: name == dict_item['name'], self.symbol_table_class)):
                self.symbol_table_class.append({'name': name, 'kind': kind, 'type': type0, 'number': number})
            else:
                raise SyntaxError(name+' redefined.')
        elif kind in ['argument', 'local']:
            if len(self.symbol_table_subroutine) == 0 or \
                    not list(filter(lambda dict_item: name == dict_item['name'], self.symbol_table_subroutine)):
                self.symbol_table_subroutine.append({'name': name, 'kind': kind, 'type': type0, 'number': number})
            else:
                raise SyntaxError(name + ' redefined.')

    def var_count(self, kind):
        if kind in ['static','field']:
            if len(self.symbol_table_class) == 0:
                return 0
            else:
                return len(list(filter(lambda dict_item: kind == dict_item['kind'], self.symbol_table_class)))
        elif kind in ['argument','local']:
            if len(self.symbol_table_subroutine)==0:
                return 0
            else:
                return len(list(filter(lambda dict_item: kind == dict_item['kind'], self.symbol_table_subroutine)))
        pass

    def kind_of(self, name):
        pass

    def type_of(self, name):
        pass

    def index_of(self, name):
        pass
