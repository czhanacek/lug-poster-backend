FROM python as runstage
EXPOSE 80
ENV FLASK_APP server.py
RUN pip install pipenv
RUN pipenv install
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]




