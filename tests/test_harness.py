import time
import network_harness as hn

def test_tiebreaker_protocol():
    
    net = hn.Network()
    nodes = []

    normal_node = hn.Node(1)
    nodes.append(normal_node)
    net.add_node(1, normal_node)

    rogue_node = hn.Node(2, target_func="tie")
    nodes.append(rogue_node)
    net.add_node(2, rogue_node)

    net.create_channel(1, 2)

    normal_node.start()
    time.sleep(5)
    rogue_node.start()

    normal_node_id = normal_node.thisDevice.get_id()
    rogue_node_id = rogue_node.thisDevice.get_id()

    time.sleep(30)
    
    normal_node.stop()
    rogue_node.stop()

    print(normal_node)
    print(rogue_node)



def main():
    test_tiebreaker_protocol()


if __name__ == "__main__":
    main()