# sqm-webapp



### Container build Instructions:
```
$ docker login

$ docker build --build-arg ENV_MODE=[production|development] -f Dockerfile -t mcorreaiz/sqmapp:latest .

$ docker push mcorreaiz/sqmapp
```
  

### To test container locally:

`$ docker run -p 5000:5000 mcorreaiz/sqmapp`