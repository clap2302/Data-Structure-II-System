# Import para pegar os dict's de vôos
from modules.flight_manager import FlightManager

# libs para mostrar as rotas no mapa
import folium
from folium.plugins import AntPath

# lib para pegar as longitudes e latitudes
import airportsdata

# lib dos grafos
from igraph import *

# para calculcar a distância baseada na longitude e latitude
from math import radians, sin, cos, sqrt, atan2

# para gerar o mapa html na pasta de templates
import os


class Routes_Graph:
    def __init__(self):
        self.graph = Graph(directed=True)
        self.flights = FlightManager.load_flights_dict()
        self.airports_db = airportsdata.load("IATA")

        # --- Coleta os nomes dos aeroportos ---
        airport_names = (
            {f["origin"] for f in self.flights.values()} |
            {f["destiny"] for f in self.flights.values()}
        )
        airport_names = list(airport_names)

        # cria vértices
        self.graph.add_vertices(len(airport_names))
        self.index_of = {airport_names[i]: i for i in range(len(airport_names))}

        # define o nome e a label de cada vértice
        for i, name in enumerate(airport_names):
            self.graph.vs[i]["name"] = name
            self.graph.vs[i]["label"] = name

        # --- Criar as arestas ---
        edges = []
        weights = []

        for code, f in self.flights.items():
            o = f["origin"]
            d = f["destiny"]

            o_idx = self.index_of[o]
            d_idx = self.index_of[d]

            if o not in self.airports_db or d not in self.airports_db:
                continue  # pula aeroportos desconhecidos

            # pega as coordenadas de cada aeroporto
            a1 = self.airports_db[o]
            a2 = self.airports_db[d]

            distance = haversine(a1["lat"], a1["lon"], a2["lat"], a2["lon"])

            edges.append((o_idx, d_idx))
            weights.append(distance)

        self.graph.add_edges(edges)
        self.graph.es["weight"] = weights


    '''
        Adiciona vertice
    '''
    def add_vertice(self, vertice_id: str):
        """
        vertice_id = "GRU"
        """
        name = vertice_id.upper()

        if name in self.graph.vs["name"]:
            return  # já existe

        self.graph.add_vertex(name=name, label=name)
        self.index_of[name] = len(self.graph.vs) - 1

    '''
        Remove vertice
    '''
    def remove_vertice(self, vertice_id: str):
        """
        vertice_id = "GRU"
        """
        name = vertice_id.upper()

        if name not in self.graph.vs["name"]:
            return

        idx = self.graph.vs.find(name=name).index
        self.graph.delete_vertices(idx)

        # importante: precisamos remover também do index_of
        if name in self.index_of:
            del self.index_of[name]

    '''
        Adiciona Edge
    '''
    def add_edge(self, edge: dict):
        """
        edge = {
            "origin": "GRU",
            "destiny": "LAX",
            ...
        }
        """
        o = edge["origin"]
        d = edge["destiny"]

        # garantir que os vértices existem
        if o not in self.graph.vs["name"]:
            self.add_vertice(o)
        if d not in self.graph.vs["name"]:
            self.add_vertice(d)

        o_idx = self.graph.vs.find(name=o).index
        d_idx = self.graph.vs.find(name=d).index

        # calcular distância geográfica
        a1 = self.airports_db[o]
        a2 = self.airports_db[d]

        distance = haversine(a1["lat"], a1["lon"], a2["lat"], a2["lon"])

        # criar a aresta
        self.graph.add_edge(o_idx, d_idx)
        self.graph.es[-1]["weight"] = distance
        

    '''
        Remove Edge
    '''
    def remove_edge(self, origin: str, destiny:str):
        if origin not in self.graph.vs["name"] or destiny not in self.graph.vs["name"]:
            return

        o_idx = self.graph.vs.find(name=origin).index
        d_idx = self.graph.vs.find(name=destiny).index

        eid = self.graph.get_eid(o_idx, d_idx, directed=True, error=False)
        if eid != -1:
            self.graph.delete_edges(eid)


    """
        Utiliza o Dikstra para calcular a menor distância entre rotas
    """
    def shortest_path(self, origin: str, destination: str):
        if origin not in self.graph.vs["name"] or destination not in self.graph.vs["name"]:
            raise ValueError("Aeroporto não existe no grafo.")

        o_idx = self.graph.vs.find(name=origin).index
        d_idx = self.graph.vs.find(name=destination).index

        path = self.graph.get_shortest_paths(o_idx, to=d_idx, weights="weight", output="vpath")[0]

        # converte os índices em nomes
        route = [self.graph.vs[i]["name"] for i in path]

        # calcula a distância total
        total_distance = sum(
            self.graph.es[self.graph.get_eid(path[i], path[i+1])]["weight"]
            for i in range(len(path)-1)
        )

        return {
            "route": route,
            "distance_km": total_distance
        }

    def show_all_routes_map(self, filename="routes_map.html"):
        # ==========================================
        #  PAINEL DE PERSONALIZAÇÃO VISUAL
        # ==========================================
        
        # 1. TEMA DO MAPA
        # Opções: "OpenStreetMap" (Claro/Padrão), "CartoDB dark_matter" (Escuro/Contraste alto), "CartoDB positron" (Minimalista)
        # O tema escuro é excelente para fazer as rotas coloridas "brilharem".
        MAP_THEME = "CartoDB dark_matter" 

        # 2. COR DA ROTA
        # A cor principal da linha animada. Pode usar nomes ("orange") ou Hex ("#FF5733").
        ROUTE_COLOR = "orange" 
        
        # 3. COR DO PULSO (O "fundo" da linha)
        # A cor que fica "atrás" da animação. Se for "white", parece que a luz corre sobre um trilho branco.
        PULSE_COLOR = "white"

        # 4. ESPESSURA DA LINHA
        # Para evitar o "Spaghetti Plot", use valores baixos (1 ou 2). Linhas grossas poluem o mapa.
        LINE_WEIGHT = 1.5 

        # 5. TRANSPARÊNCIA (0.0 a 1.0)
        # CRUCIAL: Se 0.5, duas linhas sobrepostas criam uma cor mais forte. 
        # Isso ajuda a ver onde há congestionamento de rotas.
        LINE_OPACITY = 0.6

        # 6. VELOCIDADE DA ANIMAÇÃO
        # Valor em milissegundos. Quanto maior, mais lenta a "formiguinha". 
        # Ajuste para não deixar o mapa frenético demais.
        ANIMATION_DELAY = 800 

        # ==========================================

        # Cria o mapa usando o tema escolhido
        m = folium.Map(zoom_start=2, tiles=MAP_THEME)
        
        for e in self.graph.es:
            o_idx = e.source
            d_idx = e.target

            o_name = self.graph.vs[o_idx]["name"]
            d_name = self.graph.vs[d_idx]["name"]

            if o_name not in self.airports_db or d_name not in self.airports_db:
                continue

            a1 = self.airports_db[o_name]
            a2 = self.airports_db[d_name]

            coords = [
                (a1["lat"], a1["lon"]),
                (a2["lat"], a2["lon"])
            ]

            # Cria o texto que aparece ao passar o mouse (Tooltip)
            # Ajuda a identificar a rota no meio da bagunça
            route_info = f"Rota: {o_name} ➝ {d_name}"

            AntPath(
                coords,
                color=ROUTE_COLOR,       # Usa a var do painel
                pulse_color=PULSE_COLOR, # Usa a var do painel
                delay=ANIMATION_DELAY,   # Usa a var do painel
                weight=LINE_WEIGHT,      # Usa a var do painel
                opacity=LINE_OPACITY,    # Usa a var do painel
                tooltip=route_info,      # Adiciona interatividade
                popup=f"Origem: {o_name}<br>Destino: {d_name}" # Clique para detalhes
            ).add_to(m)

        # Salva o arquivo
        path = os.path.join("templates", filename)
        m.save(path)
        print(f"Mapa gerado com o tema '{MAP_THEME}' em: {path}")
        return m


'''
    Função para calcular a distância entre aeroportos
'''
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # raio da Terra em km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
