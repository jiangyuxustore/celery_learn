FROM python:3
WORKDIR /home
RUN touch a.txt
RUN ls
RUN apt-get update && apt-get upgrade -y && apt-get install -y git
RUN git clone https://github.com/jiangyuxustore/dxflearn.git
ENV basepath /home/dxflearn
WORKDIR $basepath
RUN pwd
RUN git config --global url.https://github.com/.insteadOf git://github.com/
RUN pip install -r requirements.txt
ENTRYPOINT ["/home/dxflearn/startflask.sh"]
CMD ["/bin/bash"]

