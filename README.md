# S3 Metadata Download Tool

This tool writes S3 object metadata to a CSV file.

In [AWS S3](https://aws.amazon.com/s3/), the user can store key-value pairs for objects in metadata. For some applications, you might have to do processing on these metadata, so this ability would be useful to have.

This tool provides the capabilities to:

* Get the metadata for a given prefix
* Store the S3 filename in either long format (default, e.g. "photos/2016-04-22/file.jpg"), or in short format (e.g. "file.jpg").

## Installation

Installation uses `pip` and `virtualenv`.

```
$ source env/bin/activate
$ pip install -r requirements.txt
```

Then, in scrape_metadata.py, make sure to set the values for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `BUCKET_NAME`.

---

## Usage

### Options

To **view metadata for a given prefix**: provide the `-p` or `--prefix` flag followed by the prefix value.

```
$ python scrape_metadata.py --prefix photos/2016-04-22
```

By default, if this flag is not provided it returns metadata for all keys in the bucket.

To **write the filename in short format**: provide the `-s` or `--short-filename` flag like so:

```
$ python scrape_metadata.py --short-filename
```