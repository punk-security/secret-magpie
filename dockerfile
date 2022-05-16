FROM python:3.10
RUN apt-get update && apt-get install git 

# Create app directory
RUN mkdir -p /app/results
WORKDIR /app

# Install dependencies
COPY --from=trufflesecurity/trufflehog:3.4.5 /usr/bin/trufflehog /usr/bin/trufflehog
COPY --from=zricethezav/gitleaks:v8.8.4 /usr/bin/gitleaks /usr/bin/gitleaks
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exports
ENV SM_COMMAND "docker run punksecurity/secret-magpie --" 
ENTRYPOINT [ "python3", "/app/main.py" ]