CREATE TABLE logins(
	id		serial primary key,
	username	varchar(256) not null,
	role		varchar(256) not null default 'user',
	password	varchar(256) not null
);

CREATE TABLE recipes(
	id		serial primary key,
	name		varchar(256) not null,
	secret		boolean not null default false,
	recipe		text

);

