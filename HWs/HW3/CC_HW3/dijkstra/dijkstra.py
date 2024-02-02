from mrjob.job import MRJob
from mrjob.step import MRStep


class Dijkstra(MRJob):

    def configure_args(self):
        # Inherit arguments configuration
        super(Dijkstra, self).configure_args()

    def steps(self):
        # Define the steps for the MapReduce job
        return [MRStep(mapper=self.mapper, reducer=self.reducer)]

    def mapper(self, _, line):
        # Parse each line from the input
        _, node, data = line.strip().split('"', 2)
        node = node.strip('"')
        data = self.my_eval(data)

        # Emit the node and its data
        yield node, data

        # Process and emit data for adjacent nodes
        if data['Distance'] != float('inf'):
            for key, value in data['AdjacencyList'].items():
                new_data = {'Distance': data['Distance'] + value}
                yield key, new_data

    def reducer(self, key, values):
        # Initialize variables for the shortest distance and adjacency list
        min_distance = float('inf')
        adjacency_list = None

        # Iterate over values to find the minimum distance
        for value in values:
            min_distance = min(min_distance, value['Distance'])
            if 'AdjacencyList' in value:
                adjacency_list = value['AdjacencyList']

        # Yield the key and updated data
        yield key, {'Distance': min_distance, 'AdjacencyList': adjacency_list}

    @staticmethod
    def my_eval(line):
        # Replace Infinity with float('inf') and evaluate the line
        line = line.replace("Infinity", "float('inf')")
        return eval(line)


if __name__ == '__main__':
    Dijkstra.run()
