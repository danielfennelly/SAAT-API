CREATE TABLE rr_intervals(
	user_id varchar(20),
	mobile_time timestamptz,
	batch_index smallint,
	value int,
	PRIMARY KEY (user_id,mobile_time,batch_index)
);

CREATE TABLE subjective(
	user_id varchar(20),
	mobile_time timestamptz,
	event_type varchar(20),
	value int,
	PRIMARY KEY (user_id,mobile_time)
);
