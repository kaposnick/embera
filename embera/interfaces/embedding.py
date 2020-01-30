__all__ = ["Embedding"]


class Embedding(dict):

    properties = {}
    def __init__(self, embedding, **properties):
        super(Embedding,self).__init__(embedding)
        self.properties = properties

    """ ############################ Histograms ############################ """
    def chain_histogram(self):
        # Based on dwavesystems/minorminer quality_key by Boothby, K.
        hist = {}
        for s in map(len,self.values()):
            hist[s] = 1 + hist.get(s, 0)
        return hist

    def interactions_histogram(self, source_edgelist, target_edgelist):
        interactions = self.interactions(source_edgelist,target_edgelist)

        hist = {}
        for size in map(len,interactions.values()):
            hist[size] = 1 + hist.get(size, 0)

        return hist

    def connectivity_histogram(self, source_edgelist, target_edgelist):
        connections = self.connections(source_edgelist,target_edgelist)

        source_degree = {}
        for u,v in source_edgelist:
            if (u==v): continue
            source_degree[u] = 1 + source_degree.get(u,0)
            source_degree[v] = 1 + source_degree.get(v,0)

        hist = {}
        for t,edges in connections.items():
            u,v = edges[0]
            edgeset = set(edges)
            connectivity = len(edgeset)/source_degree[u]
            hist[connectivity] = 1 + hist.get(connectivity,0)

        return hist

    """ ############################## Metrics ############################# """
    def interactions(self,source_edgelist,target_edgelist):
        target_adj = {}
        for s,t in target_edgelist:
            if (s==t): continue
            target_adj[s] = [t] + target_adj.get(s,[])
            target_adj[t] = [s] + target_adj.get(t,[])

        interactions = {}
        for u,v in source_edgelist:
            if (u==v): continue
            edge_interactions = []
            for s in self[u]:
                for t in self[v]:
                    if t in target_adj[s]:
                        edge_interactions.append((s,t))
            interactions[(u,v)] = edge_interactions

        return interactions

    def connections(self,source_edgelist,target_edgelist):
        interactions = self.interactions(source_edgelist,target_edgelist)

        connections = {}
        for (u,v),edge_interactions in interactions.items():
            for s,t in edge_interactions:
                connections[s] = [(u,v)] + connections.get(s,[])
                connections[t] = [(v,u)] + connections.get(t,[])

        return connections

    @property
    def max_chain(self):
        hist = self.chain_histogram()
        return max(hist)

    @property
    def total_qubits(self):
        QK = self.quality_key
        return sum([QK[i]*QK[i+1] for i in range(0,len(QK),2)])

    @property
    def quality_key(self):
        #TEMP: Can be better
        hist = self.chain_histogram()
        return [value for item in sorted(hist.items(), reverse=True) for value in item]

    """ ############################# Interface ############################ """
    @property
    def id(self):
        # To create a unique ID we use the quality key as an ID string...
        if not self: return "NATIVE" # ..., unless empty,
        else: quality_id = "".join([str(v) for v in self.quality_key])
        # ...and the last 8 digits of this object's hash.
        hash_id = f"{self.__hash__():08}"[-8:]
        return f"{quality_id}_{hash_id}"

    def __key(self):
        embedding_key = []
        for v,chain in self.items():
            chain_key = []
            for q in chain:
                chain_key.append(hash(q))
            embedding_key.append(hash(tuple(sorted(chain_key))))
        return hash(tuple(embedding_key))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()
    def __ne__(self, other):
        return self.__key() != other.__key()
    def __lt__(self, other):
        return self.quality_key < other.quality_key
    def __le__(self, other):
        return self.quality_key <= other.quality_key
    def __gt__(self, other):
        return self.quality_key > other.quality_key
    def __ge__(self, other):
        return self.quality_key >= other.quality_key
