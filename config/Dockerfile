FROM ubuntu:20.04
WORKDIR /home   # 改变工作目录的路径用RUN cd /home是不行的, 要用 WORKDIR /home
# apt-get install -y 是为了有的包安装的时候会问你是否需要continue, -y 默认是继续
RUN apt-get update -y && apt-get install -y git && apt-get install -y python3 && apt-get install -y python3-pip
RUN git clone https://github.com/jiangyuxustore/dxflearn.git
ENV basepath /home/dxflearn
WORKDIR $basepath
RUN git config --global url.https://github.com/.insteadOf git://github.com/
RUN pip install --upgrade pip
RUN pip install -i https://pypi.douban.com/simple -r requirements.txt
RUN pip install -e git+git://github.com/hbasria/celery-redis-cluster-backend.git#egg=celery-redis-cluster-backend
ENTRYPOINT ["/home/dxflearn/startflask.sh"]
CMD ["/bin/bash"]

