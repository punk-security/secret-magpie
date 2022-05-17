FROM python:3.10-alpine as builder
RUN apk update && apk add git 
RUN apk add gcc musl-dev libffi-dev

# Create app directory
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-alpine
RUN apk update && apk add git
COPY --from=trufflesecurity/trufflehog:3.4.5 /usr/bin/trufflehog /usr/bin/trufflehog
COPY --from=zricethezav/gitleaks:v8.8.4 /usr/bin/gitleaks /usr/bin/gitleaks
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir -p /app/results
WORKDIR /app

COPY . .

# Exports
ENV SM_COMMAND "docker run punksecurity/secret-magpie --" 
ENTRYPOINT [ "python3", "/app/main.py" ]