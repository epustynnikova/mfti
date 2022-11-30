import logging
import re
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from itertools import groupby
from typing import List

import plotly.express as px

logging.basicConfig(level=logging.DEBUG)


class Status(Enum):
    START = 0
    END = 1


@dataclass(eq=True)
class Data:
    stage: str
    status: Status
    date: datetime


def parse_args(input_args):
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        dest="input_file_path",
        default="data/17357.ngp.cli-output.txt",
        help="input file path",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_chart_path",
        default="data/ganta_chart.png",
        help="output chart path",
    )
    parser.add_argument(
        "-s",
        "--stages",
        dest="stages_file",
        default="data/stages.tsv",
        help="stages list file",
    )
    parser.add_argument(
        "-b",
        "--begin",
        dest="begin_codewords",
        default="data/begin.tsv",
        help="begin codewords list file",
    )
    parser.add_argument(
        "-f",
        "--finish",
        dest="finish_codewords",
        default="data/finish.tsv",
        help="finish codewords list file",
    )
    return parser.parse_args(input_args)


def read_file(path: str) -> List[str]:
    values = []
    with open(path, "r") as f:
        values.extend([line_in.strip() for line_in in f])
    logging.info(f"Read file {path}")
    return values


def read_tasks(
    path: str,
    start_pattern: str = r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}",
    datetime_pattern: str = "%d-%m-%Y %H:%M:%S",
) -> List[Data]:
    datas = []
    with open(path, "r") as file_in:
        pattern = re.compile(start_pattern)
        for line in file_in:
            stage = next(filter(lambda item: item in line, stages), None)
            if pattern.search(line) and stage:
                date = datetime.strptime(pattern.search(line).group(), datetime_pattern)
                start = next(filter(lambda item: item in line, begin_codewords), False)
                end = next(filter(lambda item: item in line, finish_codewords), False)
                if start:
                    datas.append(Data(stage, Status.START, date))
                elif end:
                    datas.append(Data(stage, Status.END, date))
    logging.info(f"Collect information {len(datas)} lines from file {path}")
    return datas


def assembl_tasks(datas: List[Data]) -> List[dict]:
    df_tasks = []
    for task, task_datas in groupby(datas, lambda x: x.stage):
        group_by_status = {
            x: list(y) for x, y in groupby(task_datas, lambda x: x.status)
        }
        finish_data = next(iter(group_by_status[Status.END]), None)
        start_data = next(iter(group_by_status[Status.START]), None)
        if finish_data and start_data:
            logging.info(f"Assembled task {task}")
            df_tasks.append(
                dict(Task=task, Begin=start_data.date, Finish=finish_data.date)
            )
        else:
            logging.error(
                f"Task {task} cannot be assembled as whole task! Start date: {start_data} Finish date: {finish_data}"
            )
    return df_tasks


def create_chart(df: List, path: str):
    fig = px.timeline(df, x_start="Begin", x_end="Finish", y="Task")
    fig.update_yaxes(autorange="reversed")
    fig.write_image(path)
    logging.info(f"Chart created in {path}")


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    stages = read_file(args.stages_file)
    begin_codewords = read_file(args.begin_codewords)
    finish_codewords = read_file(args.finish_codewords)
    data = read_tasks(args.input_file_path)
    create_chart(assembl_tasks(data), args.output_chart_path)
