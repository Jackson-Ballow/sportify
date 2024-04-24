create table organizations_admins(
    user_id number(38),
    org_id number(38),
    CONSTRAINT pk_organizations_admins PRIMARY KEY (user_id, org_id),
    CONSTRAINT fk_oa_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_oa_org FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);