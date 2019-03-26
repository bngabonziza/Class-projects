import pandas as pd
from models.ConceptRelation import *

if __name__ == "__main__":
    mg = Med_Knowledge_Graph()
    mg.getDatabaseConcepts()
    # mg.getDistTags()
    mg.associateTags()