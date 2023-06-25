FROM python:3.10-alpine
LABEL org.opencontainers.image.source="https://github.com/joakimwinum/py-snake"
LABEL org.opencontainers.image.licenses="MIT"
WORKDIR /usr/src/py-snake
COPY . .
CMD ["python", "./py-snake.py"]
