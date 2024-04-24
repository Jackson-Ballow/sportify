create table games_users(
    user_id number(38),
    game_id number(38),
    CONSTRAINT pk_games_users PRIMARY KEY (user_id, game_id),
    CONSTRAINT fk_gu_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_gu_game FOREIGN KEY (game_id) REFERENCES games(game_id)
);