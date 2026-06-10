FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libopenblas-dev \
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

# Pre-install numpy and Cython so scikit-surprise can find them
# during its legacy build (required before --no-build-isolation takes effect)
RUN pip install --no-cache-dir numpy Cython

RUN pip install --no-cache-dir --upgrade --no-build-isolation -r /code/requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
