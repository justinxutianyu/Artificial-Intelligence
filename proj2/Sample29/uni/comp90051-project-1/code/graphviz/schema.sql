DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS session

CREATE TABLE user (
    userId integer primary key not null,
    activityId integer foreign key not null,
    sessionId text foreign key not null,
    userName text,
);

CREATE TABLE activity (
    activityId integer primary key not null autoincrement,
    activityGroup text not null,
    activityTime timestamp not null
);

CREATE TABLE session (
    sessionId text primary key not null,
    activityGroup integer foreign key not null,
    browser text
);
