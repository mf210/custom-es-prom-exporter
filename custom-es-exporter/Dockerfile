FROM python:3.12
WORKDIR /custom-es-exporter
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . /custom-es-exporter/
RUN pip install pipenv && pipenv install --dev --system
CMD [ "python", "quick-start.py" ]