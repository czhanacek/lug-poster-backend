FROM python as runstage
EXPOSE 80
RUN git clone https://github.com/czhanacek/lug-poster-backend
WORKDIR lug-poster-backend
ENV FLASK_APP server.py
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]




