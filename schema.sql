--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.1
-- Dumped by pg_dump version 9.6.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: rr_intervals; Type: TABLE; Schema: public; Owner: watson
--

CREATE TABLE rr_intervals (
    user_id character varying(20) NOT NULL,
    mobile_time timestamp with time zone NOT NULL,
    batch_index smallint NOT NULL,
    value integer
);


ALTER TABLE rr_intervals OWNER TO watson;

--
-- Name: rr_intervals rr_intervals_pkey; Type: CONSTRAINT; Schema: public; Owner: watson
--

ALTER TABLE ONLY rr_intervals
    ADD CONSTRAINT rr_intervals_pkey PRIMARY KEY (user_id, mobile_time, batch_index);


--
-- PostgreSQL database dump complete
--

