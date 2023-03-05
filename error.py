from flask import Flask, jsonify
import datetime, os, sys, traceback

app = Flask(__name__)

def err():
    # 方法一：
    # log_path = os.getcwd() + '/logs/err.log'
    # with open(log_path, 'a') as f:
    #     traceback.print_exc(file = f)

    # 方法二：
    exc_type, exc_value, exc_traceback = sys.exc_info()

    for filename, linenum, funcname, source in traceback.extract_tb(exc_traceback):
        err = 'File %s, line %s, in %s, %s' % (filename, str(linenum), funcname, source)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_path = os.getcwd() + '/logs/err.log'
        with open(log_path, 'a') as f:
            err_info = 'exc_type: %s\nexc_value: %s\nerr_info: %s\ntime: %s\n' % (str(exc_type), str(exc_value), err, time)
            f.write(err_info)

    return jsonify({'code': 500, 'msg': 'error'})

@app.get('/route1')
def fun1():
    try:
        a = '1'
        b = 2
        print(a + b)

        return jsonify({'code': 200})
    except:
        return err()

@app.get('/route2')
def fun2():
    try:
        a = 1
        b = 0
        print(a / b)

        return jsonify({'code': 200})
    except:
        return err()

if __name__ == '__main__':
    app.run(debug=True)