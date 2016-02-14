import argparse
from chord import Node, Key, Uid


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a node")

    parser.add_argument("-m", "--main", action="store_true",
            help="Define the created node as a central one :"
            "the one which will be contacted by others")
    parser.add_argument("-a", "--address", help="IP address of node")
    parser.add_argument("-p", "--port", help="Listening port of node")

    args = parser.parse_args()
    ip = args.address
    port = args.port

    ip = "127.0.0.1"
    node0 = Node(ip, "0")
    node1 = Node(ip, "1")
    node2 = Node(ip, "2")
    node3 = Node(ip, "3")
    node4 = Node(ip, "4")
    node5 = Node(ip, "5")
    node6 = Node(ip, "6")
    node7 = Node(ip, "7")

    node0.addToRing(node1)
    node1.addToRing(node2)
    node1.addToRing(node3)
    node3.addToRing(node4)
    node3.addToRing(node5)
    node5.addToRing(node6)
    node1.addToRing(node7)
    
    node0.printRing()
    node1.printRing()
    node2.printRing()
    node3.printRing()
    node4.printRing()
    node5.printRing()
    node6.printRing()
    node7.printRing()

    node0.printFingers()
    node1.printFingers()
    node2.printFingers()
    node3.printFingers()
    node4.printFingers()
    node5.printFingers()
    node6.printFingers()
    node7.printFingers()
    print "succ de 03:" + node2.lookup("3").uid.value
    print "succ de 03:" + node3.lookup("3").uid.value
    print "succ de 03:" + node4.lookup("3").uid.value
    print "succ de 03:" + node5.lookup("3").uid.value
    print "succ de 03:" + node6.lookup("3").uid.value
    print "succ de 03:" + node7.lookup("3").uid.value
    print "succ de 03:" + node0.lookup("3").uid.value



