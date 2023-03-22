#！/bin/bash
echo start python
nohup python3 /home/dxflearn/flask_server.py > /dev/null 2>&1 &
echo end python