create table posts(
    post_id number(38) PRIMARY KEY,
    user_id number(38) NOT NULL,
    org_id number(38) NOT NULL,
    title varchar2(50) NOT NULL,
    text varchar2(500),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);