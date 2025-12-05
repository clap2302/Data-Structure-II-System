from igraph import *

class Routes_Graph:
    def __init__(self, flights: list[dict]):
        self.graph = Graph(directed=True)
        self.flifhts = flights

        # 1. Pegar a lista de aeroportos que se tem dentro da lista

        # 2. Criar as arestas

        # 3. Atribuir os pesos

    def add_vertice(self, vertice: dict):
        pass

    def remove_vertice(self):
        pass

    




# Criando o grafo
g = Graph(directed=True)

# Adicinando 5 vertices
g.add_vertices(5)
g
# Adicionando id's e labels aos vertices
for i in range(len(g.vs)):
    g.vs[i]["id"]= i
    g.vs[i]["label"]= str(i)

# Adicionando arestas
g.add_edges([(0,2),(0,1),(0,3),(1,2),(1,3),(2,4),(3,4)])

# Adicionando pesos e  labels de arestas
weights = [8,6,3,5,6,4,9]
g.es['weight'] = weights
g.es['label'] = weights

# visual_style = {}

# out_name = "graph.png"

# # Set bbox and margin
# visual_style["bbox"] = (300,300)
# visual_style["margin"] = 27

# # Set vertex colours
# visual_style["vertex_color"] = 'white'

# # Set vertex size
# visual_style["vertex_size"] = 45

# # Set vertex lable size
# visual_style["vertex_label_size"] = 22

# # Don't curve the edges
# visual_style["edge_curved"] = False

# # Set  layout
# my_layout = g.layout_lgl()
# visual_style["layout"] = my_layout

# # Plot o grafo
# plot(g, out_name, **visual_style)