ARG SOURCE_CONTAINER_TAG
FROM python:${SOURCE_CONTAINER_TAG}
WORKDIR /usr/local/src
COPY src/ pyproject.toml ./
WORKDIR /usr/local/src/logparser
RUN python -m pip install --upgrade pip && pip install poetry
RUN useradd -m logparser
RUN poetry export -o /tmp/logparser-requirements.txt
ARG LOG_DIR LISTEN_PORT
ENV LOG_DIR=${LOG_DIR} LOG_FILE=${LOG_FILE} LISTEN_IP=${LISTEN_IP} LISTEN_PORT=${LISTEN_PORT}
RUN mkdir -p ${LOG_DIR}
USER logparser
ENV PATH="${PATH}:${HOME}/.local/bin"
RUN pip install -r /tmp/logparser-requirements.txt
CMD /usr/local/src/logparser/parser.py --logfile $LOG_FILE --ip $LISTEN_IP --port $LISTEN_PORT
EXPOSE ${LISTEN_PORT}/tcp
