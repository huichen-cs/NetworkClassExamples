"""Send (via multicast) images in a directory to a receiver using UDP.


   send_gallery.py
"""

import argparse
import glob
import pathlib
import socket
import time

WAIT_INTERVAL = 3


def parse_cmdline():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--img_dir",
        type=str,
        help="The directory containing the images to send.",
        default="images/small",
        dest="img_dir",
    )
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
        "--outbound_ip",
        type=str,
        help="The IP address of the NIC to send the multicast datagrams.",
        default="localhost",
        dest="outbound_ip",
    )
    return parser.parse_args()


def send_images(img_dir, destination, outbound_ip):
    """Send images to a receiver using UDP.

    Args:
        img_dir (str): The directory containing the images to send.
        destination (str): the multicast end point of the receiver, a tuple consiting of
                           the IP address and port number.
        outbound_ip (str): The IP address of the NIC to send the multicast datagrams.
    """
    for img_idx, img_path in enumerate(
        glob.glob(str(pathlib.Path(img_dir).joinpath("*.jpg")))
    ):
        with open(img_path, "rb") as img_file:
            img_data = img_file.read()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # This defines how many hops a multicast datagram can travel.
            # The IP_MULTICAST_TTL's default value is 1 unless we set it otherwise.
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

            # This defines to which network interface (NIC) is responsible for
            # transmitting the multicast datagram; otherwise, the socket
            # uses the default interface (ifindex = 1 if loopback is 0)
            # If we wish to transmit the datagram to multiple NICs, we
            # ought to create a socket for each NIC.
            s.setsockopt(
                socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(outbound_ip)
            )

            s.sendto(img_data, destination)
            print(f"Image {img_idx}: sent {len(img_data)} bytes to {destination}.")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        s.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(outbound_ip)
        )
        # Why do we need this? Is it a good way
        time.sleep(WAIT_INTERVAL)
        s.sendto("".encode(), destination)
        print("End of Transmission")


def main():
    args = parse_cmdline()
    destination = (args.mcast_ip, args.mcast_port)
    send_images(args.img_dir, destination, args.outbound_ip)
    print("Done.")


if __name__ == "__main__":
    main()
