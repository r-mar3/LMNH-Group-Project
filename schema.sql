DROP TABLE IF EXISTS reading;
DROP TABLE IF EXISTS plant;
DROP TABLE IF EXISTS origin;
DROP TABLE IF EXISTS species;
DROP TABLE IF EXISTS image;
DROP TABLE IF EXISTS city;
DROP TABLE IF EXISTS country;
DROP TABLE IF EXISTS license;
DROP TABLE IF EXISTS botanist;

CREATE TABLE license (
    license_id INT UNIQUE,
    license_number INT UNIQUE,
    license_name VARCHAR(255) UNIQUE,
    license_url VARCHAR(255) UNIQUE,
    PRIMARY KEY (license_id)
);

CREATE TABLE image (
    image_id INT UNIQUE,
    image_original_url VARCHAR(255) UNIQUE,
    image_regular_url VARCHAR(255) UNIQUE,
    image_medium_url VARCHAR(255) UNIQUE,
    image_small_url VARCHAR(255) UNIQUE,
    image_thumbnail_url VARCHAR(255) UNIQUE,
    license_id INT,
    PRIMARY KEY (image_id),
    FOREIGN KEY (license_id) REFERENCES license(license_id)
);

CREATE TABLE country (
    country_id INT UNIQUE,
    country_name VARCHAR(255) UNIQUE,
    PRIMARY KEY (country_id)
);

CREATE TABLE city (
    city_id INT UNIQUE,
    city_name VARCHAR(255), -- Not unique, cities can have the same name
    country_id INT,
    PRIMARY KEY (city_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE origin (
    origin_id INT UNIQUE,
    origin_longitude FLOAT, -- left non-unique in case of rounding errors
    origin_latitude FLOAT, -- left non-unique in case of rounding errors
    city_id INT,
    PRIMARY KEY (origin_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE species (
    species_id INT UNIQUE,
    species_name VARCHAR(255) UNIQUE,
    species_scientific_name VARCHAR(255) UNIQUE,
    image_id INT,
    PRIMARY KEY (species_id),
    FOREIGN KEY (image_id) REFERENCES image(image_id)
);

CREATE TABLE plant (
    plant_id INT UNIQUE,
    origin_id INT,
    species_id INT,
    PRIMARY KEY (plant_id),
    FOREIGN KEY (origin_id) REFERENCES origin(origin_id),
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);

CREATE TABLE botanist (
    botanist_id INT UNIQUE,
    botanist_name VARCHAR(255), -- left non-unique for John Smiths
    botanist_email VARCHAR(255) UNIQUE,
    botanist_phone VARCHAR(255) UNIQUE,
    PRIMARY KEY (botanist_id)
);

CREATE TABLE reading (
    reading_id INT IDENTITY(1, 1),
    reading_last_watered DATETIME, -- plants can be watered at the same time
    reading_time_taken DATETIME, -- plants can be read at the same time
    reading_soil_moisture FLOAT, -- plants can be equally moist
    reading_temperature FLOAT, -- plants can be equally hot or cold
    reading_error TEXT,
    botanist_id INT,
    plant_id INT,
    PRIMARY KEY (reading_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);
