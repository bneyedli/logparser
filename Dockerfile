FROM python:slim
ARG LOG_DIR LISTEN_PORT
WORKDIR /usr/local/src
COPY src/ pyproject.toml ./
WORKDIR /usr/local/src/logparser
RUN python -m pip install --upgrade pip && pip install poetry
RUN useradd -m logparser
RUN poetry export -o /tmp/logparser-requirements.txt
RUN mkdir -p ${LOG_DIR}
USER logparser
ENV PATH="${PATH}:${HOME}/.local/bin"
RUN pip install -r /tmp/logparser-requirements.txt
ENV LOG_FILE=${LOG_FILE} LISTEN_IP=${LISTEN_IP} LISTEN_PORT=${LISTEN_PORT}
CMD /usr/local/src/logparser/parser.py --logfile $LOG_FILE --ip $LISTEN_IP --port $LISTEN_PORT
EXPOSE ${LISTEN_PORT}/tcp
