FROM ubuntu:20.04
WORKDIR /home
RUN touch a.txt
RUN ls
RUN apt-get update && apt-get install -y whatever && apt-get upgrade -y && apt-get install -y git && apt-get install python3-pip
RUN git clone https://github.com/jiangyuxustore/dxflearn.git
ENV basepath /home/dxflearn
WORKDIR $basepath
RUN pwd
RUN git config --global url.https://github.com/.insteadOf git://github.com/
RUN pip install --upgrade pip
RUN pip install -i https://pypi.douban.com/simple -r requirements.txt
RUN pip install -e git+git://github.com/hbasria/celery-redis-cluster-backend.git#egg=celery-redis-cluster-backend
ENTRYPOINT ["/home/dxflearn/startflask.sh"]
CMD ["/bin/bash"]

