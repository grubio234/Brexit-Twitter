""""
As the original files were not kept, there is no reason to run this script.
It is merely kept for the sake of completeness.

As an intermediate step, the tweets collected by us from a Twitter API were
stored in some big .csv files.
This script performs some cleanup for these big files.
Additionally it can be used to merge all those files into one big file while
removing duplicate entries.
In some of our collection runs we mined for a larger set of parameters.
To standardize the output, only the shared set of parameters is kept
"""
from __future__ import print_function

sep_char = ","

long_header = "id,created_at,geo,place,retweet_count,text,user_screen_name,user_time_zone,user_followers_count,user_friends_count,user_favourites_count,user_statuses_count,lang,misc"
shorter_header = "id,created_at,geo,place,text,user_time_zone,lang"
coss_header = "id,created_at,lang,user_time_zone,text"

goal_header = coss_header
source_headers = [
    long_header,
    shorter_header,
    coss_header,
]


def createStandardizationFunctions():
    def positionsInSource(a_source_header):
        destination_keys = goal_header.split(sep_char)
        source_keys = a_source_header.split(sep_char)
        def getPositionList():
            get_from_position = []
            for to_field in destination_keys:
                for i, from_field in enumerate(source_keys):
                    if to_field == from_field:
                        get_from_position.append(i)
                        break
            return get_from_position

        def checkConversionValidity(get_from_position):
            if len(get_from_position) != len(destination_keys):
                print(destination_keys)
                print(source_keys)
                raise Exception("One of the destination fields was not found "
                    "in the source fields.")

        get_from_position = getPositionList()
        checkConversionValidity(get_from_position)
        return get_from_position

    def getStandardizationFunctionFromPositions(position_in_source):
        def standardizationFunction(line):
            line_parts = line.split(sep_char)
            standard_parts = [line_parts[pos] for pos in position_in_source]
            standardized_line = sep_char.join(standard_parts)
            return standardized_line
        return standardizationFunction

    def getStandardizationFunction(a_source_header):
        position_in_source = positionsInSource(a_source_header)
        func = getStandardizationFunctionFromPositions(position_in_source)
        return func

    def checkDictValidity(func_dict, source_list):
        if len(func_dict) != len(source_list):
            raise Exception("The 1:1 mapping of header to standardization "
                "function was not successful. Note that the algorithm requires "
                "that all headers have different numbers of fields.")

    def getFunctionDict(source_headers):
        standardization_functions = {}
        for source_header in source_headers:
            n_fields = len(source_header.split(sep_char))
            standardization_func = getStandardizationFunction(source_header)
            standardization_functions[n_fields] = standardization_func
        return standardization_functions

    standardization_functions = getFunctionDict(source_headers)
    checkDictValidity(standardization_functions, source_headers)
    return standardization_functions


def withHeader(list_of_lines):
    list_with_header = [goal_header]
    list_with_header.extend(list_of_lines)
    return list_with_header

