create table comments(
	comment_id number(38) PRIMARY KEY, 
	user_id number(38) NOT NULL,
	post_id number(38) NOT NULL,
	text varchar2(500),
	CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id),
	CONSTRAINT fk_post FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
