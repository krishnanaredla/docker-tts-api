

```sh
git clone https://github.com/krishnanaredla/docker-tts-api.git
cd docker-tts-api
# unzip the models downloaded and place them in models folder
docker build -t mtts:1.0 .

# After build success

docker run  --entrypoint "/bin/bash" -it -p 8081:8081 mtts:1.0
root@xx/app# cd tts_api/
root@xx:/app/tts_api# pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org pyworld
root@xx:/app/tts_api# python3 main.py

```

