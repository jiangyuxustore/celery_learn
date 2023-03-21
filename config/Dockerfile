FROM python:3
RUN cd /home
RUN touch a.txt
RUN ls
RUN apt-get update && apt-get upgrade -y && apt-get install -y git
RUN git clone https://github.com/jiangyuxustore/dxflearn.git
ENV basepath /home/dxflearn
WORKDIR $basepath
RUN pwd
RUN pip install -r requirements.txt
ENTRYPOINT ["/home/dxflearn/startflask.sh"]
CMD ["/bin/bash"]

