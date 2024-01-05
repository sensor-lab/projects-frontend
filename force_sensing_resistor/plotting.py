from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
import argparse
import pathlib
import datetime
import csv

def update(data):
    global x, y, y_line, ax, y_line2, y2
    x.append(datetime.datetime.now())
    y.append(data["ch5"])
    y2.append(data["ch1"])
    y_line.set_xdata(x)
    y_line.set_ydata(y)
    y_line2.set_xdata(x)
    y_line2.set_ydata(y2)
    ax.set_xlim([min(x), max(x)])
    ax.set_ylim([min(min(y), min(y2)) * 0.8, max(max(y), max(y2)) * 1.2])
    ax.autoscale_view()
    print(f"x: {x}, y: {y}")
    print(f"x: {x}, y2: {y2}")
    return [y_line, y_line2]

def data_gen():
    data = {
        "ch1": 0,
        "ch2": 1,
        "ch3": 2,
        "ch4": 3,
        "ch5": 4
    }
    while True:
        data["ch1"] += 1
        data["ch2"] += 0.9
        data["ch3"] += 0.8
        data["ch4"] += 1.1
        data["ch5"] += 1.2
        yield(data)


def main(capture_interval, no_plot, csv_output_filename):
    global x, y, y_line, ax, y_line2, y2
    fig, ax = plt.subplots()
    x = []
    y = []
    y2 = []
    y_line, = ax.plot(x, y, color="r")
    y_line2, = ax.plot(x, y2, color="g")
    animation = FuncAnimation(fig, update, data_gen, interval=1000)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture thermistor readings")
    parser.add_argument(
        "--capture-interval",
        type=int,
        default=60,
        required=False,
        help="Capture interval in seconds",
    )
    parser.add_argument(
        "--no-plot",
        default=False,
        action="store_true",
        required=False,
        help="Not plotting graph",
    )
    parser.add_argument(
        "--csv-output",
        type=pathlib.Path,
        required=False,
        default="thermistor_capture.csv",
        help="output csv filename",
    )
    args = parser.parse_args()
    main(args.capture_interval, args.no_plot, args.csv_output)
