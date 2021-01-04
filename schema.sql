
CREATE TABLE IF NOT EXISTS comments (
	id INTEGER,
	parent STRING NOT NULL,
	content STRING NOT NULL,
	user STRING NOT NULL,
	score INTEGER
	);

CREATE TABLE IF NOT EXISTS posts (
	id INTEGER NOT NULL,
	title STRING NOT NULL,
	content STRING,
	score INTEGER,
	subreddit STRING,
	user STRING NOT NULL
	);

CREATE TABLE IF NOT EXISTS subreddits (
	id INTEGER,
	title STRING,
	user STRING
	);

CREATE TABLE IF NOT EXISTS users (
	id INTEGER,
	userName STRING,
	password STRING,
	isActive BOOLEAN,
	roles STRING
	);

