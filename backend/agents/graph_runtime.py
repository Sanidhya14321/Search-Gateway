try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover
    START = "__start__"
    END = "__end__"

    class _CompiledGraph:
        def __init__(self, nodes, edges, conditional_edges):
            self.nodes = nodes
            self.edges = edges
            self.conditional_edges = conditional_edges

        async def ainvoke(self, state: dict) -> dict:
            current = self.edges.get(START)
            working = dict(state)
            while current and current != END:
                updates = await self.nodes[current](working)
                if updates:
                    working.update(updates)

                if current in self.conditional_edges:
                    chooser, routes = self.conditional_edges[current]
                    route_key = chooser(working)
                    current = routes.get(route_key, END)
                    continue

                current = self.edges.get(current, END)
            return working

    class StateGraph:
        def __init__(self, _state_type):
            self.nodes = {}
            self.edges = {}
            self.conditional_edges = {}

        def add_node(self, name, fn):
            self.nodes[name] = fn

        def add_edge(self, src, dst):
            self.edges[src] = dst

        def add_conditional_edges(self, src, chooser, routes):
            self.conditional_edges[src] = (chooser, routes)

        def compile(self):
            return _CompiledGraph(self.nodes, self.edges, self.conditional_edges)
