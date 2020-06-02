import shutil
import time

from flask import Flask
from flask import send_file

from screenshot import BigBigWork, LoggingUtil

app = Flask(__name__, static_url_path='')

logging = LoggingUtil.get_logging()
file_name = ''


@app.route('/screenshot/prod')
def screenshot_prod():
    try:
        rs1 = BigBigWork.normal_user_test('prod')
        rs2 = BigBigWork.vip_user_test('prod')
        rs = {'normal_user': rs1, 'vip_user': rs2}
        zip_compress('prod', 'prod')
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
        rs = {'normal_user': rs1, 'vip_user': rs2}
        zip_compress('test', 'test')
        shutil.rmtree('test')
        return rs
    except Exception as e:
        logging.error('error', e)
        return {'status': 'error'}


def date():
    time.strftime('%Y-%m-%d')


def zip_compress(dir_name, output_filename):
    global file_name
    shutil.rmtree(file_name + '.zip', True)
    output_filename += date()
    file_name = output_filename
    zip_file = shutil.make_archive(output_filename, 'zip', dir_name)
    print(zip_file)


@app.route('/download/prod')
def download_prod():
    return send_file(file_name + '.zip')


@app.route('/download/test')
def download_test():
    return send_file(file_name + 'test.zip')


if __name__ == "__main__":
    # zip_compress('prod', 'prod')
    app.run(host='0.0.0.0')
