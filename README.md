# Flask_Doll
Кеукла проекта на Flask с возможностью запускать Python скрипты из  JS кода

<pre>HTML:<script></script>
    <script src="static/js/jquery.min.js"></script>
    <script type="text/javascript" src="static/js/socket.io.min.js"></script>
    <script src="static/js/application.js"></script>
 JS:
   sendServer('control.test.MyTestFun', function(msg) { $('#mycontent').text(msg); }, 111, 2222222)
</pre>