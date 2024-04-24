create table users_organizations(
    user_id number(38),
    org_id number(38),
    date_joined date NOT NULL,
    CONSTRAINT pk_users_organizations PRIMARY KEY (user_id, org_id),
    CONSTRAINT fk_uo_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_uorg FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);