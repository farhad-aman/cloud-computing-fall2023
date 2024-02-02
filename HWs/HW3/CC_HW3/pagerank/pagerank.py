from mrjob.job import MRJob
from mrjob.step import MRStep

# PageRank's convergence threshold
EPSILON = 0.1


class PageRank(MRJob):

    def configure_args(self):
        super(PageRank, self).configure_args()

    def steps(self):
        return [MRStep(mapper=self.mapper, reducer=self.reducer)]

    def mapper(self, _, line):
        # Parse each line from the input
        _, node, data = line.strip().split('"', 2)
        node = node.strip('"')
        data = eval(data)

        # Emit the node and its structure
        yield node, ('node_data', data)

        # Emit PageRank contributions to adjacent nodes
        if data['AdjacencyList']:
            page_rank_contribution = data['PageRank'] / len(data['AdjacencyList'])
            for neighbor in data['AdjacencyList']:
                yield neighbor, ('page_rank_contribution', page_rank_contribution)

    def reducer(self, node, values):
        total_page_rank_contribution = 0
        node_data = None

        for value_type, value in values:
            if value_type == 'node_data':
                node_data = value
            else:
                total_page_rank_contribution += value

        # Calculate the new PageRank
        new_pagerank = 0.15 + 0.85 * total_page_rank_contribution
        node_data['PageRank'] = new_pagerank

        # Emit the node with updated PageRank and its structure
        yield node, node_data

        # Emit a special key for checking convergence
        if abs(new_pagerank - node_data['PageRank']) > EPSILON:
            yield 'convergence_check', 1


if __name__ == '__main__':
    PageRank.run()
