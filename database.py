import psycopg2 

db_connection = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="1234",
    port="5432",
)

cursor = db_connection.cursor()

cursor.execute("""
    DROP TABLE IF EXISTS matches;
    DROP TABLE IF EXISTS group_teams;
    DROP TABLE IF EXISTS teams;
    DROP TABLE IF EXISTS groups;

    CREATE TABLE IF NOT EXISTS groups (
        group_id SERIAL PRIMARY KEY,
        group_name VARCHAR(100) NOT NULL
    );
               
    CREATE TABLE IF NOT EXISTS teams (
        team_id SERIAL PRIMARY KEY, 
        team_name VARCHAR(100) NOT NULL,
        player1 VARCHAR(100) NOT NULL,
        player2 VARCHAR(100) NOT NULL,
        top_seeded BOOLEAN DEFAULT FALSE
    );

    CREATE TABLE IF NOT EXISTS group_teams (
        group_id INT NOT NULL,
        team_id INT NOT NULL,
        points INT DEFAULT 0,
        sets_won INT DEFAULT 0,
        PRIMARY KEY (group_id, team_id),
        FOREIGN KEY (group_id) REFERENCES groups(group_id),
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
    );
                

    CREATE TABLE IF NOT EXISTS matches (
        match_id SERIAL PRIMARY KEY,
        group_id INT NULL,
        team1_id INT NOT NULL,
        team2_id INT NOT NULL,
        match_time TIMESTAMP NOT NULL,
        match_location VARCHAR(100),
        match_status VARCHAR(20) DEFAULT 'scheduled',
        winner_team_id INT,
        set1_team1 INT,
        set1_team2 INT,
        set2_team1 INT,
        set2_team2 INT,
        super_tiebreak_team1 INT,
        super_tiebreak_team2 INT,
        FOREIGN KEY (group_id) REFERENCES groups(group_id),
        FOREIGN KEY (team1_id) REFERENCES teams(team_id),
        FOREIGN KEY (team2_id) REFERENCES teams(team_id),
        FOREIGN KEY (winner_team_id) REFERENCES teams(team_id)
    );
""")


db_connection.commit()
cursor.close()
db_connection.close()
