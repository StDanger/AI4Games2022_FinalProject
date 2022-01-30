class Specie:
    def __init__(self,**kwargs):
        self.representative = kwargs.get('representative',None)
        self.members = kwargs.get('members',[])
        self.size = kwargs.get('size',None)
        self.offspring_size = kwargs.get('offspring_size',None)
        self.fitness = kwargs.get('fitness',[])
        self.adjusted_fitness = kwargs.get('adjusted_fitness',[])
        self.max_score = kwargs.get('max_score',float('-inf'))
        self.generation_since_improved = kwargs.get('max_score',0)
        self.avg_fitness_adjusted = kwargs.get('avg_fitness_adjusted',None)
