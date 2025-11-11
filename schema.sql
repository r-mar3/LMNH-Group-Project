DROP DATABASE IF EXISTS plants;
CREATE DATABASE plants;
\c plants;

CREATE TABLE license (
    license_id INT GENERATED ALWAYS AS IDENTITY,
    license_number UNIQUE INT,
    license_name UNIQUE TEXT,
    license_url UNIQUE TEXT,
    PRIMARY KEY (license_id)
);

CREATE TABLE image (
    image_id INT GENERATED ALWAYS AS IDENTITY,
    image_original_url UNIQUE TEXT,
    image_regular_url UNIQUE TEXT,
    image_medium_url UNIQUE TEXT,
    image_small_url UNIQUE TEXT,
    image_thumbnail_url UNIQUE TEXT,
    license_id INT,
    PRIMARY KEY (image_id),
    FOREIGN KEY (license_id) REFERENCES license(license_id)
);

CREATE TABLE country (
    country_id INT GENERATED ALWAYS AS IDENTITY,
    country_name UNIQUE TEXT,
    PRIMARY KEY (country_id)
);

CREATE TABLE city (
    city_id INT GENERATED ALWAYS AS IDENTITY,
    city_name TEXT, -- Not unique, cities can have the same name
    country_id INT,
    PRIMARY KEY (city_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE origin (
    origin_id INT GENERATED ALWAYS AS IDENTITY,
    origin_longitude FLOAT, -- left non-unique in case of rounding errors
    origin_latitude FLOAT, -- left non-unique in case of rounding errors
    city_id INT,
    PRIMARY KEY (origin_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE species (
    species_id INT GENERATED ALWAYS AS IDENTITY,
    species_name UNIQUE TEXT,
    species_scientific_name UNIQUE TEXT,
    image_id INT,
    PRIMARY KEY (species_id),
    FOREIGN KEY (image_id) REFERENCES image(image_id)
);

CREATE TABLE plant (
    plant_id INT GENERATED ALWAYS AS IDENTITY,
    origin_id INT,
    species_id INT,
    PRIMARY KEY (plant_id),
    FOREIGN KEY (origin_id) REFERENCES origin(origin_id)
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);

CREATE TABLE botanist (
    botanist_id INT GENERATED ALWAYS AS IDENTITY,
    botanist_name TEXT, -- left non-unique for John Smiths
    botanist_email UNIQUE TEXT,
    botanist_phone UNIQUE TEXT,
    PRIMARY KEY (botanist_id)
);

CREATE TABLE reading (
    reading_id INT GENERATED ALWAYS AS IDENTITY,
    reading_last_watered TIMESTAMP, -- plants can be watered at the same time
    reading_time_taken TIMESTAMP, -- plants can be read at the same time
    reading_soil_moisture FLOAT, -- plants can be equally moist
    reading_temperature FLOAT, -- plants can be equally hot or cold
    botanist_id INT,
    plant_id INT,
    PRIMARY KEY (reading_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);

-- SQL ids start at 1

INSERT INTO 
    license (license_number, license_name, license_url) 
VALUES
    (9, 'test', 'https://curriculum.sigmalabs.co.uk/Advanced-Data/Week%205/overview')
    (20, 'testing', 'https://curriculum.sigmalabs.co.uk/')

INSERT INTO 
    image (license_id, image_medium_url, image_original_url, image_regular_url, image_small_url, image_thumbnail_url) 
VALUES
    (1, 'https://curriculum.sigmalabs.co.uk/assets/images/overview-374a124b9ca035b674ea6513e5d49898.png','https://curriculum.sigmalabs.co.uk/assets/images/overview-374a124b9ca035b674ea6513e5d49898.png', 'https://curriculum.sigmalabs.co.uk/assets/images/overview-374a124b9ca035b674ea6513e5d49898.png', 'https://curriculum.sigmalabs.co.uk/assets/images/overview-374a124b9ca035b674ea6513e5d49898.png', 'https://curriculum.sigmalabs.co.uk/assets/images/overview-374a124b9ca035b674ea6513e5d49898.png')

INSERT INTO
    country (country_name)
VALUES
    ('Totally-Real-Land')

INSERT INTO
    city (city_name, country_id)
VALUES
    ('Fake Town', 1)

INSERT INTO
    origin (origin_latitude, origin_longitude, city_id)
VALUES
    (0.6, 0.66, 1)