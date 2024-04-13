create table games_users(
    user_id number(38) PRIMARY KEY,
    game_id number(38) PRIMARY KEY,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_game FOREIGN KEY (game_id) REFERENCES games(game_id)
);