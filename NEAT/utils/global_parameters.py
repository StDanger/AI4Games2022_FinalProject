

class Global_parameters:
    def __init__(self, **kwargs):
        self.pop_size = kwargs.get('pop_size',10)
        self.input_n = kwargs.get('input_n',3)
        self.output_n = kwargs.get('output_n',3)
        self.hidden_n = kwargs.get('hidden_n',2)
        self.init_connection_density = kwargs.get('init_connection_density',0.5)
        self.innov = 1
        self.lookup_table = [[0] * 10 for _ in range(10)]

    def get_innov(self,input,output):
        innov = self.lookup_table[input][output]
        if innov == 0:
            innov = self.innov
            self.lookup_table[input][output] = innov
            self.innov += 1
        return innov