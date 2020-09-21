from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request
import importlib
import os
import io
from contextlib import redirect_stdout
from inspect import getfullargspec
# import inspect

__author__ = 'MyasnikovIA'
global APPFLASK
APPFLASK = Flask(__name__)
APPFLASK.config['SECRET_KEY'] = 'secret!'
APPFLASK.config['DEBUG'] = True
APPFLASK.config['HOST'] = '0.0.0.0'

socketio = SocketIO(APPFLASK, async_mode=None, logger=True, engineio_logger=True)

# =========================================================================================================
# =====================  Обработка Socket IO  =============================================================
# HTML:
#    <script src="static/js/jquery.min.js"></script>
#    <script type="text/javascript" src="static/js/socket.io.min.js"></script>
#    <script src="static/js/application.js"></script>
# JS:
#   sendServer('control.test.MyTestFun', function(msg) { $('#mycontent').text(msg); }, 111, 2222222)
# =========================================================================================================

@socketio.on('message', namespace='/socket_controller')
def message_from_socketio(message):
    """обработка запуска Python функции из JS кода"""
    if 'FunName' in message:
        defName = message['FunName']
        if '.' in defName:
            packName = defName[:defName.rfind('.')]
            defName = defName[defName.rfind('.') + 1:]
            meth = importlib.import_module(packName)
            with io.StringIO() as buf, redirect_stdout(buf):
                if hasattr(meth, defName):
                    function_name = getattr(meth, defName)
                    try:
                      # infoMeth = inspect.getfullargspec(function_name)
                      infoMeth = getfullargspec(function_name)
                      funArgsNameList = infoMeth.args
                      funArgsDefaultsList = infoMeth.defaults
                      del infoMeth
                      rgsVar = {}
                      indDef = -1
                      for nam in funArgsNameList:
                          indDef+=1
                          if message['args'][indDef]:
                              rgsVar[nam] = message['args'][indDef]
                          elif funArgsDefaultsList[indDef]:
                              rgsVar[nam] = funArgsDefaultsList[indDef]
                          else:
                              rgsVar[nam] = None
                      del indDef, funArgsNameList, funArgsDefaultsList
                      res = function_name(**rgsVar)
                      del meth, function_name, rgsVar
                    except Exception:
                        socketio.emit('javascript', {'eval': f""" console.log("error run","{defName}","{message}") """},namespace='/socket_controller')
                        return
                    if res == None:
                        socketio.emit(message['FunName'], buf.getvalue(), namespace='/socket_controller')
                    else:
                        socketio.emit(message['FunName'], res, namespace='/socket_controller')
                else:
                    socketio.emit(message['FunName'], {'eval': f""" console.log("No def","{message}") """},namespace='/socket_controller')
                    return
            socketio.emit(message['FunName'], {'eval': f""" console.log("{message}") """}, namespace='/socket_controller')
        else:
            socketio.emit('javascript', {'eval': f""" console.log("error","{message}") """}, namespace='/socket_controller')

@socketio.on('connect', namespace='/socket_controller')
def socket_connect():
    """обработка нового подключения"""
    print('Client connected', request.sid)

@socketio.on('disconnect', namespace='/socket_controller')
def socket_disconnect():
    """обработка отключения"""
    print('Client disconnected', request.sid)
# =========================================================================================================
# =========================================================================================================


@APPFLASK.errorhandler(404)
def not_found(error):
    the_path = request.query_string
    expansion = the_path[the_path.rfind(".") + 1:].lower()
    if expansion == 'frm':  # обработка  страниц с расширением '*.frm' не дописано
        pass
    return render_template('404.html', **locals()), 404


@APPFLASK.route('/')
def index():
    return render_template('index.html')


@APPFLASK.route('/examples')
def examples_page():
    return APPFLASK.send_static_file('index.html')


@APPFLASK.route('/<path:the_path>', methods=['GET', 'POST'])
def all_other_routes(the_path):
    """
        Обработка всех запросов от пользователя
    """
    rootDir = os.path.dirname(__file__)
    htmlContent = ""
    if os.path.isfile(os.path.abspath(os.path.join(rootDir, 'templates', the_path))):
       # htmlContent = render_template(the_path, **locals())
       htmlContent = render_template(the_path, request=request)
    elif os.path.isfile(os.path.abspath(os.path.join(rootDir, 'static', the_path))):
       htmlContent = APPFLASK.send_static_file(the_path)
    else:
        return render_template('404.html', **locals()), 404
    if htmlContent != "":
        return htmlContent, 200
    return None


if __name__ == '__main__':
    socketio.run(APPFLASK, port=8080)

