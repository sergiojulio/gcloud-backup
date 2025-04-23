FROM python:3.11.12-slim

ADD main.py .

ADD requirements.txt .

RUN pip install -r requirements.txt

#CMD ["python", "-m uvicorn main:app --host 0.0.0.0 --port 8080 --reload"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
