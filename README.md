# sqm-webapp



### Container build Instructions:
```
$ docker build --build-arg "ENV_MODE=[PROD|DEV]" -f Dockerfile -t sqmapp:<tag> .

$ docker login

$ docker tag sqmapp:<tag> mcorreaiz/sqmapp

$ docker push mcorreaiz/sqmapp
```
  

### To test container locally:

`$ docker run -p 5000:5000 sqmapp`