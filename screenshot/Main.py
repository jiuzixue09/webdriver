import os
import re
import shutil
import time
from threading import Thread

from flask import Flask, request
from flask import send_file

from screenshot import BigBigWork, LoggingUtil

app = Flask(__name__, static_url_path='')

logging = LoggingUtil.get_logging()


@app.route('/screenshot/prod')
def screenshot_prod():
    try:
        rs1 = BigBigWork.normal_user_test('prod')
        rs2 = BigBigWork.vip_user_test('prod')
        file_name = zip_compress('prod', 'prod')
        rs = {'normal_user': rs1, 'vip_user': rs2, 'file_name': file_name}
        shutil.rmtree('prod')
        return rs
    except Exception as e:
        logging.error('error', e)
        return {'status': 'error'}


@app.route('/screenshot/test')
def screenshot_test():
    try:
        rs1 = BigBigWork.normal_user_test('test')
        rs2 = BigBigWork.vip_user_test('test')
        file_name = zip_compress('test', 'test')
        rs = {'normal_user': rs1, 'vip_user': rs2, 'file_name': file_name}
        shutil.rmtree('test')
        return rs
    except Exception as e:
        logging.error('error', e)
        return {'status': 'error'}


def date():
    return str(time.strftime('%Y%m%d%H%M'))


def zip_compress(dir_name, output_filename):
    output_filename += date()
    zip_file = shutil.make_archive(output_filename, 'zip', dir_name)
    return zip_file.split('/')[-1]


@app.route('/download/prod')
def download_prod():
    name = request.args.get("name")
    return send_file(name)


@app.route('/download/test')
def download_test():
    name = request.args.get("name")
    return send_file(name)


class DeleteFile(Thread):
    dirs = os.listdir('.')
    for f in dirs:
        if (f.startswith('test') or f.startswith('prod')) and f.endswith('.zip'):
            d = re.findall('[0-9]+', f)
            if d and (int(date()) - int(d[0])) > 10:
                os.remove(f)


if __name__ == "__main__":
    DeleteFile().start()
    app.run(host='0.0.0.0')
