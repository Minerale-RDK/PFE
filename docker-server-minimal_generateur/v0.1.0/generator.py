class Generator:
  def __init__(self, Capacity):
    self.capacity = Capacity


  def Production(self,cpt,consommation,productionSolaire):
    # Le réseau doit est stable à la fréquence f0=50Hz
    f0 = 50
    # Ma production P varie en fonction de la journée
    production = consommation
    if(production > self.capacity):
      production = self.capacity

    # f1 - f0 = (Production-Consommation) / Capacité Totale
    f1 = (production  + productionSolaire - consommation)/self.capacity + f0
    
    return f1