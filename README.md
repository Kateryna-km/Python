# Flask project python 3.6, virtualenv + requirements.txt

Для створення необхідної версії python встановити **pyenv**. Для Windows команди у *PowerShell*:
```
pip install pyenv-win --target %USERPROFILE%\.pyenv 
[System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
[System.Environment]::SetEnvironmentVariable('path', $HOME + "\.pyenv\pyenv-win\bin;" + $HOME + "\.pyenv\pyenv-win\shims;" + $env:Path,"User")
```

Обираємо версію:

```pyenv install 3.6.8``` 

Далі інсталюємо віртуальне середовище

```pip install virtualenv```

Створюємо середовище з встанвленою зазделегідь версією python

```virtualenv --python=<шлях_до_файлу_python.exe> <ім'я_середовища>```

Переходимо у папку Scripts і активуємо його:
*activate.bat*

Далі інсталюємо неохідні залежності:
```
pip install flask
pip install gevent
```
gevent виконує роль wsgi-сервера. Запускається командою:

server = WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()

Після запуску за посиланням:

http://127.0.0.1:5000/api/v1/hello-world-10

маємо необхідний варіант виконання з HTTP статус кодом відповіді '200'
