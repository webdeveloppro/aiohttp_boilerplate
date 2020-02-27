create table post_post
(
	id serial
		constraint post_post_pk
		primary key,
	name varchar(50) default '' not null,
	content text default '' not null
);
insert into post_post (name,content) values ('Post 1', 'Content');
insert into post_post (name,content) values ('Post 2', 'Blabla');
