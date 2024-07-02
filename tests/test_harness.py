import time
import network_harness as hn
import csv

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

    time.sleep(10)

    normal_node.stop()
    rogue_node.stop()

    normal_log = f'output/device_log_{normal_node_id}.csv'
    rogue_log = f'output/device_log_{rogue_node_id}.csv'

    with open(normal_log, newline='') as normal_logs:
        normal_reader = csv.reader(normal_logs, dialect='excel')
        with open(rogue_log, newline='') as rogue_logs:
            rogue_reader = csv.reader(rogue_logs, dialect='excel')

            normal_leader = (normal_node_id > rogue_node_id)

            if normal_leader:
                for row in normal_reader:
                    pass





def main():
    test_tiebreaker_protocol()


if __name__ == "__main__":
    main()