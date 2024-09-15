#!/usr/bin/env python
"""
shaney.py by Greg McFarlane some editing by Joe Strout
search for "Mark V.  Shaney" on the WWW for more info!

The original code implements a 2nd-order markov chain, where output is
based on the two previous inputs. This is implemented in this module
using the two functions:

- train -- train the markov chain on some input text.
- generate -- generate text based on the training data.

Additionally, a 3rd-order markov chain is implemented here as well, in
the following functions:

- train3 -- train the markov chain on some input text.
- generate3 -- generate text based on the training data.

Original code listed without a license, here:
http://www.strout.net/info/coding/python/shaney.py

"""

import argparse  # For handling command-line arguments
import random  # To randomly select words during generation
import re  # For regular expressions (used in cleaning and parsing the text)
import sys  # For outputting to the console
import textwrap  # For formatting text output
from string import ascii_lowercase  # Used for non-ending abbreviations like "A."


def write(msg, verbose=False):
    """
    Write a message to standard out if verbose is true.
    This function ensures that the message is wrapped at 80 characters per line.
    """
    if verbose:
        msg = "\n".join(textwrap.wrap(msg, width=80))
        sys.stdout.write("{0}\n".format(msg))  # Print the message to stdout


def read(filename, verbose=False):
    """
    Reads content from the given filename, performs some cleanup, and returns a list of words.
    The cleanup process involves:
    - Removing unicode characters
    - Replacing smart quotes with normal quotes
    - Reducing all whitespace to single spaces
    - Removing unwanted characters
    """
    write("-" * 80, verbose)  # Optional separator if verbose
    write("Reading File.", verbose)  # Inform the user that we're reading the file

    try:
        # Attempt to open and read the file
        content = open(filename, "r").read()
    except Exception:
        # If the file read fails, treat the input as raw content
        content = filename

    # Remove non-ASCII characters (like smart quotes)
    content = content.encode("ascii", "ignore").decode("utf8")

    # Replace all whitespace (spaces, tabs, newlines) with a single space
    content = re.sub("\s+", " ", content)

    # Replace smart quotes with standard ones
    content = content.replace("\u2018", "'").replace("\u2019", "'")
    content = content.replace("\u201c", "").replace("\u201d", "")

    # Remove everything except letters, major punctuation, and spaces
    content = re.sub("[^A-Za-z\.\?\!' ]+", "", content)
    content = content.split()  # Split into words

    def _clean(word):
        """
        A helper function to filter out certain unwanted words, such as:
        - URLs
        - Twitter mentions (@username)
        - Common unwanted words (like "RT", "amp", etc.)
        """
        return (
            not word.startswith("http")  # Filter out URLs
            and not word.startswith("@")  # Filter out Twitter mentions
            and not (word.startswith("&") and len(word) > 1)
            and word != "RT"  # Remove common tweet artifacts
            and word != "..."
            and word != "amp"  # Filter out "&amp;" from HTML
        )

    content = list(filter(_clean, content))  # Apply the filter to remove unwanted words
    write("Read {0} lines.".format(len(content)), verbose)  # Output the number of words
    return content


def analyze_text(data, verbose=True):
    """
    Analyzes the dictionary of trained data and prints the mean word sample size.
    This function gives insight into how well the training data is structured.
    """
    size = 0
    for word_list in data.values():
        size += len(word_list)
    avg_sample_size = float(size) / len(
        data.values()
    )  # Calculate the average sample size

    write("-" * 80, verbose)
    write("Average Sample Size: {0}".format(avg_sample_size), verbose)
    if avg_sample_size < 2:
        write(
            "--> This is a small sample size, likely poor at generating text.", verbose
        )
    elif avg_sample_size > 2:
        write("--> This looks like a decent sample size.", verbose)
    else:
        write("--> This looks like a good sample size.", verbose)
    write("-" * 80, verbose)


def _is_ending(word):
    """
    Determines if a word is likely the end of a sentence.
    It checks if the word ends with certain punctuation or common non-ending abbreviations.
    """
    # List of abbreviations that are often mistaken for sentence endings
    non_endings = [
        "mr.",
        "mrs.",
        "ms.",
        "dr.",
        "phd.",
        "d.c.",
        "u.s.",
        "a.m.",
        "p.m.",
        ".",
        ".net",
        "no.",
        "i.e.",
        "e.g.",
        "st.",
        "lt.",
        "n.c.",
        "adm.",
        "u.n.",
        "jr.",
        "rep.",
        "u.a.e.",
        "u.k.",
        "s.m.a.r.t.",
        "sen.",
        "inc.",
        "u.i.",
        "u.x.",
        "sr.",
        "s.m.",
        "ph.",
    ]

    # Add single-letter initials (A., B., C., etc.) as non-endings
    non_endings.extend(["{}.".format(letter) for letter in ascii_lowercase])

    # Check if the word is a number with a decimal point (e.g., 4.5)
    is_number = bool(re.match(r"\d+\.\d+", word))

    # If it's a number or a known non-ending, return False
    if is_number or word.lower().strip() in non_endings:
        return False

    # Otherwise, check if the word ends with sentence-ending punctuation
    endings = [".", "?", "!", ";"]
    return any([word.endswith(punct) for punct in endings])


