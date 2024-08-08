import csv
import io
import os
import time
import zipfile

from django.http import StreamingHttpResponse, HttpResponse


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in
        a buffer."""
        return value


def streaming_csv_view(header, data):
    """
    A view that streams a large CSV file.
    Generate a sequence of rows. The range is based on the maximum
    number of
    rows that can be handled by a single sheet in most spreadsheet
    applications.

    :param header:
    :param data:
    :return:
    """
    file_name = "history_" + str(int(time.time()))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    res_header = [{key: key for key in header}]
    res_data = res_header + data
    response = StreamingHttpResponse(
        (writer.writerow([row.get(key) for key in header]) for row in res_data),
        content_type="text/csv",
    )
    response["Content-Disposition"] = 'attachment; filename="' + file_name + '.csv"'
    return response


def downloadable_zip(file_path):
    zip_io = io.BytesIO()
    with zipfile.ZipFile(
        zip_io, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as backup_zip:
        # u can also make use of list of filename location
        backup_zip.write(file_path)
        # and do some iteration over it

    # post creation of zip file, delete source file from disk.
    if os.path.exists(file_path):
        os.remove(file_path)

    response = HttpResponse(
        zip_io.getvalue(), content_type="application/x-zip-compressed"
    )
    file_name = "history_" + str(int(time.time()))
    response["Content-Disposition"] = "attachment; filename=%s" % (file_name + ".zip")
    response["Content-Length"] = zip_io.tell()
    return response


def streaming_zip_view(header, data):
    """
    A view that streams a large CSV file.
    Generate a sequence of rows. The range is based on the maximum
    number of
    rows that can be handled by a single sheet in most spreadsheet
    applications.

    :param header:
    :param data:
    :return:
    """
    file_name = "file_" + str(int(time.time()))
    res_header = [{key: key for key in header}]
    # res_data = res_header + data
    file_path = "%s.csv" % file_name
    with open(file_path, "w") as fob:
        w = csv.DictWriter(fob, res_header[0].keys())
        w.writeheader()
        for row in data:
            w.writerow(row)
    return downloadable_zip(file_path)
