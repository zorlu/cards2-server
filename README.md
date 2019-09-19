# cards2-server
This is an open source educational Online Trading Card Game (TCG) Server written with Python and Django Web Framework.

Example Client (HTML5/Javascript) repo is [here](https://github.com/zorlu/cards2-client).


### Requirements
* **memcached** https://memcached.org/
  
  for connecting and debugging active game instance via django shell.
  
* **phantomjs** https://phantomjs.org/download.html
  
  in case of use random name generator, phantomjs executable must be in your PATH.

### Installation (python3 only)

    git clone https://github.com/zorlu/cards2-server.git
    cd cards2-server/
    virtualenv env --python /path/to/python3
    source env/bin/activate
    pip install -r requirements.txt
    

### Start Django Server (Administration)

    python manage.py runserver 127.0.0.1:8000
    
locate **http://127.0.0.1:8000/admin/** from your browser.
username: **zorlu**  password: **112345**

### Start Game Server

    python manage.py game_server

Websocket server will start **127.0.0.1:5678**

#### Game modes

* Player vs AI free style (uncomment required block in game_server.py) also not tested!
* Player vs AI Dungeon stages (modify requires in client wsocket.js)
* AI vs AI (inspector mode) (modify requires in client wsocket.js)

### TODO

* documentation (soon)
