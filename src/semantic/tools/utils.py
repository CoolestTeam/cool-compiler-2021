import itertools
import pydot
import uuid

def path_to_objet(typex):
    path = []
    c_type = typex

    while c_type:
        path.append(c_type)
        c_type = c_type.parent

    path.reverse()
    return path


def get_common_basetype(types):
    index = []
    paths = []
    for typex in types:
        paths.append(path_to_objet(typex))

    index = 0
    result = paths[0][index]
    
    while True:        
        if index >= len(paths[0]):
            return result

        pivot = paths[0][index]

        for p in paths:
            if index >= len(p) or p[index].name != pivot.name:
                return result

        result = paths[0][index]
        index += 1

def parse_tree_right(productions):
    
    def parse(G, productions, i):
        left, right = productions[i]
        
        node = pydot.Node(uuid.uuid4().hex, label=left.Name, shape ="circle", style="filled", fillcolor="white") 
        G.add_node(node)

        for symbol in reversed(right):
            if symbol.IsTerminal:
                child = pydot.Node(uuid.uuid4().hex, label=symbol.Name, shape="circle", style="filled", fillcolor="white")
                G.add_node(child)
                G.add_edge(pydot.Edge(node, child))
            else:
                child, i = parse(G, productions, i + 1)
                G.add_edge(pydot.Edge(node, child))

        if right.IsEpsilon:
            child = pydot.Node(uuid.uuid4().hex, label='ε', shape="circle", style="filled", fillcolor="white")
            G.add_node(child)
            G.add_edge(pydot.Edge(node, child)) 
        return node, i
    
    productions.reverse()
    G = pydot.Dot(graph_type='digraph')
    node, i = parse(G, productions, 0)
   
    return G