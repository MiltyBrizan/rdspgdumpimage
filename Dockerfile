FROM amazonlinux:latest

RUN mkdir /mnt/share
RUN yum -y install python3  sudo util-linx samba-client cifs-utils
RUN sudo amazon-linux-extras install postgresql11 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
WORKDIR /usr/src/rdsbackup

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "python3", "src/app.py"]