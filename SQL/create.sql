CREATE TABLE Rideshare_user
(netid VARCHAR(7) NOT NULL UNIQUE PRIMARY KEY,
 name VARCHAR(50) NOT NULL,
 duke_email VARCHAR(40) NOT NULL,
 phone_number VARCHAR(12) NOT NULL,
 affiliation VARCHAR(20) NOT NULL,
 password VARCHAR(100) NOT NULL);

CREATE TABLE Driver
(netid VARCHAR(7) NOT NULL PRIMARY KEY REFERENCES rideshare_user(netid),
 license_no VARCHAR(50) NOT NULL,
 license_plate_no VARCHAR(10) NOT NULL,
 plate_state VARCHAR(4) NOT NULL);

CREATE TABLE Ride
(ride_no SERIAL NOT NULL UNIQUE PRIMARY KEY,
 origin VARCHAR(50) NOT NULL,
 destination VARCHAR(50) NOT NULL CHECK(destination <> origin), 
 driver_netid VARCHAR(7) NOT NULL REFERENCES Driver(netid),
 date DATE NOT NULL, 
 earliest_departure TIME CHECK(earliest_departure <= latest_departure),
 latest_departure TIME CHECK (latest_departure >= earliest_departure),
 seats_available INTEGER NOT NULL,
 max_seats_available INTEGER NOT NULL, 
 gas_price INTEGER NOT NULL,
 comments VARCHAR(200));

CREATE TABLE Reserve
(rider_netid VARCHAR(7) NOT NULL,
  ride_no INTEGER NOT NULL, 
  seats_needed INTEGER NOT NULL,
  note VARCHAR(200), 
  PRIMARY KEY(rider_netid, ride_no),
  FOREIGN KEY (rider_netid) REFERENCES rideshare_user(netid),
  FOREIGN KEY (ride_no) REFERENCES Ride(ride_no));

CREATE TABLE Driving_locations
(location VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY);

CREATE TABLE Plate_states
(state VARCHAR(10) NOT NULL UNIQUE PRIMARY KEY);


-- Triggers

CREATE FUNCTION TF_Driver_own_rider() RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT driver_netid
             FROM Ride
             WHERE NEW.ride_no = ride_no AND NEW.rider_netid = driver_netid) THEN
    RAISE EXCEPTION 'Driver cannot reserve own ride.';
    RETURN NULL;
  ELSE
    RETURN NEW;                                    
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TG_Driver_own_rider
  BEFORE INSERT OR UPDATE ON Reserve
  FOR EACH ROW
  EXECUTE PROCEDURE TF_Driver_own_rider();

------

CREATE FUNCTION TF_Not_enough_seats() RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT * FROM Ride R
      WHERE NEW.ride_no = R.ride_no
      AND NEW.seats_needed > R.seats_available) THEN
    RAISE EXCEPTION 'Not enough seats available in ride';
    RETURN NULL;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TG_Not_enough_Seats
  BEFORE INSERT OR UPDATE ON Reserve
  FOR EACH ROW
  EXECUTE PROCEDURE TF_Not_enough_Seats();


CREATE FUNCTION TF_One_res_per_date() RETURNS TRIGGER AS $$
BEGIN
  IF ((SELECT MAX(userRideDates.counts) FROM (SELECT RD.date AS dates, COUNT(RD.date) AS counts
                        FROM Ride RD, Reserve RS
                        WHERE RD.ride_no = RS.ride_no
                        AND RS.rider_netid = NEW.rider_netid
                        GROUP BY RD.date) AS userRideDates) > 1) THEN
    RAISE EXCEPTION 'Cannot book ride on same date';
    RETURN NULL;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TG_One_res_per_date
  BEFORE INSERT OR UPDATE ON Reserve
  FOR EACH ROW
  EXECUTE PROCEDURE TF_One_res_per_date();

---

CREATE FUNCTION TF_Only_driver_list_ride() RETURNS TRIGGER AS $$
BEGIN
  IF (NEW.driver_netid NOT IN (SELECT netid FROM Driver)) THEN
    RAISE EXCEPTION 'User not registered as Driver';
    RETURN NULL;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER TG_Only_driver_list_ride
  BEFORE INSERT ON Ride
  FOR EACH ROW
  EXECUTE PROCEDURE TF_Only_driver_list_ride();

---

CREATE FUNCTION TF_One_drive_per_day() RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT * FROM Ride R
            WHERE NEW.driver_netid = R.driver_netid
            AND NEW.date = R.date
            AND NEW.earliest_departure < R.latest_departure) THEN
    RAISE EXCEPTION 'Cannot schedule two overlapping rides.';
    RETURN NULL;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TG_One_drive_per_day
  BEFORE INSERT ON Ride
  FOR EACH ROW
  EXECUTE PROCEDURE TF_One_drive_per_day();

-- Indexes

CREATE INDEX idx_reserve_ride_no
ON reserve(ride_no);

CREATE INDEX idx_ride_driver_netid
ON ride(driver_netid);

CREATE INDEX idx_reserve_rider_netid
ON reserve(rider_netid);

