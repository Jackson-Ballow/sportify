create table users_events(
    user_id number(38),
    event_id number(38),
    CONSTRAINT pk_users_events PRIMARY KEY (user_id, event_id),
    CONSTRAINT fk_ue_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_ue_event FOREIGN KEY (event_id) REFERENCES events(event_id)
);