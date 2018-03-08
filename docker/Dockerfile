# Use jupyter's datascience notebook image
FROM jupyter/datascience-notebook:65f1c4bea0b2

# Install stellar-py and its requirements 
COPY stellar-py /tmp/stellar-py
RUN pip install --no-cache-dir /tmp/stellar-py

USER root
RUN mkdir -p /data/user
RUN chmod -R o=r /data/user
USER $UID

CMD start-notebook.sh --NotebookApp.token='' --NotebookApp.ip=0.0.0.0
