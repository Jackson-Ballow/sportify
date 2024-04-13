create table games(
    game_id number(38) PRIMARY KEY,
    event_id number(38) NOT NULL,
    team1_name varchar2(100),
    team1_score number(38),
    team2_name varchar2(100),
    team2_score number(38),
    CONSTRAINT fk_event FOREIGN KEY (event_id) REFERENCES events(event_id)
);