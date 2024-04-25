create table teams_users(
    user_id number(38),
    team_id number(38),
    CONSTRAINT pk_teams_users PRIMARY KEY (user_id, team_id),
    CONSTRAINT fk_tu_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_tu_game FOREIGN KEY (team_id) REFERENCES teams(team_id)
);
