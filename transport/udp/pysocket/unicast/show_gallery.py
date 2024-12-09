"""Receive (via unicast) images sent by a sender using UDP.

   show_gallery.py
"""

import argparse
import io
import socket

from matplotlib import animation
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

MAX_PLAYLOD_SIZE = 65535 - 20 - 8


def parse_cmdline():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bind_ip",
        type=str,
        help="The IP address of the receiver.",
        default="localhost",
        dest="bind_ip",
    )
    parser.add_argument(
        "--bind_port",
        type=int,
        help="The port number of the receiver.",
        default=25000,
        dest="bind_port",
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


def receive_and_show_images(end_point):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(end_point)
        print(f"bound to {end_point}")
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
    end_point = (args.bind_ip, args.bind_port)
    receive_and_show_images(end_point)
    print("Done.")


if __name__ == "__main__":
    main()
