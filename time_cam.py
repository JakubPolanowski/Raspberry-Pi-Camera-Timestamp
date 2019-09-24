#!/usr/bin/python3

import picamera
import datetime
import argparse

from time import sleep

# Default Config

delay = False
delay_time = 5  # seconds

camera_label = "LABEL"
timestamp_font_size = 50

camera_resolution = [640, 480]
framerate = 25

record_time = -1
intervals = 1

output = 'placeholder'

# Read in Args

parser = argparse.ArgumentParser(description="""Picamera based script for
                                  recording and previewing Raspberry camera
                                  output with a timestamp, time is pulled
                                  in from the system time""")

parser.add_argument("-p", "--preview", action='store_true', help="""enable
                     preview""")
parser.add_argument("-c", "--capture", action='store_true', help="""enable
                     video capture to file""")
parser.add_argument("-o", "--output", help="""set recording output destination
                    , only useful if recording has been enabled""")
parser.add_argument("-s", "--screen_resolution", help="""set screen resolution
                    , default is 640x480""")
parser.add_argument("-r", "--framerate", type=int, help="""set video framerate,
                     default is 25""")
parser.add_argument("-l", "--timestamp_label", help="""set label that is
                     displayed prior the the date and time in the timestamp.
                     Default is 'LABEL'""")
parser.add_argument("-ts", "--timestamp_size", type=int, help="""set timestamp
                     size, can be between 1 and 170. Default is 50""")
parser.add_argument("-t", "--record_time", type=int, help="""set video record
                     time per interval, default is infinite (-t -1)""")
parser.add_argument("-i", "--intervals", type=int, help="""record how many
                     intervals, each interval will record for specified time
                     to a file, the next interval will record to a new file
                     with an incrementing number appended to the filename.
                     Default is 1. Can specifiy infinite with (-i -1)""")
parser.add_argument("-d", "--delay_time", type=int, help="""set delay time
                     (seconds) before any video action (preview, capture) is
                     performed. Default is not to delay""")

args = parser.parse_args()

if not args.preview and not args.capture:
    print("Neither preview nor capture was enabled. Exiting...")
    exit()

if args.capture and args.output is None:
    print("An output must be specified if capturing video")
    exit()


def start_camera():
    global delay
    global delay_time
    global camera_label
    global timestamp_font_size
    global camera_resolution
    global framerate
    global record_time
    global intervals
    global output

    if args.screen_resolution is not None:
        camera_resolution = args.screen_resolution.split('x')

    if args.framerate is not None:
        framerate = args.framerate

    if args.timestamp_label is not None:
        camera_label = args.timestamp_label

    if args.timestamp_size is not None:
        timestamp_font_size = args.timestamp_size

    if args.delay_time is not None:
        delay = True
        delay_time = args.delay_time

    if args.record_time is not None:
        record_time = args.record_time

    if args.intervals is not None:
        intervals = args.intervals

    if args.output is not None:
        output = args.output

    if not output.endswith('.h264'):
        output += '.h264'

    if delay:
        sleep(delay_time)

    camera = picamera.PiCamera()
    camera.resolution = (int(camera_resolution[0]), int(camera_resolution[1]))
    camera.framerate = framerate

    camera.annotate_background = picamera.Color('black')
    camera.annotate_text_size = timestamp_font_size

    if args.preview:
        camera.start_preview()

    interval_iter = 0

    while True:

        output_file = output

        if intervals != -1 and interval_iter >= intervals:

            if args.preview:
                camera.stop_preview()

            print("Finished... exiting")
            exit()

        if intervals > 1:
            output_file = output[:-5] + str(interval_iter) + '.h264'

        if args.capture:
            try:
                camera.start_recording(output_file)
            except:
                print("""Error: Could not capture to file, please make sure
                    file path exists (folders must exist, if they do, this
                    script will create the output file on its own)""")
                exit()

        time_iter = 0

        while True:

            if record_time != -1 and time_iter >= record_time * 5:
                if args.capture:
                    camera.stop_recording()

                break

            camera.annotate_text = (camera_label + " | " +
                                    datetime.datetime.now().strftime(
                                        '%m/%d/%Y | %H:%M:%S'))
            if args.capture:
                camera.wait_recording(.2)
            else:
                sleep(.2)

            time_iter += 1

        if intervals > 0:
            print("Finished Interval #" + str(interval_iter))

        interval_iter += 1


# run camera function
start_camera()