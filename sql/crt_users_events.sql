create table users_events(
    user_id number(38) PRIMARY KEY,
    event_id number(38) PRIMARY KEY,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_event FOREIGN KEY (event_id) REFERENCES events(event_id)
);