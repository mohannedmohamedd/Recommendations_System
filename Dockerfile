FROM python:3.10-slim

# Install system build deps required by some python packages (scikit-surprise, wordcloud)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	g++ \
	libatlas-base-dev \
	liblapack-dev \
	libblas-dev \
	libfreetype6-dev \
	libpng-dev \
	pkg-config \
	git \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN python -m pip install --upgrade pip setuptools
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Port 7860 commonly used for web UI on Spaces; expose for clarity
EXPOSE 7860

# Start app using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]