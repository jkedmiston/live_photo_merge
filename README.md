# Instructions
Had issue with the opening the `mkv` file produced in the docker container from the main os via `vlc`, this gets around that, see [link](https://vsupalov.com/docker-shared-permissions/).
* `python setup.py` # a one time script, it creates a folder in `../live_photos_volume` to mount as an input volume. This is so that `docker build` doesn't take a long time if a lot of files build up.
* `docker-compose build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)
* Set up the `.env` file, `cp env.sample .env` and edit accordingly (see `env.sample` for instructions). 
* `docker-compose up` will start the conversion service. 
* Now, moving a `zip` archive into `../live_photos_volume` will trigger the processing pipeline. The output of the pipeline a file depending on the name of the zip file. E.g. if the zipfile is called myzipfile.zip, the output file produced is called `out_myzipfile.mkv`. It can be opened with a program like `vlc` to view.
* The operation will ingest the source `zip` file and delete it. So if you want to keep a copy, you should use `cp` to move it over. 
* You'll need to stop the container if you change a parameter in the `.env` file. For example, for a final output, changing `ANNOTATIONS` from `1` to `0` would need to be stopped and restarted.
