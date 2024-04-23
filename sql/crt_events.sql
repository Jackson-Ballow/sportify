create table events(
    event_id number(38) PRIMARY KEY,
    org_id number(38) NOT NULL,
    sport_name varchar2(30),
    start_date date NOT NULL,
    end_date date NOT NULL,
    event_name varchar2(50) NOT NULL,
    event_bio varchar2(500),
    event_logo BLOB,
    capacity number(38) NOT NULL,
    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);