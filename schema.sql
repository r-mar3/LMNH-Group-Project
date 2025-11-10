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

-- TODO: check what numbers to use after decimal for long and lat
CREATE TABLE origin (
    origin_id INT GENERATED ALWAYS AS IDENTITY,
    origin_longitude DECIMAL(9, 6),
    origin_longitude DECIMAL(9, 6),
    city_id INT,
    PRIMARY KEY (origin_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE plant (
    plant_id INT GENERATED ALWAYS AS IDENTITY,
    plant_name TEXT,
    plant_scientific_name TEXT,
    plant_origin_id INT,
    plant_images_id INT,
    PRIMARY KEY (plant_id),
    FOREIGN KEY (plant_origin_id) REFERENCES origin(origin_id)
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
    reading_botanist_id INT,
    reading_plant_id INT,
    PRIMARY KEY (reading_id),
    FOREIGN KEY (reading_botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (reading_plant_id) REFERENCES plant(plant_id)
);