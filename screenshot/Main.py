import shutil
import time

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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
