create table organizations_admins(
    user_id number(38) PRIMARY KEY,
    org_id number(38) PRIMARY KEY,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);