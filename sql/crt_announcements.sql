create table announcements(
    announcement_id number(38) PRIMARY KEY,
    org_id number(38) NOT NULL,
    date_posted date NOT NULL,
    subject varchar2(100) NOT NULL,
    text varchar2(500),
    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);