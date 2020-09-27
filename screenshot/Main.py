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

file_path = 'files'
if not os.path.exists(file_path):
    os.mkdir(file_path)

test_running, prod_running = False, False


@app.route('/screenshot/prod')
def screenshot_prod():
    global prod_running
    if prod_running:
        return {'status': 423, 'message': 'please waiting for another job finished'}
    try:
        rs1 = BigBigWork.normal_user_test('prod')
        rs2 = BigBigWork.vip_user_test('prod')
        file_name = zip_compress('prod', 'prod')
        rs = {'normal_user': rs1, 'vip_user': rs2, 'file_name': file_name, 'status': 200}
        shutil.rmtree('prod')
        return rs
    except:
        logging.exception('error')
        return {'status': 500}
    finally:
        prod_running = False


@app.route('/screenshot/test')
def screenshot_test():
    global test_running
    if test_running:
        return {'status': 423, 'message': 'please waiting for another job finished'}
    try:
        test_running = True
        rs1 = BigBigWork.normal_user_test('test')
        rs2 = BigBigWork.vip_user_test('test')
        file_name = zip_compress('test', 'test')
        rs = {'normal_user': rs1, 'vip_user': rs2, 'file_name': file_name, 'status': 200}
        shutil.rmtree('test')
        return rs
    except:
        logging.exception('error')
        return {'status': 500}
    finally:
        test_running = False


def date():
    return str(time.strftime('%Y%m%d%H%M'))


def zip_compress(dir_name, output_filename):
    output_filename += date()
    output_filename = file_path + '/' + output_filename
    zip_file = shutil.make_archive(output_filename, 'zip', dir_name)
    return zip_file.split('/')[-1]


@app.route('/download/prod')
def download_prod():
    name = request.args.get("name")
    logging.info(name)
    if not name:
        return {'status': 'empty name'}
    name = file_path + '/' + name
    return send_file(name)


@app.route('/download/test')
def download_test():
    name = request.args.get("name")
    logging.info(name)
    if not name:
        return {'status': 'empty name'}
    name = file_path + '/' + name
    return send_file(name)


class DeleteFile(Thread):

    def run(self) -> None:
        super().run()
        while True:
            try:
                dirs = os.listdir('.')
                for f in dirs:
                    if (f.startswith('test') or f.startswith('prod')) and f.endswith('.zip'):
                        d = re.findall('[0-9]+', f)
                        if d and (int(date()) - int(d[0])) > 10:
                            os.remove(f)
                time.sleep(10 * 60)
            except :
                logging.exception('delete file error')


if __name__ == "__main__":
    # DeleteFile().start()
    app.run(host='0.0.0.0')
