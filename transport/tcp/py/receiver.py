"""Receive images sent by a sender using TCP."""

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
        "--listen_ip",
        type=str,
        help="The IP address of the receiver.",
        default="localhost",
        dest="listen_ip",
    )
    parser.add_argument(
        "--listen_port",
        type=int,
        help="The port number of the receiver.",
        default=25000,
        dest="listen_port",
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(end_point)
        sock.listen(1)
        print(f"Listening on {end_point}")
        images = []
        idx = 0
        while True:
            conn, _ = sock.accept()
            with conn:
                img_data = conn.recv(MAX_PLAYLOD_SIZE)
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
    end_point = (args.listen_ip, args.listen_port)
    receive_and_show_images(end_point)
    print("Done.")


if __name__ == "__main__":
    main()
