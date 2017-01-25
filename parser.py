#!/usr/bin/env python

import re
import sys
import json
import time
import argparse
import logging as log

def to_json(lines):
    out = []
    pattern = "^(.+):\ ([0-9\.]+) sec$"
    log.info("Parsing...")
    for line in lines:
        match = re.search(pattern, line)
        if match and len(match.groups()) == 2:
            log.debug("Extracted task name:{} and time:{} from line: {}".format(match.group(1),
                                                                                match.group(2),
                                                                                line.rstrip("\n")))
            # We are not that interested in the summary line that matches regex
            if match.group(1) == "Total time":
                continue
            out.append({"task_name": match.group(1), "duration": match.group(2)})
        elif match and len(match.groups()) != 2:
            log.warn("Unexpected match for line: {}; matched groups: {}".format(line,
                                                                                match.groups()))
    return json.dumps(out, sort_keys=True, indent=2)

def format_for_elk(input_json, index):
    out = []
    now = int(round(time.time() * 1000))
    for entry in json.loads(input_json):
        out.append(json.dumps({"index":{"_index":index,"_type":entry["task_name"].replace(" ", "").replace(".", "-").lower()}}))
        # Convert seconds to miliseconds since ELK expects miliseconds
        entry["duration"] = int(float(entry["duration"])*1000)
        entry["timestamp"] = now
        out.append(json.dumps(entry))
    return "\n".join(out)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="print debug info", dest="debug",
                        action="store_true")
    parser.add_argument("-i", "--input-file", help="file to parse", dest="input",
                        required=True)
    parser.add_argument("-o", "--output-file", help="file to store output, out.json if not specified", dest="output",
                        default="out.json")

    subparsers = parser.add_subparsers(help="You can generate either plain json or one preformated to be loaded to ELK")
    parser_json = subparsers.add_parser("json", help="Format output as plain json")
    parser_elk = subparsers.add_parser("elk", help="Format output for uploading to ELK")
    parser_elk.add_argument("-n", "--index", help="Index name, antprofiler if not specified", dest="index", default="antprofiler")

    return parser.parse_args()

def main(argv):
    args = parse_args(argv)

    log_format = "%(levelname)s: [%(filename)s:%(lineno)s - %(funcName)s() ] - %(message)s"
    if args.debug == True:
        log.basicConfig(level=log.DEBUG, format=log_format)
    else:
        log.basicConfig(level=log.INFO, format=log_format)

    with open(args.output, 'w') as outfile, open(args.input, 'r') as infile:
        result = to_json(infile)
        # if elk was specified then we will index as part of namespace object
        # which make them suituable for checking if elk was mentioned since there is not flag for elk itself 
        if "index" in args:
            log.info("Formating for ELK...")
            result = format_for_elk(result, args.index)
        log.info("Writing results to {}".format(args.output))
        outfile.write(result)
    log.info("Done!")

if __name__ == "__main__":
    main(sys.argv)
