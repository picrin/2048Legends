2048wc.com is organised as multiple cooperating microservices.
This part is responsible for serving static files:
You should be able to go to src/static and execute, first ./dockerPull and then ./dockerRun. both scripts are one-liners.
You can also build your own image "./dockerBuild" and if all is well it should be no different then the one downloaded from the web.
All commands need to be executed as a superuser and you need to make sure that docker's deamon is running in the background.
