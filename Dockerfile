FROM python:3.10-alpine
LABEL org.opencontainers.image.source="https://github.com/joakimwinum/python-snake"
LABEL org.opencontainers.image.licenses="MIT"
WORKDIR /usr/src/python-snake
COPY . .
CMD ["python", "./python-snake.py"]