def train(filename, verbose=False):
    """
    Trains a 2nd-order Markov chain on the provided input text.
    Returns a dictionary with 'content' as key-value pairs of word pairs and their next words,
    and 'endings' as a set of word pairs that mark the end of a sentence.
    """
    write("Training...", verbose)
    endings = set()  # Track word pairs that signify the end of a sentence
    data = {}  # Initialize the data dictionary

    prev1 = ""  # Previous word 1
    prev2 = ""  # Previous word 2

    # Process each word in the input text
    for word in read(filename, verbose):
        if prev1 != "" and prev2 != "":
            key = (prev2, prev1)  # Create a tuple of the previous two words
            if key in data:
                data[key].append(word)  # Append the next word to the list
            else:
                data[key] = [word]  # Start a new list for this pair
                if _is_ending(key[-1]):
                    endings.add(key)  # Add to endings if it's a sentence end

        prev2 = prev1  # Shift words forward
        prev1 = word

    assert (
        endings != set()
    ), "Sorry, there are no sentences in the text."  # Ensure text has endings
    if verbose:
        analyze_text(data)  # Optionally analyze the data

    return {"content": data, "endings": list(endings)}  # Return the training data


def generate(data, count=10, verbose=False):
    """
    Generates text based on the trained 2nd-order Markov chain model.
    Returns a list of generated sentences.
    """
    write("Generating output:", verbose)

    output = ""  # Initialize the output text
    generated_strings = []  # Store the generated sentences
    key = ()  # Initialize the current word pair

    while True:
        if key in data["content"]:
            word = random.choice(data["content"][key])  # Randomly select the next word
            output = "{0}{1} ".format(output, word)  # Append the word to the output

            key = (key[1], word)  # Move to the next word pair
            if key in data["endings"]:
                generated_strings.append(output)  # Store the sentence
                output = ""  # Reset output for the next sentence
                key = random.choice(
                    data["endings"]
                )  # Start from a random sentence ending
                count = count - 1  # Decrement the count of sentences to generate
                if count <= 0:
                    break
        else:
            key = random.choice(
                data["endings"]
            )  # Reset key if no continuation is found

    return generated_strings  # Return the list of generated sentences


def train3(filename, verbose=False):
    """
    Trains a 3rd-order Markov chain, using three-word sequences instead of two.
    Works similarly to the 2nd-order version but looks at triples of words.
    """
    write("Training...", verbose)
    endings = []  # Track word triples that signify the end of a sentence
    data = {}

    prev1 = ""  # Previous word 1
    prev2 = ""  # Previous word 2
    prev3 = ""  # Previous word 3

    for word in read(filename, verbose):
        if prev1 != "" and prev2 != "" and prev3 != "":
            key = (prev3, prev2, prev1)  # Create a tuple of the previous three words

            if key in data:
                data[key].append(word)  # Append the next word to the list
            else:
                data[key] = [word]  # Start a new list for this triple
                if _is_ending(key[-1]):
                    endings.append(key)  # Add to endings if it's a sentence end

        prev3 = prev2  # Shift words forward
        prev2 = prev1
        prev1 = word

    assert (
        endings != []
    ), "Sorry, there are no sentences in the text."  # Ensure text has endings
    if verbose:
        analyze_text(data)  # Optionally analyze the data

    return {"content": data, "endings": endings}  # Return the training data


def generate3(data, count=10, verbose=False):
    """
    Generates text based on the trained 3rd-order Markov chain model.
    Returns a list of generated sentences.
    """
    write("Generating output:", verbose)

    output = ""  # Initialize the output text
    generated_strings = []  # Store the generated sentences
    key = None  # Initialize the current word triple

    while True:
        if key and key in data["content"]:
            word = random.choice(data["content"][key])  # Randomly select the next word
            output = "{0}{1} ".format(output, word)  # Append the word to the output

            key = (key[1], key[2], word)  # Move to the next word triple
            if key in data["endings"]:
                generated_strings.append(output)  # Store the sentence
                output = ""  # Reset output for the next sentence
                key = random.choice(
                    data["endings"]
                )  # Start from a random sentence ending
                count = count - 1  # Decrement the count of sentences to generate
                if count <= 0:
                    break
        else:
            key = random.choice(
                data["endings"]
            )  # Reset key if no continuation is found

    return generated_strings  # Return the list of generated sentences


def run(filename=None, count=10, verbose=False, order=2, interactive=False):
    """
    The main function that orchestrates the process:
    - Reads the input file
    - Trains the appropriate Markov chain model (2nd or 3rd order)
    - Generates and prints sentences
    """
    write("Running in verbose mode.", verbose)
    if filename is None:
        filename = input("Enter name of a textfile to read: ")

    # Train based on the specified order (2nd or 3rd order Markov chain)
    if order == 2:
        data = train(filename, verbose)
        generate_func = generate
    elif order == 3:
        data = train3(filename, verbose)
        generate_func = generate3

    # Main loop: generate sentences until the user decides to quit
    selection = ""
    while selection.lower() != "q":
        write("\n\n", verbose)
        results = generate_func(data, count, verbose)
        for r in results:
            write("* {0}".format(r.strip()), verbose)
            write("\n", verbose)
        write("-" * 80, verbose)
        if interactive:
            selection = input("Press Enter key to continue, Q to quit: ")
        else:
            selection = "q"
    return results


if __name__ == "__main__":
    # Argument parsing for command-line usage
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Path to the training text.", type=str)
    parser.add_argument(
        "-i", "--interactive", help="Run in interactive mode", action="store_true"
    )
    parser.add_argument(
        "-o",
        "--order",
        help="Order: how many words to consider at a time? 2 or 3",
        type=int,
        default=2,
    )
    parser.add_argument(
        "-v", "--verbose", help="Run in verbose mode", action="store_true"
    )
    args = parser.parse_args()

    # Run the program with the specified arguments
    run(
        args.filename,
        verbose=args.verbose,
        order=args.order,
        interactive=args.interactive,
    )
