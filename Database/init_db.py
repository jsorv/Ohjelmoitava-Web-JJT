import sqlite3

def init_db(db_path='database.db'):
    """Initializes the database by creating necessary tables."""

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    #locations table
    cur.execute(""""
        CREATE TABLE IF NOT EXISTS locations (
            location_id INTEGER PRIMARY KEY,
            county TEXT NOT NULL,
            city TEXT NOT NULL,
        ;
        """)
    
    #weather_data report
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_report (
            report_id INTEGER PRIMARY KEY CHECK(report_id > 0),
            location_id INTEGER NOT NULL,
            temperature REAL,
            humidity INTEGER CHECK(humidity BETWEEN 0 AND 100),
            wind_speed REAL CHECK(wind_speed >= 0),
            cloud_cover INTEGER CHECK(cloud_cover BETWEEN 0 AND 100),
            rain INTEGER CHECK (rain IN (0, 1)),
            fog INTEGER CHECK (fog IN (0, 1)),
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );
        """)
    
    conn.commit()
    conn.close()