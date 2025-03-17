# CUROTEC Technica Assessment
by Tiago Barufi

## This is an experiment aimed at a demonstration of ORM, web service and geospatial capabilities.
The goal of this app is to demonstrate some concepts I find interesting, both for geospatial as for text searching and frontend rendering using the React-Leaflet library.


### Requisites

docker and docker-compose
PostgreSQL 15 or upper, with the PostGIS extension enabled

### Prepare the database 
The database must have the PostGIS extension enabled. The credentials must be stored in a .env file located in the backend directory, and the keys must be defined as in the .env.sample file.

The database must be accessible from the docker network.

### run the app
The docker-compose.yml defines two containers, backend and frontend.
They are set to be built from the respective DOckerfiles as they are located in the corresponding directories.

The app must be started with

`docker-compose up -d`

This command will create the containers and the app will be available at http://localhost:3001 (frontend) and http://localhost:2000 (backend).

### testing
`docker exec -ti backend pytest` 

to trigger the backend tests. The frontend runs as 

`docker exec -ti frontend npm test`

### Using the application
The screen shows two fields and a map pane. In order to use the application the user must load a gpkg map. 
Once the file is selected, ther will be an upload proceeding.
A sample file is provided in the project root folder: mex.gpkg. 
The "Search" field allows the user to search for roads in the map once the database is configured.

