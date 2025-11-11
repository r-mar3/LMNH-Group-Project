DROP DATABASE IF EXISTS plants;
CREATE DATABASE plants;
\c plants;

CREATE TABLE license (
    license_id INT GENERATED ALWAYS AS IDENTITY,
    license_number INT,
    license_name TEXT,
    license_url TEXT,
    PRIMARY KEY (license_id)
);

CREATE TABLE image (
    image_id INT GENERATED ALWAYS AS IDENTITY,
    image_original_url TEXT,
    image_regular_url TEXT,
    image_medium_url TEXT,
    image_small_url TEXT,
    image_thumbnail_url TEXT,
    license_id INT,
    PRIMARY KEY (image_id),
    FOREIGN KEY (license_id) REFERENCES license(license_id)
);

CREATE TABLE country (
    country_id INT GENERATED ALWAYS AS IDENTITY,
    country_name TEXT,
    PRIMARY KEY (country_id)
);

CREATE TABLE city (
    city_id INT GENERATED ALWAYS AS IDENTITY,
    city_name TEXT,
    country_id INT,
    PRIMARY KEY (city_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE origin (
    origin_id INT GENERATED ALWAYS AS IDENTITY,
    origin_longitude FLOAT,
    origin_latitude FLOAT,
    city_id INT,
    PRIMARY KEY (origin_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE species (
    species_id INT GENERATED ALWAYS AS IDENTITY,
    species_name TEXT,
    species_scientific_name TEXT,
    image_id INT,
    PRIMARY KEY (species_id),
    FOREIGN KEY (image_id) REFERENCES image(image_id)
)

CREATE TABLE plant (
    plant_id INT GENERATED ALWAYS AS IDENTITY,
    origin_id INT,
    PRIMARY KEY (plant_id),
    FOREIGN KEY (origin_id) REFERENCES origin(origin_id)
);

CREATE TABLE botanist (
    botanist_id INT GENERATED ALWAYS AS IDENTITY,
    botanist_name TEXT,
    botanist_email TEXT,
    botanist_phone TEXT,
    PRIMARY KEY (botanist_id)
);

CREATE TABLE reading (
    reading_id INT GENERATED ALWAYS AS IDENTITY,
    reading_last_watered TIMESTAMP,
    reading_time_taken TIMESTAMP,
    reading_soil_moisture FLOAT,
    reading_temperature FLOAT,
    botanist_id INT,
    plant_id INT,
    PRIMARY KEY (reading_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);