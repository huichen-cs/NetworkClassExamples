"""Receive (via multicast) images sent by a sender using UDP.

   show_gallery.py
"""

import argparse
import io
import socket
import struct

from matplotlib import animation
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

MAX_PLAYLOD_SIZE = 65535 - 20 - 8


def parse_cmdline():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mcast_ip",
        type=str,
        help="The muticast IP address of the receiver.",
        default="localhost",
        dest="mcast_ip",
    )
    parser.add_argument(
        "--mcast_port",
        type=int,
        help="The port number of the receiver.",
        default=25000,
        dest="mcast_port",
    )
    parser.add_argument(
        "--arrival_ip",
        type=str,
        help="The IP address of the NIC to receive the multicast datagrams.",
        default=25000,
        dest="arrival_ip",
    )
    return parser.parse_args()


class Gallery:
    """A simple gallery to display images in animation."""

    def __init__(self, images, interval=1000):
        self.images = images
        self.interval = interval
        self.fig, self.ax = plt.subplots()

    def display_frame(self, i):
        self.ax.clear()
        self.ax.imshow(self.images[i])
        self.ax.set_title(f"Image {i} at host {socket.gethostname()}")

    def display_gallery(self):
        self.anim = animation.FuncAnimation(
            self.fig,
            self.display_frame,
            frames=len(self.images),
            interval=self.interval,
        )
        plt.show()
        self.anim = None


def receive_and_show_images(mcast_end_point, arrival_ip):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(mcast_end_point)
        print(f"bound to {mcast_end_point}")

        # This joins the socket to the intended multicast group. The implications
        # are two. It specifies the intended multicast group identified by the
        # multicast IP address.  This also specifies from which network interface
        # (NIC) the socket receives the datagrams for the intended multicast group.
        # It is important to note that socket.INADDR_ANY means the default network
        # interface in the system (ifindex = 1 if loopback interface present). To
        # receive multicast datagrams from multiple NICs, we ought to create a
        # socket for each NIC. Also note that we identify a NIC by its assigned IP
        # address.
        if arrival_ip == "0.0.0.0":
            mreq = struct.pack(
                "=4sl", socket.inet_aton(mcast_end_point[0]), socket.INADDR_ANY
            )
        else:
            mreq = struct.pack(
                "=4s4s",
                socket.inet_aton(mcast_end_point[0]),
                socket.inet_aton(arrival_ip),
            )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        images = []
        idx = 0
        while True:
            img_data = sock.recv(MAX_PLAYLOD_SIZE)
            if not img_data:
                print("End of Transmission")
                break
            print(f"Image {idx}: received {len(img_data)} bytes.")
            img = mpimg.imread(io.BytesIO(img_data), "jpg")
            images.append(img)
            idx += 1
    gallery = Gallery(images)
    gallery.display_gallery()


def main():
    args = parse_cmdline()
    end_point = (args.mcast_ip, args.mcast_port)
    receive_and_show_images(end_point, args.arrival_ip)
    print("Done.")


if __name__ == "__main__":
    main()
