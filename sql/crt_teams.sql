create table teams(
    team_id number(38) PRIMARY KEY,
    event_id number(38) NOT NULL,
    team_name varchar2(100),
    CONSTRAINT fk_t_event FOREIGN KEY (event_id) REFERENCES events(event_id)
);
