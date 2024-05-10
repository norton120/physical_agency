FROM python:3.11
COPY ./app /src/app
ENV PYTHONPATH=/src
WORKDIR /src/app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]