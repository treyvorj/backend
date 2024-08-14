DROP DATABASE trace ;
DROP OWNED BY trace_admin ;
DROP ROLE trace_admin;

CREATE ROLE trace_admin LOGIN PASSWORD trace_admin ;
CREATE DATABASE trace OWNER trace_admin ;