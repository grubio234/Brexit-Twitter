""""
Script used to transform tweets supplied to us by the [Computational Social
Science group at ETH Zurich](https://coss.ethz.ch/) into the format used in this
project.
As the original files were not kept, there is no reason to run this script.
It is merely kept for the sake of completeness.
"""
from __future__ import print_function
import pandas as pd
from datetime import datetime
from merge_to_single_csv import goal_header, sep_char

coss_days = [
    "feb_18", "feb_19", "feb_20", "feb_21", "feb_22",
    "apr_14", "apr_15", "apr_16", "apr_17",
    "may_01", "may_02", "may_03", "may_04",
]

coss_field_names = goal_header.replace("user_time_zone", "utc_offset")
goal_field_order = coss_field_names.split(sep_char)

def dailyCOSSToCSV(source_prefix, destination_prefix=None):
    if destination_prefix is None:
        destination_prefix = source_prefix
    def withoutSpuriousNewlines(lines):
        newline_less = []
        for i, line in enumerate(lines):
            line = line.replace("\n", " ")
            if len(line) < 3 or line[:3] != "id:":
                newline_less[-1] = newline_less[-1]  + line
            else:
                newline_less.append(line)
        return newline_less

    def fieldValue(string, field_name):
        def newFieldStart(field_start):
            new_field_indizes = []
            for field in goal_field_order:
                if field == field_name:
                    continue
                new_field_indicator = "{} {}:".format(sep_char, field)
                new_field_start = string.find(new_field_indicator, field_start)
                if new_field_start != -1:
                    new_field_indizes.append(new_field_start)
            if len(new_field_indizes) == 0:
                new_field_start = -1
            else:
                new_field_start = min(new_field_indizes)
            return new_field_start

        def fieldStart():
            if string[:len(field_name)+1] == field_name+":":
                return 0
            field_start = string.find("{} {}:".format(sep_char, field_name))
            if field_start == -1:
                raise Exception("The required field {} is missing."
                    "".format(field_name))
            return field_start

        field_start = fieldStart()
        name_decoration = len(sep_char+" ") + len(":")
        field_value_start = field_start + len(field_name) + name_decoration
        field_end = newFieldStart(field_start)
        field_value = string[field_value_start:field_end]
        return field_value

    def datetimeAndDate(dt_string):
        dt = datetime.strptime(dt_string, "%a %b %d %H:%M:%S %z %Y")
        new_format_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        date = dt.strftime("%Y-%m-%d")
        return new_format_dt, date

    def fieldValuesAndDate(string):
        field_values = []
        for field_name in goal_field_order:
            field_value = fieldValue(string, field_name)
            if field_name == "created_at":
                field_value, date_string = datetimeAndDate(field_value)
            if field_name == "text":
                field_value = field_value.replace(sep_char, " ")
            field_values.append(field_value)
        return field_values, date_string

    def csvLinesAndDate(bare_lines):
        csv_lines = []
        date_set = set()
        for line in bare_lines:
            csv_values, date_string = fieldValuesAndDate(line)
            csv_lines.append(sep_char.join(csv_values))
            date_set.add(date_string)
        if len(date_set) != 1:
            print(date_set)
            raise Exception("All entries should origin from the same day.")
        date = date_set.pop()
        return csv_lines, date

    for file_stump in coss_days:
        file_name = source_prefix + file_stump
        with open(file_name) as file:
            coss_lines = file.readlines()
        bare_lines = withoutSpuriousNewlines(coss_lines)
        csv_lines, date = csvLinesAndDate(bare_lines)
        save_name = destination_prefix + date + ".csv"
        print("File saved at: {}.".format(save_name))
        with open(save_name, "w") as out_file:
            csv_lines = [goal_header] + csv_lines
            out_file.write("\n".join(csv_lines))

if __name__ == "__main__":
    coss_data_folder = "brexit_tweets_COSS_2016/"
    destination = "./"
    dailyCOSSToCSV(coss_data_folder, destination)