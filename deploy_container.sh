docker build --build-arg ENV_MODE=production -f Dockerfile -t mcorreaiz/sqmapp:latest .
docker push mcorreaiz/sqmapp:latest