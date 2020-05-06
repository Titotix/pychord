import chord
import random

def createlocalnodes(nb, *args, printports=True, setfingers=False, setpredecessor=False):
    """
    Return a list of LocalNode instantiated
    Their ip are 127.0.0.1 and their ports are either provided as args,
    if not their are randomly generated

    @param nb: number of node to generate
    @param port1,port2,... ports of generated nodes
    @param printports: If it print ports of nodes. Default True
    """
    if not isinstance(nb, int) or nb < 1:
        raise ValueError
    if len(args) > 0 and len(args) != nb:
        raise ValueError
    ports = []
    if len(args) == 0:
        for i in range(0, nb):
            ports.append(random.randint(1025, 60000))
    else:
        for port in args:
            ports.append(port)

    #closure fction inspired by
    #https://stackoverflow.com/questions/52453635/changing-the-duplicate-values-in-the-multi-dimensional-list-in-python
    # purpose is to avoid equality port in ports list
    def f():
        seen = set()
        def g(a):
            while a in seen:
                a += 1
            seen.add(a)
            return a
        return g
    t = f()
    ports = [t(x) for x in ports]

    nodelist = []
    for i in range(0, nb):
        nodelist.append(chord.LocalNode("127.0.0.1", ports[i]))

    if printports:
        output = ", ".join([str(x.port) for x in nodelist])
        print("Generated nodes ports: (%s)" % (output))

    if setfingers:
        if nb == 2 or nb == 3:
            hardsetfingers(nodelist)
        else:
            print("ERROR: setfingers is supported only for 2 and 3 nodes ring. Passed")
    if setpredecessor:
        try:
            hardsetpredecessor(nodelist)
        except ValueError:
            print("ERROR: hardsetpredecessor only supports 2 and 3 nodes ring. Passed")

    return nodelist

def hardsetfingers(nodelist):
    if len(nodelist) == 2:
        return _setfingersTwoNode(nodelist)
    elif len(nodelist) == 3:
        return _setfingersThreeNode(nodelist)
    else:
        raise ValueError("Supports only for 2 and 3 nodes")

def _setfingersTwoNode(nodelist):
    for k, node in enumerate(nodelist):
        othernode = nodelist[(k+1) % len(nodelist)]
        for i in range(0, node.uid.idlength):
            if node.fingers[i].key.isbetween(node.uid, othernode.uid):
                node.fingers[i].setnode(othernode)
            else:
                node.fingers[i].setnode(node)

def _setfingersThreeNode(nodelist):
    for k, node in enumerate(nodelist):
        node1 = nodelist[(k+1) % len(nodelist)]
        node2 = nodelist[(k+2) % len(nodelist)]
        if node.uid.isbetween(node1.uid, node2.uid):
            nodesuccessor = node2
            nodepredecessor = node1
        else:
            nodesuccessor = node1
            nodepredecessor = node2
        for i in range(0, node.uid.idlength):
            if node.fingers[i].key.isbetween(node.uid, nodesuccessor.uid):
                node.fingers[i].setnode(nodesuccessor)
            elif node.fingers[i].key.isbetween(nodesuccessor.uid, nodepredecessor.uid):
                node.fingers[i].setnode(nodepredecessor)
            else:
                node.fingers[i].setnode(node)

def hardsetpredecessor(nodelist):
    if len(nodelist) == 2:
        _setpredecessorTwoNode(nodelist[0], nodelist[1])
    elif len(nodelist) == 3:
        _setpredecessorThreeNode(nodelist)
    else:
        raise ValueError

def _setpredecessorTwoNode(node0, node1):
    node0.setpredecessor(node1.asdict())
    node1.setpredecessor(node0.asdict())

def _setpredecessorThreeNode(nodelist):
    for k, node in enumerate(nodelist):
        node1 = nodelist[(k+1) % len(nodelist)]
        node2 = nodelist[(k+2) % len(nodelist)]
        if node.uid.isbetween(node1.uid, node2.uid):
            node.setpredecessor(node1.asdict())
        else:
            node.setpredecessor(node2.asdict())

def stoplocalnodes(nodes):
    for node in nodes:
        node.stopXmlRPCServer()