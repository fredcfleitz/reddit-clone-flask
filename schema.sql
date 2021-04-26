
CREATE TABLE IF NOT EXISTS comments (
	id INTEGER,
	parent VARCHAR NOT NULL,
	content VARCHAR NOT NULL,
	userName VARCHAR NOT NULL,
	score INTEGER
	);

CREATE TABLE IF NOT EXISTS posts (
        id INTEGER NOT NULL,
        title VARCHAR NOT NULL,
        content VARCHAR,
        score INTEGER,
        subreddit VARCHAR,
        userName VARCHAR NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );


CREATE TABLE IF NOT EXISTS subreddits (
	id INTEGER,
	title VARCHAR,
	userName VARCHAR
	);

CREATE TABLE IF NOT EXISTS users (
	id INTEGER,
	userName VARCHAR,
	password VARCHAR,
	isActive BOOLEAN,
	roles VARCHAR
	);

