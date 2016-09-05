import argparse
from chord import Node, Key, Uid


class Ring():

    def __init__(self, nbNode):
        self.nbNode = nbNode

    def createLocalRing(self):
        ip = "127.0.0.1"
        self.nodes = []
        for n, node in enumerate(range(0, self.nbNode)):
            self.nodes.append(Node(ip, repr(n)))

        # TODO IMPROVE: Randomize which node add the new one
        for node in self.nodes:
            if node is not self.nodes[0]:
                self.nodes[0].addToRing(node)
        return self.nodes

    def printRings(self):
        for node in self.nodes:
            node.printRing()

    def printFingers(self):
        for node in self.nodes:
            node.printFingers()

    def lookupNode(self, fromNode, key):
        successorFound = fromNode.lookup(key, False)
        fromNode.log.debug(
            "succ de {key} is {successorFound}"
            .format(key=key,
                    successorFound=successorFound.uid)
        )
    def lookupFromAllNode(self, key):
        for node in self.nodes:
            self.lookupNode(node, key)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a ring")

    parser.add_argument("-m", "--main", action="store_true",
            help="Define the created node as a central one :"
            "the one which will be contacted by others")
    parser.add_argument("-a", "--address", help="IP address of node")
    parser.add_argument("-p", "--port", help="Listening port of node")

    args = parser.parse_args()
    ip = args.address
    port = args.port


    print("########\n## DEBUG RING\n#########\n\n")
    ring = Ring(10)
    ring.createLocalRing()
    ring.printRings()
    ring.nodes[8].printFingers()
    
    ring.lookupFromAllNode("3")

