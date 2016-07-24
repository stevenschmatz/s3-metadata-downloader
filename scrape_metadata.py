"""
S3 metadata downloader

Author: Steven Schmatz @stevenschmatz
Website: https://steven.party
Created: 23 July 2016
"""

from boto.s3.connection import S3Connection
from optparse import OptionParser
import csv

AWS_ACCESS_KEY_ID = "<your-access-key-here>"
AWS_SECRET_ACCESS_KEY = "<your-secret-access-key-here>"
BUCKET_NAME = "<bucket-name>"


class Parser():
    """Provides utility methods for parsing command line args."""
    def __init__(self):
        self._parser = OptionParser()
        self._parser.add_option("-p",
                                "--prefix",
                                dest="prefix",
                                help="Enter a prefix for the S3 bucket.")

        self._parser.add_option("-s", "--short-filename",
                                dest="short_filename",
                                action="store_true",
                                help="If the --short-filename flag is added, "
                                "the parser returns the last part of the path "
                                "of the image, rather than the full path "
                                " in S3. E.g., instead of returning photos"
                                "/2016-04-22/file.jpg, returns only file.jpg")

    # Returns the S3 bucket prefix for the given command line arguments.
    def get_s3_prefix(self):
        (options, args) = self._parser.parse_args()
        return options.prefix

    # Sets the filenames returned from the scraper to include the full path
    # eg. "photos/2016-04-22/filename.jpeg" rather than "filename.jpeg"
    def get_short_filename_opt(self):
        (options, args) = self._parser.parse_args()
        short_filename_arg = options.short_filename

        if short_filename_arg is not None:
            return True
        else:
            return False


class FileMetadataScraper():
    """Connects to S3 and runs the scraper."""
    def __init__(self, access_key, secret_key, bucket):
        self.s3_conn = S3Connection(access_key, secret_key)
        self.bucket = self.s3_conn.get_bucket(bucket)
        self.short_filename_opt = False

    # Sets the filenames returned from the scraper to include the full path
    # eg. "photos/2016-04-22/filename.jpeg" rather than "filename.jpeg"
    def config_set_short_filename(self):
        self.short_filename_opt = True

    # Gets all metadata matching the given prefix.
    def get_all_metadata(self, prefix=None):
        results = {}

        for key in self.bucket.list(prefix=prefix):
            if self.short_filename_opt:
                filename = key.name.split("/")[-1]
            else:
                filename = key.name

            metadata = self.bucket.get_key(key.name).metadata
            results[filename] = metadata

        return results


class CSVWriter():
    """Writes metadata to a CSV file."""
    def __init__(self, filename, metadata_dict):
        self.file = open(filename, "wb")
        self.writer = csv.writer(self.file)
        self.metadata_dict = metadata_dict
        pass

    # Gets all the metadata keys and writes them to a header in the CSV file.
    def _write_header(self):
        self.metadata_keys = ["filename"]

        # Used for duplicate checking for metadata keys
        metadata_keys_set = set("filename")

        for key in self.metadata_dict:
            for metadata_key in self.metadata_dict[key]:
                if metadata_key not in metadata_keys_set:
                    self.metadata_keys.append(metadata_key)
                    metadata_keys_set.add(metadata_key)

        self.writer.writerow(self.metadata_keys)

    # Writes all rows to the CSV file.
    def write(self):
        self._write_header()
        for filename in self.metadata_dict:
            row = [filename]

            for metadata_key in self.metadata_keys[1:]:
                if metadata_key in self.metadata_dict[filename]:
                    row.append(self.metadata_dict[filename][metadata_key])
                else:
                    row.append("")
            self.writer.writerow(row)

    # Closes the file.
    def close_file(self):
        self.file.close()


# Performs validation that all of the keys are set.
def validate():
    valid = True
    if AWS_ACCESS_KEY_ID == "<your-access-key-here>":
        print ("AWS_ACCESS_KEY_ID not set! Change the value in "
               "scrape_metadata.py.")
        valid = False
    if AWS_SECRET_ACCESS_KEY == "<your-secret-access-key-here>":
        print ("AWS_SECRET_ACCESS_KEY not set! Change the value in "
               "scrape_metadata.py.")
        valid = False
    if BUCKET_NAME == "<bucket-name>":
        print ("BUCKET_NAME not set! Change the value in "
               "scrape_metadata.py.")
        valid = False

    if not valid:
        exit(1)


# Runs the metadata downloader.
def main():
    validate()

    scraper = FileMetadataScraper(AWS_ACCESS_KEY_ID,
                                  AWS_SECRET_ACCESS_KEY,
                                  BUCKET_NAME)
    parser = Parser()
    prefix = parser.get_s3_prefix()

    short_filename_opt = parser.get_short_filename_opt()
    if short_filename_opt:
        scraper.config_set_short_filename()

    metadata = scraper.get_all_metadata(prefix)

    if not metadata:
        print "There are no keys which match the given prefix."
        return

    if prefix is not None and prefix.split("/")[-1] != "":
        output_filename = prefix.split("/")[-1]
    else:
        output_filename = "output"

    csv_filename = "metadata/" + output_filename + ".csv"

    csv_writer = CSVWriter(csv_filename, metadata)
    csv_writer.write()
    csv_writer.close_file()


if __name__ == '__main__':
    main()
