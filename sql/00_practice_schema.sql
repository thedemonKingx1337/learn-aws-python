-- Small tables that the retail_db schema in `public` cannot teach:
--   * a manager hierarchy  -> recursive CTEs
--   * deliberate ties       -> RANK vs DENSE_RANK vs ROW_NUMBER
--   * NULLs and duplicates  -> DISTINCT, COUNT and aggregate semantics
--   * a gap in a date series -> ROWS vs RANGE window frames
--
-- Lives in its own schema so `public` (retail_db, 172k rows) is never touched.
-- Safe to re-run: it drops and recreates only the `practice` schema.

DROP SCHEMA IF EXISTS practice CASCADE;
CREATE SCHEMA practice;

CREATE TABLE practice.employees (
    emp_id     int PRIMARY KEY,
    emp_name   text NOT NULL,
    dept       text NOT NULL,
    salary     numeric,          -- deliberately nullable
    manager_id int REFERENCES practice.employees(emp_id),
    hire_date  date NOT NULL
);

INSERT INTO practice.employees VALUES
    (12, 'Lena',   'Executive',   220000, NULL, '2015-02-01'),
    (10, 'Jia',    'Engineering', 140000,   12, '2016-01-10'),
    (11, 'Kemal',  'Sales',       135000,   12, '2016-04-18'),
    -- Engineering: two pairs of tied salaries
    ( 1, 'Asha',   'Engineering',  95000,   10, '2019-03-01'),
    ( 2, 'Bala',   'Engineering',  95000,   10, '2020-07-15'),
    ( 3, 'Chen',   'Engineering',  88000,   10, '2021-01-20'),
    ( 4, 'Dmitri', 'Engineering',  88000,   10, '2021-06-11'),
    ( 5, 'Elif',   'Engineering',  72000,   10, '2022-09-05'),
    -- Sales: one tie, and one NULL salary
    ( 6, 'Farid',  'Sales',        67000,   11, '2018-05-02'),
    ( 7, 'Gita',   'Sales',        67000,   11, '2019-11-30'),
    ( 8, 'Hugo',   'Sales',          NULL,  11, '2023-02-14'),
    ( 9, 'Ivy',    'Sales',        59000,   11, '2023-08-21');

CREATE TABLE practice.sales_daily (
    sale_date date NOT NULL,
    region    text NOT NULL,
    amount    numeric NOT NULL,
    PRIMARY KEY (sale_date, region)
);

-- Note the deliberate GAP: 2024-01-05 is missing for both regions.
-- ROWS BETWEEN 2 PRECEDING and RANGE BETWEEN '2 days' PRECEDING
-- give DIFFERENT answers because of it.
INSERT INTO practice.sales_daily VALUES
    ('2024-01-01','North',100), ('2024-01-01','South', 80),
    ('2024-01-02','North',120), ('2024-01-02','South', 95),
    ('2024-01-03','North', 90), ('2024-01-03','South',110),
    ('2024-01-04','North',150), ('2024-01-04','South', 70),
    ('2024-01-06','North',130), ('2024-01-06','South',125),
    ('2024-01-07','North', 60), ('2024-01-07','South', 90),
    ('2024-01-08','North',200), ('2024-01-08','South',105);

CREATE TABLE practice.signups (
    id    int PRIMARY KEY,
    email text,              -- nullable on purpose
    plan  text
);

-- Duplicates AND nulls, so DISTINCT behaviour is visible.
INSERT INTO practice.signups VALUES
    (1,'a@x.com','free'),
    (2,'a@x.com','free'),      -- exact duplicate of row 1 (ignoring id)
    (3,'a@x.com','pro'),       -- same email, different plan
    (4,'b@x.com','pro'),
    (5, NULL,    'free'),
    (6, NULL,    'free'),      -- two NULLs: DISTINCT treats them as ONE
    (7, NULL,    'pro');
