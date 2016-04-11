CREATE TABLE InterviewboxUser
(
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    education VARCHAR(255) NOT NULL,
    employment VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    num_ratings INT NOT NULL,
    total_ratings INT NOT NULL,
    resume BYTEA,
    is_interviewer INT NOT NULL,
    availability VARCHAR(1912)  -- pickle of range object
);
--asdfasdg
-- CREATE TABLE UserSchedule
-- (
--     id INTEGER PRIMARY KEY,
--     user_id INTEGER REFERENCES InterviewboxUser (id) NOT NULL,
--     schedule VARCHAR(168) NOT NULL
-- );

CREATE TABLE Interview
(
    id INTEGER PRIMARY KEY,
    user1 INTEGER REFERENCES InterviewboxUser(id) NOT NULL,
    user2 INTEGER REFERENCES InterviewboxUser(id) NOT NULL,
    time TIMESTAMP NOT NULL
);

CREATE TABLE InterviewFeedback
(
    id INTEGER PRIMARY KEY,
    interview_id INTEGER REFERENCES Interview(id) NOT NULL,
    feedback VARCHAR(255) NOT NULL
);

