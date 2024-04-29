create table users(
    user_id number(38) PRIMARY KEY,
    email varchar2(50) NOT NULL,
    password varchar(200) NOT NULL,
    fullname varchar2(50) NOT NULL,
    profile_picture BLOB
);
