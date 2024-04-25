create table games(
    game_id number(38) PRIMARY KEY,
    event_id number(38) NOT NULL,
    team1_id number(38),
    team1_score number(38),
    team2_id number(38),
    team2_score number(38),
    date_played date,
    CONSTRAINT fk_g_event FOREIGN KEY (event_id) REFERENCES events(event_id),
    CONSTRAINT fk_g_team1 FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    CONSTRAINT fk_g_team2 FOREIGN KEY (team2_id) REFERENCES teams(team_id)
);
