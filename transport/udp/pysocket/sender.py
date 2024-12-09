"""Send images in a directory to a receiver using UDP."""

import argparse
import glob
import pathlib
import socket


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
        "--to_ip",
        type=str,
        help="The IP address of the receiver.",
        default="localhost",
        dest="to_ip",
    )
    parser.add_argument(
        "--to_port",
        type=int,
        help="The port number of the receiver.",
        default=25000,
        dest="to_port",
    )
    return parser.parse_args()


def send_images(img_dir, destination):
    """Send images to a receiver using UDP.

    Args:
        img_dir (str): The directory containing the images to send.
        destination (str): the end point of the receiver, a tuple consiting of
                           the IP address and port number.
    """
    for img_idx, img_path in enumerate(
        glob.glob(str(pathlib.Path(img_dir).joinpath("*.jpg")))
    ):
        with open(img_path, "rb") as img_file:
            img_data = img_file.read()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(img_data, destination)
            print(f"Image {img_idx}: sent {len(img_data)} bytes to {destination}.")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto("".encode(), destination)
        print("End of Transmission")


def main():
    args = parse_cmdline()
    destination = (args.to_ip, args.to_port)
    send_images(args.img_dir, destination)
    print("Done.")


if __name__ == "__main__":
    main()
