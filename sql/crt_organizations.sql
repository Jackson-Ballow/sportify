create table organizations(
    org_id number(38) PRIMARY KEY,
    name varchar2(100) NOT NULL,
    profile_picture BLOB,
    bio varchar2(500) NOT NULL,
    owner_id number(38) NOT NULL,
    CONSTRAINT fk_o_user FOREIGN KEY (owner_id) REFERENCES users(user_id)
);