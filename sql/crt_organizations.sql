create table organizations(
    org_id number(38) PRIMARY KEY,
    name varchar2(100) NOT NULL,
    profile_picture BLOB,
    bio varchar2(500) NOT NULL
);