sep_char_quot = '"' + sep_char + '"'
def cleanLines(file_name):
    def oneLinePerTweet(lines):
        startsWithTweetId = lambda line: (
            (len(line) > 21) and (line[0] == '"')
            and (line[1:19].isdigit()) and (line[19:22] == sep_char_quot)
        )
        def withoutNewlines(line):
            def isBetweenFields(line, newline_pos):
                is_between = False
                if newline_pos == 0 or line[newline_pos - 1] in [sep_char, '"']:
                    char_after = newline_pos + 1
                    if len(line) <= char_after or line[char_after] in '" ':
                        is_between = True
                return is_between

            newline_pos = line.find("\n", 0)
            while newline_pos != -1:
                if isBetweenFields(line, newline_pos):
                    line = line[:newline_pos] + line[newline_pos+1:]
                else:
                    line = line[:newline_pos] + " " + line[newline_pos+1:]
                newline_pos = line.find("\n", newline_pos)
            return line

        true_lines = [withoutNewlines(lines[0])]
        for i, line in enumerate(lines[1:]):
            line = withoutNewlines(line)
            if startsWithTweetId(line):
                true_lines.append(line)
            else:
                true_lines[-1] += line
        return true_lines

    def removeTextCommas(lines):
        validAroundDelimeter = [sep_char, '\n', '"']
        isTrueDelimeter = lambda chars: (
            chars[0] in validAroundDelimeter
            and ((len(chars) < 3) or (chars[2] in validAroundDelimeter))
        )
        i = 0
        # The first line might be the column names with different convention.
        skip_header_l = 1
        for i, line in enumerate(lines[skip_header_l:], skip_header_l):
            comma_pos = line.find(sep_char)
            if comma_pos == 0:
                if line[comma_pos+1] not in validAroundDelimeter:
                    line = " " + line[1:]
            while comma_pos != -1:
                if not isTrueDelimeter(line[comma_pos-1:]):
                    line = line[:comma_pos] + " " + line[comma_pos+1:]
                    lines[i] = line
                    comma_pos -= 1 # Else we would miss second consecutive comma in text.
                comma_pos = line.find(sep_char, comma_pos+1)

    def removeExcessCommas(lines):
        """Remove the remaining excess commas in a line.

        All new lines and most commas from inside the text strings should be removed by now.
        The remaining excess of commas will be removed by a brute-force assumption:
        Since we know how many fields should be before and after the text field,
        we know how many commas should be before and after.
        Remaining commas will be assumed to be part of the text and removed.
        """
        n_required = lines[0].count(sep_char)
        def firstCommaToRemove(n_separators=n_required):
            """Depends on the (number of) fields that were mined."""
            if n_separators == 13:
                return 5
            elif n_separators == 6:
                return 4
            else:
                raise Exception("The case of {} seperators is not implemented "
                    "yet.".format(n_separators))

        def lineWithoutExcessCommas(line, n_commas_in_line):
            first_removed = firstCommaToRemove()
            n_excess_commas = n_commas_in_line - n_required
            last_removed = first_removed + n_excess_commas
            i_comma = 0
            comma_pos = 0
            while i_comma < last_removed:
                comma_pos = line.find(sep_char, comma_pos)
                if i_comma < first_removed:
                    comma_pos += 1
                else:
                    line = line[:comma_pos] + " " + line[comma_pos+1:]
                i_comma += 1
            return line

        for i, line in enumerate(lines):
            if line.count(sep_char) != n_required:
                n_in_line = line.count(sep_char)
                if n_in_line < n_required:
                    raise Exception("This .csv file line does not have "
                        "the right number of seperators: {} != {}."
                        "".format(n_in_line, n_required), line)
                #print("This line needed the brute-force approach:\n", line)
                lines[i] = lineWithoutExcessCommas(line, n_in_line)
                #print("Result: ", lines[i])
                i -= 1 # To check wether the procedure worked.

    def removeSomeEscapeCharacters(lines):
        """Issues were experienced with some escape characters.

        (The following lines include (raw) escape characters.
        Depending on how you read this string, the formatting might render this docstring useless).
        While e.g. \', \", \\ should be fine, those listed below might be problematic.
        As they are not useful in a text analysis anyways, there is no harm in removing them.
        Note that \n is not part of these characters, as it is only sometimes removed and handled separately.
        """
        remove_escape_chars = ['\r', '\t', '\b', '\f', '\v', '\0']
        for i, line in enumerate(lines):
            for to_remove in remove_escape_chars:
                if to_remove in line:
                    print(line)
                    line.replace(to_remove, " ")
                    lines[i] = line
                    print(lines[i])

    with open(file_name) as f:
        lines = f.readlines()
        true_lines = oneLinePerTweet(lines)
        removeTextCommas(true_lines)
        removeExcessCommas(true_lines)
        #removeSomeEscapeCharacters(true_lines)
    return true_lines

def mergeCSV(file_names, destination="all.csv"):
    def multiFileCleanLines(file_names):
        clean_lines = []
        for fn in file_names:
            clean_lines.extend(cleanLines(fn))
        return clean_lines

    def uniqueTweetsDict(lines_with_duplicates):
        isHeader = lambda line: line[:2] == "id"
        unique_tweets = {}
        for line in lines_with_duplicates:
            tweet_id = line[1:19]
            if tweet_id.isdigit():
                if tweet_id not in unique_tweets:
                    unique_tweets[tweet_id] = line
            else:
                if not isHeader(line):
                    raise Exception("The following line has a faulty format: "
                        "\n {}".format(line))
        return unique_tweets

    def orderedLinesList(dict_of_lines):
        lines = []
        for key in sorted(list(dict_of_lines)):
            lines.append(dict_of_lines[key])
        return lines

    def standardizedLines(lines_without_standard):
        transformers = createStandardizationFunctions()
        standardized_lines = []
        for line in lines_without_standard:
            n_fields = len(line.split(sep_char))
            line_transformer = transformers[n_fields]
            standardized_lines.append(line_transformer(line))
        return standardized_lines

    clean_lines = multiFileCleanLines(file_names)
    dict_of_lines = uniqueTweetsDict(clean_lines)
    ordered_lines = orderedLinesList(dict_of_lines)
    sorted_keys = sorted(list(dict_of_lines.keys()))
    ordered_lines = withHeader(ordered_lines)
    standard_lines = standardizedLines(ordered_lines)
    with open(destination, "w") as out_file:
        out_file.write("\n".join(standard_lines))

if __name__ == "__main__":
    csv_2017 = [
        "data/brexit_all_2.csv",
        "data/brexit_backup0805.csv",
        "data/brexit_data.csv",
    ]
    mergeCSV(csv_2017)